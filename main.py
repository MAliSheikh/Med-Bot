from typing import List
from fastapi import FastAPI
from models.user import UserResponse
from db.conn import users_collection, user_helper
from api.routers.auth import router as auth_router
from api.routers.hospitals import router as booking_router
from api.routers.doctors import router as doctor_router
from api.routers.appointments import router as appointment_router
from api.routers.reports import router as report_router

app = FastAPI(title="Med Bot Backend APIS")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(booking_router, prefix="/booking", tags=["Hospital Booking"])
app.include_router(doctor_router, prefix="/doctors", tags=["Doctors"])
app.include_router(appointment_router, prefix="/appointments", tags=["Appointments"])
app.include_router(report_router, prefix="/reports", tags=["Medical Reports"])   