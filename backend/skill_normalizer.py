import re


SKILL_ALIASES = {
    "python": "Python",
    "python programming": "Python",

    "java": "Java",
    "java programming": "Java",

    "javascript": "JavaScript",
    "js": "JavaScript",

    "typescript": "TypeScript",
    "ts": "TypeScript",

    "c++": "C++",
    "cpp": "C++",

    "c#": "C#",
    "csharp": "C#",

    "machine learning": "Machine Learning",
    "ml": "Machine Learning",

    "deep learning": "Deep Learning",
    "dl": "Deep Learning",

    "artificial intelligence": "Artificial Intelligence",
    "ai": "Artificial Intelligence",

    "data science": "Data Science",

    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",

    "sql": "SQL",

    "mysql": "MySQL",

    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",

    "mongodb": "MongoDB",

    "react": "React",
    "react.js": "React",
    "reactjs": "React",

    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",

    "html": "HTML",
    "css": "CSS",

    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",

    "git": "Git",
    "github": "GitHub",

    "docker": "Docker",
    "kubernetes": "Kubernetes",

    "aws": "AWS",
    "amazon web services": "AWS",

    "azure": "Microsoft Azure",

    "google cloud": "Google Cloud",
    "gcp": "Google Cloud",

    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",

    "pandas": "Pandas",
    "numpy": "NumPy",

    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",

    "computer vision": "Computer Vision",

    "natural language processing":
        "Natural Language Processing",

    "nlp":
        "Natural Language Processing",

    "linux": "Linux",

    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful api": "REST APIs",
    "restful apis": "REST APIs",
    "api": "REST APIs",
    "apis": "REST APIs",

    "api development": "API Development",

    "data structures and algorithms":
        "Data Structures and Algorithms",
    "dsa":
        "Data Structures and Algorithms",
}


def normalize_skill(skill):
    if not skill:
        return None

    skill = str(skill).strip().lower()

    if not skill:
        return None

    skill = re.sub(
        r"\s+",
        " ",
        skill
    )

    return SKILL_ALIASES.get(
        skill,
        skill.title()
    )


def normalize_skills(skills):
    if not skills:
        return []

    if isinstance(skills, str):
        skills = skills.split(",")

    normalized = []

    for skill in skills:
        normalized_skill = normalize_skill(
            skill
        )

        if (
            normalized_skill
            and normalized_skill not in normalized
        ):
            normalized.append(
                normalized_skill
            )

    return normalized


if __name__ == "__main__":
    test_skills = [
        "python",
        "Python Programming",
        "ML",
        "machine learning",
        "reactjs",
        "JavaScript",
        "REST API",
        "sklearn",
    ]

    print(
        normalize_skills(test_skills)
    )