from pathlib import Path
from config import OPENAI_MODEL
from ai.client import get_client


def tailor_resume(master_resume: str, job_description: str, output_path: Path) -> Path:
    client = get_client()
    prompt = f"""
Rewrite the resume to match this job while staying truthful.
Use ATS-friendly plain text with sections: Summary, Skills, Experience, Education.
Emphasize keywords from the job description.

MASTER RESUME:
{master_resume}

JOB DESCRIPTION:
{job_description}
"""
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    output_path.write_text(response.output_text.strip(), encoding="utf-8")
    return output_path
