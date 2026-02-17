from dotenv import load_dotenv
import os
from uuid import uuid4

# Load .env file
load_dotenv()

# Groq Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")

# OCR Space Settings
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY")
OCR_SPACE_API_URL = os.getenv("OCR_SPACE_API_URL")
OCR_DAILY_LIMIT=int(os.getenv("OCR_DAILY_LIMIT"))

def generate_id():
    return str(uuid4())

# Access variables
MONGO_URI = os.getenv("MONGO_DB_CONNECTION_STRING")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
