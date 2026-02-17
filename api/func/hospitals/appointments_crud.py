from typing import List, Optional
from datetime import datetime
from bson.objectid import ObjectId
from db.conn import appointments_collection
from models.appointments import Appointment
from .doctors_crud import get_doctor, update_doctor
from .hospitals_crud import get_hospital


async def book_appointment(user_id: str, doctor_id: str, date_time: datetime) -> Appointment:
    """Book a new appointment in MongoDB"""
    doctor = await get_doctor(doctor_id)
    if not doctor:
        raise ValueError("Doctor not found")

    # Check availability
    if date_time not in doctor.available_slots:
        raise ValueError("Slot not available")

    # Get hospital info for the appointment record
    hospital = await get_hospital(doctor.hospital_id)
    hospital_name = hospital.name if hospital else "Unknown Hospital"

    # Create Appointment
    appointment_dict = {
        "user_id": user_id,
        "doctor_id": doctor_id,
        "hospital_name": hospital_name,
        "specialty": doctor.specialty,
        "date_time": date_time,
        "status": "Scheduled"
    }
    
    result = await appointments_collection.insert_one(appointment_dict)
    
    # Remove slot from doctor's availability
    updated_slots = [slot for slot in doctor.available_slots if slot != date_time]
    await update_doctor(doctor_id, available_slots=updated_slots)
    
    appointment = Appointment(**appointment_dict)
    appointment.id = str(result.inserted_id)
    return appointment


async def get_appointment(appointment_id: str) -> Optional[Appointment]:
    """Retrieve a specific appointment by ID"""
    try:
        appointment = await appointments_collection.find_one({"_id": ObjectId(appointment_id)})
        if appointment:
            return Appointment(**appointment_helper(appointment))
    except:
        pass
    return None


async def get_user_appointments(user_id: str) -> List[Appointment]:
    """Retrieve all appointments for a specific user"""
    appointments = []
    async for appointment in appointments_collection.find({"user_id": user_id}):
        appointment_data = appointment_helper(appointment)
        appointments.append(Appointment(**appointment_data))
    return appointments


async def update_appointment(appointment_id: str, **kwargs) -> Optional[Appointment]:
    """Update an appointment in MongoDB"""
    try:
        await appointments_collection.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$set": kwargs}
        )
        return await get_appointment(appointment_id)
    except:
        return None


async def cancel_appointment(appointment_id: str) -> bool:
    """Cancel an appointment and return the slot to the doctor"""
    appointment = await get_appointment(appointment_id)
    if appointment and appointment.status != "Cancelled":
        await update_appointment(appointment_id, status="Cancelled")
        
        # Return slot to doctor
        doctor = await get_doctor(appointment.doctor_id)
        if doctor:
            doctor.available_slots.append(appointment.date_time)
            doctor.available_slots.sort()
            await update_doctor(doctor.id, available_slots=doctor.available_slots)
        return True
    return False


def appointment_helper(appointment) -> dict:
    """Convert MongoDB appointment document to dict"""
    return {
        "id": str(appointment["_id"]),
        "user_id": appointment.get("user_id", ""),
        "doctor_id": appointment.get("doctor_id", ""),
        "hospital_name": appointment.get("hospital_name", ""),
        "specialty": appointment.get("specialty", ""),
        "date_time": appointment.get("date_time"),
        "status": appointment.get("status", "Scheduled")
    }
