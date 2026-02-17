from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from core.config import generate_id

# Doctor Models

class DoctorCreate(BaseModel):
    hospital_id: str
    name: str
    specialty: str
    # List of datetime objects representing available slots
    available_slots: List[datetime] = []
    experience: str
    ratings: float = 0.0

class Doctor(DoctorCreate):
    id: str = Field(default_factory=generate_id)
