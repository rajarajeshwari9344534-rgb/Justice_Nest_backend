from pydantic import BaseModel
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


class ComplaintUpdate(BaseModel):
    number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    complaint_details: Optional[str] = None
    complaint_file_url: Optional[str] = None



class ComplaintAccept(BaseModel):
    lawyer_id: int






