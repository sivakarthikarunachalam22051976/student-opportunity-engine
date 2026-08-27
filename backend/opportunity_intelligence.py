import re

from urllib.parse import urlparse

from .eligibility import (
    check_eligibility,
)

from .gap_analysis import (
    find_skill_gaps,
)

from .matching import (
    calculate_match,
)


OFFICIAL_HINTS = (
    "google.com",
    "microsoft.com",
    "amazon.com",
    "meta.com",
    "ibm.com",
    "oracle.com",
    "github.com",
    "devpost.com",
    "unstop.com",
    "kaggle.com",
    "ac.in",
    "edu",
    "gov",
)


SUSPICIOUS_PATTERNS = [
    "telegram",
    "whatsapp only",
    "pay registration fee",
    "guaranteed selection",
    "send money",
    "urgent payment",
    "processing fee",
]


def domain_of(url):
    try:
        return (
            urlparse(
                url or ""
            )
            .netloc
            .lower()
        )
    except Exception:
        return ""


def trust_score(opportunity):
    source_url = (
        opportunity.get("source_url")
        or ""
    )

    application_url = (
        opportunity.get("application_url")
        or ""
    )

    domain = domain_of(source_url)

    score = 20
    reasons = []

    if source_url.startswith("https://"):
        score += 20
        reasons.append(
            "Secure source URL"
        )

    if domain:
        score += 15
        reasons.append(
            "Source domain available"
        )

    if any(
        hint in domain
        for hint in OFFICIAL_HINTS
    ):
        score += 30
        reasons.append(
            "Recognized or official domain"
        )

    if application_url:
        score += 15
        reasons.append(
            "Application destination found"
        )

    if opportunity.get("description"):
        score += 10

    return min(score, 100), reasons


def suspicion_signals(opportunity):
    text = " ".join(
        str(
            opportunity.get(field)
            or ""
        )
        for field in [
            "title",
            "description",
            "organization",
        ]
    ).lower()

    flags = [
        pattern
        for pattern in SUSPICIOUS_PATTERNS
        if pattern in text
    ]

    return flags


def deadline_intelligence(
    deadline,
):
    if not deadline:
        return {
            "status": "Unknown",
            "days_left": None,
            "urgency": "Unknown",
        }

    value = str(deadline)

    if (
        "active" in value.lower()
        or "open" in value.lower()
    ):
        return {
            "status": "Open",
            "days_left": None,
            "urgency": "Normal",
        }

    match = re.search(
        r"(\d{4}-\d{2}-\d{2})",
        value,
    )

    if not match:
        return {
            "status": value,
            "days_left": None,
            "urgency": "Unknown",
        }

    from datetime import date

    try:
        target = (
            date.fromisoformat(
                match.group(1)
            )
        )

        days_left = (
            target - date.today()
        ).days

        if days_left < 0:
            urgency = "Expired"
        elif days_left <= 3:
            urgency = "Critical"
        elif days_left <= 7:
            urgency = "Urgent"
        elif days_left <= 21:
            urgency = "Soon"
        else:
            urgency = "Normal"

        return {
            "status": value,
            "days_left": days_left,
            "urgency": urgency,
        }

    except ValueError:
        return {
            "status": value,
            "days_left": None,
            "urgency": "Unknown",
        }


def enrich_opportunity(
    opportunity,
):
    opportunity = dict(opportunity)

    score, reasons = trust_score(
        opportunity
    )

    deadline = (
        deadline_intelligence(
            opportunity.get("deadline")
        )
    )

    suspicion = (
        suspicion_signals(
            opportunity
        )
    )

    opportunity[
        "trust_score"
    ] = score

    opportunity[
        "trust_reasons"
    ] = reasons

    opportunity[
        "suspicion_flags"
    ] = suspicion

    opportunity[
        "deadline_intelligence"
    ] = deadline

    opportunity[
        "is_still_accepting"
    ] = (
        deadline["urgency"]
        != "Expired"
    )

    return opportunity


def deduplicate_opportunities(
    opportunities,
):
    seen = set()
    result = []

    for opportunity in opportunities:
        key = (
            str(
                opportunity.get(
                    "title",
                    "",
                )
            )
            .strip()
            .lower(),

            str(
                opportunity.get(
                    "organization",
                    "",
                )
            )
            .strip()
            .lower(),
        )

        if key in seen:
            continue

        seen.add(key)
        result.append(opportunity)

    return result


