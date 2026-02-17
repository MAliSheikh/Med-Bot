from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from models.appointments import Appointment
from models.booking import BookingRequest
from api.func.hospitals.appointments_crud import (
    book_appointment,
    get_appointment,
    get_user_appointments,
    cancel_appointment,
)
from api.func.auth.jwt_handler import get_current_user

router = APIRouter()


@router.post("/appointments/book", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def book_appointment_route(request: BookingRequest, current_user: dict = Depends(get_current_user)):
    try:
        return await book_appointment(
            user_id=request.user_id,
            doctor_id=request.doctor_id,
            date_time=request.date_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment_route(appointment_id: str, current_user: dict = Depends(get_current_user)):
    appointment = await get_appointment(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.get("/users/{user_id}/appointments", response_model=List[Appointment])
async def get_user_appointments_route(user_id: str, current_user: dict = Depends(get_current_user)):
    return await get_user_appointments(user_id)

@router.put("/appointments/{appointment_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_appointment_route(appointment_id: str, current_user: dict = Depends(get_current_user)):
    success = await cancel_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=400, detail="Appointment not found or already cancelled")
    return {"message": "Appointment cancelled successfully"}