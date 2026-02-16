from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Doctor Models
class Doctor(BaseModel):
    hospital_id: str
    name: str
    specialty: str
    available_slots: List[datetime]
    experience: int
    ratings: Optional[float] = None
