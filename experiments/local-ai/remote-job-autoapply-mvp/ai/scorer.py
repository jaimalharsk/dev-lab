from config import OPENAI_MODEL
from ai.client import get_client


def score_job_relevance(candidate_profile: str, job_description: str) -> int:
    client = get_client()
    prompt = f"""
You are a strict recruiter assistant.
Score job relevance from 1-10 based on candidate profile fit.
Return only an integer.

Candidate profile:
{candidate_profile}

Job description:
{job_description}
"""
    response = client.responses.create(model=OPENAI_MODEL, input=prompt)
    text = response.output_text.strip()
    try:
        return max(1, min(10, int(''.join(ch for ch in text if ch.isdigit())[:2] or "1")))
    except ValueError:
        return 1
