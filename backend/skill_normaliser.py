"""Backward-compatible alias for the canonical skill_normalizer module."""
from .skill_normalizer import SKILL_ALIASES, normalize_skill, normalize_skills

__all__ = ["SKILL_ALIASES", "normalize_skill", "normalize_skills"]
