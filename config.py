from dotenv import load_dotenv
import os
from uuid import uuid4

# Load .env file
load_dotenv()


def generate_id():
    return str(uuid4())

# Access variables
MONGO_URI = os.getenv("MONGO_DB_CONNECTION_STRING")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")