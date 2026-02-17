from typing import List, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field, BeforeValidator


PyObjectId = Annotated[str, BeforeValidator(str)]

class ReportResponse(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    report_name: str
    hospital: Optional[str] = None
    date: Optional[str] = None
    abnormal_tests: List[str] = []
    severity: Optional[str] = None
    file_path: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True