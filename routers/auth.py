from datetime import timedelta
from typing import List, Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import  OAuth2PasswordRequestForm
from cruds.auth.jwt_handler import create_access_token, get_current_user
from models.user import Token, User, UserResponse
from db.conn import users_collection, user_helper
from cruds.auth.auth import hash_password, verify_password


router = APIRouter()

# Create user
@router.post("/register/", response_model=UserResponse)
async def create_user(user: User):
    user_exists = await users_collection.find_one({"email": user.email})
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_dict["password"])
    result = await users_collection.insert_one(user_dict)
    new_user = await users_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)

# User Login
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[dict, Depends(get_current_user)]):
    return current_user

# Get all users
@router.get("/users/", response_model=List[UserResponse])
async def get_users():
    users = []
    async for user in users_collection.find():
        users.append(user_helper(user))
    return users