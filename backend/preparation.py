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

    current_readiness = gaps.get("readiness_percentage", 0)
    matched_skills = gaps.get("matched_skills", [])

    estimated_total_hours = sum(
        int(item.get("estimated_hours", 0) or 0)
        for item in roadmap
        if isinstance(item, dict)
    )

    estimated_weeks = max(
        1,
        (estimated_total_hours + 9) // 10,
    )

    readiness_level = (
        "Ready"
        if current_readiness >= 80
        else "Strong foundation"
        if current_readiness >= 60
        else "Developing"
        if current_readiness >= 35
        else "Early stage"
    )

    priority_actions = []
    for item in roadmap[:3]:
        skill = item.get("skill", "the next skill")
        priority_actions.append(f"Strengthen {skill} with hands-on practice.")

    if not priority_actions:
        priority_actions.append(
            "Strengthen your existing projects and make your current skills visible through portfolio evidence."
        )

    return {
        "opportunity": opportunity.get("title"),
        "readiness_percentage": current_readiness,
        "current_readiness": current_readiness,
        "readiness_level": readiness_level,
        "required_skills": gaps.get("required_skills", []),
        "current_skills": gaps.get("student_skills", []),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "estimated_total_hours": estimated_total_hours,
        "estimated_weeks": estimated_weeks,
        "roadmap": roadmap,
        "priority_actions": priority_actions,
        "next_action": (
            f"Start with {roadmap[0].get('skill', 'your highest-priority gap')}."
            if roadmap
            else "Strengthen your existing projects and turn your current skills into visible portfolio proof."
        ),
        "engine": engine,
    }