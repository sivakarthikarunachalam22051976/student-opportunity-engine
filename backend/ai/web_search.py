import hashlib
import json
import os
import re

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from google import genai
from google.genai import types


load_dotenv()


GEMINI_MODEL = (
    "gemini-2.5-flash"
)


def clean_env_value(
    value
):

    if not value:

        return ""

    return str(
        value
    ).strip()


def generate_unique_id(
    title,
    organization,
    source_url
):

    text = (
        f"{title}|"
        f"{organization}|"
        f"{source_url}"
    )

    digest = (
        hashlib.sha256(
            text.encode(
                "utf-8"
            )
        )
        .hexdigest()
    )

    return int(
        digest[:12],
        16
    ) % 900000000


# ============================================================
# BUILD SEARCH QUERY
# ============================================================

def build_search_query(
    student
):

    opportunity_type = (

        student.get(
            "opportunity_type",
            "internship"
        )

        .strip()

        .lower()
    )

    branch = student.get(
        "branch",
        ""
    ).strip()

    location = student.get(
        "location",
        "India"
    ).strip()

    interests = student.get(
        "interests",
        []
    )

    skills = student.get(
        "skills",
        []
    )

    keywords = []

    if branch:

        keywords.append(
            branch
        )

    keywords.extend(
        interests[:3]
    )

    keywords.extend(
        skills[:3]
    )

    keyword_text = " ".join(

        str(item).strip()

        for item in keywords

        if str(item).strip()
    )

    search_map = {

        "internship":
        (
            f"{keyword_text} internship "
            f"students apply openings "
            f"{location}"
        ),

        "hackathon":
        (
            f"{keyword_text} hackathon "
            f"registration students "
            f"{location}"
        ),

        "job":
        (
            f"{keyword_text} fresher "
            f"entry level job apply "
            f"{location}"
        ),

        "scholarship":
        (
            f"{keyword_text} scholarship "
            f"students apply "
            f"{location}"
        ),

        "competition":
        (
            f"{keyword_text} competition "
            f"registration students "
            f"{location}"
        ),
    }

    return search_map.get(

        opportunity_type,

        (
            f"{keyword_text} "
            f"{opportunity_type} "
            f"opportunities "
            f"{location}"
        )
    )


# ============================================================
# SERPAPI SEARCH
# ============================================================

def search_serpapi(
    query,
    max_results
):

    serpapi_key = (
        clean_env_value(
            os.getenv(
                "SERPAPI_API_KEY"
            )
        )
    )

    if not serpapi_key:

        raise ValueError(
            "SERPAPI_API_KEY is missing."
        )

    url = (
        "https://serpapi.com/search"
    )

    params = {

        "engine":
        "google",

        "q":
        query,

        "hl":
        "en",

        "gl":
        "in",

        "num":
        max_results,

        "api_key":
        serpapi_key
    }

    response = requests.get(

        url,

        params=params,

        timeout=30
    )

    if response.status_code != 200:

        raise ValueError(

            f"SerpApi request failed: "
            f"{response.status_code}"
        )

    data = response.json()

    return data.get(
        "organic_results",
        []
    )


# ============================================================
# FETCH PAGE CONTENT
# ============================================================

def fetch_page_content(
    url
):

    if not url:

        return ""

    try:

        headers = {

            "User-Agent":
            (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120 Safari/537.36"
            )
        }

        response = requests.get(

            url,

            headers=headers,

            timeout=12
        )

        if response.status_code != 200:

            return ""

        soup = BeautifulSoup(

            response.text,

            "html.parser"
        )

        for tag in soup([

            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"

        ]):

            tag.decompose()


        text = soup.get_text(

            " ",

            strip=True
        )

        text = re.sub(

            r"\s+",

            " ",

            text
        )

        return text[:12000]


    except Exception as error:

        print(
            f"Could not fetch page: "
            f"{error}"
        )

        return ""


# ============================================================
# CREATE RAG DOSSIER
# ============================================================

