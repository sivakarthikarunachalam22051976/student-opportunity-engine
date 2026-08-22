import re

from .skill_normalizer import (
    normalize_skills
)


KNOWN_SKILLS = [

    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C++",
    "C#",

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",

    "Data Science",
    "Data Analysis",

    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",

    "React",
    "Node.js",
    "HTML",
    "CSS",

    "FastAPI",
    "Django",
    "Flask",

    "Git",
    "GitHub",

    "Docker",
    "Kubernetes",

    "AWS",
    "Microsoft Azure",
    "Google Cloud",

    "TensorFlow",
    "PyTorch",

    "Pandas",
    "NumPy",

    "Computer Vision",
    "Natural Language Processing",

    "Linux",
    "REST APIs"
]


def extract_resume_text(
    file_path
):

    if file_path.lower().endswith(
        ".pdf"
    ):

        from pypdf import PdfReader

        reader = PdfReader(
            file_path
        )

        text = ""

        for page in reader.pages:

            text += (
                page.extract_text()
                or ""
            )

        return text


    if file_path.lower().endswith(
        ".txt"
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()


    raise ValueError(
        "Unsupported resume format"
    )


def parse_resume_text(
    text: str
):

    if not text:

        return {

            "skills": [],

            "raw_text":
            ""
        }


    detected_skills = []


    for skill in KNOWN_SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(
                skill
            )
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            detected_skills.append(
                skill
            )


    normalized_skills = (
        normalize_skills(
            detected_skills
        )
    )


    return {

        "skills":
        normalized_skills,

        "raw_text":
        text
    }