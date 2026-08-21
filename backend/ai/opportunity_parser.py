import json
import re

from google.genai import (
    types
)

from .client import (
    client
)


GEMINI_MODEL = (
    "gemini-2.5-flash"
)


def parse_opportunity_text(
    text: str
):

    prompt = f"""
You are an opportunity information extraction engine.

Extract structured information from the opportunity text below.

Return only JSON.

Use exactly this schema:

{{
    "title": null,
    "organization": null,
    "year": [],
    "branches": [],
    "skills": [],
    "location": null,
    "remote": null,
    "deadline": null,
    "stipend": null,
    "documents": []
}}

Rules:

- Do not invent information.
- year must be an array.
- branches must be an array.
- skills must be an array.
- documents must be an array.
- stipend must be a number only if clearly stated.
- remote must be true or false only if clearly supported.
- Use null when a scalar value is unknown.
- Use [] when list information is unknown.
- Return JSON only.

Opportunity text:

{text}
"""

    try:

        response = (
            client.models.generate_content(

                model=GEMINI_MODEL,

                contents=prompt,

                config=(
                    types.GenerateContentConfig(

                        temperature=0.0,

                        response_mime_type=(
                            "application/json"
                        )
                    )
                )
            )
        )

        raw_text = (
            response.text
            or ""
        )

        clean_text = re.sub(
            r"```json|```",
            "",
            raw_text,
            flags=re.IGNORECASE
        ).strip()

        return json.loads(
            clean_text
        )


    except Exception as error:

        return {

            "error":
            str(error)
        }