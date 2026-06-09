import google.generativeai as genai
import os
import json
import re

# Configure generative AI if API key is present
api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

async def analyse_resume(resume_text: str, job_description: str, match_result: dict) -> dict:
    fallback_result = {
        "recommendations": [
            "Tailor your professional summary to highlight matching skills.",
            "Integrate missing keywords into your experience descriptions.",
            "Ensure your achievements are quantifiable with metrics.",
            "List project experience that demonstrates your skills.",
            "Review formatting to make it clean and easy to scan."
        ],
        "skill_scores": {
            "Core Match": match_result["score"],
            "Unmatched Skills": 100 - match_result["score"]
        },
        "summary": "The resume has some match with the job requirements. Add missing keywords to increase ATS compatibility."
    }

    if not api_key:
        print("Warning: GEMINI_API_KEY environment variable is not set. Using fallback analysis.")
        return fallback_result

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
You are an expert ATS (Applicant Tracking System) resume coach and professional recruiter.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

MATCH SCORE: {match_result['score']}%
MISSING KEYWORDS: {', '.join(match_result['missing'][:20])}

Analyse the resume against the job description and determine:
1. A list of 5 specific, actionable recommendations to improve the resume.
2. Skill scores (0-100) for the top 3-5 key skills found or missing.
3. A 2-3 sentence professional summary of the candidate's fit.

Respond ONLY with valid JSON (no markdown block, no leading/trailing text) in this exact format:
{{
  "recommendations": ["rec 1", "rec 2", "rec 3", "rec 4", "rec 5"],
  "skill_scores": {{"Python": 85, "SQL": 60, "Leadership": 40}},
  "summary": "Professional summary of fit."
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean potential markdown wrapping
        text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"```$", "", text).strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"Error during Gemini analysis: {e}")
        return fallback_result
