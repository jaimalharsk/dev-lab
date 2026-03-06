from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, Session
from config import DATABASE_URL


Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    company: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(200))
    application_link: Mapped[str] = mapped_column(String(600), unique=True)
    date_found: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    relevance_score: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), unique=True)
    date_applied: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50), default="applied")
    tailored_resume_path: Mapped[str | None] = mapped_column(String(400), nullable=True)
    cover_letter_path: Mapped[str | None] = mapped_column(String(400), nullable=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
