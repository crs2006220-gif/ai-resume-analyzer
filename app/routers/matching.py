from fastapi import APIRouter, HTTPException

from app.config import config
from app.models.resume import ErrorResponse, MatchingRequest, ResumeAnalysisResponse, ScoreDetail
from app.services.matcher import calculate_match

router = APIRouter(prefix=config.API_PREFIX, tags=["matching"])


@router.post(
    "/matching/score",
    response_model=ResumeAnalysisResponse,
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def score_matching(body: MatchingRequest):
    try:
        match_result = await calculate_match(
            resume_info=body.resume_info,
            position=body.position,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"匹配度分析失败: {str(e)}")

    return ResumeAnalysisResponse(
        scores=ScoreDetail(**{
            k: match_result[k]
            for k in ("overall", "matching", "structure", "content")
        }),
        strengths=match_result.get("strengths", []),
        weaknesses=match_result.get("weaknesses", []),
        suggestions=match_result.get("suggestions", []),
        summary=match_result.get("summary", ""),
    )
