from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from dependencies import get_db
from auth_utils import get_current_user
from models.message import Messages
from models.user import User
from models.lawyers import Lawyers
from schemas.message import MessageCreate, MessageResponse, MessageUpdate, ConversationResponse

message_router = APIRouter(prefix="/messages", tags=["Messages"])

@message_router.post("/", response_model=MessageResponse)
def send_message(msg: MessageCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    
    # Infer role if not explicitly set
    if not token_role:
        token_role = "user"
        
    print(f"LOG: send_message attempt by {token_role} ID {token_user_id}. Target User: {msg.user_id}, Target Lawyer: {msg.lawyer_id}")
    
    # Verify authorization
    if token_role == "user" and int(token_user_id or 0) != int(msg.user_id):
        print(f"FORBIDDEN: Token ID {token_user_id} != msg.user_id {msg.user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized: Token ID {token_user_id} != msg.user_id {msg.user_id}"
        )
    elif token_role == "lawyer" and int(token_user_id or 0) != int(msg.lawyer_id):
        print(f"FORBIDDEN: Token ID {token_user_id} != msg.lawyer_id {msg.lawyer_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized: Token ID {token_user_id} != msg.lawyer_id {msg.lawyer_id}"
        )
    
    try:
        # Pydantic v2 uses model_dump, v1 uses dict
        data = msg.model_dump() if hasattr(msg, "model_dump") else msg.dict()
        new_msg = Messages(**data)
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        return new_msg
    except Exception as e:
        db.rollback()
        print(f"ERROR SENDING MESSAGE: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Backend Error: {str(e)}. Ensure User ID {msg.user_id} and Lawyer ID {msg.lawyer_id} exist."
        )

@message_router.get("/{user_id}/{lawyer_id}", response_model=List[MessageResponse])
def get_chat_history(user_id: int, lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    
    # Infer role if not explicitly set
    if not token_role:
        token_role = "user"
    
    # Verify authorization
    is_authorized = False
    if token_role == "user" and int(token_user_id or 0) == int(user_id):
        is_authorized = True
    elif token_role == "lawyer" and int(token_user_id or 0) == int(lawyer_id):
        is_authorized = True
        
    if not is_authorized:
        print(f"FORBIDDEN Error in chat history: role={token_role}, token_id={token_user_id}, req_user_id={user_id}, req_lawyer_id={lawyer_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this chat history"
        )
    
    return db.query(Messages).filter(
        Messages.user_id == user_id,
        Messages.lawyer_id == lawyer_id
    ).order_by(Messages.created_at.asc()).all()

@message_router.put("/{message_id}", response_model=MessageResponse)
def edit_message(message_id: int, msg_data: MessageUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    msg = db.query(Messages).filter(Messages.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    
    # Verify authorization - only the sender can edit
    if token_role == "user" and int(token_user_id or 0) != int(msg.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this message"
        )
    elif token_role == "lawyer" and int(token_user_id or 0) != int(msg.lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this message"
        )
    
    msg.content = msg_data.content
    db.commit()
    db.refresh(msg)
    return msg

@message_router.delete("/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    msg = db.query(Messages).filter(Messages.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    
    # Verify authorization - only the sender can delete
    if token_role == "user" and int(token_user_id or 0) != int(msg.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this message"
        )
    elif token_role == "lawyer" and int(token_user_id or 0) != int(msg.lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this message"
        )
    
    db.delete(msg)
    db.commit()
    return {"message": "Message deleted successfully"}

@message_router.get("/conversations/{role}/{id}", response_model=List[ConversationResponse])
def get_conversations(role: str, id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    
    # Infer role if not explicitly set
    if not token_role:
        token_role = "user"
    
    print(f"DEBUG: get_conversations requested for role={role}, id={id}. Token: role={token_role}, id={token_user_id}")
    
    # Verify authorization
    if role == "user":
        if token_role != "user" or int(token_user_id or 0) != int(id):
            print(f"FORBIDDEN: Token {token_role}/{token_user_id} cannot view user {id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized: {token_role} {token_user_id} cannot view user {id} conversations"
            )
    elif role == "lawyer":
        if token_role != "lawyer" or int(token_user_id or 0) != int(id):
            print(f"FORBIDDEN: Token {token_role}/{token_user_id} cannot view lawyer {id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not authorized: {token_role} {token_user_id} cannot view lawyer {id} conversations"
            )
    
    if role == "user":
        # Get all lawyers this user has chatted with
        distinct_lawyers = db.query(Messages.lawyer_id).filter(Messages.user_id == id).distinct().all()
        print(f"DEBUG: Distinct lawyers for user {id}: {distinct_lawyers}")
        conversations = []
        for (l_id,) in distinct_lawyers:
            lawyer = db.query(Lawyers).filter(Lawyers.id == l_id).first()
            last_msg = db.query(Messages).filter(Messages.user_id == id, Messages.lawyer_id == l_id).order_by(Messages.created_at.desc()).first()
            if lawyer and last_msg:
                conversations.append({
                    "lawyer_id": l_id,
                    "name": lawyer.name,
                    "last_message": last_msg.content,
                    "timestamp": last_msg.created_at
                })
        print(f"DEBUG: Returning {len(conversations)} conversations for user {id}")
        return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)
    
    elif role == "lawyer":
        # Get all users this lawyer has chatted with
        distinct_users = db.query(Messages.user_id).filter(Messages.lawyer_id == id).distinct().all()
        print(f"DEBUG: Distinct users for lawyer {id}: {distinct_users}")
        conversations = []
        for (u_id,) in distinct_users:
            user = db.query(User).filter(User.id == u_id).first()
            last_msg = db.query(Messages).filter(Messages.user_id == u_id, Messages.lawyer_id == id).order_by(Messages.created_at.desc()).first()
            if user and last_msg:
                conversations.append({
                    "user_id": u_id,
                    "name": user.name,
                    "last_message": last_msg.content,
                    "timestamp": last_msg.created_at
                })
        print(f"DEBUG: Returning {len(conversations)} conversations for lawyer {id}")
        return sorted(conversations, key=lambda x: x["timestamp"], reverse=True)
    
    return []
