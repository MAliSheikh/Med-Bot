import requests
import time
import pypdf
from core import config
from services import quota

def extract_text_from_pdf(file_file_obj):
    """
    Extracts text directly from a PDF file object using pypdf.
    """
    text = ""
    try:
        reader = pypdf.PdfReader(file_file_obj)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    return text.strip()

def extract_text_from_image(file_bytes, filename):
    """
    Sends image bytes to OCR.space API.
    """
    if quota.check_ocr_limit_reached():
        print("Daily OCR limit reached")
        return None

    url = "https://api.ocr.space/parse/image"
    
    # Prepare the file for the request
    files = {'file': (filename, file_bytes)}
    data = {'apikey': config.OCR_API_KEY, 'language': 'eng', 'OCREngine': 2}
    
    try:
        resp = requests.post(url, files=files, data=data)
        result = resp.json()
    except Exception as e:
        print(f"OCR Request failed: {e}")
        return None

    quota.increment_ocr_quota()
    time.sleep(2)  # Sleep as per original logic to be polite to the API
    
    if result.get('IsErroredOnProcessing') or not result.get('ParsedResults'):
        return None
        
    return result['ParsedResults'][0].get('ParsedText', "")