from pathlib import Path
import json

from fastapi import (
    FastAPI,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import (
    BaseModel,
    Field
)

from student import student_profile

from eligibility import (
    check_eligibility
)

from matching import (
    calculate_match
)

from gap_analysis import (
    find_skill_gaps
)

from semantic_matching import (
    get_semantic_skill_match
)

from resource_roadmap import (
    create_resource_roadmap
)

from resume_parser import (
    parse_resume_text
)

from skill_normalizer import (
    normalize_skills
)

from live_opportunities import (
    save_live_opportunities,
    get_all_live_opportunities
)

from ai.opportunity_parser import (
    parse_opportunity_text
)

from ai.web_search import (
    search_real_opportunities
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Student Opportunity Engine",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://student-opportunity-engine-eta.vercel.app",
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
            encoding="utf-8"
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
# OPPORTUNITY HELPERS
# ============================================================

def get_all_opportunities():

    built_in = load_opportunities()

    live = get_all_live_opportunities()

    return built_in + live


def find_opportunity_by_id(
    opportunity_id: int
):

    opportunities = get_all_opportunities()

    return next(

        (
            item
            for item in opportunities
            if item.get("id") == opportunity_id
        ),

        None
    )


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

    opportunity_type: str = (
        "internship"
    )


class ResumeTextRequest(
    BaseModel
):

    text: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message":
        (
            "Student Opportunity Engine "
            "backend is running!"
        )
    }


# ============================================================
# OPPORTUNITIES
# ============================================================

@app.get(
    "/api/opportunities"
)
def get_opportunities():

    return get_all_opportunities()


# ============================================================
# STUDENT
# ============================================================

@app.get(
    "/api/student"
)
def get_student():

    return student_profile


@app.post(
    "/api/student/profile"
)
def update_student_profile(
    request: StudentProfileRequest
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

        "opportunity_type":
        (
            request.opportunity_type
            .strip()
            .lower()
        )
    })

    return {

        "message":
        (
            "Student profile updated "
            "successfully"
        ),

        "student":
        student_profile
    }


# ============================================================
# LIVE AI SEARCH
# ============================================================

@app.get(
    "/api/ai/search-opportunities"
)
def ai_search_opportunities():

    print(
        "\n========================================"
    )

    print(
        "STARTING LIVE OPPORTUNITY SEARCH"
    )

    print(
        "========================================"
    )

    print(
        "Current student profile:"
    )

    print(student_profile)

    results = (
        search_real_opportunities(
            student_profile,
            max_results=10
        )
    )

    save_live_opportunities(
        results
    )

    print(
        f"Live opportunities stored: "
        f"{len(results)}"
    )

    return {

        "count":
        len(results),

        "opportunities":
        results,

        "student":
        student_profile
    }


# ============================================================
# ELIGIBILITY
# ============================================================

@app.get(
    "/api/eligibility/{opportunity_id}"
)
def check_opportunity_eligibility(
    opportunity_id: int
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )

    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Opportunity not found"
            )
        )

    result = (
        check_eligibility(
            student_profile,
            opportunity
        )
    )

    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **result
    }


# ============================================================
# BASIC MATCH
# ============================================================

@app.get(
    "/api/match/{opportunity_id}"
)
def match_opportunity(
    opportunity_id: int
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )

    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Opportunity not found"
            )
        )

    eligibility = (
        check_eligibility(
            student_profile,
            opportunity
        )
    )

    if not eligibility.get(
        "eligible"
    ):

        return {

            "opportunity":
            opportunity.get(
                "title"
            ),

            "eligible":
            False,

            "match_score":
            0,

            "matched_skills":
            [],

            "missing_skills":
            opportunity.get(
                "skills",
                []
            ),

            "message":
            (
                "Student is not eligible "
                "for this opportunity."
            )
        }

    match = (
        calculate_match(
            student_profile,
            opportunity
        )
    )

    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        "eligible":
        True,

        **match
    }


# ============================================================
# SEMANTIC MATCHING
# ============================================================

@app.get(
    "/api/semantic-match/{opportunity_id}"
)
def semantic_match_opportunity(
    opportunity_id: int
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )

    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Opportunity not found"
            )
        )

    result = (
        get_semantic_skill_match(

            student_profile.get(
                "skills",
                []
            ),

            opportunity.get(
                "skills",
                []
            )
        )
    )

    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **result
    }


# ============================================================
# GAP ANALYSIS
# ============================================================

@app.get(
    "/api/gap_analysis/{opportunity_id}"
)
def get_skill_gaps(
    opportunity_id: int
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )

    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Opportunity not found"
            )
        )

    gaps = (
        find_skill_gaps(

            student_profile.get(
                "skills",
                []
            ),

            opportunity.get(
                "skills",
                []
            )
        )
    )

    return {

        "opportunity":
        opportunity.get(
            "title"
        ),

        **gaps
    }


# ============================================================
# RESOURCE ROADMAP
# ============================================================

@app.get(
    "/api/resource-roadmap/{opportunity_id}"
)
def get_resource_roadmap(
    opportunity_id: int
):

    opportunity = (
        find_opportunity_by_id(
            opportunity_id
        )
    )

    if opportunity is None:

        raise HTTPException(

            status_code=404,

            detail=(
                "Opportunity not found"
            )
        )

    gaps = (
        find_skill_gaps(

            student_profile.get(
                "skills",
                []
            ),

            opportunity.get(
                "skills",
                []
            )
        )
    )

    roadmap = (
        create_resource_roadmap(

            gaps.get(
                "missing_skills",
                []
            ),

            opportunity.get(
                "skills",
                []
            )
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
                []
            )
        ),

        "missing_skills":
        gaps.get(
            "missing_skills",
            []
        ),

        "roadmap":
        roadmap
    }


# ============================================================
# RESUME PARSER
# ============================================================

@app.post(
    "/api/resume/parse"
)
def parse_resume(
    request: ResumeTextRequest
):

    return parse_resume_text(
        request.text
    )


# ============================================================
# AI OPPORTUNITY PARSER
# ============================================================

@app.post(
    "/api/ai/parse-opportunity"
)
def ai_parse_opportunity(
    request: OpportunityTextRequest
):

    result = (
        parse_opportunity_text(
            request.text
        )
    )

    return {

        "result":
        result
    }