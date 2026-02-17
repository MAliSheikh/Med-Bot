from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from api.func.auth.jwt_handler import get_current_user
from services.report import extraction, llm

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
        extracted_text = extraction.extract_text_from_pdf(file.file)
        
    elif file.content_type.startswith("image/"):
        # Extract Image Data via OCR
        print("Detected Image. Sending to OCR...")
        # Read bytes for the requests library
        file_bytes = await file.read()
        extracted_text = extraction.extract_text_from_image(file_bytes, file.filename)
        
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and Images allowed.")

    if not extracted_text:
        raise HTTPException(status_code=422, detail="Could not extract text from file. It might be empty or quota exceeded.")

    # 2. Send to Hugging Face
    print("Sending text to LLM...")
    analysis_result = llm.analyze_text(extracted_text)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "analysis": analysis_result
    }