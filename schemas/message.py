from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    user_id: int
    lawyer_id: int
    content: str
    sender_role: str

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: str

class MessageResponse(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    lawyer_id: Optional[int] = None
    user_id: Optional[int] = None
    name: str
    last_message: str
    timestamp: datetime
