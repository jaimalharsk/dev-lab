from typing import Literal
from pydantic import BaseModel, Field


class JobRelevanceResult(BaseModel):
    score: int = Field(..., ge=1, le=10)
    fit_level: Literal["low", "medium", "high"]
    reasons: list[str] = Field(..., min_length=1)
    recommended_keywords: list[str]


class CoverLetter(BaseModel):
    opening: str
    body: str
    closing: str

    def to_text(self) -> str:
        return f"{self.opening}\n\n{self.body}\n\n{self.closing}"


class TailoredResume(BaseModel):
    summary: str
    skills: list[str]
    experience: list[str]
    education: list[str]

    def to_text(self) -> str:
        sections = [
            "SUMMARY\n" + self.summary,
            "SKILLS\n" + "\n".join(f"- {s}" for s in self.skills),
            "EXPERIENCE\n" + "\n".join(self.experience),
            "EDUCATION\n" + "\n".join(self.education),
        ]
        return "\n\n".join(sections)
