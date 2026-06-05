from pathlib import Path
from config import OPENAI_MODEL
from ai.client import get_client
from ai.schemas import TailoredResume


def tailor_resume(master_resume: str, job_description: str, output_path: Path) -> Path:
    client = get_client()
    response = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Rewrite the resume to match the job while staying truthful. "
                    "Return structured sections. Emphasize keywords from the job description."
                ),
            },
            {
                "role": "user",
                "content": f"MASTER RESUME:\n{master_resume}\n\nJOB DESCRIPTION:\n{job_description}",
            },
        ],
        response_format=TailoredResume,
    )
    resume: TailoredResume = response.choices[0].message.parsed
    output_path.write_text(resume.to_text(), encoding="utf-8")
    return output_path
