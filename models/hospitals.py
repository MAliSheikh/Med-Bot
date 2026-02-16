from pydantic import BaseModel
from typing import List


# Hospital Models
class Hospital(BaseModel):
    name: str
    address: str
    departments: List[str]

