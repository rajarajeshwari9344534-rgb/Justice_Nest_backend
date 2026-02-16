from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from db.session import Base
from datetime import datetime

class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"), nullable=False)
    sender_role = Column(String, nullable=False) # "user" or "lawyer"
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
