from datetime import date
import re


def normalize_text(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def normalize_branch(value):
    """Normalize common branch abbreviations and punctuation."""
    text = normalize_text(value)
    compact = re.sub(r"[^a-z0-9]", "", text)
    aliases = {
        "cse": "computerscienceengineering",
        "cs": "computerscience",
        "computerscience": "computerscience",
        "computerscienceengineering": "computerscienceengineering",
        "ise": "informationtechnology",
        "it": "informationtechnology",
        "informationtechnology": "informationtechnology",
        "ai": "artificialintelligence",
        "aiml": "artificialintelligencemachinelearning",
        "artificialintelligence": "artificialintelligence",
        "ece": "electronicscommunicationengineering",
        "eee": "electricalelectronicsengineering",
        "me": "mechanicalengineering",
        "civil": "civilengineering",
    }
    return aliases.get(compact, compact)


def normalize_year(year):
    """
    Converts:
        1 -> "1st"
        2 -> "2nd"
        3 -> "3rd"
        4 -> "4th"
    """

    try:
        year_number = int(year)

        suffix = {
            1: "st",
            2: "nd",
            3: "rd",
            4: "th",
        }.get(year_number, "")

        if suffix:
            return f"{year_number}{suffix}"

    except (TypeError, ValueError):
        pass

    return normalize_text(year)


def check_eligibility(student, opportunity):

    reasons = []
    warnings = []

    eligible = True

    # ========================================================
    # YEAR
    # ========================================================

    student_year = normalize_year(
        student.get("year")
    )

    opportunity_years = opportunity.get(
        "year",
        []
    )

    if opportunity_years:

        normalized_opportunity_years = {
            normalize_year(year)
            for year in opportunity_years
        }

        if (
            student_year
            and student_year not in normalized_opportunity_years
        ):
            eligible = False

            reasons.append(
                "Student year does not match the opportunity eligibility."
            )

    else:

        warnings.append(
            "Year eligibility was not specified."
        )

    # ========================================================
    # BRANCH
    # ========================================================

    student_branch = normalize_branch(
        student.get("branch")
    )

    opportunity_branches = opportunity.get(
        "branches",
        []
    )

    if opportunity_branches:

        normalized_branches = {
            normalize_branch(branch)
            for branch in opportunity_branches
        }

        if student_branch not in normalized_branches:

            eligible = False

            reasons.append(
                "Student branch does not match the listed eligible branches."
            )

    else:

        warnings.append(
            "Branch eligibility was not specified."
        )

    # ========================================================
    # OPPORTUNITY TYPE
    # ========================================================

    student_opportunity_type = normalize_text(
        student.get(
            "opportunity_type",
            ""
        )
    )

    opportunity_type = normalize_text(
        opportunity.get(
            "type",
            ""
        )
    )

    if (
        student_opportunity_type
        and opportunity_type
        and student_opportunity_type != opportunity_type
    ):

        eligible = False

        reasons.append(
            "Opportunity type does not match the student's selected opportunity type."
        )

    # ========================================================
    # DEADLINE
    # ========================================================

    deadline = opportunity.get(
        "deadline"
    )

    if deadline:

        try:

            deadline_date = date.fromisoformat(
                str(deadline)[:10]
            )

            if deadline_date < date.today():

                eligible = False

                reasons.append(
                    "The application deadline has passed."
                )

        except ValueError:

            warnings.append(
                "Deadline could not be verified as a standard date."
            )

    else:

        warnings.append(
            "No deadline was provided."
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "eligible": eligible,
        "reasons": reasons,
        "warnings": warnings,
    }