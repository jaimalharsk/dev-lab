from pathlib import Path
import os
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'jobs.db'}")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", "7"))
MAX_APPLICATIONS_PER_DAY = int(os.getenv("MAX_APPLICATIONS_PER_DAY", "5"))
CANDIDATE_PROFILE_PATH = Path(os.getenv("CANDIDATE_PROFILE_PATH", DATA_DIR / "candidate_profile.txt"))
MASTER_RESUME_PATH = Path(os.getenv("MASTER_RESUME_PATH", DATA_DIR / "master_resume.txt"))
