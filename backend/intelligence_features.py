from __future__ import annotations

from collections import Counter
from datetime import date
import re
from typing import Any


def _norm(value: Any) -> str:
    """
    Normalize text for safe comparisons.
    """
    return re.sub(
        r"[^a-z0-9+#.-]+",
        " ",
        str(value or "").lower(),
    ).strip()


def _skills(value: Any) -> list[str]:
    """
    Return a cleaned, unique list of skills.
    """
    if not isinstance(value, list):
        return []

    out: list[str] = []
    seen: set[str] = set()

    for item in value:
        skill = str(item or "").strip()
        normalized = _norm(skill)

        if skill and normalized and normalized not in seen:
            out.append(skill)
            seen.add(normalized)

    return out


def _skill_set(value: Any) -> set[str]:
    return {
        _norm(skill)
        for skill in _skills(value)
    }


def _days(deadline: Any) -> int | None:
    """
    Calculate days remaining from an ISO date.
    Returns None when the deadline is unavailable
    or cannot be parsed.
    """
    if not deadline:
        return None

    try:
        deadline_date = date.fromisoformat(
            str(deadline)[:10]
        )

        return (
            deadline_date - date.today()
        ).days

    except Exception:
        return None


def _estimated_hours(missing: list[str]) -> int:
    """
    Conservative prototype estimates.

    These estimates are only used for high-level
    readiness calculations.
    """
    known = {
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
        "tensorflow": 24,
        "pytorch": 24,
        "java": 20,
        "c++": 20,
        "data structures": 24,
        "algorithms": 24,
        "node.js": 18,
        "node": 18,
        "aws": 20,
    }

    return sum(
        known.get(_norm(skill), 12)
        for skill in missing
    )


def _match(
    profile: dict[str, Any],
    opp: dict[str, Any],
) -> tuple[int, list[str], list[str]]:
    """
    Calculate a lightweight explainable match score.
    """

    have = _skill_set(
        profile.get("skills", [])
    )

    required = _skills(
        opp.get("skills", [])
    )

    matched = [
        skill
        for skill in required
        if _norm(skill) in have
    ]

    missing = [
        skill
        for skill in required
        if _norm(skill) not in have
    ]

    # --------------------------------------------------
    # Skill score: 60 points
    # --------------------------------------------------

    if required:
        skill_score = (
            len(matched)
            / len(required)
            * 60
        )
    else:
        skill_score = 30

    # --------------------------------------------------
    # Interest score: 20 points
    # --------------------------------------------------

    opportunity_text = _norm(
        " ".join(
            [
                str(opp.get("title", "")),
                str(opp.get("description", "")),
                *required,
            ]
        )
    )

    interests = _skills(
        profile.get("interests", [])
    )

    interest_hits = sum(
        1
        for interest in interests
        if _norm(interest)
        and _norm(interest) in opportunity_text
    )

    if interests:
        interest_score = (
            interest_hits
            / len(interests)
            * 20
        )
    else:
        interest_score = 8

    # --------------------------------------------------
    # Branch score: 15 points
    # --------------------------------------------------

    branch = _norm(
        profile.get("branch")
    )

    branches = {
        _norm(item)
        for item in _skills(
            opp.get("branches", [])
        )
    }

    if not branches:
        branch_score = 15

    elif branch and branch in branches:
        branch_score = 15

    else:
        branch_score = 0

    # --------------------------------------------------
    # Location score: 5 points
    # --------------------------------------------------

    location = _norm(
        profile.get("location")
    )

    opportunity_location = _norm(
        opp.get("location")
    )

    if (
        bool(opp.get("remote"))
        or not opportunity_location
        or not location
        or location in opportunity_location
        or opportunity_location in location
    ):
        location_score = 5

    else:
        location_score = 0

    # --------------------------------------------------
    # Final score
    # --------------------------------------------------

    score = round(
        min(
            100,
            skill_score
            + interest_score
            + branch_score
            + location_score,
        )
    )

    return score, matched, missing


