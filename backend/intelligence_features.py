"""
Student Opportunity Engine
Intelligence + Reliability Layer

This module contains the deterministic intelligence features used
by the Student Opportunity Engine.

IMPORTANT:
- This file does NOT call Gemini/Groq.
- This file does NOT require an API key.
- It works entirely from profile/opportunity data.
- It is safe to import from FastAPI main.py.
- Existing functions such as profile_intelligence(),
  readiness_simulator(), and application_strategy() are preserved.

Main capabilities:
- Explainable opportunity matching
- Duplicate detection
- Freshness scoring
- Source evidence
- Readiness analysis
- Deadline intelligence
- Best next action
- Portfolio impact
- Opportunity change detection
- Weekly mission generation
- Quality control
- In-memory caching
- Preparation plan export
- Demo snapshot
- Workspace intelligence
"""


from __future__ import annotations

from collections import Counter
from datetime import date, datetime
import hashlib
import re
import time
from typing import Any


# ============================================================
# CONSTANTS
# ============================================================

CACHE_TTL_SECONDS = 300


# Conservative prototype estimates.
# These are NOT claims about real learning time.
# They are only used to make the prototype's preparation
# and investment calculations explainable.
ESTIMATED_LEARNING_HOURS: dict[str, int] = {
    "python": 18,
    "react": 22,
    "fastapi": 16,
    "sql": 18,
    "docker": 12,
    "git": 8,
    "github": 8,
    "javascript": 18,
    "typescript": 18,
    "machine learning": 24,
    "machine learning": 24,
    "tensorflow": 24,
    "pytorch": 24,
    "java": 20,
    "c++": 20,
    "c": 18,
    "data structures": 24,
    "algorithms": 24,
    "node.js": 18,
    "node": 18,
    "nodejs": 18,
    "aws": 20,
    "mongodb": 18,
    "postgresql": 18,
    "mysql": 18,
    "html": 8,
    "css": 10,
    "tailwind": 10,
    "tailwind css": 10,
    "next.js": 20,
    "nextjs": 20,
    "express": 16,
    "express.js": 16,
    "flask": 16,
    "django": 20,
    "rest api": 14,
    "api": 12,
    "gitlab": 8,
    "linux": 14,
    "cloud": 18,
    "azure": 20,
    "gcp": 20,
    "firebase": 14,
    "redis": 12,
    "figma": 10,
    "ui ux": 14,
    "data analysis": 20,
    "pandas": 16,
    "numpy": 12,
    "scikit-learn": 20,
    "scikitlearn": 20,
    "deep learning": 28,
    "nlp": 24,
    "natural language processing": 24,
    "computer vision": 24,
}


# ============================================================
# GENERIC HELPERS
# ============================================================

def _text(value: Any) -> str:
    """
    Convert a value into clean text.
    """
    if value is None:
        return ""

    return str(value).strip()


def _lower(value: Any) -> str:
    """
    Lowercase text safely.
    """
    return _text(value).lower()


def _norm(value: Any) -> str:
    """
    Normalize text for comparisons.

    Examples:
        "Python" -> "python"
        "Node.js" -> "node.js"
        "C++" -> "c++"
        "Machine Learning" -> "machine learning"
    """
    value = _lower(value)

    value = re.sub(
        r"[^a-z0-9+#.\-]+",
        " ",
        value,
    )

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def _list(value: Any) -> list[Any]:
    """
    Return a list if value is a list/tuple/set.
    Otherwise return an empty list.
    """
    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, set):
        return list(value)

    return []


def _clean_list(value: Any) -> list[str]:
    """
    Return unique, cleaned string values while preserving order.
    """
    output: list[str] = []
    seen: set[str] = set()

    for item in _list(value):

        text = _text(item)
        normalized = _norm(text)

        if not text or not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        output.append(text)

    return output


def _skills(value: Any) -> list[str]:
    """
    Clean a skill list.

    This intentionally returns a list rather than a set so that
    original display values can be preserved in API responses.
    """
    return _clean_list(value)


def _skill_set(value: Any) -> set[str]:
    """
    Return normalized skills as a set.
    """
    return {
        _norm(skill)
        for skill in _skills(value)
        if _norm(skill)
    }


def _safe_number(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Safely convert a value to float.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(
    value: float,
    minimum: float = 0.0,
    maximum: float = 100.0,
) -> float:
    """
    Clamp a numeric value into a range.
    """
    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def _dedupe_preserve_order(
    values: list[str],
) -> list[str]:
    """
    Remove duplicate strings without changing order.
    """
    output: list[str] = []
    seen: set[str] = set()

    for value in values:

        normalized = _norm(value)

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)
        output.append(value)

    return output


# ============================================================
# DATE HELPERS
# ============================================================

def _parse_date(
    value: Any,
) -> date | None:
    """
    Parse common date formats.

    Supported examples:
        2026-08-31
        2026-08-31T12:00:00
        2026-08-31T12:00:00Z
    """
    raw = _text(value)

    if not raw:
        return None

    raw = raw[:10]

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _days(deadline: Any) -> int | None:
    """
    Calculate days remaining from an ISO-style deadline.

    Returns None when unavailable or invalid.
    """
    deadline_date = _parse_date(deadline)

    if deadline_date is None:
        return None

    return (
        deadline_date - date.today()
    ).days


# ============================================================
# LEARNING ESTIMATION
# ============================================================

def _estimated_hours(
    missing: list[str],
) -> int:
    """
    Estimate preparation hours for missing skills.

    Unknown skills receive a conservative 12-hour estimate.
    """
    total = 0

    for skill in missing:

        normalized = _norm(skill)

        total += ESTIMATED_LEARNING_HOURS.get(
            normalized,
            12,
        )

    return total


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES: dict[str, set[str]] = {
    "python": {
        "python",
    },
    "javascript": {
        "javascript",
        "js",
    },
    "typescript": {
        "typescript",
        "ts",
    },
    "react": {
        "react",
        "react.js",
        "reactjs",
    },
    "node.js": {
        "node",
        "node.js",
        "nodejs",
    },
    "next.js": {
        "next",
        "next.js",
        "nextjs",
    },
    "fastapi": {
        "fastapi",
    },
    "c++": {
        "c++",
        "cpp",
    },
    "c": {
        "c",
    },
    "sql": {
        "sql",
        "structured query language",
    },
    "machine learning": {
        "machine learning",
        "ml",
    },
    "deep learning": {
        "deep learning",
        "dl",
    },
    "natural language processing": {
        "natural language processing",
        "nlp",
    },
    "computer vision": {
        "computer vision",
        "cv",
    },
}


def _canonical_skill(
    value: Any,
) -> str:
    """
    Convert common skill aliases into a canonical form.
    """
    normalized = _norm(value)

    if not normalized:
        return ""

    for canonical, aliases in SKILL_ALIASES.items():

        normalized_aliases = {
            _norm(alias)
            for alias in aliases
        }

        if normalized in normalized_aliases:
            return canonical

    return normalized


