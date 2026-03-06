from pathlib import Path
from config import OPENAI_MODEL
from ai.client import get_client


def generate_cover_letter(company: str, role: str, candidate_profile: str, output_path: Path) -> Path:
    client = get_client()
    prompt = f"""
Write a concise, natural cover letter (120-180 words) for this application.
Company: {company}
Role: {role}
Candidate profile:
{candidate_profile}
"""
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    output_path.write_text(response.output_text.strip(), encoding="utf-8")
    return output_path
