from pydantic import BaseModel, field_validator
import re
from typing import Optional

class ComplaintCreate(BaseModel):
    user_id: int
    name: str
    number: str
    city: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    complaint_details: str
    complaint_file_url: Optional[str] = None

    @field_validator('number')
    @classmethod
    def validate_number(cls, v):
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Phone number must be exactly 10 digits starting with 6-9")
        return v


class ComplaintUpdate(BaseModel):
    number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    complaint_details: Optional[str] = None
    complaint_file_url: Optional[str] = None
    status: Optional[str] = None



class ComplaintAccept(BaseModel):
    lawyer_id: int






