from .ai.learning_roadmap import (
    create_ai_learning_roadmap,
)

from .gap_analysis import (
    find_skill_gaps,
)

from .resource_roadmap import (
    create_resource_roadmap,
)


def build_preparation_plan(
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

    missing_skills = (
        gaps.get(
            "missing_skills",
            [],
        )
    )

    ai_roadmap = (
        create_ai_learning_roadmap(
            missing_skills,
            opportunity.get(
                "deadline"
            ),
        )
    )

    if ai_roadmap:
        roadmap = ai_roadmap
        engine = "AI"
    else:
        roadmap = (
            create_resource_roadmap(
                missing_skills,
                opportunity.get(
                    "skills",
                    [],
                ),
            )
        )

        engine = "Rule-based fallback"

    return {
        "opportunity":
            opportunity.get(
                "title"
            ),

        "readiness_percentage":
            gaps.get(
                "readiness_percentage",
                0,
            ),

        "missing_skills":
            missing_skills,

        "roadmap":
            roadmap,

        "engine":
            engine,
    }