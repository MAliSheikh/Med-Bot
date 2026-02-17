from pydantic import BaseModel
from datetime import datetime



class BookingRequest(BaseModel):
    user_id: str
    doctor_id: str
    date_time: datetime