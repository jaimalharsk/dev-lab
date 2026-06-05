from pathlib import Path
from config import OPENAI_MODEL
from ai.client import get_client
from ai.schemas import CoverLetter


def generate_cover_letter(company: str, role: str, candidate_profile: str, output_path: Path) -> Path:
    client = get_client()
    response = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Write concise, natural cover letters (120-180 words total). Return structured sections.",
            },
            {
                "role": "user",
                "content": f"Company: {company}\nRole: {role}\n\nCandidate profile:\n{candidate_profile}",
            },
        ],
        response_format=CoverLetter,
    )
    letter: CoverLetter = response.choices[0].message.parsed
    output_path.write_text(letter.to_text(), encoding="utf-8")
    return output_path
