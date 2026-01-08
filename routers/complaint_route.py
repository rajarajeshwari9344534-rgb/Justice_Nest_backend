from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models.complaint import Complaints
from schemas.complaint import ComplaintCreate,ComplaintUpdate,ComplaintAccept


complaint_router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


@complaint_router.post("/", status_code=status.HTTP_201_CREATED)
def create_complaint(data: ComplaintCreate,db: Session = Depends(get_db)):
    complaint = Complaints(
        user_id=data.user_id,
        name=data.name,
        number=data.number,
        city=data.city,
        state=data.state,
        gender=data.gender,
        complaint_details=data.complaint_details,
        complaint_file_url=data.complaint_file_url
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return {
        "message": "Complaint created successfully",
        "complaint_id": complaint.id
    }



@complaint_router.get("/user/{user_id}")
def get_user_complaints(user_id: int,db: Session = Depends(get_db)):
    return (db.query(Complaints).filter(Complaints.user_id == user_id).all())


@complaint_router.get("/pending")
def get_pending_complaints(db: Session = Depends(get_db)):
    return (db.query(Complaints).filter(Complaints.status == "pending") .all())


@complaint_router.put("/{complaint_id}/accept")
def accept_complaint(complaint_id: int,data: ComplaintAccept, db: Session = Depends(get_db)):
    complaint = (db.query(Complaints).filter(Complaints.id == complaint_id,Complaints.status == "pending") .first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Complaint not found")
    
    complaint.lawyer_id = data.lawyer_id
    complaint.status = "accepted"

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint accepted successfully"}



@complaint_router.get("/lawyer/{lawyer_id}")
def get_lawyer_complaints(lawyer_id: int,db: Session = Depends(get_db)):
    return (db.query(Complaints).filter(Complaints.lawyer_id == lawyer_id).all() )


@complaint_router.put("/{complaint_id}")
def update_complaint(
complaint_id: int,  data: ComplaintUpdate,db: Session = Depends(get_db)):
    complaint = ( db.query(Complaints).filter(Complaints.id == complaint_id).first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Complaint not found")

    if data.number is not None:
        complaint.number = data.number
    if data.city is not None:
        complaint.city = data.city
    if data.state is not None:
        complaint.state = data.state
    if data.gender is not None:
        complaint.gender = data.gender
    if data.complaint_details is not None:
        complaint.complaint_details = data.complaint_details
    if data.complaint_file_url is not None:
        complaint.complaint_file_url = data.complaint_file_url

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint updated successfully"}



@complaint_router.delete("/{complaint_id}")
def delete_complaint(complaint_id: int,db: Session = Depends(get_db)):
    complaint = (db.query(Complaints).filter(Complaints.id == complaint_id).first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Complaint not found")

    db.delete(complaint)
    db.commit()

    return {"message": "Complaint deleted successfully"}





