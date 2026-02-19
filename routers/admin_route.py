from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from auth_utils import get_current_user, create_access_token
from models.lawyers import Lawyers
from pydantic import BaseModel, EmailStr

class AdminLogin(BaseModel):
    email: str
    password: str


admin_router = APIRouter(prefix="/admin", tags=["Admin"])

@admin_router.post("/login")
def admin_login(credentials: AdminLogin):
    if credentials.email == "admin@justicenest.com" and credentials.password == "admin123":
        access_token = create_access_token(data={"sub": credentials.email, "role": "admin"})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": 0,  # Static ID for admin
            "name": "Administrator",
            "email": credentials.email,
            "status": "approved"
        }

    raise HTTPException(status_code=401, detail="Invalid admin credentials")


# GET PENDING LAWYERS

@admin_router.get("/pending_lawyers")
def get_pending_lawyers(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view pending lawyers"
        )
    # Fetch all lawyers where status is 'pending'
    return db.query(Lawyers).filter(Lawyers.status == "pending", Lawyers.is_active == True).all()


# APPROVE LAWYER

@admin_router.patch("/approve_lawyer/{lawyer_id}")
def approve_lawyer(lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve lawyers"
        )
    
    lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    lawyer.status = "approved"
    db.commit()
    db.refresh(lawyer)

    return {"message": "Lawyer approved successfully", "status": lawyer.status}

from models.complaint import Complaints

@admin_router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view statistics"
        )
    
    total_complaints = db.query(Complaints).count()
    pending_complaints = db.query(Complaints).filter(Complaints.status == "pending").count()
    accepted_complaints = db.query(Complaints).filter(Complaints.status == "accepted").count()
    resolved_complaints = db.query(Complaints).filter(Complaints.status == "resolved").count()
    approved_lawyers = db.query(Lawyers).filter(Lawyers.status == "approved").count()

    return {
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "accepted_complaints": accepted_complaints,
        "resolved_complaints": resolved_complaints,
        "approved_lawyers": approved_lawyers
    }

# -----------------------------
# REJECT LAWYER 
# -----------------------------
@admin_router.patch("/reject_lawyer/{lawyer_id}")
def reject_lawyer(lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can reject lawyers"
        )
    
    lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    lawyer.status = "rejected"
    db.commit()
    db.refresh(lawyer)

    return {"message": "Lawyer rejected", "status": lawyer.status}
