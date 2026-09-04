import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
try:
    from groq import Groq
except ImportError:  # Keep the rule-based backend usable without the optional AI package.
    Groq = None


# ============================================================
# LOAD BACKEND ENVIRONMENT VARIABLES
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]

load_dotenv(
    BACKEND_DIR / ".env"
)


# ============================================================
# CONFIGURATION
# ============================================================

GROQ_API_KEY = (
    os.getenv("GROQ_API_KEY") or ""
).strip()


GROQ_MODEL = (
    os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-20b"
    )
).strip()


# ============================================================
# GROQ CLIENT
# ============================================================

client = None


if GROQ_API_KEY and Groq is not None:
    client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# AI AVAILABILITY
# ============================================================

class _AIAvailability:

    def __bool__(self):
        return client is not None

    def __call__(self):
        return client is not None


ai_available = _AIAvailability()


# ============================================================
# GENERATE STRUCTURED JSON
# ============================================================

def generate_json(
    prompt: str | None = None,
    system_prompt: str = (
        "You are a precise data extraction engine. "
        "Return only valid JSON. "
        "Do not use markdown. "
        "Do not include explanations."
    ),
    model: str | None = None,
    user_prompt: str | None = None,
    schema_name: str | None = None,
    schema: dict | None = None,
) -> dict:

    if client is None:
        raise RuntimeError(
            "Groq AI is unavailable. "
            "Check GROQ_API_KEY in backend/.env"
        )

    final_prompt = (
        user_prompt
        if user_prompt is not None
        else prompt
    )

    if not final_prompt:
        raise ValueError(
            "A prompt or user_prompt must be provided."
        )

    final_system_prompt = system_prompt

    if schema:
        final_system_prompt = (
            f"{system_prompt}\n\n"
            "You must follow this JSON structure exactly. "
            "Return a single valid JSON object and nothing else.\n\n"
            f"JSON SCHEMA:\n"
            f"{json.dumps(schema, indent=2)}"
        )

    response = client.chat.completions.create(
        model=model or GROQ_MODEL,

        messages=[
            {
                "role": "system",
                "content": final_system_prompt,
            },
            {
                "role": "user",
                "content": final_prompt,
            },
        ],

        temperature=0,

        response_format={
            "type": "json_object"
        },
    )

    raw_content = (
        response
        .choices[0]
        .message
        .content
        or "{}"
    )

    clean_content = re.sub(
        r"^```(?:json)?|```$",
        "",
        raw_content.strip(),
        flags=re.IGNORECASE,
    ).strip()

    try:
        data = json.loads(
            clean_content
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "Groq returned invalid JSON: "
            f"{clean_content[:500]}"
        ) from error

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "Groq response was not a JSON object."
        )

    return data