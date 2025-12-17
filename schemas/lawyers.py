from pydantic import BaseModel
from typing import Optional

class LawyerCreate(BaseModel):
    name: str
    email: str
    phone_number: str
    city: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: int
    fees_range: int
    id_proof_file_url:str
    password: str


class LawyerUpdate(BaseModel):
    phone_number: Optional[str] = None
    city: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    fees_range: Optional[int] = None
    id_proof_file_url:str






