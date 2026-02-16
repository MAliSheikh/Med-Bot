from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from config import MONGO_URI

MONGO_DETAILS = MONGO_URI # Change if using Atlas

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.ai_medical_app

print("INFO:      Connected to MongoDB")

# Collections
users_collection = database.get_collection("users")
reports_collection = database.get_collection("reports")
appointments_collection = database.get_collection("appointments")
doctors_collection = database.get_collection("doctors")
hospitals_collection = database.get_collection("hospitals")
medicines_collection = database.get_collection("medicines")

# Helper to convert Mongo object to dict
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "age": user.get("age", None),
        "gender": user.get("gender", ""),
        "family_members": user.get("family_members", []),
        "allergies": user.get("allergies", []),
        "chronic_conditions": user.get("chronic_conditions", []),
        "blood_type": user.get("blood_type", None),
        "past_surgeries": user.get("past_surgeries", []),
        "genetic_disorders": user.get("genetic_disorders", []),
        "preferences": user.get("preferences", {}),
        "emergency_contacts": user.get("emergency_contacts", [])
    }

def report_helper(report) -> dict:
    return {
        "id": str(report["_id"]),
        "user_id": str(report["user_id"]),
        "report_name": report["report_name"],
        "hospital": report["hospital"],
        "date": report["date"],
        "abnormal_tests": report.get("abnormal_tests", []),
        "severity": report.get("severity", None),
        "file_path": report.get("file_path", "")
    }