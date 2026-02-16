from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
MONGO_URI = os.getenv("MONGO_DB_CONNECTION_STRING")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")