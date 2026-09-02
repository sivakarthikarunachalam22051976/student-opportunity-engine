from pathlib import Path
import json
import os
import re
from datetime import date, datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Support BOTH:
#   1. uvicorn backend.main:app (package import)
#   2. uvicorn main:app from inside backend/
try:
    from .student import student_profile
    from .eligibility import check_eligibility
    from .matching import calculate_match
    from .gap_analysis import find_skill_gaps
    from .semantic_matching import get_semantic_skill_match
    from .resource_roadmap import create_resource_roadmap
    from .resume_parser import parse_resume_text
    from .skill_normalizer import normalize_skills

    from .live_opportunities import (
        save_live_opportunities,
        get_all_live_opportunities,
    )

    from .ai.opportunity_parser import parse_opportunity_text
    from .ai.web_search import search_real_opportunities

    from .intelligence_features import (
    profile_intelligence,
    readiness_simulator,
    application_strategy,
    build_opportunity_workspace,
    demo_snapshot,
    detect_changes,
    export_preparation_plan,
    explain_ranking,
    calculate_freshness,
    build_source_evidence,
    readiness_checklist,
    deadline_intelligence,
    best_next_action,
    portfolio_impact,
    weekly_mission,
    quality_control,
        remove_duplicate_opportunities,
    )
except ImportError:
    from student import student_profile
    from eligibility import check_eligibility
    from matching import calculate_match
    from gap_analysis import find_skill_gaps
    from semantic_matching import get_semantic_skill_match
    from resource_roadmap import create_resource_roadmap
    from resume_parser import parse_resume_text
    from skill_normalizer import normalize_skills

    from live_opportunities import (
        save_live_opportunities,
        get_all_live_opportunities,
    )

    from ai.opportunity_parser import parse_opportunity_text
    from ai.web_search import search_real_opportunities

    from intelligence_features import (
        profile_intelligence,
        readiness_simulator,
        application_strategy,
        build_opportunity_workspace,
        demo_snapshot,
        detect_changes,
        export_preparation_plan,
        explain_ranking,
        calculate_freshness,
        build_source_evidence,
        readiness_checklist,
        deadline_intelligence,
        best_next_action,
        portfolio_impact,
        weekly_mission,
        quality_control,
        remove_duplicate_opportunities,
    )


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Student Opportunity Engine",
    version="2.0.0",
    description=(
        "AI-powered opportunity discovery, student matching, "
        "gap analysis, preparation intelligence and career path planning."
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin
        for origin in [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "https://student-opportunity-engine-eta.vercel.app",
            os.getenv("FRONTEND_URL"),
        ]
        if origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA
# ============================================================

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "opportunities.json"
)


def load_opportunities():

    if not DATA_FILE.exists():
        return []

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception as error:

        print(
            f"Error loading opportunities.json: {error}"
        )

        return []


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_text_value(value):

    return str(
        value or ""
    ).strip().lower()


def normalize_skill_set(skills):

    if not isinstance(skills, (list, tuple, set)):
        return set()

    return {
        normalize_text_value(skill)
        for skill in skills
        if normalize_text_value(skill)
    }


def normalize_branch(value):

    text = normalize_text_value(value)

    text = re.sub(
        r"[^a-z0-9]",
        "",
        text,
    )

    aliases = {

        "cse":
        "computerscienceengineering",

        "cs":
        "computerscience",

        "computerscience":
        "computerscience",

        "computerscienceengineering":
        "computerscienceengineering",

        "ise":
        "informationtechnology",

        "it":
        "informationtechnology",

        "informationtechnology":
        "informationtechnology",

        "ai":
        "artificialintelligence",

        "aiml":
        "artificialintelligencemachinelearning",

        "artificialintelligence":
        "artificialintelligence",

        "artificialintelligencemachinelearning":
        "artificialintelligencemachinelearning",

        "ece":
        "electronicscommunicationengineering",

        "eee":
        "electricalelectronicsengineering",

        "me":
        "mechanicalengineering",

        "civil":
        "civilengineering",
    }

    return aliases.get(
        text,
        text,
    )


def normalize_opportunity_type(value):

    value = normalize_text_value(value)

    aliases = {

        "intern":
        "internship",

        "internships":
        "internship",

        "job":
        "job",

        "jobs":
        "job",

        "hackathon":
        "hackathon",

        "competition":
        "competition",

        "course":
        "course",

        "fellowship":
        "fellowship",

        "scholarship":
        "scholarship",
    }

    return aliases.get(
        value,
        value or "opportunity",
    )


# ============================================================
# OPPORTUNITY ID AND DEDUPLICATION
# ============================================================

def create_opportunity_identity(
    opportunity,
):

    title = normalize_text_value(
        opportunity.get("title")
    )

    organization = normalize_text_value(
        opportunity.get("organization")
        or opportunity.get("company")
    )

    application_url = normalize_text_value(
        opportunity.get("application_url")
    )

    source_url = normalize_text_value(
        opportunity.get("source_url")
    )

    return (
        f"{title}|"
        f"{organization}|"
        f"{application_url}|"
        f"{source_url}"
    )


def ensure_unique_opportunity_ids(
    opportunities: list[dict],
) -> list[dict]:
    """Return valid, identity-deduplicated opportunities with unique integer IDs."""

    if not isinstance(opportunities, list):
        return []

    used_ids: set[int] = set()
    seen_identity: set[str] = set()
    valid_ids: list[int] = []

    for original_item in opportunities:
        if not isinstance(original_item, dict):
            continue
        try:
            candidate = int(original_item.get("id"))
        except (TypeError, ValueError):
            continue
        if candidate > 0:
            valid_ids.append(candidate)

    next_id = max(valid_ids, default=0) + 1
    result: list[dict] = []

    for original_item in opportunities:
        if not isinstance(original_item, dict):
            continue

        item = dict(original_item)
        identity = create_opportunity_identity(item)

        # Empty records are not useful and repeated records should not reach the API.
        if identity in seen_identity:
            continue
        seen_identity.add(identity)

        try:
            candidate = int(item.get("id"))
        except (TypeError, ValueError):
            candidate = 0

        if candidate <= 0 or candidate in used_ids:
            while next_id in used_ids:
                next_id += 1
            candidate = next_id
            next_id += 1

        item["id"] = candidate
        used_ids.add(candidate)
        result.append(item)

    return result



