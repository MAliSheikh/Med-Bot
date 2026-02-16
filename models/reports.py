from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


# Report Models
class Report(BaseModel):
    user_id: str
    report_name: str
    hospital: str
    date: datetime
    abnormal_tests: Optional[List[str]] = []
    severity: Optional[str] = None
    file_path: Optional[str] = None

class ReportResponse(Report):
    id: str

