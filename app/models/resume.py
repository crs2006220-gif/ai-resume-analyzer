from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    position: str = Field(default="", description="Target position for analysis context")
    language: str = Field(default="zh", description="Response language, zh or en")


class ResumeInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    education: list[dict] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class ScoreDetail(BaseModel):
    overall: float = Field(default=0.0, ge=0, le=100, description="Overall score")
    matching: float = Field(default=0.0, ge=0, le=100, description="Position matching score")
    structure: float = Field(default=0.0, ge=0, le=100, description="Resume structure score")
    content: float = Field(default=0.0, ge=0, le=100, description="Content quality score")


class ResumeAnalysisResponse(BaseModel):
    resume_info: ResumeInfo = Field(default_factory=ResumeInfo)
    scores: ScoreDetail = Field(default_factory=ScoreDetail)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    summary: str = ""


class MatchingRequest(BaseModel):
    resume_info: dict
    position: str


class ErrorResponse(BaseModel):
    detail: str
