from fastapi import APIRouter, HTTPException, status, Body, Depends
from typing import List

from models.doctors import Doctor, DoctorCreate
from api.func.hospitals.doctors_crud import (
    create_doctor,
    get_all_doctors,
    get_doctor,
    get_doctors_by_hospital,
    update_doctor,
    delete_doctor,
)
from api.func.auth.jwt_handler import get_current_user

router = APIRouter()


@router.post("/doctors/", response_model=Doctor, status_code=status.HTTP_201_CREATED)
async def create_doctor_route(doctor_data: DoctorCreate, current_user: dict = Depends(get_current_user)):
    doctor = Doctor(**doctor_data.dict())
    return await create_doctor(doctor)

@router.get("/doctors/", response_model=List[Doctor])
async def get_all_doctors_route(current_user: dict = Depends(get_current_user)):
    return await get_all_doctors()

@router.get("/doctors/{doctor_id}", response_model=Doctor)
async def get_doctor_route(doctor_id: str, current_user: dict = Depends(get_current_user)):
    doctor = await get_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.get("/hospitals/{hospital_id}/doctors", response_model=List[Doctor])
async def get_doctors_by_hospital_route(hospital_id: str, current_user: dict = Depends(get_current_user)):
    return await get_doctors_by_hospital(hospital_id)

@router.put("/doctors/{doctor_id}", response_model=Doctor)
async def update_doctor_route(doctor_id: str, doctor_data: DoctorCreate, current_user: dict = Depends(get_current_user)):
    updated_doctor = await update_doctor(doctor_id, **doctor_data.dict())
    if not updated_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated_doctor

@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor_route(doctor_id: str, current_user: dict = Depends(get_current_user)):
    success = await delete_doctor(doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return None
