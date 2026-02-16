import re
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
import cloudinary.uploader
from dependencies import get_db
from auth_utils import get_current_user
from models.complaint import Complaints
from schemas.complaint import ComplaintUpdate, ComplaintAccept

complaint_router = APIRouter(
    prefix="/complaints",
    tags=["Complaints"]
)


@complaint_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_complaint(
    user_id: int = Form(...),
    name: str = Form(...),
    number: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    gender: str = Form(...),
    complaint_details: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # ensure the caller is the same user as the form `user_id`
    token_user_id = current_user.get("user_id") or current_user.get("id")
    if token_user_id is None or int(token_user_id) != int(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted for this user")
    if not re.match(r"^[6-9]\d{9}$", number):
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits starting with 6-9")
    
    file_url = None
    if file:
        try:
            upload_result = cloudinary.uploader.upload(file.file)
            file_url = upload_result.get("secure_url")
        except Exception as e:
            print(f"CLOUDINARY UPLOAD ERROR: {e}")

    complaint = Complaints(
        user_id=user_id,
        name=name,
        number=number,
        city=city,
        state=state,
        gender=gender,
        complaint_details=complaint_details,
        complaint_file_url=file_url
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return {
        "message": "Complaint created successfully",
        "complaint_id": complaint.id
    }



@complaint_router.get("/user/{user_id}")
def get_user_complaints(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    if int(token_user_id or 0) != int(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these complaints"
        )
    
    from models.lawyers import Lawyers
    
    results = (
        db.query(Complaints, Lawyers.name.label("lawyer_name"), Lawyers.phone_number.label("lawyer_phone"))
        .outerjoin(Lawyers, Complaints.lawyer_id == Lawyers.id)
        .filter(Complaints.user_id == user_id)
        .all()
    )
    
    complaints = []
    for complaint, lawyer_name, lawyer_phone in results:
        c_dict = {column.name: getattr(complaint, column.name) for column in complaint.__table__.columns}
        c_dict["lawyer_name"] = lawyer_name
        c_dict["lawyer_phone"] = lawyer_phone
        complaints.append(c_dict)
        
    return complaints


@complaint_router.get("/pending")
def get_pending_complaints(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") not in ["admin", "lawyer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and lawyers can view pending complaints"
        )
    return (db.query(Complaints).filter(Complaints.status == "pending") .all())


@complaint_router.put("/{complaint_id}/accept")
def accept_complaint(complaint_id: int, data: ComplaintAccept, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Verify lawyer status first
    from models.lawyers import Lawyers
    # only the lawyer who is accepting (and approved) may accept
    if current_user.get("role") != "lawyer" or int(current_user.get("id") or 0) != int(data.lawyer_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned lawyer may accept this complaint")

    lawyer = db.query(Lawyers).filter(Lawyers.id == data.lawyer_id).first()

    if not lawyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lawyer not found")

    if lawyer.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is pending approval. You cannot accept cases yet."
        )

    complaint = (db.query(Complaints).filter(Complaints.id == complaint_id).first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    complaint.lawyer_id = data.lawyer_id
    complaint.status = "accepted"

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint accepted successfully"}



@complaint_router.get("/lawyer/{lawyer_id}")
def get_lawyer_complaints(lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("id")
    if int(token_user_id or 0) != int(lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these complaints"
        )
    return (db.query(Complaints).filter(Complaints.lawyer_id == lawyer_id).all() )


@complaint_router.put("/{complaint_id}")
async def update_complaint(
    complaint_id: int,
    number: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    complaint_details: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    complaint = (db.query(Complaints).filter(Complaints.id == complaint_id).first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    # permission: owner user or assigned lawyer may update
    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    if int(token_user_id or 0) != int(complaint.user_id) and not (token_role == "lawyer" and int(token_user_id or 0) == int(complaint.lawyer_id or 0)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this complaint")

    if number is not None:
        if not re.match(r"^[6-9]\d{9}$", number):
            raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits starting with 6-9")
        complaint.number = number
    if city is not None:
        complaint.city = city
    if state is not None:
        complaint.state = state
    if gender is not None:
        complaint.gender = gender
    if complaint_details is not None:
        complaint.complaint_details = complaint_details
    if status is not None:
        complaint.status = status

    if file:
        try:
            upload_result = cloudinary.uploader.upload(file.file)
            complaint.complaint_file_url = upload_result.get("secure_url")
        except Exception as e:
            print(f"CLOUDINARY UPDATE ERROR: {e}")

    db.commit()
    db.refresh(complaint)

    return {"message": "Complaint updated successfully"}



@complaint_router.delete("/{complaint_id}")
def delete_complaint(complaint_id: int,db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    complaint = (db.query(Complaints).filter(Complaints.id == complaint_id).first())

    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Complaint not found")

    token_user_id = current_user.get("user_id") or current_user.get("id")
    token_role = current_user.get("role")
    if int(token_user_id or 0) != int(complaint.user_id) and not (token_role == "lawyer" and int(token_user_id or 0) == int(complaint.lawyer_id or 0)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this complaint")

    db.delete(complaint)
    db.commit()

    return {"message": "Complaint deleted successfully"}