def rank_opportunities(
    student,
    opportunities,
):
    ranked = []

    for opportunity in opportunities:
        enriched = enrich_opportunity(
            opportunity
        )

        match = calculate_match(
            student,
            enriched,
        )

        ranking_score = (
            match.get(
                "match_score",
                0,
            )
            * 0.60
            +
            enriched.get(
                "trust_score",
                0,
            )
            * 0.25
        )

        deadline = (
            enriched.get(
                "deadline_intelligence",
                {},
            )
        )

        if (
            deadline.get("urgency")
            == "Soon"
        ):
            ranking_score += 5

        if (
            deadline.get("urgency")
            == "Urgent"
        ):
            ranking_score += 8

        if (
            deadline.get("urgency")
            == "Critical"
        ):
            ranking_score += 10

        if enriched.get(
            "suspicion_flags"
        ):
            ranking_score -= 25

        enriched[
            "match_score"
        ] = match.get(
            "match_score",
            0,
        )

        enriched[
            "ranking_score"
        ] = round(
            max(
                0,
                min(
                    ranking_score,
                    100,
                ),
            )
        )

        ranked.append(enriched)

    return sorted(
        ranked,

        key=lambda item:
        item.get(
            "ranking_score",
            0,
        ),

        reverse=True,
    )


def why_not_me(
    student,
    opportunity,
):
    eligibility = (
        check_eligibility(
            student,
            opportunity,
        )
    )

    match = calculate_match(
        student,
        opportunity,
    )

    gaps = find_skill_gaps(
        student.get(
            "skills",
            [],
        ),

        opportunity.get(
            "skills",
            [],
        ),
    )

    blockers = list(
        eligibility.get(
            "reasons",
            [],
        )
    )

    if (
        match.get(
            "missing_skills",
            []
        )
    ):
        blockers.append(
            "Some required skills are missing."
        )

    return {
        "eligible":
            eligibility.get(
                "eligible",
                True,
            ),

        "match_score":
            match.get(
                "match_score",
                0,
            ),

        "blockers":
            blockers,

        "warnings":
            eligibility.get(
                "warnings",
                [],
            ),

        "missing_skills":
            gaps.get(
                "missing_skills",
                [],
            ),

        "next_actions":
            [
                (
                    f"Build evidence for "
                    f"{skill}"
                )
                for skill in gaps.get(
                    "missing_skills",
                    [],
                )[:3]
            ],
    }


def hidden_opportunities(
    student,
):
    interests = [
        str(item).lower()
        for item in student.get(
            "interests",
            [],
        )
    ]

    skills = [
        str(item).lower()
        for item in student.get(
            "skills",
            [],
        )
    ]

    suggestions = []

    if any(
        word in " ".join(
            interests + skills
        )
        for word in [
            "python",
            "ai",
            "machine learning",
            "data",
        ]
    ):
        suggestions.append(
            {
                "type":
                    "research fellowship",
                "reason":
                    "Your profile suggests research "
                    "and technical project potential.",
            }
        )

    suggestions.append(
        {
            "type":
                "hackathon",
            "reason":
                "Hackathons reward practical proof "
                "of skills, not only resumes.",
        }
    )

    suggestions.append(
        {
            "type":
                "open-source program",
            "reason":
                "Your technical skills can become "
                "public portfolio evidence.",
        }
    )

    return suggestions[:3]


def future_opportunity_path(
    student,
    opportunity,
):
    gaps = find_skill_gaps(
        student.get(
            "skills",
            [],
        ),

        opportunity.get(
            "skills",
            [],
        ),
    )

    missing = gaps.get(
        "missing_skills",
        [],
    )

    path = []

    for skill in missing[:5]:
        path.append(
            {
                "skill": skill,
                "goal":
                    f"Build one demonstrable "
                    f"project using {skill}.",
            }
        )

    return {
        "current_profile":
            student.get(
                "opportunity_type",
                "internship",
            ),

        "next_skills":
            missing[:5],

        "future_path":
            path,

        "message":
            (
                "The fastest route to stronger "
                "future opportunities is converting "
                "missing skills into visible proof."
            ),
    }
