from dotenv import load_dotenv
import os
from uuid import uuid4

# Load .env file
load_dotenv()

# Hugging Face Settings
HF_API_KEY = os.getenv("HF_API_KEY", "YOUR_HF_API_KEY")
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/gpt2")

def generate_id():
    return str(uuid4())

# Access variables
MONGO_URI = os.getenv("MONGO_DB_CONNECTION_STRING")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
