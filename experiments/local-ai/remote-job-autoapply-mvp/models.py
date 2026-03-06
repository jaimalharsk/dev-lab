from datetime import datetime
from pydantic import BaseModel, HttpUrl


class JobListing(BaseModel):
    source: str
    company: str
    title: str
    description: str
    location: str
    application_link: HttpUrl | str
    date_found: datetime = datetime.utcnow()


class ApplicationRecord(BaseModel):
    job_id: int
    date_applied: datetime = datetime.utcnow()
    status: str = "applied"
    tailored_resume_path: str | None = None
    cover_letter_path: str | None = None
