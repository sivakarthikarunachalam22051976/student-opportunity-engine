from skill_normalizer import (
    normalize_skills
)


def normalize_text(value):

    return str(value or "").strip().lower()


def calculate_match(
    student,
    opportunity
):

    score = 0

    student_skills = set(
        normalize_skills(
            student.get(
                "skills",
                []
            )
        )
    )

    opportunity_skills = set(
        normalize_skills(
            opportunity.get(
                "skills",
                []
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

    # ========================================================
    # 1. SKILL MATCH — 50 POINTS
    # ========================================================

    if opportunity_skills:

        skill_score = (
            len(matched_skills)
            / len(opportunity_skills)
        ) * 50

    else:

        skill_score = 50

    score += skill_score


    # ========================================================
    # 2. INTEREST MATCH — 20 POINTS
    # ========================================================

    student_interests = [

        normalize_text(interest)

        for interest in student.get(
            "interests",
            []
        )

        if normalize_text(interest)
    ]

    opportunity_text = " ".join([

        normalize_text(
            opportunity.get(
                "title",
                ""
            )
        ),

        normalize_text(
            opportunity.get(
                "description",
                ""
            )
        ),

        " ".join(

            normalize_text(skill)

            for skill in opportunity.get(
                "skills",
                []
            )
        )

    ])

    if any(
        interest in opportunity_text
        for interest in student_interests
    ):

        score += 20


    # ========================================================
    # 3. BRANCH MATCH — 15 POINTS
    # ========================================================

    student_branch = normalize_text(
        student.get(
            "branch",
            ""
        )
    )

    opportunity_branches = {

        normalize_text(branch)

        for branch in opportunity.get(
            "branches",
            []
        )
    }

    if (
        not opportunity_branches
        or student_branch in opportunity_branches
    ):

        score += 15


    # ========================================================
    # 4. LOCATION / REMOTE — 15 POINTS
    # ========================================================

    student_location = normalize_text(
        student.get(
            "location",
            ""
        )
    )

    opportunity_location = normalize_text(
        opportunity.get(
            "location",
            ""
        )
    )

    if opportunity.get("remote") is True:

        score += 15

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

        score += 15


    return {

        "match_score":
        round(
            min(score, 100)
        ),

        "matched_skills":
        matched_skills,

        "missing_skills":
        missing_skills,
    }


def calculate_skill_match(
    student_skills,
    required_skills
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

    matched = student.intersection(
        required
    )

    return round(

        (
            len(matched)
            / len(required)
        ) * 100
    )