def _canonical_skill_set(
    value: Any,
) -> set[str]:
    """
    Canonical normalized skill set.
    """
    result: set[str] = set()

    for skill in _skills(value):

        canonical = _canonical_skill(skill)

        if canonical:
            result.add(canonical)

    return result


# ============================================================
# CORE MATCHING
# ============================================================

def _match(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> tuple[
    int,
    list[str],
    list[str],
]:
    """
    Calculate a deterministic explainable match score.

    Score:
        Skills       = 60
        Interests    = 20
        Branch       = 15
        Location     = 5
        ----------------
        Total        = 100
    """

    student_skills = _canonical_skill_set(
        profile.get(
            "skills",
            [],
        )
    )

    required_skills = _skills(
        opportunity.get(
            "skills",
            [],
        )
    )

    matched: list[str] = []
    missing: list[str] = []

    for skill in required_skills:

        canonical = _canonical_skill(skill)

        if canonical in student_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    # --------------------------------------------------------
    # Skill score
    # --------------------------------------------------------

    if required_skills:

        skill_score = (
            len(matched)
            / len(required_skills)
            * 60
        )

    else:
        # A listing with no explicit skills should not
        # automatically receive a perfect skill score.
        skill_score = 30

    # --------------------------------------------------------
    # Interest score
    # --------------------------------------------------------

    interests = _skills(
        profile.get(
            "interests",
            [],
        )
    )

    opportunity_text = _norm(
        " ".join(
            [
                _text(
                    opportunity.get(
                        "title",
                    )
                ),
                _text(
                    opportunity.get(
                        "description",
                    )
                ),
                *required_skills,
                *_skills(
                    opportunity.get(
                        "tags",
                        [],
                    )
                ),
            ]
        )
    )

    interest_hits = 0

    for interest in interests:

        normalized_interest = _norm(
            interest
        )

        if not normalized_interest:
            continue

        if normalized_interest in opportunity_text:
            interest_hits += 1
            continue

        canonical_interest = _canonical_skill(
            interest
        )

        if canonical_interest:
            if canonical_interest in {
                _canonical_skill(skill)
                for skill in required_skills
            }:
                interest_hits += 1

    if interests:

        interest_score = (
            interest_hits
            / len(interests)
            * 20
        )

    else:
        interest_score = 8

    interest_score = min(
        20,
        interest_score,
    )

    # --------------------------------------------------------
    # Branch score
    # --------------------------------------------------------

    profile_branch = _norm(
        profile.get(
            "branch",
            "",
        )
    )

    opportunity_branches = {
        _norm(branch)
        for branch in _skills(
            opportunity.get(
                "branches",
                [],
            )
        )
    }

    if not opportunity_branches:

        branch_score = 15

    elif not profile_branch:

        # Missing student branch should not be treated as
        # a branch mismatch.
        branch_score = 8

    elif profile_branch in opportunity_branches:

        branch_score = 15

    else:

        # Lightweight partial branch matching.
        branch_match = any(
            profile_branch in branch
            or branch in profile_branch
            for branch in opportunity_branches
        )

        branch_score = (
            10
            if branch_match
            else 0
        )

    # --------------------------------------------------------
    # Location score
    # --------------------------------------------------------

    profile_location = _norm(
        profile.get(
            "location",
            "",
        )
    )

    opportunity_location = _norm(
        opportunity.get(
            "location",
            "",
        )
    )

    remote = opportunity.get(
        "remote"
    )

    if remote is True:

        location_score = 5

    elif (
        not profile_location
        or not opportunity_location
    ):

        # Unknown location should not destroy an otherwise
        # good match.
        location_score = 3

    elif (
        profile_location in opportunity_location
        or opportunity_location in profile_location
    ):

        location_score = 5

    else:

        location_score = 0

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    total = round(
        _clamp(
            skill_score
            + interest_score
            + branch_score
            + location_score,
            0,
            100,
        )
    )

    return (
        total,
        matched,
        missing,
    )


# ============================================================
# PUBLIC DECISION ENGINE
# ============================================================

def decision_for(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate an explainable decision for one opportunity.
    """

    match_score, matched, missing = _match(
        profile,
        opportunity,
    )

    required_skills = _skills(
        opportunity.get(
            "skills",
            [],
        )
    )

    # --------------------------------------------------------
    # Readiness
    # --------------------------------------------------------

    if required_skills:

        readiness = round(
            len(matched)
            / len(required_skills)
            * 100
        )

    else:

        readiness = 50

    readiness = int(
        _clamp(
            readiness,
            0,
            100,
        )
    )

    # --------------------------------------------------------
    # Deadline
    # --------------------------------------------------------

    days_remaining = _days(
        opportunity.get(
            "deadline"
        )
    )

    # --------------------------------------------------------
    # Preparation estimate
    # --------------------------------------------------------

    estimated_hours = _estimated_hours(
        missing
    )

    # --------------------------------------------------------
    # Action decision
    # --------------------------------------------------------

    if (
        days_remaining is not None
        and days_remaining < 0
    ):

        action = "LOW PRIORITY"

    elif (
        match_score >= 75
        and readiness >= 70
    ):

        action = "APPLY NOW"

    elif (
        match_score >= 60
        and readiness >= 45
    ):

        action = "APPLY + PREPARE"

    elif match_score >= 45:

        action = "PREPARE FIRST"

    elif match_score >= 30:

        action = "SAVE FOR FUTURE"

    else:

        action = "LOW PRIORITY"

    # --------------------------------------------------------
    # Deadline feasibility
    # --------------------------------------------------------

    if days_remaining is None:

        ready_before_deadline = None

    else:

        available_hours = (
            max(
                0,
                days_remaining,
            )
            * 2
        )

        ready_before_deadline = (
            estimated_hours
            <= available_hours
        )

    return {
        "match_score": match_score,
        "readiness": readiness,
        "matched_skills": matched,
        "missing_skills": missing,
        "estimated_hours": estimated_hours,
        "days_remaining": days_remaining,
        "action": action,
        "ready_before_deadline": ready_before_deadline,
    }


# ============================================================
# STEP 38 — DUPLICATE DETECTION
# ============================================================

def opportunity_fingerprint(
    opportunity: dict[str, Any],
) -> str:
    """
    Generate a stable fingerprint for an opportunity.

    Uses:
        title
        organization/company
        source/application URL
    """

    title = _norm(
        opportunity.get(
            "title"
        )
    )

    organization = _norm(
        opportunity.get(
            "organization"
        )
        or opportunity.get(
            "company"
        )
    )

    source = _lower(
        opportunity.get(
            "source_url"
        )
        or opportunity.get(
            "application_url"
        )
        or opportunity.get(
            "link"
        )
        or opportunity.get(
            "url"
        )
    )

    raw = "|".join(
        [
            title,
            organization,
            source,
        ]
    )

    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


def remove_duplicate_opportunities(
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Remove duplicate opportunities while preserving order.
    """

    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    for opportunity in opportunities:

        fingerprint = (
            opportunity_fingerprint(
                opportunity
            )
        )

        if fingerprint in seen:
            continue

        seen.add(fingerprint)
        result.append(opportunity)

    return result


# ============================================================
# STEP 39 — FRESHNESS INTELLIGENCE
# ============================================================

def calculate_freshness(
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate freshness from posted_time_ago.
    """

    posted = _text(
        opportunity.get(
            "posted_time_ago"
        )
    )

    if not posted:

        return {
            "freshness_score": 50,
            "freshness_label": "Unknown",
        }

    value = _lower(
        posted
    )

    # --------------------------------------------------------
    # Minutes
    # --------------------------------------------------------

    if "minute" in value:

        score = 100
        label = "Very Fresh"

    # --------------------------------------------------------
    # Hours
    # --------------------------------------------------------

    elif "hour" in value:

        score = 95
        label = "Very Fresh"

    # --------------------------------------------------------
    # Days
    # --------------------------------------------------------

    elif "day" in value:

        match = re.search(
            r"\d+",
            value,
        )

        number = (
            int(match.group())
            if match
            else 7
        )

        if number <= 1:

            score = 90
            label = "Fresh"

        elif number <= 3:

            score = 80
            label = "Fresh"

        elif number <= 7:

            score = 65
            label = "Recent"

        elif number <= 14:

            score = 50
            label = "Older"

        else:

            score = 40
            label = "Older"

    # --------------------------------------------------------
    # Weeks
    # --------------------------------------------------------

    elif "week" in value:

        score = 30
        label = "Older"

    # --------------------------------------------------------
    # Months
    # --------------------------------------------------------

    elif "month" in value:

        score = 15
        label = "Stale"

    else:

        score = 50
        label = "Unknown"

    return {
        "freshness_score": score,
        "freshness_label": label,
    }


# ============================================================
# STEP 40 — SOURCE EVIDENCE
# ============================================================

def build_source_evidence(
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Build explainable source evidence.
    """

    source_url = _text(
        opportunity.get(
            "source_url"
        )
    )

    application_url = _text(
        opportunity.get(
            "application_url"
        )
    )

    if not application_url:

        application_url = _text(
            opportunity.get(
                "link"
            )
        )

    if not application_url:

        application_url = _text(
            opportunity.get(
                "url"
            )
        )

    verification = _text(
        opportunity.get(
            "verification_score"
        )
    )

    evidence: list[str] = []

    if source_url:

        evidence.append(
            "A source URL was identified."
        )

    if application_url:

        evidence.append(
            "A direct application URL was identified."
        )

    if verification:

        evidence.append(
            f"Verification level: {verification}."
        )

    if opportunity.get(
        "is_still_accepting"
    ) is True:

        evidence.append(
            "The opportunity is marked as currently accepting applications."
        )

    if not evidence:

        evidence.append(
            "Limited source evidence is available."
        )

    return {
        "source_url": source_url or None,
        "application_url": application_url or None,
        "verification_score": (
            verification
            or "Unknown"
        ),
        "evidence": evidence,
    }


# ============================================================
# STEP 41 — EXPLAINABLE RANKING
# ============================================================

def explain_ranking(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Return the explainable ranking breakdown.
    """

    score, matched, missing = _match(
        profile,
        opportunity,
    )

    required_skills = _skills(
        opportunity.get(
            "skills",
            [],
        )
    )

    # --------------------------------------------------------
    # Recalculate factor scores so the explanation matches
    # the actual score.
    # --------------------------------------------------------

    if required_skills:

        skill_points = (
            len(matched)
            / len(required_skills)
            * 60
        )

    else:

        skill_points = 30

    interests = _skills(
        profile.get(
            "interests",
            [],
        )
    )

    opportunity_text = _norm(
        " ".join(
            [
                _text(
                    opportunity.get(
                        "title"
                    )
                ),
                _text(
                    opportunity.get(
                        "description"
                    )
                ),
                *required_skills,
                *_skills(
                    opportunity.get(
                        "tags",
                        [],
                    )
                ),
            ]
        )
    )

    interest_hits = 0

    for interest in interests:

        normalized_interest = _norm(
            interest
        )

        if not normalized_interest:
            continue

        if normalized_interest in opportunity_text:
            interest_hits += 1
            continue

        canonical_interest = _canonical_skill(
            interest
        )

        required_canonical = {
            _canonical_skill(skill)
            for skill in required_skills
        }

        if (
            canonical_interest
            and canonical_interest
            in required_canonical
        ):
            interest_hits += 1

    if interests:

        interest_points = (
            interest_hits
            / len(interests)
            * 20
        )

    else:

        interest_points = 8

    interest_points = min(
        20,
        interest_points,
    )

    profile_branch = _norm(
        profile.get(
            "branch"
        )
    )

    branches = {
        _norm(branch)
        for branch in _skills(
            opportunity.get(
                "branches",
                [],
            )
        )
    }

    if not branches:

        branch_points = 15

    elif not profile_branch:

        branch_points = 8

    elif profile_branch in branches:

        branch_points = 15

    elif any(
        profile_branch in branch
        or branch in profile_branch
        for branch in branches
    ):

        branch_points = 10

    else:

        branch_points = 0

    profile_location = _norm(
        profile.get(
            "location"
        )
    )

    opportunity_location = _norm(
        opportunity.get(
            "location"
        )
    )

    if opportunity.get(
        "remote"
    ) is True:

        location_points = 5

    elif (
        not profile_location
        or not opportunity_location
    ):

        location_points = 3

    elif (
        profile_location
        in opportunity_location
        or
        opportunity_location
        in profile_location
    ):

        location_points = 5

    else:

        location_points = 0

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "factors": [
            {
                "factor": "Skill alignment",
                "points": round(
                    skill_points
                ),
                "maximum": 60,
            },
            {
                "factor": "Interest alignment",
                "points": round(
                    interest_points
                ),
                "maximum": 20,
            },
            {
                "factor": "Branch eligibility",
                "points": branch_points,
                "maximum": 15,
            },
            {
                "factor": "Location / remote fit",
                "points": location_points,
                "maximum": 5,
            },
        ],
    }


# ============================================================
# STEP 42 — READINESS CHECKLIST
# ============================================================

def readiness_checklist(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Generate an explainable application-readiness checklist.
    """

    required = _skills(
        opportunity.get(
            "skills"
        )
    )

    student = _canonical_skill_set(
        profile.get(
            "skills"
        )
    )

    checklist: list[dict[str, Any]] = []

    # --------------------------------------------------------
    # Required skills
    # --------------------------------------------------------

    for skill in required:

        canonical = _canonical_skill(
            skill
        )

        checklist.append(
            {
                "item": skill,
                "complete": (
                    canonical in student
                ),
                "category": "Skill",
                "importance": "High",
            }
        )

    # --------------------------------------------------------
    # Deadline
    # --------------------------------------------------------

    if opportunity.get(
        "deadline"
    ):

        deadline_days = _days(
            opportunity.get(
                "deadline"
            )
        )

        checklist.append(
            {
                "item": "Application deadline reviewed",
                "complete": (
                    deadline_days is not None
                ),
                "category": "Deadline",
                "importance": "High",
            }
        )

    # --------------------------------------------------------
    # Application URL
    # --------------------------------------------------------

    application_url = (
        opportunity.get(
            "application_url"
        )
        or opportunity.get(
            "source_url"
        )
        or opportunity.get(
            "link"
        )
        or opportunity.get(
            "url"
        )
    )

    if application_url:

        checklist.append(
            {
                "item": "Application/source link available",
                "complete": True,
                "category": "Application",
                "importance": "High",
            }
        )

    else:

        checklist.append(
            {
                "item": "Application/source link available",
                "complete": False,
                "category": "Application",
                "importance": "High",
            }
        )

    # --------------------------------------------------------
    # Resume
    # --------------------------------------------------------

    checklist.append(
        {
            "item": "Resume tailored to opportunity",
            "complete": False,
            "category": "Application",
            "importance": "Medium",
        }
    )

    # --------------------------------------------------------
    # Portfolio evidence
    # --------------------------------------------------------

    has_projects = bool(
        _list(
            profile.get(
                "projects"
            )
        )
    )

    has_evidence = bool(
        _list(
            profile.get(
                "evidence"
            )
        )
    )

    checklist.append(
        {
            "item": "Portfolio evidence prepared",
            "complete": (
                has_projects
                or has_evidence
            ),
            "category": "Portfolio",
            "importance": "Medium",
        }
    )

    return checklist


# ============================================================
# STEP 43 — DEADLINE COUNTDOWN
# ============================================================

def deadline_intelligence(
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate deadline countdown and urgency.
    """

    raw = opportunity.get(
        "deadline"
    )

    if not raw:

        return {
            "days_remaining": None,
            "urgency": "Unknown",
        }

    deadline = _parse_date(
        raw
    )

    if deadline is None:

        return {
            "days_remaining": None,
            "urgency": "Unknown",
        }

    days = (
        deadline
        - date.today()
    ).days

    if days < 0:

        urgency = "Expired"

    elif days <= 2:

        urgency = "Critical"

    elif days <= 5:

        urgency = "Urgent"

    elif days <= 10:

        urgency = "Soon"

    else:

        urgency = "Normal"

    return {
        "days_remaining": days,
        "urgency": urgency,
    }


# ============================================================
# STEP 44 — BEST NEXT ACTION
# ============================================================

def best_next_action(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Select the most useful immediate action.
    """

    deadline = deadline_intelligence(
        opportunity
    )

    checklist = readiness_checklist(
        profile,
        opportunity,
    )

    incomplete = [
        item
        for item in checklist
        if not item["complete"]
    ]

    # --------------------------------------------------------
    # Deadline has highest priority.
    # --------------------------------------------------------

    if deadline["urgency"] == "Critical":

        return {
            "action": "Apply / verify immediately",
            "reason": (
                "The deadline is within two days, "
                "so immediate application readiness "
                "has priority."
            ),
            "priority": "Critical",
        }

    if deadline["urgency"] == "Urgent":

        return {
            "action": "Apply / verify immediately",
            "reason": (
                "The deadline is close, so application "
                "readiness has priority."
            ),
            "priority": "Critical",
        }

    # --------------------------------------------------------
    # Missing requirements.
    # --------------------------------------------------------

    if incomplete:

        first = incomplete[0]

        return {
            "action": first["item"],
            "reason": (
                "Completing this item improves "
                "your application readiness."
            ),
            "priority": first["importance"],
        }

    return {
        "action": "Review application and apply",
        "reason": (
            "The main readiness checks are complete."
        ),
        "priority": "High",
    }


# ============================================================
# STEP 45 — PORTFOLIO IMPACT
# ============================================================

def portfolio_impact(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Estimate how portfolio work could improve the profile.
    """

    existing_projects = len(
        _list(
            profile.get(
                "projects"
            )
        )
    )

    required_skills = _canonical_skill_set(
        opportunity.get(
            "skills"
        )
    )

    student_skills = _canonical_skill_set(
        profile.get(
            "skills"
        )
    )

    missing = sorted(
        required_skills
        - student_skills
    )

    matched_count = len(
        required_skills
        & student_skills
    )

    if missing:

        display_missing = [
            skill
            for skill in _skills(
                opportunity.get(
                    "skills"
                )
            )
            if _canonical_skill(skill)
            in missing
        ]

        project_value = (
            "Build a focused project demonstrating "
            + ", ".join(
                display_missing[:3]
            )
        )

    else:

        project_value = (
            "Strengthen an existing project with "
            "measurable results, documentation and "
            "clear technical ownership."
        )

    portfolio_value = (
        50
        + existing_projects * 10
        + matched_count * 8
    )

    portfolio_value = int(
        _clamp(
            portfolio_value,
            0,
            100,
        )
    )

    return {
        "existing_projects": existing_projects,
        "missing_skill_count": len(
            missing
        ),
        "recommended_project": project_value,
        "portfolio_value": portfolio_value,
    }


# ============================================================
# STEP 47 — CHANGE DETECTION
# ============================================================

def detect_changes(
    previous: dict[str, Any] | None,
    current: dict[str, Any],
) -> list[str]:
    """
    Compare two opportunity snapshots.
    """

    if not previous:

        return [
            "This opportunity has no previous snapshot."
        ]

    changes: list[str] = []

    fields = [
        (
            "title",
            "Title",
        ),
        (
            "organization",
            "Organization",
        ),
        (
            "company",
            "Company",
        ),
        (
            "deadline",
            "Deadline",
        ),
        (
            "stipend",
            "Stipend",
        ),
        (
            "location",
            "Location",
        ),
        (
            "application_url",
            "Application URL",
        ),
        (
            "source_url",
            "Source URL",
        ),
        (
            "remote",
            "Remote status",
        ),
        (
            "is_still_accepting",
            "Acceptance status",
        ),
    ]

    checked_labels: set[str] = set()

    for field, label in fields:

        if label in checked_labels:
            continue

        # Organization/company are aliases. Compare the
        # effective organization value once.
        if field == "organization":

            old = _text(
                previous.get(
                    "organization"
                )
                or previous.get(
                    "company"
                )
            )

            new = _text(
                current.get(
                    "organization"
                )
                or current.get(
                    "company"
                )
            )

            checked_labels.add(
                "Organization"
            )

            if old != new:

                changes.append(
                    "Organization changed."
                )

            continue

        if field == "company":

            continue

        old = _text(
            previous.get(
                field
            )
        )

        new = _text(
            current.get(
                field
            )
        )

        if old != new:

            changes.append(
                f"{label} changed."
            )

    old_skills = {
        _canonical_skill(skill)
        for skill in _skills(
            previous.get(
                "skills"
            )
        )
    }

    new_skills = {
        _canonical_skill(skill)
        for skill in _skills(
            current.get(
                "skills"
            )
        )
    }

    if old_skills != new_skills:

        changes.append(
            "Required skills changed."
        )

    old_branches = {
        _norm(branch)
        for branch in _skills(
            previous.get(
                "branches"
            )
        )
    }

    new_branches = {
        _norm(branch)
        for branch in _skills(
            current.get(
                "branches"
            )
        )
    }

    if old_branches != new_branches:

        changes.append(
            "Eligible branches changed."
        )

    return _dedupe_preserve_order(
        changes
    )


# ============================================================
# STEP 48 — WEEKLY MISSION
# ============================================================

def weekly_mission(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate one practical weekly mission from the
    highest-impact missing skill.
    """

    student = _canonical_skill_set(
        profile.get(
            "skills"
        )
    )

    missing: Counter[str] = Counter()

    display_names: dict[str, str] = {}

    for opportunity in opportunities:

        for skill in _skills(
            opportunity.get(
                "skills"
            )
        ):

            canonical = _canonical_skill(
                skill
            )

            if not canonical:
                continue

            if canonical not in student:

                missing[canonical] += 1

                display_names.setdefault(
                    canonical,
                    skill,
                )

    ranked = sorted(
        missing.items(),
        key=lambda pair: (
            pair[1],
            _estimated_hours(
                [pair[0]]
            ) * -1,
        ),
        reverse=True,
    )

    if ranked:

        top_skill = ranked[0][0]

        display_skill = display_names.get(
            top_skill,
            top_skill,
        )

        return {
            "title": (
                "Close your highest-impact skill gap"
            ),
            "skill": display_skill,
            "frequency": missing[top_skill],
            "goal": (
                f"Spend this week building practical "
                f"evidence for {display_skill}."
            ),
            "tasks": [
                (
                    f"Learn the core concepts of "
                    f"{display_skill}."
                ),
                (
                    f"Build one small practical "
                    f"project using {display_skill}."
                ),
                (
                    "Document the project and add "
                    "proof to your profile."
                ),
                (
                    "Re-run opportunity matching "
                    "after completion."
                ),
            ],
        }

    return {
        "title": (
            "Strengthen your application profile"
        ),
        "skill": None,
        "frequency": 0,
        "goal": (
            "Turn existing skills into stronger evidence."
        ),
        "tasks": [
            "Improve one portfolio project.",
            "Document measurable results.",
            "Tailor your resume.",
            "Review newly discovered opportunities.",
        ],
    }


# ============================================================
# STEP 49 — QUALITY CONTROLS
# ============================================================

def quality_control(
    opportunities: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Validate opportunity records for obvious data problems.
    """

    issues: list[str] = []

    valid_verification_scores = {
        "high",
        "medium",
        "low",
    }

    for index, opportunity in enumerate(
        opportunities,
        start=1,
    ):

        title = _text(
            opportunity.get(
                "title"
            )
        )

        display_title = (
            title
            or f"Opportunity #{index}"
        )

        if not title:

            issues.append(
                f"{display_title} is missing a title."
            )

        source_url = _text(
            opportunity.get(
                "source_url"
            )
        )

        application_url = _text(
            opportunity.get(
                "application_url"
            )
        )

        link = _text(
            opportunity.get(
                "link"
            )
        )

        url = _text(
            opportunity.get(
                "url"
            )
        )

        if not (
            source_url
            or application_url
            or link
            or url
        ):

            issues.append(
                f"{display_title} has no source/application URL."
            )

        verification = _text(
            opportunity.get(
                "verification_score"
            )
        )

        if (
            verification
            and _lower(verification)
            not in valid_verification_scores
        ):

            issues.append(
                f"{display_title} has an invalid verification score."
            )

        skills = opportunity.get(
            "skills"
        )

        if skills is not None and not isinstance(
            skills,
            list,
        ):

            issues.append(
                f"{display_title} has an invalid skills field."
            )

        branches = opportunity.get(
            "branches"
        )

        if branches is not None and not isinstance(
            branches,
            list,
        ):

            issues.append(
                f"{display_title} has an invalid branches field."
            )

        deadline = opportunity.get(
            "deadline"
        )

        if deadline and _parse_date(
            deadline
        ) is None:

            issues.append(
                f"{display_title} has an invalid deadline."
            )

    return {
        "passed": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues[:50],
    }


# ============================================================
# STEP 50 — SIMPLE IN-MEMORY CACHE
# ============================================================

_CACHE: dict[
    str,
    tuple[
        float,
        Any,
    ],
] = {}


def cache_get(
    key: str,
) -> Any | None:
    """
    Retrieve a cached value if it is still valid.
    """

    item = _CACHE.get(
        key
    )

    if item is None:

        return None

    created_at, value = item

    if (
        time.time()
        - created_at
        > CACHE_TTL_SECONDS
    ):

        _CACHE.pop(
            key,
            None,
        )

        return None

    return value


def cache_set(
    key: str,
    value: Any,
) -> None:
    """
    Store a value in the in-memory cache.
    """

    _CACHE[key] = (
        time.time(),
        value,
    )


def clear_cache() -> None:
    """
    Clear the entire in-memory cache.
    """

    _CACHE.clear()


# ============================================================
# PROFILE INTELLIGENCE
# ============================================================

def profile_intelligence(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate profile-level intelligence across opportunities.

    This preserves the original API expected by main.py.
    """

    evidence = (
        evidence
        if isinstance(
            evidence,
            dict,
        )
        else {}
    )

    skills = _skills(
        profile.get(
            "skills",
            [],
        )
    )

    interests = _skills(
        profile.get(
            "interests",
            [],
        )
    )

    projects = _clean_list(
        evidence.get(
            "projects",
            profile.get(
                "projects",
                [],
            ),
        )
    )

    evidence_items = _clean_list(
        evidence.get(
            "evidence",
            profile.get(
                "evidence",
                [],
            ),
        )
    )

    # --------------------------------------------------------
    # Analyse each opportunity
    # --------------------------------------------------------

    decisions = [
        (
            opportunity,
            decision_for(
                profile,
                opportunity,
            ),
        )
        for opportunity in opportunities
    ]

    categories = Counter(
        decision["action"]
        for _, decision in decisions
    )

    # --------------------------------------------------------
    # Opportunity skill patterns
    # --------------------------------------------------------

    skill_counts: Counter[str] = Counter()

    impact_counts: Counter[str] = Counter()

    skill_display_names: dict[str, str] = {}

    for opportunity, decision in decisions:

        for skill in _skills(
            opportunity.get(
                "skills",
                [],
            )
        ):

            canonical = _canonical_skill(
                skill
            )

            if not canonical:
                continue

            skill_counts[
                canonical
            ] += 1

            skill_display_names.setdefault(
                canonical,
                skill,
            )

        for skill in decision[
            "missing_skills"
        ]:

            canonical = _canonical_skill(
                skill
            )

            if not canonical:
                continue

            impact_counts[
                canonical
            ] += 1

            skill_display_names.setdefault(
                canonical,
                skill,
            )

    pattern_total = max(
        1,
        len(decisions),
    )

    patterns: list[dict[str, Any]] = []

    for skill, count in skill_counts.most_common(
        8
    ):

        patterns.append(
            {
                "skill": skill_display_names.get(
                    skill,
                    skill,
                ),
                "frequency": count,
                "percentage": round(
                    count
                    / pattern_total
                    * 100
                ),
            }
        )

    # --------------------------------------------------------
    # Best skill investments
    # --------------------------------------------------------

    investment: list[dict[str, Any]] = []

    for skill, count in impact_counts.most_common(
        8
    ):

        display_skill = skill_display_names.get(
            skill,
            skill,
        )

        hours = _estimated_hours(
            [display_skill]
        )

        investment.append(
            {
                "skill": display_skill,
                "learning_hours": hours,
                "opportunities_impacted": count,
                "return_per_hour": round(
                    count
                    / max(
                        1,
                        hours,
                    ),
                    2,
                ),
            }
        )

    investment.sort(
        key=lambda item: (
            item[
                "return_per_hour"
            ],
            item[
                "opportunities_impacted"
            ],
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Profile weaknesses
    # --------------------------------------------------------

    weaknesses: list[str] = []

    if not projects:

        weaknesses.append(
            "Your profile has no visible project evidence yet."
        )

    if not evidence_items:

        weaknesses.append(
            "Your claimed skills are not backed by explicit evidence."
        )

    if len(skills) < 3:

        weaknesses.append(
            "Add more concrete skills so the engine can distinguish your strengths."
        )

    if interests and skills:

        skill_canonicals = {
            _canonical_skill(skill)
            for skill in skills
        }

        overlap = sum(
            1
            for interest in interests
            if (
                _canonical_skill(
                    interest
                )
                in skill_canonicals
                or any(
                    _norm(interest)
                    in _norm(skill)
                    or _norm(skill)
                    in _norm(interest)
                    for skill in skills
                )
            )
        )

        if overlap == 0:

            weaknesses.append(
                "Your interests and current skills show limited visible specialization overlap."
            )

    # --------------------------------------------------------
    # Direction drift
    # --------------------------------------------------------

    target_counts: Counter[str] = Counter()

    interest_display_names: dict[str, str] = {}

    for interest in interests:

        canonical = _canonical_skill(
            interest
        )

        if canonical:

            interest_display_names.setdefault(
                canonical,
                interest,
            )

    for opportunity, _ in decisions:

        text = _norm(
            " ".join(
                [
                    _text(
                        opportunity.get(
                            "title"
                        )
                    ),
                    _text(
                        opportunity.get(
                            "description"
                        )
                    ),
                    *_skills(
                        opportunity.get(
                            "skills",
                            [],
                        )
                    ),
                    *_skills(
                        opportunity.get(
                            "tags",
                            [],
                        )
                    ),
                ]
            )
        )

        for interest in interests:

            normalized_interest = _norm(
                interest
            )

            canonical_interest = _canonical_skill(
                interest
            )

            if (
                normalized_interest
                and normalized_interest
                in text
            ):

                target_counts[
                    canonical_interest
                    or normalized_interest
                ] += 1

            elif (
                canonical_interest
                and any(
                    canonical_interest
                    == _canonical_skill(
                        skill
                    )
                    for skill in _skills(
                        opportunity.get(
                            "skills",
                            [],
                        )
                    )
                )
            ):

                target_counts[
                    canonical_interest
                ] += 1

    dominant_interest = ""

    if target_counts:

        dominant_canonical = (
            target_counts
            .most_common(
                1
            )[0][0]
        )

        dominant_interest = (
            interest_display_names.get(
                dominant_canonical,
                dominant_canonical,
            )
        )

    elif interests:

        dominant_interest = interests[0]

    related_skill_hits = 0

    if dominant_interest:

        dominant_canonical = _canonical_skill(
            dominant_interest
        )

        for skill in skills:

            if (
                _canonical_skill(skill)
                == dominant_canonical
            ):

                related_skill_hits += 1

            elif (
                _norm(dominant_interest)
                in _norm(skill)
                or
                _norm(skill)
                in _norm(dominant_interest)
            ):

                related_skill_hits += 1

    if (
        dominant_interest
        and skills
        and related_skill_hits == 0
    ):

        drift = {
            "detected": True,
            "focus": dominant_interest,
            "message": (
                f"You are targeting "
                f"{dominant_interest}-related "
                f"opportunities, but your visible "
                f"skills do not yet show a clear "
                f"specialization in that direction."
            ),
            "action": (
                f"Add one "
                f"{dominant_interest}-focused "
                f"project or strengthen evidence "
                f"for your existing skills."
            ),
        }

    else:

        drift = {
            "detected": False,
            "focus": dominant_interest,
            "message": (
                "Your visible profile is reasonably "
                "aligned with the current opportunity "
                "direction."
            ),
            "action": (
                "Keep building evidence in your "
                "strongest area."
            ),
        }

    # --------------------------------------------------------
    # Skill proof analysis
    # --------------------------------------------------------

    skill_proof: list[dict[str, Any]] = []

    for skill in skills:

        normalized_skill = _norm(
            skill
        )

        canonical_skill = _canonical_skill(
            skill
        )

        project_hit = any(
            (
                normalized_skill
                in _norm(project)
                or canonical_skill
                == _canonical_skill(project)
            )
            for project in projects
        )

        evidence_hit = any(
            (
                normalized_skill
                in _norm(item)
                or canonical_skill
                == _canonical_skill(item)
            )
            for item in evidence_items
        )

        proof_score = (
            35
            + (
                35
                if project_hit
                else 0
            )
            + (
                30
                if evidence_hit
                else 0
            )
        )

        demonstrated = (
            project_hit
            or evidence_hit
        )

        skill_proof.append(
            {
                "skill": skill,
                "proof_score": proof_score,
                "claimed": True,
                "demonstrated": demonstrated,
                "missing_proof": (
                    []
                    if demonstrated
                    else [
                        (
                            "Add a project, repository, "
                            "certificate, assessment or "
                            f"other evidence for {skill}."
                        )
                    ]
                ),
            }
        )

    # --------------------------------------------------------
    # Opportunity timeline
    # --------------------------------------------------------

    timeline = {
        "apply_now": [],
        "prepare_this_week": [],
        "prepare_this_month": [],
        "future_targets": [],
    }

    for opportunity, decision in decisions:

        item = {
            "id": opportunity.get(
                "id"
            ),
            "title": opportunity.get(
                "title",
                "Opportunity",
            ),
            "match_score": decision[
                "match_score"
            ],
            "readiness": decision[
                "readiness"
            ],
            "days_remaining": decision[
                "days_remaining"
            ],
            "action": decision[
                "action"
            ],
        }

        days_remaining = decision[
            "days_remaining"
        ]

        if decision[
            "action"
        ] == "APPLY NOW":

            timeline[
                "apply_now"
            ].append(item)

        elif (
            days_remaining is not None
            and 0 <= days_remaining <= 7
        ):

            timeline[
                "prepare_this_week"
            ].append(item)

        elif (
            days_remaining is not None
            and 8 <= days_remaining <= 31
        ):

            timeline[
                "prepare_this_month"
            ].append(item)

        else:

            timeline[
                "future_targets"
            ].append(item)

    # --------------------------------------------------------
    # Evidence locker
    # --------------------------------------------------------

    locker = [
        {
            "skill": item[
                "skill"
            ],
            "status": (
                "demonstrated"
                if item[
                    "demonstrated"
                ]
                else "claimed only"
            ),
            "proof_score": item[
                "proof_score"
            ],
            "missing_proof": item[
                "missing_proof"
            ],
        }
        for item in skill_proof
    ]

    # --------------------------------------------------------
    # Final profile intelligence
    # --------------------------------------------------------

    return {
        "profile_weaknesses": weaknesses,
        "skill_proof": skill_proof,
        "evidence_locker": locker,
        "direction_drift": drift,
        "opportunity_patterns": patterns,
        "skill_investments": investment,
        "best_skill_investment": (
            investment[0]
            if investment
            else None
        ),
        "decision_counts": dict(
            categories
        ),
        "timeline": timeline,
        "summary": {
            "skills": len(skills),
            "interests": len(interests),
            "projects": len(projects),
            "evidence_items": len(
                evidence_items
            ),
            "opportunities_analysed": len(
                decisions
            ),
        },
    }


# ============================================================
# READINESS SIMULATOR
# ============================================================

def readiness_simulator(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
    added_skills: list[str],
    added_projects: int = 0,
) -> dict[str, Any]:
    """
    Simulate how additional skills/projects could improve
    the student's opportunity readiness.
    """

    simulated = dict(
        profile
    )

    simulated["skills"] = _dedupe_preserve_order(
        _skills(
            profile.get(
                "skills",
                [],
            )
        )
        + _skills(
            added_skills
        )
    )

    base_scores = [
        decision_for(
            profile,
            opportunity,
        )
        for opportunity in opportunities
    ]

    new_scores = [
        decision_for(
            simulated,
            opportunity,
        )
        for opportunity in opportunities
    ]

    unlocked: list[str] = []

    for opportunity, before, after in zip(
        opportunities,
        base_scores,
        new_scores,
    ):

        if (
            before[
                "action"
            ]
            in {
                "LOW PRIORITY",
                "SAVE FOR FUTURE",
                "PREPARE FIRST",
            }
            and after[
                "action"
            ]
            in {
                "APPLY NOW",
                "APPLY + PREPARE",
            }
        ):

            unlocked.append(
                opportunity.get(
                    "title",
                    "Opportunity",
                )
            )

    if base_scores:

        base_readiness = round(
            sum(
                item[
                    "readiness"
                ]
                for item in base_scores
            )
            / len(
                base_scores
            )
        )

    else:

        base_readiness = 0

    if new_scores:

        simulated_readiness = round(
            sum(
                item[
                    "readiness"
                ]
                for item in new_scores
            )
            / len(
                new_scores
            )
        )

    else:

        simulated_readiness = 0

    # Projects are treated as an evidence/readiness boost
    # only for the simulation, not as actual skill ownership.
    simulated_readiness = int(
        _clamp(
            simulated_readiness
            + max(
                0,
                added_projects,
            )
            * 8,
            0,
            100,
        )
    )

    return {
        "current_readiness": base_readiness,
        "simulated_readiness": simulated_readiness,
        "added_skills": _skills(
            added_skills
        ),
        "added_projects": max(
            0,
            added_projects,
        ),
        "new_missing_skills": sorted(
            {
                skill
                for item in new_scores
                for skill in item[
                    "missing_skills"
                ]
            }
        )[:12],
        "unlocked_opportunities": unlocked[
            :20
        ],
        "preparation_hours": sum(
            item[
                "estimated_hours"
            ]
            for item in new_scores
        ),
    }


# ============================================================
# APPLICATION STRATEGY
# ============================================================

def application_strategy(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a simple explainable application strategy.
    """

    decision = decision_for(
        profile,
        opportunity,
    )

    strengths = decision[
        "matched_skills"
    ][:5]

    weaknesses = decision[
        "missing_skills"
    ][:5]

    suggestions: list[str] = []

    for skill in weaknesses:

        suggestions.append(
            f"Add concrete evidence for {skill} "
            "before applying if time permits."
        )

    if not suggestions:

        suggestions.append(
            "Lead with your strongest matching "
            "skills and one concrete project outcome."
        )

    return {
        "strongest_selling_points": (
            strengths
            or [
                "Relevant academic background",
                "Relevant interests",
            ]
        ),
        "weaknesses": (
            weaknesses
            or [
                "No major technical gap detected "
                "from the supplied listing."
            ]
        ),
        "what_to_emphasize": (
            strengths[:3]
            or [
                "Your most relevant project"
            ]
        ),
        "improvements_before_applying": (
            suggestions[:5]
        ),
        "decision": decision[
            "action"
        ],
        "readiness": decision[
            "readiness"
        ],
        "estimated_hours": decision[
            "estimated_hours"
        ],
        "days_remaining": decision[
            "days_remaining"
        ],
    }


# ============================================================
# STEP 54 — EXPORTABLE PREPARATION PLAN
# ============================================================

def export_preparation_plan(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> str:
    """
    Generate a plain-text preparation plan.
    """

    ranking = explain_ranking(
        profile,
        opportunity,
    )

    deadline = deadline_intelligence(
        opportunity,
    )

    checklist = readiness_checklist(
        profile,
        opportunity,
    )

    portfolio = portfolio_impact(
        profile,
        opportunity,
    )

    action = best_next_action(
        profile,
        opportunity,
    )

    organization = (
        opportunity.get(
            "organization"
        )
        or opportunity.get(
            "company"
        )
        or "Unknown"
    )

    lines = [
        "STUDENT OPPORTUNITY ENGINE",
        "PREPARATION PLAN",
        "=" * 50,
        "",
        (
            "Opportunity: "
            f"{opportunity.get('title', 'Unknown')}"
        ),
        (
            "Organization: "
            f"{organization}"
        ),
        (
            f"Match score: "
            f"{ranking['score']}%"
        ),
        "",
        "DEADLINE",
        "-" * 30,
        (
            "Deadline: "
            f"{opportunity.get('deadline') or 'Unknown'}"
        ),
        (
            "Days remaining: "
            f"{deadline['days_remaining']}"
        ),
        (
            "Urgency: "
            f"{deadline['urgency']}"
        ),
        "",
        "BEST NEXT ACTION",
        "-" * 30,
        action["action"],
        action["reason"],
        "",
        "MATCHING SKILLS",
        "-" * 30,
        (
            ", ".join(
                ranking["matched_skills"]
            )
            or "None identified"
        ),
        "",
        "SKILL GAPS",
        "-" * 30,
        (
            ", ".join(
                ranking["missing_skills"]
            )
            or "None identified"
        ),
        "",
        "READINESS CHECKLIST",
        "-" * 30,
    ]

    for item in checklist:

        mark = (
            "[x]"
            if item["complete"]
            else "[ ]"
        )

        lines.append(
            f"{mark} {item['item']}"
        )

    lines.extend(
        [
            "",
            "PORTFOLIO STRATEGY",
            "-" * 30,
            portfolio[
                "recommended_project"
            ],
            "",
            "Generated by Student Opportunity Engine",
        ]
    )

    return "\n".join(
        lines
    )


# ============================================================
# STEP 55 — DEMO MODE
# ============================================================

def demo_snapshot(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate a compact judge-demo snapshot.
    """

    safe = opportunities[:6]

    enriched: list[dict[str, Any]] = []

    for opportunity in safe:

        ranking = explain_ranking(
            profile,
            opportunity,
        )

        deadline = deadline_intelligence(
            opportunity,
        )

        freshness = calculate_freshness(
            opportunity,
        )

        source_evidence = (
            build_source_evidence(
                opportunity
            )
        )

        enriched.append(
            {
                "id": opportunity.get(
                    "id"
                ),
                "title": opportunity.get(
                    "title"
                ),
                "organization": (
                    opportunity.get(
                        "organization"
                    )
                    or opportunity.get(
                        "company"
                    )
                    or "Unknown"
                ),
                "match_score": ranking[
                    "score"
                ],
                "deadline": opportunity.get(
                    "deadline"
                ),
                "deadline_intelligence": deadline,
                "freshness": freshness,
                "trust_score": opportunity.get(
                    "trust_score",
                    opportunity.get(
                        "verification_score",
                        50,
                    ),
                ),
                "verification_score": opportunity.get(
                    "verification_score"
                ),
                "source_url": source_evidence[
                    "source_url"
                ],
                "application_url": source_evidence[
                    "application_url"
                ],
            }
        )

    enriched.sort(
        key=lambda item: item[
            "match_score"
        ],
        reverse=True,
    )

    return {
        "mode": "judge_demo",
        "generated_at": datetime.utcnow().isoformat(),
        "profile": profile,
        "opportunities": enriched,
        "weekly_mission": weekly_mission(
            profile,
            opportunities,
        ),
        "quality": quality_control(
            opportunities
        ),
    }


# ============================================================
# MASTER WORKSPACE ANALYSIS
# ============================================================

def build_opportunity_workspace(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate all intelligence for a selected opportunity.
    """

    ranking = explain_ranking(
        profile,
        opportunity,
    )

    deadline = deadline_intelligence(
        opportunity
    )

    return {
        "opportunity": opportunity,
        "ranking": ranking,
        "freshness": calculate_freshness(
            opportunity
        ),
        "source_evidence": build_source_evidence(
            opportunity
        ),
        "readiness_checklist": readiness_checklist(
            profile,
            opportunity,
        ),
        "deadline": deadline,
        "best_next_action": best_next_action(
            profile,
            opportunity,
        ),
        "portfolio_impact": portfolio_impact(
            profile,
            opportunity,
        ),
        "fingerprint": opportunity_fingerprint(
            opportunity
        ),
    }


# ============================================================
# ADDITIONAL RELIABILITY HELPERS
# ============================================================

def enrich_opportunity(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Return the original opportunity plus deterministic
    intelligence fields.

    This is useful when main.py or the frontend wants a
    single enriched opportunity object.
    """

    result = dict(
        opportunity
    )

    decision = decision_for(
        profile,
        opportunity,
    )

    result.update(
        {
            "match_score": decision[
                "match_score"
            ],
            "readiness": decision[
                "readiness"
            ],
            "matched_skills": decision[
                "matched_skills"
            ],
            "missing_skills": decision[
                "missing_skills"
            ],
            "estimated_hours": decision[
                "estimated_hours"
            ],
            "days_remaining": decision[
                "days_remaining"
            ],
            "recommended_action": decision[
                "action"
            ],
            "ready_before_deadline": decision[
                "ready_before_deadline"
            ],
            "freshness": calculate_freshness(
                opportunity
            ),
            "source_evidence": build_source_evidence(
                opportunity
            ),
        }
    )

    return result


def enrich_opportunities(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Enrich and sort opportunities by match score.
    """

    enriched = [
        enrich_opportunity(
            profile,
            opportunity,
        )
        for opportunity in opportunities
    ]

    enriched.sort(
        key=lambda item: (
            _safe_number(
                item.get(
                    "match_score"
                )
            ),
            _safe_number(
                item.get(
                    "readiness"
                )
            ),
        ),
        reverse=True,
    )

    return enriched


# ============================================================
# SAFE JSON-FRIENDLY CACHE KEY
# ============================================================

def make_cache_key(
    prefix: str,
    *values: Any,
) -> str:
    """
    Create a deterministic cache key from arbitrary values.
    """

    raw_parts = [
        _text(prefix)
    ]

    for value in values:

        if isinstance(
            value,
            dict,
        ):

            raw_parts.append(
                repr(
                    sorted(
                        value.items()
                    )
                )
            )

        elif isinstance(
            value,
            (list, tuple, set),
        ):

            raw_parts.append(
                repr(
                    sorted(
                        _text(item)
                        for item in value
                    )
                )
            )

        else:

            raw_parts.append(
                _text(value)
            )

    raw = "|".join(
        raw_parts
    )

    return hashlib.sha256(
        raw.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# END OF MODULE
# ============================================================