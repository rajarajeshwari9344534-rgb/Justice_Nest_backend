from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from db.session import Base
from datetime import datetime

class Complaints(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=True)
    name = Column(String, nullable=False)
    number = Column(String(15), nullable=False)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    complaint_details = Column(Text, nullable=False)
    complaint_file_url = Column(String, nullable=True)
    status = Column(String, default="pending")  
    created_at = Column(DateTime, default=datetime.now, nullable=False)


