import hashlib
import json
import os
import re

from urllib.parse import urlparse

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from .client import (
    ai_available,
    generate_json,
)


load_dotenv()


KNOWN_SKILLS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "TypeScript",
    "React",
    "FastAPI",
    "Django",
    "Flask",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",
    "Git",
    "GitHub",
    "Docker",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Data Science",
    "Pandas",
    "NumPy",
    "PyTorch",
    "TensorFlow",
    "REST APIs",
]


def clean_env_value(
    value,
):
    return (
        str(value or "")
        .strip()
    )


def generate_unique_id(
    title,
    organization,
    source_url,
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
        16,
    ) % 900000000


def domain_name(
    url,
):
    try:
        return (
            urlparse(
                url or ""
            )
            .netloc
            .replace(
                "www.",
                "",
            )
        )
    except Exception:
        return ""


# ============================================================
# MULTI-QUERY DISCOVERY
# ============================================================

def build_search_queries(
    student,
):
    opportunity_type = (
        student.get(
            "opportunity_type",
            "internship",
        )
        or "internship"
    ).strip().lower()

    location = (
        student.get(
            "location",
            "India",
        )
        or "India"
    ).strip()

    keywords = []

    branch = (
        student.get(
            "branch",
            "",
        )
        or ""
    ).strip()

    if branch:
        keywords.append(branch)

    keywords.extend(
        student.get(
            "interests",
            [],
        )[:3]
    )

    keywords.extend(
        student.get(
            "skills",
            [],
        )[:4]
    )

    keyword_text = " ".join(
        str(item).strip()
        for item in keywords
        if str(item).strip()
    )

    query_map = {
        "internship": [
            (
                f"{keyword_text} internship "
                f"students apply {location}"
            ),

            (
                f"{keyword_text} student "
                f"internship 2026 official"
            ),

            (
                f"{keyword_text} internship "
                f"site:linkedin.com OR "
                f"site:internshala.com"
            ),
        ],

        "hackathon": [
            (
                f"{keyword_text} hackathon "
                f"registration students 2026"
            ),

            (
                f"{keyword_text} student "
                f"hackathon official registration"
            ),

            (
                f"{keyword_text} hackathon "
                f"site:devpost.com OR "
                f"site:unstop.com"
            ),
        ],

        "scholarship": [
            (
                f"{keyword_text} scholarship "
                f"students apply 2026"
            ),

            (
                f"{keyword_text} scholarship "
                f"official application"
            ),

            (
                f"{keyword_text} scholarship "
                f"site:gov.in OR site:edu.in"
            ),
        ],

        "competition": [
            (
                f"{keyword_text} student "
                f"competition registration"
            ),

            (
                f"{keyword_text} competition "
                f"2026 official"
            ),

            (
                f"{keyword_text} student "
                f"challenge site:unstop.com"
            ),
        ],

        "job": [
            (
                f"{keyword_text} fresher "
                f"entry level jobs {location}"
            ),

            (
                f"{keyword_text} graduate "
                f"jobs official careers"
            ),

            (
                f"{keyword_text} fresher "
                f"site:linkedin.com jobs"
            ),
        ],
    }

    return query_map.get(
        opportunity_type,

        [
            (
                f"{keyword_text} "
                f"{opportunity_type} "
                f"opportunities {location}"
            ),
        ],
    )


# ============================================================
# SERPAPI
# ============================================================

def search_serpapi(
    query,
    max_results,
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

    response = requests.get(
        "https://serpapi.com/search",

        params={
            "engine": "google",
            "q": query,
            "hl": "en",
            "gl": "in",
            "num": max_results,
            "api_key": serpapi_key,
        },

        timeout=30,
    )

    if not response.ok:
        raise ValueError(
            "SerpApi request failed: "
            f"{response.status_code}"
        )

    data = response.json()

    return data.get(
        "organic_results",
        [],
    )


def search_multiple_queries(
    student,
    max_results,
):
    queries = build_search_queries(
        student
    )

    collected = []

    per_query = max(
        3,
        max_results // max(
            1,
            len(queries),
        ),
    )

    for query in queries:
        try:
            print(
                f"\nSEARCH QUERY:\n{query}"
            )

            results = search_serpapi(
                query,
                per_query,
            )

            collected.extend(
                results
            )

        except Exception as error:
            print(
                f"Search query failed: "
                f"{error}"
            )

    seen = set()
    unique = []

    for result in collected:
        link = (
            result.get("link")
            or ""
        )

        if not link or link in seen:
            continue

        seen.add(link)
        unique.append(result)

    return unique[:max_results]


# ============================================================
# PAGE EVIDENCE
# ============================================================

