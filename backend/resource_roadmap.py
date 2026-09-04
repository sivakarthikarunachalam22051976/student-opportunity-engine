from .resource_catalog import (
    LEARNING_RESOURCES
)

from .skill_normalizer import (
    normalize_skill,
    normalize_skills
)


HIGH_PRIORITY_SKILLS = {
    "Python",
    "SQL",
    "FastAPI",
    "Machine Learning",
    "Data Structures and Algorithms",
    "REST API"
}


def get_priority(
    skill: str,
    opportunity_skills: list
):

    normalized_skill = normalize_skill(
        skill
    )

    normalized_opportunity_skills = (
        normalize_skills(
            opportunity_skills
        )
    )

    if (
        normalized_skill
        in normalized_opportunity_skills
    ):

        if (
            normalized_skill
            in HIGH_PRIORITY_SKILLS
        ):

            return "High"

        return "Medium"

    return "Low"


def get_topics_for_skill(
    skill: str
):

    topics = {

        "SQL": [
            "SELECT queries",
            "Filtering with WHERE",
            "JOINs",
            "GROUP BY",
            "Database basics"
        ],

        "FastAPI": [
            "API routes",
            "Request models",
            "Response models",
            "CRUD operations",
            "Database integration"
        ],

        "Docker": [
            "Containers",
            "Images",
            "Dockerfiles",
            "Volumes",
            "Running applications"
        ],

        "Machine Learning": [
            "Supervised learning",
            "Training data",
            "Model evaluation",
            "Regression",
            "Classification"
        ],

        "Git": [
            "Repositories",
            "Commits",
            "Branches",
            "Pull requests",
            "Version control workflow"
        ],

        "React": [
            "Components",
            "Props",
            "State",
            "Hooks",
            "API integration"
        ],

        "Python": [
            "Core syntax",
            "Functions",
            "Data structures",
            "Modules",
            "Error handling"
        ]
    }

    return topics.get(
        skill,
        [
            "Core concepts",
            "Practical examples",
            "Hands-on exercises",
            "Build a small project"
        ]
    )


def create_resource_roadmap(
    missing_skills: list,
    opportunity_skills: list
):

    roadmap = []

    normalized_missing = normalize_skills(
        missing_skills
    )

    for skill in normalized_missing:

        normalized_skill = normalize_skill(
            skill
        )

        resources = LEARNING_RESOURCES.get(
            normalized_skill,
            []
        )

        topics = get_topics_for_skill(normalized_skill)

        roadmap.append({
            "skill": normalized_skill,

            "priority": get_priority(
                normalized_skill,
                opportunity_skills
            ),

            "why_needed": (
                f"{normalized_skill} is currently "
                "missing from your profile and is "
                "relevant to this opportunity."
            ),

            # Keep both the richer resource data and the field names
            # consumed by the Preparation and Future Path screens.
            "topics": topics,
            "steps": topics,
            "learn": topics,
            "practice": [
                f"Complete a small hands-on {normalized_skill} exercise.",
                f"Apply {normalized_skill} in a practical task.",
            ],
            "project": (
                f"Build one small portfolio project that demonstrates {normalized_skill} "
                "and document what you learned."
            ),
            "estimated_hours": max(4, min(20, len(topics) * 2)),
            "resources": resources,
        })

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    roadmap.sort(
        key=lambda item:
        priority_order.get(
            item["priority"],
            99
        )
    )

    return roadmap