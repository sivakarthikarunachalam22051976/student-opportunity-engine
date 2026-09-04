from .client import GROQ_MODEL, GROQ_API_KEY, ai_available

# Backward-compatible names retained for any older modules.
AI_MODEL = GROQ_MODEL
AI_PROVIDER = "groq"
XAI_API_KEY = ""

__all__ = [
    "AI_MODEL",
    "AI_PROVIDER",
    "XAI_API_KEY",
    "GROQ_MODEL",
    "GROQ_API_KEY",
    "ai_available",
]