def fetch_page_content(
    url,
):
    if not url:
        return ""

    try:
        response = requests.get(
            url,

            headers={
                "User-Agent":
                    (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 "
                        "Chrome/120 Safari/537.36"
                    )
            },

            timeout=12,
        )

        if not response.ok:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
        ]):
            tag.decompose()

        text = soup.get_text(
            " ",
            strip=True,
        )

        return re.sub(
            r"\s+",
            " ",
            text,
        )[:6000]

    except Exception:
        return ""


def create_search_dossier(
    results,
):
    parts = []

    for index, result in enumerate(
        results
    ):
        title = (
            result.get(
                "title",
                "",
            )
        )

        snippet = (
            result.get(
                "snippet",
                "",
            )
        )

        link = (
            result.get(
                "link",
                "",
            )
        )

        page_content = (
            fetch_page_content(
                link
            )
        )

        parts.append(
            f"""
RESULT {index + 1}

TITLE:
{title}

SNIPPET:
{snippet}

SOURCE URL:
{link}

PAGE CONTENT:
{page_content}
"""
        )

    return "\n".join(parts)


# ============================================================
# GROK STRUCTURED EXTRACTION
# ============================================================

SEARCH_SCHEMA = {
    "type": "object",

    "properties": {
        "opportunities": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {
                    "title": {
                        "type": "string",
                    },

                    "organization": {
                        "type": ["string", "null"],
                    },

                    "type": {
                        "type": ["string", "null"],
                    },

                    "description": {
                        "type": "string",
                    },

                    "year": {
                        "type": "array",

                        "items": {
                            "type": "string",
                        },
                    },

                    "branches": {
                        "type": "array",

                        "items": {
                            "type": "string",
                        },
                    },

                    "skills": {
                        "type": "array",

                        "items": {
                            "type": "string",
                        },
                    },

                    "location": {
                        "type": ["string", "null"],
                    },

                    "remote": {
                        "type": ["boolean", "null"],
                    },

                    "deadline": {
                        "type": ["string", "null"],
                    },

                    "stipend": {
                        "type": [
                            "string",
                            "number",
                            "null",
                        ],
                    },

                    "posted_time_ago": {
                        "type": ["string", "null"],
                    },

                    "source_url": {
                        "type": "string",
                    },

                    "application_url": {
                        "type": ["string", "null"],
                    },
                },

                "required": [
                    "title",
                    "organization",
                    "type",
                    "description",
                    "year",
                    "branches",
                    "skills",
                    "location",
                    "remote",
                    "deadline",
                    "stipend",
                    "posted_time_ago",
                    "source_url",
                    "application_url",
                ],

                "additionalProperties": False,
            },
        },
    },

    "required": [
        "opportunities",
    ],

    "additionalProperties": False,
}


def parse_with_ai(
    student,
    dossier,
    max_results,
):

    result = generate_json(

        system_prompt="""
You are a strict retrieval-grounded student opportunity extraction engine.

Use only evidence supplied in the search dossier.

Never invent:
- deadlines
- stipend
- eligibility
- organization names
- skills
- locations
- application links

Prefer official sources when evidence supports them.

Reject irrelevant, expired or unrelated results.

If information is unknown:

- use null for unknown scalar values
- use [] for unknown list values

Return only opportunities that are genuinely relevant to
the student's requested opportunity type and profile.
""",

        user_prompt=f"""
Student profile:

{json.dumps(student, indent=2)}

Return at most {max_results} relevant opportunities.

For every opportunity:

- title must come from evidence
- organization must come from evidence where possible
- source_url must be the exact evidence URL
- application_url must only be used if the evidence clearly
  represents an application destination
- skills must only contain skills supported by evidence
- do not invent dates
- do not invent stipend information
- do not invent eligibility requirements

EVIDENCE:

{dossier}
""",

        schema_name="student_opportunity_search",

        schema=SEARCH_SCHEMA,
    )

    opportunities = (
        result.get(
            "opportunities",
            [],
        )
    )

    if not isinstance(
        opportunities,
        list,
    ):
        return {
            "opportunities": []
        }

    return {
        "opportunities":
        opportunities[:max_results]
    }
    prompt = f"""
Student profile:

{json.dumps(student, indent=2)}

Return at most {max_results} real opportunities.

For each opportunity, use exactly this JSON structure:

{{
  "opportunities": [
    {{
      "title": "string",
      "organization": "string or null",
      "type": "string or null",
      "description": "string",
      "year": [],
      "branches": [],
      "skills": [],
      "location": "string or null",
      "remote": true,
      "deadline": "string or null",
      "stipend": "string or number or null",
      "posted_time_ago": "string or null",
      "source_url": "string",
      "application_url": "string or null"
    }}
  ]
}}

Rules:

- Use only evidence supplied below.
- Never invent deadlines.
- Never invent stipend information.
- Never invent eligibility requirements.
- Never invent organization names.
- Never invent skills.
- Never invent locations.
- Never invent application links.
- Prefer official sources.
- Reject irrelevant results.
- Preserve the exact evidence source URL.
- application_url must only be used when the evidence clearly indicates an application destination.
- Unknown scalar values must be null.
- Unknown lists must be [].
- Return only valid JSON.
- Do not include markdown.

EVIDENCE:

{dossier}
"""

    return generate_json(
        prompt=prompt,

        system_prompt="""
You are a strict retrieval-grounded student opportunity extraction engine.

Use only evidence supplied by the user.

Never invent deadlines, stipend, eligibility, organization names,
skills, locations, or application links.

Prefer official sources.

Reject irrelevant results.

Return only valid JSON.
Do not use markdown.
""",
    )


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def infer_skills(
    text,
):
    lower_text = (
        text or ""
    ).lower()

    return [
        skill
        for skill in KNOWN_SKILLS
        if skill.lower()
        in lower_text
    ]


