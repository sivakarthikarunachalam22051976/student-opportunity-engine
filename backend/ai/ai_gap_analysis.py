from .client import (
    ai_available,
    generate_json,
)


GAP_SCHEMA = {
    "type": "object",

    "properties": {
        "matched_skills": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "missing_skills": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },

        "priority_skills": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },

    "required": [
        "matched_skills",
        "missing_skills",
        "priority_skills",
    ],

    "additionalProperties": False,
}


def analyze_skill_gap(
    student_skills,
    required_skills,
):
    student_skills = (
        student_skills or []
    )

    required_skills = (
        required_skills or []
    )

    if not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "priority_skills": [],
        }

    if ai_available():
        try:
            return generate_json(
                system_prompt=(
                    "Compare skills carefully. "
                    "Do not invent skills."
                ),

                user_prompt=f"""
Student skills:
{student_skills}

Required skills:
{required_skills}
""",

                schema_name="skill_gap",

                schema=GAP_SCHEMA,
            )

        except Exception as error:
            print(
                f"AI gap analysis fallback: "
                f"{error}"
            )

    student_set = {
        str(skill).strip().lower()
        for skill in student_skills
    }

    matched = []
    missing = []

    for skill in required_skills:
        if (
            str(skill).strip().lower()
            in student_set
        ):
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "priority_skills": missing,
    }