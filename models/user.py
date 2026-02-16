from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# User Models
class FamilyMember(BaseModel):
    name: str
    age: int
    relation: str

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    age: int
    gender: str
    family_members: Optional[List[FamilyMember]] = []
    
    # Additional health info
    allergies: Optional[List[str]] = []           # e.g., "Penicillin, Peanuts"
    chronic_conditions: Optional[List[str]] = [] # e.g., "Diabetes, Hypertension"
    blood_type: Optional[str] = None             # e.g., "O+"
    past_surgeries: Optional[List[str]] = []     # e.g., "Appendectomy 2019"
    genetic_disorders: Optional[List[str]] = []  # e.g., "None"
    preferences: Optional[dict] = {}             # any user preferences
    emergency_contacts: Optional[List[dict]] = [] # name, relation, phone

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    age: int
    gender: str
    family_members: Optional[List[FamilyMember]] = []
    
    # Additional health info
    allergies: Optional[List[str]] = []           # e.g., "Penicillin, Peanuts"
    chronic_conditions: Optional[List[str]] = [] # e.g., "Diabetes, Hypertension"
    blood_type: Optional[str] = None             # e.g., "O+"
    past_surgeries: Optional[List[str]] = []     # e.g., "Appendectomy 2019"
    genetic_disorders: Optional[List[str]] = []  # e.g., "None"
    preferences: Optional[dict] = {}             # any user preferences
    emergency_contacts: Optional[List[dict]] = [] # name, relation, phone

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None