def create_search_dossier(
    results
):

    dossier_parts = []

    for index, result in enumerate(
        results
    ):

        title = result.get(
            "title",
            ""
        )

        snippet = result.get(
            "snippet",
            ""
        )

        link = result.get(
            "link",
            ""
        )

        source = result.get(
            "source",
            ""
        )

        date = result.get(
            "date",
            ""
        )

        page_content = (
            fetch_page_content(
                link
            )
        )

        dossier_parts.append(

            f"""
================================================
SEARCH RESULT {index + 1}
================================================

TITLE:
{title}

SOURCE:
{source}

DATE:
{date}

SEARCH SNIPPET:
{snippet}

SOURCE URL:
{link}

PAGE CONTENT:
{page_content[:6000]}
"""
        )

    return "\n".join(
        dossier_parts
    )


# ============================================================
# GEMINI RAG EXTRACTION
# ============================================================

def parse_with_gemini(
    student,
    dossier,
    max_results
):

    gemini_key = (
        clean_env_value(
            os.getenv(
                "GEMINI_API_KEY"
            )
        )
    )

    if not gemini_key:

        raise ValueError(
            "GEMINI_API_KEY is missing."
        )

    opportunity_type = (
        student.get(
            "opportunity_type",
            "internship"
        )
    )

    prompt = f"""
You are a retrieval-grounded opportunity extraction engine.

You must use ONLY the evidence provided below.

The user is searching for:

Opportunity type:
{opportunity_type}

Student profile:
{json.dumps(student, indent=2)}

Your task:

1. Identify real opportunities.
2. Remove irrelevant results.
3. Extract only information supported by evidence.
4. Never invent deadlines, stipend, eligibility, or skills.
5. Keep the exact source URL.
6. Prefer official organization sources.

Return only valid JSON.

Schema:

{{
    "opportunities": [
        {{
            "title": "string",
            "organization": null,
            "description": "string",
            "year": [],
            "branches": [],
            "skills": [],
            "location": null,
            "remote": null,
            "deadline": null,
            "stipend": null,
            "posted_time_ago": null,
            "is_still_accepting": null,
            "verification_score": "Low",
            "source_url": "string",
            "application_url": null
        }}
    ]
}}

Rules:

- Return maximum {max_results}.
- Never invent information.
- Use null when scalar information is unknown.
- Use [] when list information is unknown.
- is_still_accepting must be null unless evidence clearly supports it.
- application_url must be an exact application URL found in the evidence.
- If no application URL is found, use null.
- verification_score must be exactly High, Medium, or Low.
- High = official organization source.
- Medium = trusted opportunity platform.
- Low = unclear or secondary source.

WEB EVIDENCE:

{dossier}
"""

    client = genai.Client(
        api_key=gemini_key
    )

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

    if not raw_text:

        raise ValueError(
            "Gemini returned empty content."
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


# ============================================================
# NORMALIZE RESULTS
# ============================================================

def normalize_opportunities(
    opportunities
):

    normalized = []

    for opportunity in opportunities:

        title = opportunity.get(
            "title"
        )

        source_url = opportunity.get(
            "source_url"
        )

        if not title or not source_url:

            continue

        organization = (
            opportunity.get(
                "organization"
            )
            or ""
        )

        opportunity["id"] = (
            generate_unique_id(

                title,

                organization,

                source_url
            )
        )

        for field in [

            "year",
            "branches",
            "skills"

        ]:

            if not isinstance(
                opportunity.get(
                    field
                ),
                list
            ):

                opportunity[field] = []

        verification_score = (
            opportunity.get(
                "verification_score",
                "Low"
            )
        )

        if verification_score not in [

            "High",
            "Medium",
            "Low"

        ]:

            opportunity[
                "verification_score"
            ] = "Low"

        normalized.append(
            opportunity
        )

    return normalized


# ============================================================
# MAIN SEARCH
# ============================================================

def search_real_opportunities(
    student,
    max_results=10
):

    try:

        search_query = (
            build_search_query(
                student
            )
        )

        search_results = (
            search_serpapi(

                search_query,

                max_results
            )
        )

        if not search_results:

            return []

        dossier = (
            create_search_dossier(
                search_results
            )
        )

        parsed_data = (
            parse_with_gemini(

                student,

                dossier,

                max_results
            )
        )

        opportunities = (
            parsed_data.get(
                "opportunities",
                []
            )
        )

        final_results = (
            normalize_opportunities(
                opportunities
            )
        )

        print(
            f"Final opportunities: "
            f"{len(final_results)}"
        )

        return final_results


    except Exception as error:

        print(
            f"LIVE SEARCH ERROR: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        return []