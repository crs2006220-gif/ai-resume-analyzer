import json

from openai import AsyncOpenAI

from app.config import config

_client = AsyncOpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)

EXTRACT_PROMPT = """你是一位专业的简历解析专家。请从以下简历文本中提取结构化信息，以 JSON 格式返回。

要求：
1. 提取姓名(name)、邮箱(email)、电话(phone)
2. 教育经历(education)：学校(school)、专业(major)、学历(degree)、时间(period)
3. 工作经历(experience)：公司(company)、职位(position)、时间(period)、主要职责(description)
4. 技能(skills)：列出所有技能

请严格按照以下 JSON schema 返回，不要包含其他内容：
{{
  "name": "",
  "email": "",
  "phone": "",
  "education": [{{"school": "", "major": "", "degree": "", "period": ""}}],
  "experience": [{{"company": "", "position": "", "period": "", "description": ""}}],
  "skills": []
}}

简历文本：
{resume_text}"""


async def extract_resume_info(resume_text: str) -> dict:
    prompt = EXTRACT_PROMPT.format(resume_text=resume_text[:8000])
    response = await _client.chat.completions.create(
        model=config.DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    content = response.choices[0].message.content or "{}"
    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
    return json.loads(content)
