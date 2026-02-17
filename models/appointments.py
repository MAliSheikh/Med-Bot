from pydantic import BaseModel, Field
from datetime import datetime

from config import generate_id


class Appointment(BaseModel):
    id: str = Field(default_factory=generate_id)
    user_id: str
    doctor_id: str
    # Denormalized fields for quick access
    hospital_name: str 
    specialty: str
    date_time: datetime
    status: str = "Scheduled"  