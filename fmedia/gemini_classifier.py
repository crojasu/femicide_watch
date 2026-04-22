import os
import time
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MAX_TEXT_CHARS = 800  # title + first paragraph only — saves ~10x tokens
_last_request_time = 0.0
_MIN_INTERVAL = 2.0  # ~30 RPM safe rate for free tier

PROMPT = """You are a classifier for news articles about femicide.

Femicide is the killing of a woman or girl because of her gender. This includes intimate partner violence resulting in death, honor killings, and other gender-motivated murders of women.

Article:
{text}

Does this article report on a specific femicide case or directly cover femicide as its main subject?
Answer with only: true or false"""


def _rate_limit() -> None:
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request_time = time.time()


def classify(text: str, rate_limit: bool = False) -> bool | None:
    """Classify article text using Groq + Llama 3.1 70B.

    Returns True/False, or None if Groq is unavailable/failed.
    Set rate_limit=True for batch/historical processing.
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — skipping LLM classification")
        return None

    if rate_limit:
        _rate_limit()

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": PROMPT.format(text=text[:MAX_TEXT_CHARS])}],
            temperature=0,
            max_tokens=10,
        )
        answer = response.choices[0].message.content.strip().lower()
        return "true" in answer
    except Exception as e:
        logger.warning(f"Groq classification failed: {e}")
        return None
