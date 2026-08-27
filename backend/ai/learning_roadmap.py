from .client import (
    ai_available,
    generate_json,
)


ROADMAP_SCHEMA = {
    "type": "object",

    "properties": {
        "roadmap": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "skill": {
                        "type": "string",
                    },

                    "priority": {
                        "type": "string",
                    },

                    "steps": {
                        "type": "array",

                        "items": {
                            "type": "string",
                        },
                    },

                    "project": {
                        "type": "string",
                    },
                },

                "required": [
                    "skill",
                    "priority",
                    "steps",
                    "project",
                ],

                "additionalProperties": False,
            },
        },
    },

    "required": [
        "roadmap",
    ],

    "additionalProperties": False,
}


def create_ai_learning_roadmap(
    missing_skills,
    deadline=None,
):
    if not missing_skills:
        return []

    if not ai_available():
        return []

    try:
        data = generate_json(
            system_prompt=(
                "Create practical student learning "
                "roadmaps. Be concise and actionable."
            ),

            user_prompt=f"""
Missing skills:
{missing_skills}

Deadline:
{deadline}
""",

            schema_name=(
                "student_learning_roadmap"
            ),

            schema=ROADMAP_SCHEMA,
        )

        return data.get(
            "roadmap",
            []
        )

    except Exception as error:
        print(
            f"AI roadmap fallback: {error}"
        )

        return []