def infer_remote(
    text,
):
    lower_text = (
        text or ""
    ).lower()

    if "remote" in lower_text:
        return True

    if (
        "on-site" in lower_text
        or "onsite" in lower_text
    ):
        return False

    return None


def infer_deadline(
    text,
):
    match = re.search(
        r"\d{4}-\d{2}-\d{2}",
        text or "",
    )

    if match:
        return match.group(0)

    return None


def rule_based_results(
    student,
    results,
):
    opportunity_type = (
        student.get(
            "opportunity_type",
            "internship",
        )
    )

    fallback = []

    for result in results:
        title = (
            result.get(
                "title",
                ""
            )
            .strip()
        )

        link = (
            result.get(
                "link",
                ""
            )
            .strip()
        )

        snippet = (
            result.get(
                "snippet",
                ""
            )
            .strip()
        )

        if not title or not link:
            continue

        text = (
            f"{title} {snippet}"
        )

        fallback.append({
            "title": title,

            "organization":
                domain_name(link),

            "type":
                opportunity_type,

            "description":
                snippet or
                "Live opportunity discovered "
                "from web search.",

            "year": [],

            "branches": [],

            "skills":
                infer_skills(text),

            "location": None,

            "remote":
                infer_remote(text),

            "deadline":
                infer_deadline(text),

            "stipend": None,

            "posted_time_ago": None,

            "source_url": link,

            "application_url": link,
        })

    return fallback


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_opportunities(
    opportunities,
):
    normalized = []

    for opportunity in opportunities:
        opportunity = dict(
            opportunity
        )

        title = (
            str(
                opportunity.get(
                    "title",
                    "",
                )
            )
            .strip()
        )

        source_url = (
            str(
                opportunity.get(
                    "source_url",
                    "",
                )
            )
            .strip()
        )

        if not title or not source_url:
            continue

        organization = (
            opportunity.get(
                "organization"
            )
            or domain_name(
                source_url
            )
        )

        opportunity[
            "organization"
        ] = organization

        opportunity[
            "id"
        ] = generate_unique_id(
            title,
            organization,
            source_url,
        )

        for field in [
            "year",
            "branches",
            "skills",
        ]:
            if not isinstance(
                opportunity.get(field),
                list,
            ):
                opportunity[field] = []

        

        normalized.append(
            opportunity
        )

    return normalized


# ============================================================
# MAIN SEARCH
# ============================================================

def search_real_opportunities(
    student,
    max_results=10,
):
    print(
        "\n========================================"
    )

    print(
        "STARTING MULTI-QUERY OPPORTUNITY SEARCH"
    )

    print(
        "========================================"
    )

    search_results = (
        search_multiple_queries(
            student,
            max_results=max_results * 2,
        )
    )

    if not search_results:
        return []

    opportunities = []

    if ai_available():
        try:
            dossier = (
                create_search_dossier(
                    search_results[:10]
                )
            )

            parsed = parse_with_ai(
                student,
                dossier,
                max_results,
            )

            opportunities = (
                parsed.get(
                    "opportunities",
                    [],
                )
            )

            print(
                "AI EXTRACTION: SUCCESS"
            )

        except Exception as error:
            print(
                f"AI EXTRACTION FAILED: "
                f"{type(error).__name__}: "
                f"{error}"
            )

    if not opportunities:
        print(
            "USING RULE-BASED FALLBACK"
        )

        opportunities = (
            rule_based_results(
                student,
                search_results,
            )
        )

    final_results = (
        normalize_opportunities(
            opportunities
        )
    )

    print(
        f"FINAL RESULTS: "
        f"{len(final_results)}"
    )

    return final_results[:max_results]