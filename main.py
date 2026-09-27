"""
CV <-> Job Description Matcher — FastAPI backend.

Pipeline:
  1. Text Cleaning / Normalization      -> app/text_cleaning.py
  2. CV Information Extraction          -> app/cv_extraction.py
  3. Job Description Extraction         -> app/jd_extraction.py
  4. Matching Engine                    -> app/matching_engine.py
  5. Scoring Engine                     -> app/scoring_engine.py
  6. Result / Explanation               -> app/scoring_engine.py (build_explanation)

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open frontend/index.html (or serve it) and point it at
http://localhost:8000.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.cv_extraction import extract_cv_profile
from app.jd_extraction import extract_jd_profile
from app.matching_engine import run_matching_engine
from app.scoring_engine import compute_overall_score, build_explanation
from app.schemas import MatchRequest, MatchResponse

app = FastAPI(
    title="CV / Job Description Matcher",
    description="Extracts structured info from a CV and a Job Description, "
                 "matches them, and returns a weighted score with explanation.",
    version="1.0.0",
)

# Wide-open CORS since this is a local/dev tool meant to be paired with a
# simple static frontend. Restrict allow_origins in a real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/match", response_model=MatchResponse)
def match_cv_to_jd(payload: MatchRequest):
    cv_text = payload.cv_text.strip()
    jd_text = payload.jd_text.strip()

    if not cv_text or not jd_text:
        raise HTTPException(status_code=400, detail="Both cv_text and jd_text are required.")

    # Steps 2 & 3: extraction (each extractor runs Step 1 cleaning internally)
    cv_profile = extract_cv_profile(cv_text)
    jd_profile = extract_jd_profile(jd_text)

    # Step 4: matching engine
    matching = run_matching_engine(cv_profile, jd_profile, cv_text, jd_text)

    # Step 5: scoring engine
    scoring = compute_overall_score(matching)

    # Step 6: result / explanation
    explanation = build_explanation(matching, scoring, cv_profile, jd_profile)

    return {
        "cv_profile": cv_profile,
        "jd_profile": jd_profile,
        "matching": matching,
        "scoring": scoring,
        "explanation": explanation,
    }