def assign_live_opportunity_ids(
    live_opportunities,
):

    built_in = (
        load_opportunities()
    )

    built_in_ids = set()
    max_id = 0


    for item in built_in:

        try:

            opportunity_id = int(
                item.get("id")
            )

            if opportunity_id > 0:

                built_in_ids.add(
                    opportunity_id
                )

                max_id = max(
                    max_id,
                    opportunity_id,
                )

        except (
            TypeError,
            ValueError,
        ):
            pass


    existing_live = (
        get_all_live_opportunities()
    )


    for item in existing_live:

        try:

            opportunity_id = int(
                item.get("id")
            )

            if opportunity_id > 0:

                built_in_ids.add(
                    opportunity_id
                )

                max_id = max(
                    max_id,
                    opportunity_id,
                )

        except (
            TypeError,
            ValueError,
        ):
            pass


    next_id = max_id + 1
    assigned = []
    seen_identity = set()


    for original_item in live_opportunities:

        if not isinstance(
            original_item,
            dict,
        ):
            continue


        item = dict(
            original_item
        )

        identity = (
            create_opportunity_identity(
                item
            )
        )

        if identity in seen_identity:
            continue


        seen_identity.add(
            identity
        )


        while next_id in built_in_ids:

            next_id += 1


        item["id"] = next_id

        built_in_ids.add(
            next_id
        )

        next_id += 1

        assigned.append(
            item
        )


    return assigned


# ============================================================
# OPPORTUNITY HELPERS
# ============================================================

def get_all_opportunities():

    built_in = (
        load_opportunities()
    )

    live = (
        get_all_live_opportunities()
    )

    combined = (
        built_in + live
    )

    return ensure_unique_opportunity_ids(
        combined
    )


