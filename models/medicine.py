from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Medicine Models
class Medicine(BaseModel):
    user_id: str
    medicine_name: str
    dose: str
    frequency: str
    start_date: datetime
    end_date: datetime
    condition: str
    taken_log: Optional[List[datetime]] = []