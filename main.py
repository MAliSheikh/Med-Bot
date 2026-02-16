from typing import List
from fastapi import FastAPI
from models.user import UserResponse
from db.conn import users_collection, user_helper
from routers.auth import router as auth_router

app = FastAPI(title="Med Bot Backend APIS")

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

