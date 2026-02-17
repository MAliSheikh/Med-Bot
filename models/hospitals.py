from pydantic import BaseModel, Field
from typing import List

from config import generate_id

class HospitalCreate(BaseModel):
    name: str
    address: str
    departments: List[str]

class Hospital(HospitalCreate):
    id: str = Field(default_factory=generate_id)