def decision_for(
    profile: dict[str, Any],
    opp: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate an explainable decision for one opportunity.
    """

    match_score, matched, missing = _match(
        profile,
        opp,
    )

    required_skills = _skills(
        opp.get("skills", [])
    )

    if required_skills:
        readiness = round(
            len(matched)
            / len(required_skills)
            * 100
        )
    else:
        readiness = 50

    readiness = max(
        0,
        min(100, readiness),
    )

    days_remaining = _days(
        opp.get("deadline")
    )

    estimated_hours = _estimated_hours(
        missing
    )

    # --------------------------------------------------
    # Action decision
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Deadline feasibility
    # --------------------------------------------------

    if days_remaining is None:
        ready_before_deadline = None

    else:
        available_hours = max(
            0,
            days_remaining,
        ) * 2

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


def profile_intelligence(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate profile-level intelligence across all opportunities.
    """

    evidence = evidence or {}

    skills = _skills(
        profile.get("skills", [])
    )

    interests = _skills(
        profile.get("interests", [])
    )

    projects = _skills(
        evidence.get(
            "projects",
            profile.get("projects", []),
        )
    )

    evidence_items = _skills(
        evidence.get(
            "evidence",
            profile.get("evidence", []),
        )
    )

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

    # --------------------------------------------------
    # Opportunity skill patterns
    # --------------------------------------------------

    skill_counts: Counter[str] = Counter()

    impact_counts: Counter[str] = Counter()

    for opportunity, decision in decisions:

        for skill in _skills(
            opportunity.get("skills", [])
        ):
            skill_counts[skill] += 1

        for skill in decision[
            "missing_skills"
        ]:
            impact_counts[skill] += 1

    pattern_total = max(
        1,
        len(decisions),
    )

    patterns = [
        {
            "skill": skill,
            "frequency": count,
            "percentage": round(
                count
                / pattern_total
                * 100
            ),
        }
        for skill, count
        in skill_counts.most_common(8)
    ]

    # --------------------------------------------------
    # Best skill investments
    # --------------------------------------------------

    investment = []

    for skill, count in impact_counts.most_common(8):

        hours = _estimated_hours(
            [skill]
        )

        investment.append(
            {
                "skill": skill,
                "learning_hours": hours,
                "opportunities_impacted": count,
                "return_per_hour": round(
                    count / max(1, hours),
                    2,
                ),
            }
        )

    investment.sort(
        key=lambda item: (
            item["return_per_hour"],
            item["opportunities_impacted"],
        ),
        reverse=True,
    )

    # --------------------------------------------------
    # Profile weaknesses
    # --------------------------------------------------

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

        overlap = sum(
            1
            for interest in interests
            if any(
                _norm(interest)
                in _norm(skill)
                or _norm(skill)
                in _norm(interest)
                for skill in skills
            )
        )

        if overlap == 0:
            weaknesses.append(
                "Your interests and current skills show limited visible specialization overlap."
            )

    # --------------------------------------------------
    # Direction drift
    # --------------------------------------------------

    target_counts: Counter[str] = Counter()

    for opportunity, _ in decisions:

        text = _norm(
            " ".join(
                [
                    str(
                        opportunity.get(
                            "title",
                            "",
                        )
                    ),
                    str(
                        opportunity.get(
                            "description",
                            "",
                        )
                    ),
                    *_skills(
                        opportunity.get(
                            "skills",
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

            if (
                normalized_interest
                and normalized_interest in text
            ):
                target_counts[
                    interest
                ] += 1

    dominant_interest = ""

    if target_counts:
        dominant_interest = (
            target_counts
            .most_common(1)[0][0]
        )

    elif interests:
        dominant_interest = interests[0]

    related_skill_hits = sum(
        1
        for skill in skills
        if dominant_interest
        and (
            _norm(dominant_interest)
            in _norm(skill)
            or _norm(skill)
            in _norm(dominant_interest)
        )
    )

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

    # --------------------------------------------------
    # Skill proof analysis
    # --------------------------------------------------

    skill_proof = []

    for skill in skills:

        normalized_skill = _norm(
            skill
        )

        project_hit = any(
            normalized_skill in _norm(project)
            for project in projects
        )

        evidence_hit = any(
            normalized_skill in _norm(item)
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

    # --------------------------------------------------
    # Opportunity timeline
    # --------------------------------------------------

    timeline = {
        "apply_now": [],
        "prepare_this_week": [],
        "prepare_this_month": [],
        "future_targets": [],
    }

    for opportunity, decision in decisions:

        item = {
            "id": opportunity.get("id"),
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

        if decision["action"] == "APPLY NOW":

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

    # --------------------------------------------------
    # Evidence locker
    # --------------------------------------------------

    locker = [
        {
            "skill": item["skill"],
            "status": (
                "demonstrated"
                if item["demonstrated"]
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


def readiness_simulator(
    profile: dict[str, Any],
    opportunities: list[dict[str, Any]],
    added_skills: list[str],
    added_projects: int = 0,
) -> dict[str, Any]:
    """
    Simulate how additional skills and projects could
    improve readiness.
    """

    simulated = dict(profile)

    simulated["skills"] = _skills(
        list(
            profile.get("skills", [])
        )
        + list(added_skills)
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

    unlocked = []

    for opportunity, before, after in zip(
        opportunities,
        base_scores,
        new_scores,
    ):

        if (
            before["action"]
            in {
                "LOW PRIORITY",
                "SAVE FOR FUTURE",
                "PREPARE FIRST",
            }
            and after["action"]
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

    base_readiness = round(
        sum(
            item["readiness"]
            for item in base_scores
        )
        / max(
            1,
            len(base_scores),
        )
    )

    simulated_readiness = round(
        sum(
            item["readiness"]
            for item in new_scores
        )
        / max(
            1,
            len(new_scores),
        )
    )

    simulated_readiness = min(
        100,
        simulated_readiness
        + max(0, added_projects) * 8,
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
            item["estimated_hours"]
            for item in new_scores
        ),
    }


def application_strategy(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate a simple application strategy for
    a selected opportunity.
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
        "decision": decision["action"],
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