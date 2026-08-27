from .skill_normalizer import (
    normalize_skills,
)


def normalize_text(value):
    return (
        str(value or "")
        .strip()
        .lower()
    )


def calculate_match(
    student,
    opportunity,
):
    score = 0
    breakdown = []
    explanations = []

    student_skills = set(
        normalize_skills(
            student.get(
                "skills",
                [],
            )
        )
    )

    opportunity_skills = set(
        normalize_skills(
            opportunity.get(
                "skills",
                [],
            )
        )
    )

    matched_skills = sorted(
        student_skills.intersection(
            opportunity_skills
        )
    )

    missing_skills = sorted(
        opportunity_skills.difference(
            student_skills
        )
    )

    if opportunity_skills:
        skill_score = round(
            (
                len(matched_skills)
                / len(opportunity_skills)
            )
            * 50
        )
    else:
        skill_score = 50

    score += skill_score

    breakdown.append({
        "factor": "Skills",
        "points": skill_score,
        "maximum": 50,
    })

    if matched_skills:
        explanations.append(
            "Your profile already matches "
            + ", ".join(
                matched_skills[:4]
            )
        )

    student_interests = [
        normalize_text(item)
        for item in student.get(
            "interests",
            [],
        )
        if normalize_text(item)
    ]

    opportunity_text = " ".join([
        normalize_text(
            opportunity.get(
                "title",
                "",
            )
        ),

        normalize_text(
            opportunity.get(
                "description",
                "",
            )
        ),

        " ".join(
            normalize_text(skill)
            for skill in opportunity.get(
                "skills",
                [],
            )
        ),
    ])

    interest_score = 0

    if any(
        interest in opportunity_text
        for interest in student_interests
    ):
        interest_score = 20
        explanations.append(
            "Your interests align with "
            "the opportunity content."
        )

    score += interest_score

    breakdown.append({
        "factor": "Interests",
        "points": interest_score,
        "maximum": 20,
    })

    student_branch = normalize_text(
        student.get(
            "branch",
            "",
        )
    )

    opportunity_branches = {
        normalize_text(branch)
        for branch in opportunity.get(
            "branches",
            [],
        )
    }

    branch_score = 0

    if (
        not opportunity_branches
        or not student_branch
        or student_branch
        in opportunity_branches
    ):
        branch_score = 15

    score += branch_score

    breakdown.append({
        "factor": "Branch",
        "points": branch_score,
        "maximum": 15,
    })

    student_location = normalize_text(
        student.get(
            "location",
            "",
        )
    )

    opportunity_location = normalize_text(
        opportunity.get(
            "location",
            "",
        )
    )

    location_score = 0

    if opportunity.get(
        "remote"
    ) is True:
        location_score = 15

    elif (
        student_location
        and opportunity_location
        and (
            student_location
            in opportunity_location

            or

            opportunity_location
            in student_location
        )
    ):
        location_score = 15

    score += location_score

    breakdown.append({
        "factor": "Location",
        "points": location_score,
        "maximum": 15,
    })

    final_score = round(
        min(score, 100)
    )

    return {
        "match_score": final_score,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "breakdown":
            breakdown,

        "explanations":
            explanations,
    }


def calculate_skill_match(
    student_skills,
    required_skills,
):
    student = set(
        normalize_skills(
            student_skills
        )
    )

    required = set(
        normalize_skills(
            required_skills
        )
    )

    if not required:
        return 100

    return round(
        (
            len(
                student.intersection(
                    required
                )
            )
            / len(required)
        )
        * 100
    )