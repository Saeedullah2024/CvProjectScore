"""
Step 5: Scoring Engine — combines the matching-engine sub-scores into one
overall weighted score.

Step 6: Result / Explanation — turns the numbers into a human-readable
verdict and bullet-point explanation for the frontend to render.
"""

WEIGHTS = {
    "skills": 0.35,
    "semantic_similarity": 0.20,
    "experience": 0.20,
    "education": 0.15,
    "certifications": 0.10,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9


def compute_overall_score(match_result: dict) -> dict:
    breakdown = {}
    weighted_total = 0.0
    for key, weight in WEIGHTS.items():
        sub_score = match_result[key]["score"]
        contribution = sub_score * weight
        weighted_total += contribution
        breakdown[key] = {
            "score": sub_score,
            "weight": weight,
            "weighted_contribution": round(contribution, 1),
        }

    return {
        "overall_score": round(weighted_total, 1),
        "breakdown": breakdown,
    }


def _verdict(score: float) -> str:
    if score >= 85:
        return "Excellent Match"
    if score >= 70:
        return "Strong Match"
    if score >= 50:
        return "Moderate Match"
    if score >= 30:
        return "Weak Match"
    return "Poor Match"


def build_explanation(match_result: dict, scoring_result: dict, cv_profile: dict, jd_profile: dict) -> dict:
    overall = scoring_result["overall_score"]
    verdict = _verdict(overall)

    highlights = []
    concerns = []

    skills = match_result["skills"]
    if skills["missing_required"]:
        concerns.append(
            f"Missing {len(skills['missing_required'])} required skill(s): "
            + ", ".join(skills["missing_required"][:8])
        )
    else:
        highlights.append("All required skills from the job description are present in the CV.")

    if skills["matched_required"]:
        highlights.append(
            f"Matched {len(skills['matched_required'])} required skill(s): "
            + ", ".join(skills["matched_required"][:8])
        )

    exp = match_result["experience"]
    if exp["required_years"] > 0:
        if exp["meets_requirement"]:
            highlights.append(
                f"Experience requirement met: {exp['cv_years']} yrs on CV vs "
                f"{exp['required_years']} yrs required."
            )
        else:
            concerns.append(
                f"Experience gap: {exp['cv_years']} yrs on CV vs "
                f"{exp['required_years']} yrs required."
            )

    edu = match_result["education"]
    if edu["required_level"]:
        if edu["meets_requirement"]:
            highlights.append(
                f"Education requirement met: highest detected degree is "
                f"'{edu['cv_level'] or 'unspecified'}', JD asks for '{edu['required_level']}'."
            )
        else:
            concerns.append(
                f"Education below JD requirement: CV shows "
                f"'{edu['cv_level'] or 'none detected'}', JD asks for '{edu['required_level']}'."
            )

    semantic = match_result["semantic_similarity"]["score"]
    if semantic < 30:
        concerns.append(
            "Overall wording/context similarity between CV and JD is low — the "
            "CV may be describing different domain experience than the role."
        )

    return {
        "overall_score": overall,
        "verdict": verdict,
        "highlights": highlights,
        "concerns": concerns,
        "summary_text": (
            f"{verdict} ({overall}/100). "
            f"{len(skills['matched_required'])}/"
            f"{len(skills['matched_required']) + len(skills['missing_required'])} "
            "required skills matched."
        ),
    }
