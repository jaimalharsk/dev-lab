from config import OPENAI_MODEL
from ai.client import get_client
from ai.schemas import JobRelevanceResult


def score_job_relevance(candidate_profile: str, job_description: str) -> JobRelevanceResult:
    client = get_client()
    response = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict recruiter assistant. Score the job fit across four dimensions "
                    "(each 0.0–1.0): "
                    "role_match (skills/experience overlap), "
                    "level_fit (seniority alignment), "
                    "growth_potential (career growth opportunity), "
                    "remote_alignment (work arrangement preference). "
                    "A composite score is computed as weighted average — be calibrated, not generous."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Candidate profile:\n{candidate_profile}\n\n"
                    f"Job description:\n{job_description}"
                ),
            },
        ],
        response_format=JobRelevanceResult,
    )
    return response.choices[0].message.parsed
