from openai import OpenAI
from config import OPENAI_API_KEY


def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY in environment.")
    return OpenAI(api_key=OPENAI_API_KEY)
