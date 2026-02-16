from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from db.session import Base
from datetime import datetime

class Lawyers(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    city = Column(String)
    state = Column(String)
    specialization = Column(String)
    years_of_experience = Column(Float, nullable=False)
    gender = Column(String, nullable=True)
    fees_range = Column(String, nullable=False)

    id_proof_url = Column(String, nullable=False)   
    photo_url = Column(String, nullable=False)      

    password = Column(String, nullable=False)
    status = Column(String, default="pending") # pending, approved, rejected
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
