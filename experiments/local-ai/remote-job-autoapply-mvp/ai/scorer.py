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
                "content": "You are a strict recruiter assistant. Evaluate job fit and return structured data.",
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
