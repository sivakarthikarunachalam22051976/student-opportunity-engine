import os
import re

from .skill_normalizer import (
    SKILL_ALIASES,
    normalize_skills,
)


def extract_resume_text(
    file_path,
):
    extension = (
        os.path.splitext(
            file_path
        )[1]
        .lower()
    )

    if extension == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(
            file_path
        )

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        ).strip()

    if extension == ".txt":
        with open(
            file_path,
            "r",
            encoding="utf-8",
        ) as file:
            return file.read()

    raise ValueError(
        "Unsupported resume format. "
        "Use PDF or TXT."
    )


def parse_resume_text(
    text,
):
    text = (
        text or ""
    ).strip()

    if not text:
        return {
            "text": "",
            "skills": [],
        }

    lower_text = text.lower()

    detected = []

    for alias in SKILL_ALIASES:
        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            lower_text,
        ):
            detected.append(alias)

    return {
        "text": text,

        "skills":
            normalize_skills(
                detected
            ),
    }