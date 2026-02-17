from typing import List, Optional
from bson.objectid import ObjectId
from db.conn import doctors_collection
from models.doctors import Doctor


async def create_doctor(doctor: Doctor) -> Doctor:
    """Create a new doctor in MongoDB"""
    doctor_dict = doctor.dict(exclude={"id"})
    result = await doctors_collection.insert_one(doctor_dict)
    doctor.id = str(result.inserted_id)
    return doctor


async def get_all_doctors() -> List[Doctor]:
    """Retrieve all doctors from MongoDB"""
    doctors = []
    async for doctor in doctors_collection.find():
        doctor_data = doctor_helper(doctor)
        doctors.append(Doctor(**doctor_data))
    return doctors


async def get_doctor(doctor_id: str) -> Optional[Doctor]:
    """Retrieve a specific doctor by ID"""
    try:
        doctor = await doctors_collection.find_one({"_id": ObjectId(doctor_id)})
        if doctor:
            return Doctor(**doctor_helper(doctor))
    except:
        pass
    return None


async def get_doctors_by_hospital(hospital_id: str) -> List[Doctor]:
    """Retrieve all doctors for a specific hospital"""
    doctors = []
    async for doctor in doctors_collection.find({"hospital_id": hospital_id}):
        doctor_data = doctor_helper(doctor)
        doctors.append(Doctor(**doctor_data))
    return doctors


async def update_doctor(doctor_id: str, **kwargs) -> Optional[Doctor]:
    """Update a doctor in MongoDB"""
    try:
        await doctors_collection.update_one(
            {"_id": ObjectId(doctor_id)},
            {"$set": kwargs}
        )
        return await get_doctor(doctor_id)
    except:
        return None


async def delete_doctor(doctor_id: str) -> bool:
    """Delete a doctor from MongoDB"""
    try:
        result = await doctors_collection.delete_one({"_id": ObjectId(doctor_id)})
        return result.deleted_count > 0
    except:
        return False


def doctor_helper(doctor) -> dict:
    """Convert MongoDB doctor document to dict"""
    return {
        "id": str(doctor["_id"]),
        "hospital_id": doctor.get("hospital_id", ""),
        "name": doctor.get("name", ""),
        "specialty": doctor.get("specialty", ""),
        "available_slots": doctor.get("available_slots", []),
        "experience": doctor.get("experience", ""),
        "ratings": doctor.get("ratings", 0.0)
    }
