from typing import List, Optional
from bson import ObjectId
from db.conn import database
from fastapi import UploadFile, File, HTTPException
from services.report import extract_report, llm

async def ai_analyze_report(file: UploadFile = File(...), user_info: dict = None, past_reports: List[dict] = None):
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
    analysis_result = llm.analyze_text(extracted_text, user_info, past_reports)
    return analysis_result

async def create_report(doc: dict) -> ObjectId:
    """Insert a report document and return the inserted id."""
    res = await database["reports"].insert_one(doc)
    return res.inserted_id


async def get_reports_by_user(user_id: str, limit: int = 100) -> List[dict]:
    """Return a list of reports for a given user id."""
    cursor = database["reports"].find({"user_id": user_id})
    reports = await cursor.to_list(length=limit)
    for report in reports:
        report["_id"] = str(report["_id"])
    return reports


async def get_report_by_id(report_id: str, user_id: str) -> Optional[dict]:
    """Return a single report by its id and owner user id."""
    if not ObjectId.is_valid(report_id):
        return None
    report = await database["reports"].find_one({"_id": ObjectId(report_id), "user_id": user_id})
    if report:
        report["_id"] = str(report["_id"])
    return report


async def delete_report_by_id(report_id: str, user_id: str) -> int:
    """Delete a report and return the deleted count (0 or 1)."""
    if not ObjectId.is_valid(report_id):
        return 0
    res = await database["reports"].delete_one({"_id": ObjectId(report_id), "user_id": user_id})
    return int(res.deleted_count)
