from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from services.parser import extract_text
from services.analyser import analyse_resume
from services.keyword import extract_keywords, compute_match
from utils.pdf_report import generate_report
import io

router = APIRouter()

@router.post("/analyse")
async def analyse(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Standard mime types or simple extension checks
    content_type = resume.content_type
    filename = resume.filename.lower()
    
    is_valid_type = (
        content_type in [
            "application/pdf", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ] or 
        filename.endswith('.pdf') or 
        filename.endswith('.docx')
    )
    
    if not is_valid_type:
        raise HTTPException(
            status_code=400, 
            detail="Only PDF and DOCX files are supported."
        )
    
    # Map content type if it's generic octet-stream
    resolved_content_type = content_type
    if content_type == "application/octet-stream":
        if filename.endswith(".pdf"):
            resolved_content_type = "application/pdf"
        elif filename.endswith(".docx"):
            resolved_content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
    try:
        content = await resume.read()
        resume_text = extract_text(content, resolved_content_type)
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to parse resume file: {str(e)}"
        )
        
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume seems to be empty or could not be parsed."
        )

    try:
        jd_keywords = extract_keywords(job_description)
        resume_keywords = extract_keywords(resume_text)
        match_result = compute_match(resume_keywords, jd_keywords)
        
        ai_analysis = await analyse_resume(resume_text, job_description, match_result)
        
        return {
            "matchScore": match_result["score"],
            "matchLabel": match_result["label"],
            "matchedKeywords": match_result["matched"],
            "missingKeywords": match_result["missing"],
            "recommendations": ai_analysis.get("recommendations", []),
            "skillScores": ai_analysis.get("skill_scores", {}),
            "summary": ai_analysis.get("summary", "")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/report")
async def download_report(payload: dict):
    try:
        pdf_bytes = generate_report(payload)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=resume-analysis.pdf"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report PDF: {str(e)}"
        )
