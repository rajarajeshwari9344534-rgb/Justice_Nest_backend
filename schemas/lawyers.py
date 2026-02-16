from pydantic import BaseModel, EmailStr, field_validator
import re
from typing import Optional
from datetime import datetime

class LawyerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone_number: str

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Phone number must be exactly 10 digits starting with 6-9")
        return v

    city: Optional[str]
    state: Optional[str]
    gender: Optional[str]
    specialization: Optional[str]
    years_of_experience: float
    id_proof_url : str
    photo_url: str
    fees_range: str
    
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class LawyerLogin(BaseModel):
    email: EmailStr
    password: str
