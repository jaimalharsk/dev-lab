from typing import Literal
from pydantic import BaseModel, Field, computed_field


class SalaryRange(BaseModel):
    is_disclosed: bool
    min_salary: int | None = None
    max_salary: int | None = None
    currency: str = "USD"
    period: Literal["annual", "monthly", "hourly"] = "annual"

    def display(self) -> str:
        if not self.is_disclosed or self.min_salary is None:
            return "not disclosed"
        sym = {"USD": "$", "GBP": "£", "EUR": "€"}.get(self.currency, self.currency)
        suffix = {"annual": "/yr", "monthly": "/mo", "hourly": "/hr"}[self.period]
        hi = f"–{sym}{self.max_salary:,}" if self.max_salary else "+"
        return f"{sym}{self.min_salary:,}{hi}{suffix}"


class JobRelevanceResult(BaseModel):
    role_match: float = Field(..., ge=0.0, le=1.0)
    level_fit: float = Field(..., ge=0.0, le=1.0)
    growth_potential: float = Field(..., ge=0.0, le=1.0)
    remote_alignment: float = Field(..., ge=0.0, le=1.0)
    fit_level: Literal["low", "medium", "high"]
    reasons: list[str] = Field(..., min_length=1)
    recommended_keywords: list[str]

    @computed_field
    @property
    def score(self) -> int:
        composite = (
            self.role_match * 0.45
            + self.level_fit * 0.30
            + self.growth_potential * 0.15
            + self.remote_alignment * 0.10
        )
        return round(composite * 10)


class LivenessResult(BaseModel):
    status: Literal["active", "expired", "uncertain"]
    reason: str


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
