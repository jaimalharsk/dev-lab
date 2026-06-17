from ai.client import client
from ai.schemas import SalaryRange
from config import OPENAI_MODEL


def extract_salary(job_description: str) -> SalaryRange:
    resp = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract salary or compensation from the job description. "
                    "Set is_disclosed=False if no salary figure is mentioned. "
                    "Use the stated period (annual/monthly/hourly) — do not convert. "
                    "If a range is given, populate both min_salary and max_salary."
                ),
            },
            {"role": "user", "content": job_description},
        ],
        response_format=SalaryRange,
    )
    return resp.choices[0].message.parsed
