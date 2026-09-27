from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    cv_text: str = Field(..., min_length=1, description="Raw CV / resume text")
    jd_text: str = Field(..., min_length=1, description="Raw job description text")


class MatchResponse(BaseModel):
    cv_profile: dict
    jd_profile: dict
    matching: dict
    scoring: dict
    explanation: dict
