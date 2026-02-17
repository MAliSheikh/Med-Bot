from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from models.hospitals import Hospital, HospitalCreate
from api.func.hospitals.hospitals_crud import (
    create_hospital,
    get_all_hospitals,
    get_hospital,
    update_hospital,
    delete_hospital,
)
from api.func.auth.jwt_handler import get_current_user

router = APIRouter()

@router.post("/hospitals/", response_model=Hospital, status_code=status.HTTP_201_CREATED)
async def create_hospital_route(hospital_data: HospitalCreate, current_user: dict = Depends(get_current_user)):
    hospital = Hospital(**hospital_data.dict())
    return await create_hospital(hospital)

@router.get("/hospitals/", response_model=List[Hospital])
async def get_all_hospitals_route(current_user: dict = Depends(get_current_user)):
    return await get_all_hospitals()

@router.get("/hospitals/{hospital_id}", response_model=Hospital)
async def get_hospital_route(hospital_id: str, current_user: dict = Depends(get_current_user)):
    hospital = await get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.put("/hospitals/{hospital_id}", response_model=Hospital)
async def update_hospital_route(hospital_id: str, hospital_data: HospitalCreate, current_user: dict = Depends(get_current_user)):
    updated_hospital = await update_hospital(hospital_id, **hospital_data.dict())
    if not updated_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return updated_hospital

@router.delete("/hospitals/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hospital_route(hospital_id: str, current_user: dict = Depends(get_current_user)):
    success = await delete_hospital(hospital_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return None