def find_opportunity_by_id(
    opportunity_id: int,
):

    opportunities = (
        get_all_opportunities()
    )


    for item in opportunities:

        try:

            item_id = int(
                item.get(
                    "id",
                    -1,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            continue


        if item_id == opportunity_id:

            return item


    return None


# ============================================================
# DEADLINE INTELLIGENCE
# ============================================================

def calculate_deadline_intelligence(
    deadline,
):

    if not deadline:

        return {

            "urgency":
            "Unknown",

            "days_remaining":
            None,

            "application_strategy":
            "Check the source for the latest application deadline.",
        }


    try:

        deadline_date = (
            date.fromisoformat(
                str(deadline)[:10]
            )
        )

        days_remaining = (
            deadline_date
            -
            date.today()
        ).days


        if days_remaining < 0:

            urgency = "Expired"

            strategy = (
                "The listed deadline has passed. "
                "Verify whether applications are still open."
            )


        elif days_remaining <= 2:

            urgency = "Critical"

            strategy = (
                "Apply immediately. Do not wait to complete every improvement."
            )


        elif days_remaining <= 7:

            urgency = "Urgent"

            strategy = (
                "Prioritize application readiness and close only the highest-impact gaps."
            )


        elif days_remaining <= 21:

            urgency = "Soon"

            strategy = (
                "Split preparation into focused milestones and apply before perfectionism delays you."
            )


        else:

            urgency = "Normal"

            strategy = (
                "You have enough runway to improve your profile and build stronger portfolio proof."
            )


        return {

            "urgency":
            urgency,

            "days_remaining":
            days_remaining,

            "application_strategy":
            strategy,
        }


    except Exception:

        return {

            "urgency":
            "Unknown",

            "days_remaining":
            None,

            "application_strategy":
            "Verify the deadline directly from the source.",
        }


# ============================================================
# TRUST INTELLIGENCE
# ============================================================

OFFICIAL_SOURCE_MARKERS = [

    ".gov",

    ".edu",

    "careers.",

    "/careers",

    "jobs.",

    "/jobs",

    "linkedin.com",

    "internshala.com",

    "unstop.com",

    "devpost.com",

    "wellfound.com",

    "greenhouse.io",

    "lever.co",
]


def calculate_trust_score(
    opportunity,
):

    score = 0

    source_url = str(
        opportunity.get(
            "source_url"
        ) or ""
    ).strip().lower()

    application_url = str(
        opportunity.get(
            "application_url"
        ) or ""
    ).strip().lower()

    organization = str(
        opportunity.get(
            "organization"
        ) or ""
    ).strip()

    description = str(
        opportunity.get(
            "description"
        ) or ""
    ).strip()

    skills = (
        opportunity.get(
            "skills",
            []
        )
    )

    deadline = (
        opportunity.get(
            "deadline"
        )
    )


    if source_url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        score += 18


    if application_url.startswith(
        (
            "http://",
            "https://",
        )
    ):

        score += 12


    if any(
        marker in source_url
        for marker in OFFICIAL_SOURCE_MARKERS
    ):

        score += 25


    if (
        application_url
        and
        application_url != source_url
    ):

        score += 5


    if (
        organization
        and
        normalize_text_value(
            organization
        )
        not in {

            "unknown",

            "unknown organization",

            "n/a",
        }
    ):

        score += 10


    if len(description) >= 80:

        score += 8


    if len(description) >= 250:

        score += 5


    if isinstance(
        skills,
        list,
    ) and len(skills) > 0:

        score += 5


    if (
        opportunity.get("location")
        or
        opportunity.get("remote") is True
    ):

        score += 3


    if deadline:

        score += 4


    verification_score = (
        str(
            opportunity.get(
                "verification_score"
            ) or ""
        )
        .strip()
        .lower()
    )


    verification_bonus = {

        "verified":
        15,

        "high":
        12,

        "medium":
        6,

        "low":
        0,
    }


    score += verification_bonus.get(
        verification_score,
        0,
    )


    if not source_url:

        score -= 15


    if not application_url:

        score -= 5


    if not description:

        score -= 12


    if (
        not organization
        or
        normalize_text_value(
            organization
        )
        in {
            "unknown",
            "unknown organization",
        }
    ):

        score -= 8


    return max(
        15,
        min(
            99,
            score,
        ),
    )


def get_trust_label(
    score,
):

    if score >= 90:
        return "Verified"

    if score >= 80:
        return "High"

    if score >= 65:
        return "Good"

    if score >= 45:
        return "Moderate"

    return "Low"


def build_trust_reasons(
    opportunity,
    score,
):

    reasons = []

    source_url = str(
        opportunity.get(
            "source_url"
        ) or ""
    ).strip()


    if source_url:

        reasons.append(
            "A source URL is available for independent verification."
        )


    if opportunity.get(
        "application_url"
    ):

        reasons.append(
            "A direct application destination is available."
        )


    if opportunity.get(
        "organization"
    ):

        reasons.append(
            "The listing identifies an organization."
        )


    if opportunity.get(
        "deadline"
    ):

        reasons.append(
            "The opportunity includes deadline information."
        )


    if score >= 80:

        reasons.append(
            "Multiple strong listing signals increase source confidence."
        )


    elif score < 45:

        reasons.append(
            "Important listing information is missing. Verify before applying."
        )


    return reasons[:5]


# ============================================================
# MATCH INTELLIGENCE
# ============================================================

def build_match_breakdown(
    student,
    opportunity,
):

    student_skills = (
        normalize_skill_set(
            student.get(
                "skills",
                [],
            )
        )
    )


    required_skills = (
        normalize_skill_set(
            opportunity.get(
                "skills",
                [],
            )
        )
    )


    if required_skills:

        matched_skills = (
            student_skills.intersection(
                required_skills
            )
        )

        skill_points = round(
            (
                len(
                    matched_skills
                )
                /
                len(
                    required_skills
                )
            )
            * 50
        )

    else:

        matched_skills = set()

        skill_points = 25


    opportunity_text = " ".join([

        normalize_text_value(
            opportunity.get(
                "title"
            )
        ),

        normalize_text_value(
            opportunity.get(
                "description"
            )
        ),

        " ".join(

            normalize_text_value(
                skill
            )

            for skill in opportunity.get(
                "skills",
                [],
            )
        ),
    ])


    interests = [

        normalize_text_value(
            interest
        )

        for interest in student.get(
            "interests",
            [],
        )

        if normalize_text_value(
            interest
        )
    ]


    interest_matches = [

        interest

        for interest in interests

        if interest in opportunity_text
    ]


    if interests:

        interest_points = round(

            min(

                1,

                len(
                    interest_matches
                )
                /
                max(
                    len(interests),
                    1,
                ),
            )

            * 20
        )

    else:

        interest_points = 5


    student_branch = (
        normalize_branch(
            student.get(
                "branch"
            )
        )
    )


    opportunity_branches = {

        normalize_branch(
            branch
        )

        for branch in opportunity.get(
            "branches",
            [],
        )

        if normalize_branch(
            branch
        )
    }


    branch_points = 0


    if not opportunity_branches:

        branch_points = 10

    elif student_branch in opportunity_branches:

        branch_points = 15


    student_location = (
        normalize_text_value(
            student.get(
                "location"
            )
        )
    )


    opportunity_location = (
        normalize_text_value(
            opportunity.get(
                "location"
            )
        )
    )


    location_points = 0


    if opportunity.get(
        "remote"
    ) is True:

        location_points = 15


    elif (
        student_location
        and
        opportunity_location
        and
        (
            student_location
            in opportunity_location

            or

            opportunity_location
            in student_location
        )
    ):

        location_points = 15


    breakdown = [

        {

            "factor":
            "Skills",

            "points":
            skill_points,

            "maximum":
            50,
        },

        {

            "factor":
            "Interests",

            "points":
            interest_points,

            "maximum":
            20,
        },

        {

            "factor":
            "Branch",

            "points":
            branch_points,

            "maximum":
            15,
        },

        {

            "factor":
            "Location",

            "points":
            location_points,

            "maximum":
            15,
        },
    ]


    match_score = sum(

        item["points"]

        for item in breakdown
    )


    return {

        "match_score":
        max(
            0,
            min(
                100,
                match_score,
            ),
        ),

        "breakdown":
        breakdown,

        "matched_skill_count":
        len(
            matched_skills
        ),

        "required_skill_count":
        len(
            required_skills
        ),
    }


# ============================================================
# STUDENT READINESS
# ============================================================

def calculate_readiness_intelligence(
    student,
    opportunity,
):

    required_skills = [

        skill

        for skill in opportunity.get(
            "skills",
            [],
        )

        if normalize_text_value(
            skill
        )
    ]


    student_skills = (
        normalize_skill_set(
            student.get(
                "skills",
                [],
            )
        )
    )


    matched_skills = [

        skill

        for skill in required_skills

        if normalize_text_value(
            skill
        )
        in student_skills
    ]


    missing_skills = [

        skill

        for skill in required_skills

        if normalize_text_value(
            skill
        )
        not in student_skills
    ]


    if required_skills:

        skill_readiness = round(

            (
                len(
                    matched_skills
                )
                /
                len(
                    required_skills
                )
            )
            * 70
        )

    else:

        skill_readiness = 35


    portfolio_readiness = 10
    profile_quality = 10
    opportunity_clarity = 10


    if not student.get("name"):

        profile_quality -= 3


    if not student.get("branch"):

        profile_quality -= 3


    if not student.get("skills"):

        profile_quality -= 4


    if not opportunity.get("description"):

        opportunity_clarity = 4


    readiness = (

        skill_readiness
        +
        portfolio_readiness
        +
        profile_quality
        +
        opportunity_clarity
    )


    readiness = max(
        0,
        min(
            100,
            readiness,
        ),
    )


    if readiness >= 85:

        readiness_level = "Application Ready"

    elif readiness >= 65:

        readiness_level = "Competitive"

    elif readiness >= 40:

        readiness_level = "Developing"

    else:

        readiness_level = "Early Preparation"


    return {

        "readiness":
        readiness,

        "readiness_level":
        readiness_level,

        "matched_skills":
        matched_skills,

        "missing_skills":
        missing_skills,

        "skill_readiness":
        skill_readiness,

        "portfolio_readiness":
        portfolio_readiness,

        "profile_quality":
        profile_quality,

        "opportunity_clarity":
        opportunity_clarity,
    }


# ============================================================
# OPPORTUNITY ENRICHMENT
# ============================================================

def enrich_opportunity(
    opportunity,
):

    enriched = dict(
        opportunity
    )


    match_result = (
        calculate_match(
            student_profile,
            enriched,
        )
    )


    breakdown_result = (
        build_match_breakdown(
            student_profile,
            enriched,
        )
    )


    enriched[
        "match_score"
    ] = (

        breakdown_result.get(
            "match_score",
            match_result.get(
                "match_score",
                0,
            ),
        )
    )


    enriched[
        "trust_score"
    ] = (

        calculate_trust_score(
            enriched
        )
    )


    enriched[
        "trust_label"
    ] = (

        get_trust_label(
            enriched[
                "trust_score"
            ]
        )
    )


    enriched[
        "trust_reasons"
    ] = (

        build_trust_reasons(
            enriched,
            enriched[
                "trust_score"
            ],
        )
    )


    enriched[
        "deadline_intelligence"
    ] = (

        calculate_deadline_intelligence(
            enriched.get(
                "deadline"
            )
        )
    )


    readiness = (
        calculate_readiness_intelligence(
            student_profile,
            enriched,
        )
    )


    enriched[
        "readiness"
    ] = readiness.get(
        "readiness",
        0,
    )


    enriched[
        "readiness_level"
    ] = readiness.get(
        "readiness_level",
        "Developing",
    )


    if not enriched.get(
        "type"
    ):

        enriched[
            "type"
        ] = (

            student_profile.get(
                "opportunity_type",
                "Opportunity",
            )
            .replace(
                "_",
                " "
            )
            .title()
        )


    enriched[
        "type"
    ] = normalize_opportunity_type(
        enriched.get(
            "type"
        )
    ).title()


    if not isinstance(
        enriched.get(
            "suspicion_flags"
        ),
        list,
    ):

        enriched[
            "suspicion_flags"
        ] = []


    return enriched


# ============================================================
# REQUEST MODELS
# ============================================================

class OpportunityTextRequest(
    BaseModel
):

    text: str


class StudentProfileRequest(
    BaseModel
):

    name: str

    year: int

    branch: str

    location: str

    interests: list[str] = Field(
        default_factory=list
    )

    skills: list[str] = Field(
        default_factory=list
    )

    projects: list[str] = Field(
        default_factory=list
    )

    evidence: list[str] = Field(
        default_factory=list
    )

    opportunity_type: str = (
        "internship"
    )


class ResumeTextRequest(
    BaseModel
):

    text: str


# ============================================================
# ROOT AND HEALTH
# ============================================================

@app.get("/")
def root():

    return {

        "message":
        "Student Opportunity Engine backend is running!",

        "version":
        "2.0.0",
    }


@app.get("/api/health")
def health_check():

    return {

        "status":
        "online",

        "message":
        "Student Opportunity Engine backend is running",

        "version":
        "2.0.0",
    }


# ============================================================
# OPPORTUNITIES
# ============================================================

@app.get("/api/opportunities")
def get_opportunities():

    opportunities = (
        get_all_opportunities()
    )


    enriched_opportunities = [

        enrich_opportunity(
            opportunity
        )

        for opportunity in opportunities
    ]


    enriched_opportunities.sort(

        key=lambda item: (

            item.get(
                "match_score",
                0,
            ),

            item.get(
                "trust_score",
                0,
            ),

            item.get(
                "readiness",
                0,
            ),
        ),

        reverse=True,
    )


    return enriched_opportunities


# ============================================================
# STUDENT
# ============================================================

@app.get("/api/student")
def get_student():

    return student_profile


def update_student_profile_data(
    request: StudentProfileRequest,
):

    normalized_student_skills = (
        normalize_skills(
            request.skills
        )
    )


    student_profile.clear()


    student_profile.update({

        "name":
        request.name.strip(),

        "year":
        request.year,

        "branch":
        request.branch.strip(),

        "location":
        request.location.strip(),

        "interests":
        [

            interest.strip()

            for interest in request.interests

            if interest.strip()
        ],

        "skills":
        normalized_student_skills,

        "projects":
        [

            project.strip()

            for project in request.projects

            if project.strip()
        ],

        "evidence":
        [

            item.strip()

            for item in request.evidence

            if item.strip()
        ],

        "opportunity_type":
        normalize_opportunity_type(
            request.opportunity_type
        ),
    })


@app.post("/api/student/profile")
def update_student_profile(
    request: StudentProfileRequest,
):

    update_student_profile_data(
        request
    )


    return {

        "message":
        "Student profile updated successfully",

        "student":
        student_profile,
    }


# ============================================================
# LIVE AI SEARCH
# ============================================================

@app.post("/api/ai/search-opportunities")
def ai_search_opportunities(
    request: StudentProfileRequest,
):

    print(
        "\n========================================"
    )

    print(
        "STARTING LIVE OPPORTUNITY SEARCH"
    )

    print(
        "========================================"
    )


    update_student_profile_data(
        request
    )


    try:

        results = (
            search_real_opportunities(
                student_profile,
                max_results=10,
            )
        )


    except Exception as error:

        print(
            f"Live search failed: {error}"
        )

        raise HTTPException(

            status_code=500,

            detail=(
                "Live opportunity search failed: "
                f"{str(error)}"
            ),
        )


    if not isinstance(
        results,
        list,
    ):

        results = []


    results = (
        assign_live_opportunity_ids(
            results
        )
    )


    enriched_results = []


    for opportunity in results:

        try:

            enriched = (
                enrich_opportunity(
                    opportunity
                )
            )

            enriched_results.append(
                enriched
            )


        except Exception as error:

            print(
                f"Skipping invalid opportunity: {error}"
            )


    enriched_results.sort(

        key=lambda item: (

            item.get(
                "match_score",
                0,
            ),

            item.get(
                "trust_score",
                0,
            ),

            item.get(
                "readiness",
                0,
            ),
        ),

        reverse=True,
    )


    save_live_opportunities(
        enriched_results
    )


    print(
        f"Live opportunities stored: "
        f"{len(enriched_results)}"
    )


    return {

        "count":
        len(
            enriched_results
        ),

        "opportunities":
        enriched_results,

        "student":
        student_profile,
    }


# ============================================================
# ELIGIBILITY
# ============================================================

@app.get("/api/eligibility/{opportunity_id}")
def check_opportunity_eligibility(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    result = (
        check_eligibility(
            student_profile,
            opportunity,
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **result,
    }


# ============================================================
# MATCH
# ============================================================

@app.get("/api/match/{opportunity_id}")
def match_opportunity(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    eligibility = (
        check_eligibility(
            student_profile,
            opportunity,
        )
    )


    skill_match = (
        calculate_match(
            student_profile,
            opportunity,
        )
    )


    breakdown_result = (
        build_match_breakdown(
            student_profile,
            opportunity,
        )
    )


    readiness = (
        calculate_readiness_intelligence(
            student_profile,
            opportunity,
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "eligible":
        eligibility.get(
            "eligible",
            True,
        ),

        "match_score":
        breakdown_result.get(
            "match_score",
            skill_match.get(
                "match_score",
                0,
            ),
        ),

        "matched_skills":
        skill_match.get(
            "matched_skills",
            readiness.get(
                "matched_skills",
                [],
            ),
        ),

        "missing_skills":
        skill_match.get(
            "missing_skills",
            readiness.get(
                "missing_skills",
                [],
            ),
        ),

        "breakdown":
        breakdown_result.get(
            "breakdown",
            [],
        ),

        "readiness":
        readiness,

        "message":
        (
            "Strong fit."
            if eligibility.get(
                "eligible",
                True,
            )
            else
            "Eligibility requirements need attention."
        ),
    }


# ============================================================
# SEMANTIC MATCHING
# ============================================================

@app.get("/api/semantic-match/{opportunity_id}")
def semantic_match_opportunity(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    result = (
        get_semantic_skill_match(

            student_profile.get(
                "skills",
                [],
            ),

            opportunity.get(
                "skills",
                [],
            ),
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **result,
    }


# ============================================================
# GAP ANALYSIS
# ============================================================

@app.get("/api/gap_analysis/{opportunity_id}")
def get_skill_gaps(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    gaps = (
        find_skill_gaps(

            student_profile.get(
                "skills",
                [],
            ),

            opportunity.get(
                "skills",
                [],
            ),
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **gaps,
    }


# ============================================================
# RESOURCE ROADMAP
# ============================================================

@app.get("/api/resource-roadmap/{opportunity_id}")
def get_resource_roadmap(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    gaps = (
        find_skill_gaps(

            student_profile.get(
                "skills",
                [],
            ),

            opportunity.get(
                "skills",
                [],
            ),
        )
    )


    roadmap = (
        create_resource_roadmap(

            gaps.get(
                "missing_skills",
                [],
            ),

            opportunity.get(
                "skills",
                [],
            ),
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "current_skills":
        normalize_skills(

            student_profile.get(
                "skills",
                [],
            )
        ),

        "missing_skills":
        gaps.get(
            "missing_skills",
            [],
        ),

        "roadmap":
        roadmap,
    }


# ============================================================
# RESUME PARSER
# ============================================================

@app.post("/api/resume/parse")
def parse_resume(
    request: ResumeTextRequest,
):

    return parse_resume_text(
        request.text
    )


# ============================================================
# AI OPPORTUNITY PARSER
# ============================================================

@app.post("/api/ai/parse-opportunity")
def ai_parse_opportunity(
    request: OpportunityTextRequest,
):

    result = (
        parse_opportunity_text(
            request.text
        )
    )


    return {

        "result":
        result,
    }


# ============================================================
# HIDDEN OPPORTUNITIES
# ============================================================

@app.get("/api/hidden-opportunities")
def get_hidden_opportunities():

    opportunities = [

        enrich_opportunity(
            item
        )

        for item in get_all_opportunities()
    ]


    opportunities.sort(

        key=lambda item: (

            item.get(
                "match_score",
                0,
            ),

            item.get(
                "trust_score",
                0,
            ),
        ),

        reverse=True,
    )


    recommendations = []


    for opportunity in opportunities[:5]:

        recommendations.append({

            "id":
            opportunity.get(
                "id"
            ),

            "title":
            opportunity.get(
                "title"
            ),

            "organization":
            opportunity.get(
                "organization"
            ),

            "type":
            opportunity.get(
                "type",
                "Opportunity",
            ),

            "reason":
            (
                f"This opportunity has a "
                f"{opportunity.get('match_score', 0)}% profile match "
                f"and a "
                f"{opportunity.get('trust_score', 0)}% trust score."
            ),
        })


    return recommendations


# ============================================================
# WHY NOT ME
# ============================================================

@app.get("/api/why-not/{opportunity_id}")
def why_not_opportunity(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    eligibility = (
        check_eligibility(
            student_profile,
            opportunity,
        )
    )


    readiness = (
        calculate_readiness_intelligence(
            student_profile,
            opportunity,
        )
    )


    blockers = list(

        eligibility.get(
            "reasons",
            [],
        )
    )


    missing_skills = (
        readiness.get(
            "missing_skills",
            [],
        )
    )


    for skill in missing_skills[:5]:

        blockers.append(

            f"{skill}: this skill is currently missing from your profile."
        )


    if not blockers:

        blockers.append(

            "No major blocker was detected from the available opportunity data."
        )


    recommendations = [

        {

            "priority":
            index + 1,

            "action":
            f"Strengthen {skill}",

            "reason":
            "This skill is directly connected to the opportunity requirements.",
        }

        for index, skill in enumerate(
            missing_skills[:5]
        )
    ]


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "blockers":
        blockers,

        "recommendations":
        recommendations,

        "current_readiness":
        readiness.get(
            "readiness",
            0,
        ),
    }


# ============================================================
# PREPARATION INTELLIGENCE DATABASE
# ============================================================

SKILL_LEARNING_PATHS = {

    "python": {

        "estimated_hours":
        18,

        "priority":
        "High",

        "learn": [

            "Variables and data types",

            "Control flow",

            "Functions",

            "Lists, dictionaries and sets",

            "File handling",

            "Object-oriented programming",

            "Error handling",
        ],

        "practice": [

            "Solve practical data-processing problems",

            "Build command-line utilities",

            "Work with real API responses",
        ],

        "project":
        "Build a practical Python automation or data-processing project.",
    },


    "react": {

        "estimated_hours":
        22,

        "priority":
        "High",

        "learn": [

            "Components and props",

            "State and events",

            "Hooks",

            "Conditional rendering",

            "API integration",

            "Component architecture",
        ],

        "practice": [

            "Build reusable components",

            "Consume a REST API",

            "Manage loading and error states",
        ],

        "project":
        "Build a responsive dashboard that consumes a live API.",
    },


    "fastapi": {

        "estimated_hours":
        16,

        "priority":
        "High",

        "learn": [

            "Routing",

            "Pydantic models",

            "Request validation",

            "Response models",

            "Error handling",

            "API documentation",
        ],

        "practice": [

            "Create CRUD endpoints",

            "Validate incoming data",

            "Connect a frontend to the API",
        ],

        "project":
        "Build and deploy a production-style REST API.",
    },


    "sql": {

        "estimated_hours":
        18,

        "priority":
        "High",

        "learn": [

            "SELECT queries",

            "Filtering and sorting",

            "JOIN operations",

            "GROUP BY",

            "Subqueries",

            "Database design basics",
        ],

        "practice": [

            "Query a realistic student database",

            "Write analytical SQL queries",

            "Design tables for an application",
        ],

        "project":
        "Design a relational database and expose it through an API.",
    },


    "machine learning": {

        "estimated_hours":
        35,

        "priority":
        "High",

        "learn": [

            "Data preprocessing",

            "Train-test split",

            "Supervised learning",

            "Model evaluation",

            "Feature engineering",

            "Overfitting",
        ],

        "practice": [

            "Train baseline models",

            "Compare model performance",

            "Explain model metrics",
        ],

        "project":
        "Build an end-to-end prediction project with a clear evaluation report.",
    },


    "artificial intelligence": {

        "estimated_hours":
        30,

        "priority":
        "High",

        "learn": [

            "AI foundations",

            "Machine learning concepts",

            "Neural network basics",

            "Generative AI concepts",

            "Prompt engineering",

            "AI application architecture",
        ],

        "practice": [

            "Build an AI-assisted workflow",

            "Evaluate model outputs",

            "Add guardrails and validation",
        ],

        "project":
        "Build an AI-powered application solving a real problem.",
    },


    "javascript": {

        "estimated_hours":
        20,

        "priority":
        "High",

        "learn": [

            "Variables and scope",

            "Functions",

            "Arrays and objects",

            "Async programming",

            "Promises",

            "API requests",
        ],

        "practice": [

            "Build DOM interactions",

            "Consume a public API",

            "Create an asynchronous application",
        ],

        "project":
        "Build a complete interactive web application.",
    },


    "typescript": {

        "estimated_hours":
        16,

        "priority":
        "Medium",

        "learn": [

            "Types",

            "Interfaces",

            "Generics",

            "Union types",

            "Type-safe API data",
        ],

        "practice": [

            "Convert JavaScript code to TypeScript",

            "Create reusable typed components",
        ],

        "project":
        "Build a TypeScript application with strongly typed API integration.",
    },


    "docker": {

        "estimated_hours":
        12,

        "priority":
        "Medium",

        "learn": [

            "Containers",

            "Images",

            "Dockerfiles",

            "Environment variables",

            "Networking basics",
        ],

        "practice": [

            "Containerize a frontend",

            "Containerize a backend",
        ],

        "project":
        "Dockerize and deploy a full-stack application.",
    },


    "git": {

        "estimated_hours":
        8,

        "priority":
        "High",

        "learn": [

            "Repositories",

            "Commits",

            "Branches",

            "Pull requests",

            "Conflict resolution",
        ],

        "practice": [

            "Use feature branches",

            "Write meaningful commits",
        ],

        "project":
        "Maintain a professional Git repository with clean documentation.",
    },
}


def get_skill_plan(
    skill,
):

    key = (
        normalize_text_value(
            skill
        )
    )


    return SKILL_LEARNING_PATHS.get(

        key,

        {

            "estimated_hours":
            12,

            "priority":
            "Medium",

            "learn": [

                f"Core concepts of {skill}",

                f"Practical usage of {skill}",

                f"Common tools and workflows for {skill}",
            ],

            "practice": [

                f"Solve practical {skill} exercises",

                f"Use {skill} in a small application",
            ],

            "project":
            f"Build one portfolio-quality project demonstrating {skill}.",
        },
    )


# ============================================================
# PREPARATION PLAN ENGINE
# ============================================================

def build_preparation_plan(
    student,
    opportunity,
):

    readiness_result = (
        calculate_readiness_intelligence(
            student,
            opportunity,
        )
    )


    required_skills = [

        skill

        for skill in opportunity.get(
            "skills",
            [],
        )

        if normalize_text_value(
            skill
        )
    ]


    missing_skills = (
        readiness_result.get(
            "missing_skills",
            [],
        )
    )


    matched_skills = (
        readiness_result.get(
            "matched_skills",
            [],
        )
    )


    plan_skills = (
        missing_skills[:6]
    )


    if not plan_skills:

        plan_skills = (
            required_skills[:3]
        )


    roadmap = []

    total_hours = 0


    for index, skill in enumerate(

        plan_skills,

        start=1,
    ):

        plan = (
            get_skill_plan(
                skill
            )
        )


        estimated_hours = (
            plan.get(
                "estimated_hours",
                12,
            )
        )


        total_hours += (
            estimated_hours
        )


        roadmap.append({

            "order":
            index,

            "skill":
            skill,

            "priority":
            plan.get(
                "priority",
                "Medium",
            ),

            "estimated_hours":
            estimated_hours,

            "learn":
            plan.get(
                "learn",
                [],
            ),

            "practice":
            plan.get(
                "practice",
                [],
            ),

            "project":
            plan.get(
                "project",
                "",
            ),

            "success_criteria":
            (
                f"You can explain {skill}, "
                f"solve a practical problem using it, "
                f"and demonstrate it through visible project evidence."
            ),

            "portfolio_evidence":
            (
                f"Add a documented {skill} project to your portfolio "
                f"with a clear README, screenshots or demo, and source code."
            ),
        })


    readiness = (
        readiness_result.get(
            "readiness",
            0,
        )
    )


    weekly_schedule = []


    if roadmap:

        hours_per_week = 8

        for index, item in enumerate(
            roadmap,
            start=1,
        ):

            weekly_schedule.append({

                "week":
                index,

                "focus":
                item.get(
                    "skill"
                ),

                "hours":
                min(
                    item.get(
                        "estimated_hours",
                        12,
                    ),
                    hours_per_week + 4,
                ),

                "goal":
                (
                    f"Complete the core learning and practical exercises for "
                    f"{item.get('skill')}."
                ),
            })


    application_strategy_result = (
        calculate_deadline_intelligence(
            opportunity.get(
                "deadline"
            )
        )
    )


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "current_readiness":
        readiness,

        "readiness_level":
        readiness_result.get(
            "readiness_level",
            "Developing",
        ),

        "required_skills":
        required_skills,

        "matched_skills":
        matched_skills,

        "missing_skills":
        missing_skills,

        "estimated_total_hours":
        total_hours,

        "estimated_weeks":
        max(
            1,
            round(
                total_hours / 8
            ),
        ),

        "roadmap":
        roadmap,

        "weekly_schedule":
        weekly_schedule,

        "application_strategy":
        application_strategy_result,

        "priority_actions":
        [

            (
                f"Close the {skill} gap."
            )

            for skill in missing_skills[:3]
        ],

        "portfolio_actions":
        [

            item.get(
                "portfolio_evidence"
            )

            for item in roadmap[:3]
        ],

        "next_action":
        (
            f"Start with {roadmap[0]['skill']}."
            if roadmap
            else
            "Strengthen your existing projects and convert your current skills into visible portfolio proof."
        ),
    }


# ============================================================
# PREPARATION PLAN
# ============================================================

@app.get("/api/prepare/{opportunity_id}")
def prepare_for_opportunity(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    return build_preparation_plan(

        student_profile,

        opportunity,
    )


# ============================================================
# FUTURE OPPORTUNITY PATH
# ============================================================

@app.get("/api/future-path/{opportunity_id}")
def future_opportunity_path(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    preparation = (
        build_preparation_plan(

            student_profile,

            opportunity,
        )
    )


    roadmap = (
        preparation.get(
            "roadmap",
            [],
        )
    )


    current_readiness = (
        preparation.get(
            "current_readiness",
            0,
        )
    )


    future_path = []


    for index, item in enumerate(

        roadmap[:6],

        start=1,
    ):

        skill = (
            item.get(
                "skill",
                "Skill",
            )
        )


        future_path.append({

            "stage":
            index,

            "stage_name":
            f"Level {index}: {skill}",

            "skill":
            skill,

            "priority":
            item.get(
                "priority",
                "Medium",
            ),

            "estimated_hours":
            item.get(
                "estimated_hours",
                12,
            ),

            "goal":
            (
                f"Build practical confidence in {skill} "
                f"and create visible proof of ability."
            ),

            "milestones":

            item.get(
                "learn",
                [],
            )[:4],

            "practice":

            item.get(
                "practice",
                [],
            )[:3],

            "proof_project":

            item.get(
                "project",
                "Build a portfolio-quality project.",
            ),

            "success_criteria":

            item.get(
                "success_criteria",
                "Demonstrate the skill through a working project.",
            ),

            "career_value":
            (
                f"Improving {skill} strengthens your competitiveness "
                f"for opportunities with similar technical requirements."
            ),
        })


    future_path.append({

        "stage":
        len(future_path) + 1,

        "stage_name":
        "Portfolio Proof",

        "skill":
        "Portfolio",

        "priority":
        "High",

        "estimated_hours":
        10,

        "goal":
        "Turn learning into visible evidence recruiters and judges can evaluate.",

        "milestones": [

            "Choose your strongest project",

            "Document the problem and solution",

            "Explain your technical decisions",

            "Publish source code and demo evidence",
        ],

        "practice": [

            "Improve project README",

            "Add architecture documentation",

            "Prepare a short project explanation",
        ],

        "proof_project":
        "Create one polished case study demonstrating your strongest technical capability.",

        "success_criteria":
        "A reviewer can understand the problem, implementation, technology choices and outcome quickly.",

        "career_value":
        "Portfolio evidence reduces the gap between claiming a skill and proving that you can use it.",
    })


    future_path.append({

        "stage":
        len(future_path) + 1,

        "stage_name":
        "Application Strategy",

        "skill":
        "Application Readiness",

        "priority":
        "High",

        "estimated_hours":
        4,

        "goal":
        "Convert your improved profile into a stronger application.",

        "milestones": [

            "Tailor your resume",

            "Prepare project explanations",

            "Practice likely technical questions",

            "Apply before the deadline",
        ],

        "practice": [

            "Run a mock interview",

            "Review the opportunity requirements",

            "Prepare achievement-focused examples",
        ],

        "proof_project":
        "Maintain a concise portfolio containing your strongest relevant projects.",

        "success_criteria":
        "You can clearly explain why you fit the opportunity and support each claim with evidence.",

        "career_value":
        "Preparation becomes useful only when the improved profile is translated into a strong application.",
    })


    readiness_projection = [

        {

            "stage":
            "Current",

            "estimated_readiness":
            current_readiness,
        },

        {

            "stage":
            "After Core Gaps",

            "estimated_readiness":
            min(
                85,
                current_readiness
                +
                len(
                    preparation.get(
                        "missing_skills",
                        [],
                    )
                )
                * 10,
            ),
        },

        {

            "stage":
            "After Portfolio Proof",

            "estimated_readiness":
            min(
                95,
                current_readiness
                +
                30,
            ),
        },
    ]


    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "current_readiness":
        current_readiness,

        "readiness_level":
        preparation.get(
            "readiness_level",
            "Developing",
        ),

        "missing_skills":
        preparation.get(
            "missing_skills",
            [],
        ),

        "matched_skills":
        preparation.get(
            "matched_skills",
            [],
        ),

        "estimated_total_hours":
        preparation.get(
            "estimated_total_hours",
            0,
        ),

        "estimated_weeks":
        preparation.get(
            "estimated_weeks",
            1,
        ),

        "readiness_projection":
        readiness_projection,

        "next_best_action":
        preparation.get(
            "next_action"
        ),

        "future_path":
        future_path,

        "message":
        (
            "This path converts the opportunity into concrete learning, "
            "practice, portfolio proof and application milestones."
        ),
    }


# ============================================================
# OPPORTUNITY INTELLIGENCE
# ============================================================

@app.get("/api/intelligence/{opportunity_id}")
def get_opportunity_intelligence(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    enriched = (
        enrich_opportunity(
            opportunity
        )
    )


    preparation = (
        build_preparation_plan(
            student_profile,
            enriched,
        )
    )


    readiness = (
        calculate_readiness_intelligence(
            student_profile,
            enriched,
        )
    )


    deadline = (
        enriched.get(
            "deadline_intelligence",
            {},
        )
    )


    decision_score = round(

        (
            enriched.get(
                "match_score",
                0,
            )
            * 0.40
        )

        +

        (
            enriched.get(
                "trust_score",
                0,
            )
            * 0.30
        )

        +

        (
            readiness.get(
                "readiness",
                0,
            )
            * 0.30
        )
    )


    if decision_score >= 80:

        decision = "Strongly Consider"

    elif decision_score >= 60:

        decision = "Worth Pursuing"

    elif decision_score >= 40:

        decision = "Strategic Preparation Needed"

    else:

        decision = "High Preparation Required"


    return {

        "opportunity":
        enriched.get(
            "title"
        ),

        "decision":
        decision,

        "decision_score":
        decision_score,

        "match_score":
        enriched.get(
            "match_score",
            0,
        ),

        "trust_score":
        enriched.get(
            "trust_score",
            0,
        ),

        "readiness":
        readiness,

        "deadline":
        deadline,

        "top_strengths":
        preparation.get(
            "matched_skills",
            [],
        )[:5],

        "top_gaps":
        preparation.get(
            "missing_skills",
            [],
        )[:5],

        "best_next_action":
        preparation.get(
            "next_action"
        ),

        "estimated_effort_hours":
        preparation.get(
            "estimated_total_hours",
            0,
        ),

        "should_apply_now":

        (
            enriched.get(
                "match_score",
                0,
            )
            >= 65

            or

            deadline.get(
                "urgency"
            )
            in {

                "Critical",

                "Urgent",
            }
        ),
    }


# ============================================================
# COMPARE OPPORTUNITIES
# ============================================================

@app.get("/api/compare")
def compare_opportunities(

    opportunity_ids: list[int] = Query(
        ...
    ),

):

    if len(opportunity_ids) < 2:

        raise HTTPException(

            status_code=400,

            detail="Select at least two opportunities to compare.",
        )


    comparison = []


    for opportunity_id in opportunity_ids[:3]:

        opportunity = (
            find_opportunity_by_id(
                opportunity_id
            )
        )


        if opportunity is None:
            continue


        enriched = (
            enrich_opportunity(
                opportunity
            )
        )


        preparation = (
            build_preparation_plan(
                student_profile,
                enriched,
            )
        )


        deadline = (
            enriched.get(
                "deadline_intelligence",
                {},
            )
        )


        readiness = (
            preparation.get(
                "current_readiness",
                0,
            )
        )


        learning_hours = (
            preparation.get(
                "estimated_total_hours",
                0,
            )
        )


        decision_score = round(

            (
                enriched.get(
                    "match_score",
                    0,
                )
                * 0.40
            )

            +

            (
                enriched.get(
                    "trust_score",
                    0,
                )
                * 0.30
            )

            +

            (
                readiness
                * 0.20
            )

            +

            (
                max(
                    0,
                    100
                    -
                    min(
                        learning_hours * 2,
                        100,
                    ),
                )
                * 0.10
            )
        )


        comparison.append({

            "id":
            enriched.get(
                "id"
            ),

            "title":
            enriched.get(
                "title",
                "Unknown opportunity",
            ),

            "organization":
            enriched.get(
                "organization",
                "Unknown organization",
            ),

            "match_score":
            enriched.get(
                "match_score",
                0,
            ),

            "trust_score":
            enriched.get(
                "trust_score",
                0,
            ),

            "trust_label":
            enriched.get(
                "trust_label",
                "Low",
            ),

            "deadline":
            enriched.get(
                "deadline",
                "Unknown",
            ),

            "deadline_urgency":
            deadline.get(
                "urgency",
                "Unknown",
            ),

            "days_remaining":
            deadline.get(
                "days_remaining"
            ),

            "location":
            enriched.get(
                "location"
            ),

            "remote":
            enriched.get(
                "remote"
            ),

            "matched_skills":
            preparation.get(
                "matched_skills",
                [],
            ),

            "missing_skills":
            preparation.get(
                "missing_skills",
                [],
            ),

            "estimated_learning_hours":
            learning_hours,

            "readiness":
            readiness,

            "decision_score":
            decision_score,

            "eligibility":
            check_eligibility(
                student_profile,
                enriched,
            ).get(
                "eligible",
                True,
            ),

            "competition_estimate":
            max(
                20,
                min(
                    95,
                    35
                    +
                    int(
                        enriched.get(
                            "match_score",
                            0,
                        )
                        * 0.40
                    )
                    +
                    int(
                        enriched.get(
                            "trust_score",
                            0,
                        )
                        * 0.15
                    ),
                ),
            ),

            "career_alignment":
            min(
                100,
                round(
                    enriched.get(
                        "match_score",
                        0,
                    )
                    * 0.65
                    +
                    readiness
                    * 0.35
                ),
            ),

            "portfolio_value":
            min(
                100,
                45
                +
                len(
                    preparation.get(
                        "missing_skills",
                        [],
                    )
                )
                * 7,
            ),

            "growth_potential":
            min(
                100,
                50
                +
                len(
                    preparation.get(
                        "missing_skills",
                        [],
                    )
                )
                * 10,
            ),

            "ready_before_deadline":
            (
                deadline.get(
                    "days_remaining"
                )
                is not None

                and

                learning_hours
                <=
                max(
                    0,
                    deadline.get(
                        "days_remaining",
                        0,
                    ),
                )
                * 2
            ),
        })


    if not comparison:

        raise HTTPException(

            status_code=404,

            detail="None of the selected opportunities could be found.",
        )


    best_match = max(

        comparison,

        key=lambda item:
        item["match_score"],
    )


    most_trusted = max(

        comparison,

        key=lambda item:
        item["trust_score"],
    )


    easiest = min(

        comparison,

        key=lambda item:
        item["estimated_learning_hours"],
    )


    most_ready = max(

        comparison,

        key=lambda item:
        item["readiness"],
    )


    recommended = max(

        comparison,

        key=lambda item:
        item["decision_score"],
    )


    recommendation_reason = (

        f"{recommended['title']} is the strongest strategic choice because "

        f"it combines a {recommended['match_score']}% profile match, "

        f"{recommended['trust_score']}% source confidence and "

        f"{recommended['readiness']}% current readiness."
    )


    return {

        "comparison":
        comparison,

        "summary": {

            "best_match":
            best_match["id"],

            "most_trusted":
            most_trusted["id"],

            "easiest_to_prepare":
            easiest["id"],

            "most_ready":
            most_ready["id"],

            "recommended":
            recommended["id"],

            "recommendation_reason":
            recommendation_reason,
        },
    }


# ============================================================
# DISCOVERY DASHBOARD
# ============================================================

@app.get("/api/dashboard-intelligence")
def dashboard_intelligence():

    opportunities = [

        enrich_opportunity(
            item
        )

        for item in get_all_opportunities()
    ]


    opportunities.sort(

        key=lambda item: (

            item.get(
                "match_score",
                0,
            ),

            item.get(
                "trust_score",
                0,
            ),
        ),

        reverse=True,
    )


    strong_matches = [

        item

        for item in opportunities

        if item.get(
            "match_score",
            0,
        ) >= 65
    ]


    urgent = [

        item

        for item in opportunities

        if item.get(
            "deadline_intelligence",
            {},
        ).get(
            "urgency"
        )
        in {

            "Critical",

            "Urgent",
        }
    ]


    return {

        "total_opportunities":
        len(
            opportunities
        ),

        "strong_matches":
        len(
            strong_matches
        ),

        "urgent_opportunities":
        len(
            urgent
        ),

        "top_opportunities":
        opportunities[:6],

        "urgent_items":
        urgent[:5],

        "profile_summary": {

            "name":
            student_profile.get(
                "name"
            ),

            "skills":
            student_profile.get(
                "skills",
                [],
            ),

            "interests":
            student_profile.get(
                "interests",
                [],
            ),
        },
    }


# ============================================================
# ADVANCED OPPORTUNITY INTELLIGENCE
# ============================================================

@app.get("/api/profile-intelligence")
def get_profile_intelligence():

    opportunities = (
        get_all_opportunities()
    )


    return profile_intelligence(

        student_profile,

        opportunities,

        {

            "projects":
            student_profile.get(
                "projects",
                [],
            ),

            "evidence":
            student_profile.get(
                "evidence",
                [],
            ),
        },
    )


@app.post("/api/readiness-simulator/{opportunity_id}")
def simulate_readiness(
    opportunity_id: int,
    payload: dict[str, Any],
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    added_skills = (
        payload.get(
            "added_skills",
            [],
        )
    )


    if not isinstance(
        added_skills,
        list,
    ):

        added_skills = []


    added_projects = (
        payload.get(
            "added_projects",
            0,
        )
    )


    try:

        added_projects = max(
            0,
            int(
                added_projects
            ),
        )

    except (
        TypeError,
        ValueError,
    ):

        added_projects = 0


    return readiness_simulator(

        student_profile,

        get_all_opportunities(),

        added_skills,

        added_projects,
    )


@app.get("/api/application-strategy/{opportunity_id}")
def get_application_strategy(
    opportunity_id: int,
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )


    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail="Opportunity not found",
        )


    return application_strategy(

        student_profile,

        opportunity,
    )

# ============================================================
# STEPS 36-55 — INTELLIGENCE ENDPOINTS
# ============================================================

@app.get("/api/intelligence/workspace/{opportunity_id}")
def intelligence_workspace(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return build_opportunity_workspace(
        student_profile,
        opportunity,
    )


@app.get("/api/intelligence/ranking/{opportunity_id}")
def intelligence_ranking(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return explain_ranking(
        student_profile,
        opportunity,
    )


@app.get("/api/intelligence/readiness/{opportunity_id}")
def intelligence_readiness(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return {
        "opportunity": opportunity.get("title"),
        "checklist": readiness_checklist(
            student_profile,
            opportunity,
        ),
    }


@app.get("/api/intelligence/deadline/{opportunity_id}")
def intelligence_deadline(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return deadline_intelligence(
        opportunity
    )


@app.get("/api/intelligence/action/{opportunity_id}")
def intelligence_action(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return best_next_action(
        student_profile,
        opportunity,
    )


@app.get("/api/intelligence/portfolio/{opportunity_id}")
def intelligence_portfolio(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return portfolio_impact(
        student_profile,
        opportunity,
    )


@app.get("/api/intelligence/freshness/{opportunity_id}")
def intelligence_freshness(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return calculate_freshness(
        opportunity
    )


@app.get("/api/intelligence/source/{opportunity_id}")
def intelligence_source(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return build_source_evidence(
        opportunity
    )


@app.get("/api/intelligence/weekly-mission")
def intelligence_weekly_mission():
    opportunities = get_all_opportunities()

    return weekly_mission(
        student_profile,
        opportunities,
    )


@app.get("/api/intelligence/quality")
def intelligence_quality():
    opportunities = get_all_opportunities()

    return quality_control(
        opportunities
    )


@app.get("/api/intelligence/deduplicated")
def intelligence_deduplicated():
    opportunities = get_all_opportunities()

    return remove_duplicate_opportunities(
        opportunities
    )


@app.get(
    "/api/intelligence/export/{opportunity_id}"
)
def intelligence_export(
    opportunity_id: int,
):
    opportunity = find_opportunity_by_id(
        opportunity_id
    )

    if opportunity is None:
        raise HTTPException(
            status_code=404,
            detail="Opportunity not found",
        )

    return {
        "filename": "preparation-plan.txt",
        "content": export_preparation_plan(
            student_profile,
            opportunity,
        ),
    }


@app.get("/api/demo")
def intelligence_demo():
    return demo_snapshot(
        student_profile,
        get_all_opportunities(),
    )
