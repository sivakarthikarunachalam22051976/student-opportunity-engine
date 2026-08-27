import json

from .client import client


def parse_opportunity_text(
    text: str
) -> dict:

    prompt = f"""
You are an opportunity data extraction engine.

Extract information ONLY from the supplied text.

Return valid JSON using exactly this structure:

{{
    "title": "",
    "organization": "",
    "description": "",
    "year": [],
    "branches": [],
    "skills": [],
    "location": "",
    "remote": false,
    "deadline": "",
    "stipend": "",
    "posted_time_ago": "",
    "is_still_accepting": true,
    "verification_score": "Medium",
    "source_url": ""
}}

Rules:

- Do not invent facts.
- Use empty strings when text is unavailable.
- Use empty arrays when list information is unavailable.
- year must always be an array.
- branches must always be an array.
- skills must always be an array.
- remote must always be true or false.
- is_still_accepting must always be true or false.
- Return JSON only.
- Do not include markdown.
- Do not include explanations.

Opportunity text:

{text}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract structured opportunity "
                    "information accurately. "
                    "Never invent missing information."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        response_format={
            "type": "json_object"
        },
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    return json.loads(content)