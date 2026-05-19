import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

UPLOADS = ROOT / "uploads"
UPLOADS.mkdir(exist_ok=True)

SHORT_ANSWER_WORDS = 25

WEIGHTS = {
    "relevance": 0.40,
    "communication": 0.25,
    "confidence": 0.20,
    "technical": 0.15,
}
