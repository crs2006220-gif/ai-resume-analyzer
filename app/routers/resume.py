import hashlib
import json as _json

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.config import config
from app.models.resume import (
    ErrorResponse,
    ResumeAnalysisResponse,
    ScoreDetail,
    ResumeInfo,
)
from app.services.ai_extractor import extract_resume_info
from app.services.pdf_parser import parse_pdf
from app.utils.cache import file_hash, get_cached, set_cache

router = APIRouter(prefix=config.API_PREFIX, tags=["resume"])


@router.post(
    "/resume/upload",
    response_model=ResumeAnalysisResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def upload_resume(
    file: UploadFile = File(...),
    position: str = Form(default=""),
):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件格式")

    file_bytes = await file.read()
    fhash = file_hash(file_bytes)
    pos_key = hashlib.md5((position or "通用岗位").encode()).hexdigest()[:8]
    cache_key = f"resume:upload:{fhash}:{pos_key}"

    cached = await get_cached(cache_key)
    if cached:
        return ResumeAnalysisResponse(**cached)

    try:
        resume_text = parse_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF 解析失败: {str(e)}")

    try:
        resume_info = await extract_resume_info(resume_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"简历信息提取失败: {str(e)}")

    from app.services.matcher import calculate_match

    try:
        match_result = await calculate_match(
            resume_info=resume_info,
            position=position or "通用岗位",
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"匹配度分析失败: {str(e)}")

    response_data = {
        "resume_info": resume_info,
        "scores": {k: match_result[k] for k in ("overall", "matching", "structure", "content")},
        "strengths": match_result.get("strengths", []),
        "weaknesses": match_result.get("weaknesses", []),
        "suggestions": match_result.get("suggestions", []),
        "summary": match_result.get("summary", ""),
    }
    await set_cache(cache_key, response_data)

    return ResumeAnalysisResponse(**response_data)


@router.post(
    "/resume/parse",
    response_model=ResumeInfo,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def parse_resume(
    file: UploadFile = File(...),
):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件格式")

    file_bytes = await file.read()
    fhash = file_hash(file_bytes)
    cache_key = f"resume:parse:{fhash}"

    cached = await get_cached(cache_key)
    if cached:
        return ResumeInfo(**cached)

    try:
        resume_text = parse_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"PDF 解析失败: {str(e)}")

    try:
        resume_info = await extract_resume_info(resume_text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"简历信息提取失败: {str(e)}")

    await set_cache(cache_key, resume_info)
    return ResumeInfo(**resume_info)


def _sse(data: dict) -> str:
    return f"data: {_json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/resume/upload/stream")
async def upload_resume_stream(
    file: UploadFile = File(...),
    position: str = Form(default=""),
):
    if file.content_type not in ("application/pdf",):
        raise HTTPException(status_code=400, detail="仅支持 PDF 文件格式")

    file_bytes = await file.read()
    pos = position or "通用岗位"

    async def generate():
        fhash = file_hash(file_bytes)
        pos_key = hashlib.md5(pos.encode()).hexdigest()[:8]
        cache_key = f"resume:upload:{fhash}:{pos_key}"

        cached = await get_cached(cache_key)
        if cached:
            yield _sse({"stage": "cache_hit", "message": "命中缓存，直接返回结果"})
            yield _sse({"stage": "complete", "data": cached})
            return

        yield _sse({"stage": "parse", "message": "正在解析 PDF 文件..."})
        try:
            resume_text = parse_pdf(file_bytes)
        except Exception as e:
            yield _sse({"stage": "error", "message": f"PDF 解析失败: {str(e)}"})
            return
        yield _sse({"stage": "parse_done", "message": f"PDF 解析完成，提取到 {len(resume_text)} 字符"})

        yield _sse({"stage": "extract", "message": "正在调用 AI 提取简历信息..."})
        try:
            resume_info = await extract_resume_info(resume_text)
        except Exception as e:
            yield _sse({"stage": "error", "message": f"AI 提取失败: {str(e)}"})
            return
        yield _sse({"stage": "extract_done", "message": f"提取完成：{resume_info.get('name', '未知')}"})

        yield _sse({"stage": "match", "message": "正在计算匹配度评分..."})
        from app.services.matcher import calculate_match

        try:
            match_result = await calculate_match(
                resume_info=resume_info,
                position=pos,
            )
        except Exception as e:
            yield _sse({"stage": "error", "message": f"匹配度分析失败: {str(e)}"})
            return
        yield _sse({"stage": "match_done", "message": f"综合评分: {match_result.get('overall', 0)}"})

        result = {
            "resume_info": resume_info,
            "scores": {k: match_result[k] for k in ("overall", "matching", "structure", "content")},
            "strengths": match_result.get("strengths", []),
            "weaknesses": match_result.get("weaknesses", []),
            "suggestions": match_result.get("suggestions", []),
            "summary": match_result.get("summary", ""),
        }
        await set_cache(cache_key, result)
        yield _sse({"stage": "cache_saved", "message": "结果已缓存"})
        yield _sse({"stage": "complete", "data": result})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
