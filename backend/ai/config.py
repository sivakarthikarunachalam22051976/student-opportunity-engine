import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)