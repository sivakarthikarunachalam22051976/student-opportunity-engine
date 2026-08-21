from google.genai import types

from ai.client import (
    client,
    GEMINI_MODEL,
)


def create_ai_learning_roadmap(
    missing_skills,
    deadline=None,
):
    if not missing_skills:
        return []

    prompt = f"""
Create a practical learning roadmap for a student.

Skills to learn:

{missing_skills}

Opportunity deadline:

{deadline}

Return ONLY valid JSON.

Use exactly:

{{
    "roadmap": [
        {{
            "skill": "string",
            "priority": "high",
            "steps": [],
            "project": "string"
        }}
    ]
}}

Rules:

- Keep the roadmap practical.
- Do not invent unnecessary prerequisites.
- Prioritize skills relevant to the opportunity.
- Keep each step actionable.
- Return JSON only.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        return []

    try:
        data = response.parsed

        if isinstance(data, dict):
            return data.get(
                "roadmap",
                []
            )

    except Exception:
        pass

    return []