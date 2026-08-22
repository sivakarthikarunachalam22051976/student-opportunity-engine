from .skill_normalizer import normalize_skills


# ============================================================
# FIND SKILL GAPS
# ============================================================

def find_skill_gaps(student_skills, required_skills):
    student_skills = normalize_skills(student_skills)
    required_skills = normalize_skills(required_skills)

    student_skills_lower = {
        skill.lower() for skill in student_skills
    }

    missing_skills = []

    matched_skills = []

    for skill in required_skills:
        if skill.lower() in student_skills_lower:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    total_required = len(required_skills)
    total_matched = len(matched_skills)

    if total_required == 0:
        readiness_percentage = 100
    else:
        readiness_percentage = round(
            (total_matched / total_required) * 100
        )

    return {
        "student_skills": student_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required_skills": total_required,
        "matched_skills_count": total_matched,
        "missing_skills_count": len(missing_skills),
        "readiness_percentage": readiness_percentage
    }