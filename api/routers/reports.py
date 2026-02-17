from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from api.func.auth.jwt_handler import get_current_user
from services.report import extract_report, llm
from api.func.reports.reports import (
    create_report,
    get_reports_by_user,
    get_report_by_id,
    delete_report_by_id,
)
import json
from datetime import datetime
from typing import List
from bson import ObjectId
from db.conn import users_collection

router = APIRouter()

@router.post("/report_analyze")
async def analyze_report(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Upload a file. 
    - If PDF: Extracts text directly.
    - If Image: Uses OCR to extract text.
    - Sends extracted text to LLM for structured analysis.
    """
    
    extracted_text = None
    
    # 1. Logic Twist: Check File Type
    if file.content_type == "application/pdf":
        # Extract PDF Data
        print("Detected PDF. Extracting text directly...")
        extracted_text = extract_report.extract_text_from_pdf(file.file)
        
    elif file.content_type.startswith("image/"):
        # Extract Image Data via OCR
        print("Detected Image. Sending to OCR...")
        # Read bytes for the requests library
        file_bytes = await file.read()
        extracted_text = extract_report.extract_text_from_image(file_bytes, file.filename)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and Images allowed.")

    if not extracted_text:
        raise HTTPException(status_code=422, detail="Could not extract text from file. It might be empty or quota exceeded.")

    # 2. Send to Hugging Face
    print("Sending text to LLM...")
    analysis_result = llm.analyze_text(extracted_text)

    if "error" in analysis_result:
        raise HTTPException(status_code=500, detail=analysis_result["error"])

    # Parse JSON from LLM response
    try:
        # Clean up markdown formatting if present
        json_str = analysis_result["analysis"].replace("```json", "").replace("```", "").strip()
        report_data = json.loads(json_str)
    except json.JSONDecodeError:
        report_data = {"raw_output": analysis_result["analysis"], "error": "JSON parsing failed"}

    # Save to MongoDB via helper
    doc = {
        "user_id": current_user.get("id"),
        "filename": file.filename,
        "uploaded_at": datetime.now(),
        "report_data": report_data
    }
    await create_report(doc)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "analysis": report_data
    }
    
    

@router.get("/")
async def get_reports(
    current_user: dict = Depends(get_current_user), # type: ignore
):
    """
    Retrieve list of user's past reports.
    """
    # Fetch reports belonging to the current user via helper
    reports = await get_reports_by_user(current_user["id"]) 
    return reports

@router.get("/{id}")
async def get_report_details(
    id: str,
    current_user: dict = Depends(get_current_user), # type: ignore
):
    """
    Retrieve specific report details and status.
    """
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid report ID format"
        )
    report = await get_report_by_id(id, current_user["id"]) 

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Report not found"
        )
    
    return report

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    id: str,
    current_user: dict = Depends(get_current_user), # type: ignore
):
    deleted_count = await delete_report_by_id(id, current_user["id"])
    if deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return {"deleted": True}