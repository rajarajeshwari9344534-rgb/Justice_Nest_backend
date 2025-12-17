from sqlalchemy import Column, Integer, String, DateTime
from db.session import Base
from datetime import datetime

class Lawyers(Base):
    __tablename__ = "lawyers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String(15), nullable=False)
    city = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    years_of_experience = Column(Integer, nullable=False)
    fees_range = Column(Integer, nullable=False)
    id_proof_file_url = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)



 