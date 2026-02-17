from typing import List, Optional
from bson.objectid import ObjectId
from db.conn import hospitals_collection
from models.hospitals import Hospital


async def create_hospital(hospital: Hospital) -> Hospital:
    """Create a new hospital in MongoDB"""
    hospital_dict = hospital.dict(exclude={"id"})
    result = await hospitals_collection.insert_one(hospital_dict)
    hospital.id = str(result.inserted_id)
    return hospital


async def get_all_hospitals() -> List[Hospital]:
    """Retrieve all hospitals from MongoDB"""
    hospitals = []
    async for hospital in hospitals_collection.find():
        hospital_data = hospital_helper(hospital)
        hospitals.append(Hospital(**hospital_data))
    return hospitals


async def get_hospital(hospital_id: str) -> Optional[Hospital]:
    """Retrieve a specific hospital by ID"""
    try:
        hospital = await hospitals_collection.find_one({"_id": ObjectId(hospital_id)})
        if hospital:
            return Hospital(**hospital_helper(hospital))
    except:
        pass
    return None


async def update_hospital(hospital_id: str, **kwargs) -> Optional[Hospital]:
    """Update a hospital in MongoDB"""
    try:
        await hospitals_collection.update_one(
            {"_id": ObjectId(hospital_id)},
            {"$set": kwargs}
        )
        return await get_hospital(hospital_id)
    except:
        return None


async def delete_hospital(hospital_id: str) -> bool:
    """Delete a hospital from MongoDB"""
    try:
        result = await hospitals_collection.delete_one({"_id": ObjectId(hospital_id)})
        return result.deleted_count > 0
    except:
        return False


def hospital_helper(hospital) -> dict:
    """Convert MongoDB hospital document to dict"""
    return {
        "id": str(hospital["_id"]),
        "name": hospital.get("name", ""),
        "address": hospital.get("address", ""),
        "departments": hospital.get("departments", [])
    }
