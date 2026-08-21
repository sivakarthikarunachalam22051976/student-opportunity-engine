from google.genai import types

from ai.client import (
    client,
    GEMINI_MODEL,
)


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

    prompt = f"""
Compare student skills with opportunity
requirements.

Student skills:

{student_skills}

Required skills:

{required_skills}

Return ONLY valid JSON:

{{
    "matched_skills": [],
    "missing_skills": [],
    "priority_skills": []
}}

Rules:

- Do not invent skills.
- Every missing skill must come
  from the required skills.
- priority_skills must come
  from missing_skills.
- Return JSON only.
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
            ),
        )

        data = response.parsed

        if isinstance(data, dict):
            return {
                "matched_skills":
                    data.get(
                        "matched_skills",
                        []
                    ),

                "missing_skills":
                    data.get(
                        "missing_skills",
                        []
                    ),

                "priority_skills":
                    data.get(
                        "priority_skills",
                        []
                    ),
            }

    except Exception as error:
        print(
            f"AI gap analysis failed: {error}"
        )

    student_set = {
        str(skill).strip().lower()
        for skill in student_skills
    }

    matched = []
    missing = []

    for skill in required_skills:
        if str(skill).strip().lower() in student_set:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "priority_skills": missing,
    }