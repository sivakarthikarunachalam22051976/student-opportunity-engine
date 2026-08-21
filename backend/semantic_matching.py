from skill_normalizer import normalize_skill, normalize_skills


RELATED_SKILLS = {

    "Machine Learning": [
        "Python",
        "NumPy",
        "Pandas",
        "Scikit-learn"
    ],

    "Deep Learning": [
        "Machine Learning",
        "Python",
        "PyTorch",
        "TensorFlow"
    ],

    "Artificial Intelligence": [
        "Python",
        "Machine Learning",
        "Deep Learning"
    ],

    "FastAPI": [
        "Python",
        "REST APIs",
        "API Development"
    ],

    "Django": [
        "Python",
        "SQL",
        "REST APIs"
    ],

    "React": [
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS"
    ],

    "Docker": [
        "Linux",
        "Git"
    ],

    "Data Structures and Algorithms": [
        "Python",
        "Java",
        "C++"
    ]
}


def get_semantic_skill_match(
    student_skills,
    required_skills
):

    student = normalize_skills(
        student_skills
    )

    required = normalize_skills(
        required_skills
    )

    student_lower = {
        skill.lower()
        for skill in student
    }

    exact_matches = []
    related_matches = []
    missing_skills = []

    for required_skill in required:

        required_normalized = normalize_skill(
            required_skill
        )

        if not required_normalized:
            continue

        required_lower = (
            required_normalized.lower()
        )

        # ====================================================
        # EXACT MATCH
        # ====================================================

        if required_lower in student_lower:

            exact_matches.append(
                required_normalized
            )

            continue

        # ====================================================
        # RELATED MATCH
        # ====================================================

        related = RELATED_SKILLS.get(
            required_normalized,
            []
        )

        related_found = False

        for related_skill in related:

            normalized_related = normalize_skill(
                related_skill
            )

            if (
                normalized_related
                and normalized_related.lower()
                in student_lower
            ):

                related_matches.append({
                    "required_skill":
                        required_normalized,

                    "related_student_skill":
                        normalized_related
                })

                related_found = True

                break

        # ====================================================
        # MISSING
        # ====================================================

        if not related_found:

            missing_skills.append(
                required_normalized
            )

    total_required = len(required)

    if total_required == 0:

        semantic_score = 100

    else:

        exact_points = (
            len(exact_matches) * 100
        )

        related_points = (
            len(related_matches) * 60
        )

        semantic_score = round(
            (
                exact_points
                + related_points
            )
            / total_required
        )

        semantic_score = min(
            semantic_score,
            100
        )

    return {
        "semantic_match_score":
            semantic_score,

        "exact_matches":
            exact_matches,

        "related_matches":
            related_matches,

        "missing_skills":
            missing_skills
    }