import json

from openai import AsyncOpenAI

from app.config import config

_client = AsyncOpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)

MATCH_PROMPT = """你是一位专业的招聘顾问。请根据候选人的简历信息和目标岗位，评估匹配度并给出详细分析。

候选人信息：
{resume_info}

目标岗位：
{position}

请严格按照以下 JSON schema 返回评分和分析，不要包含其他内容：
{{
  "overall": <0-100 综合匹配度>,
  "matching": <0-100 岗位匹配度>,
  "structure": <0-100 简历结构评分>,
  "content": <0-100 内容质量评分>,
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["建议1", "建议2"],
  "summary": "综合评价总结（200字以内）"
}}"""


async def calculate_match(resume_info: dict, position: str) -> dict:
    prompt = MATCH_PROMPT.format(
        resume_info=json.dumps(resume_info, ensure_ascii=False, indent=2),
        position=position,
    )
    response = await _client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = response.choices[0].message.content or "{}"
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
    return json.loads(content)
