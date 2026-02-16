import re
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from typing import Optional
import cloudinary
import cloudinary.uploader

from sqlalchemy.orm import Session
from dependencies import get_db
from models.lawyers import Lawyers
from schemas.lawyers import LawyerLogin
from auth_utils import verify_password, get_password_hash, create_access_token, get_current_user

lawyerrouter = APIRouter(prefix="/lawyers", tags=["Lawyers"])

# -----------------------------
# TEST ROUTE
# -----------------------------
@lawyerrouter.get("/test")
def lawyer_test():
    return {"status": "lawyer router working"}

# -----------------------------
# LOGIN LAWYER
# -----------------------------
@lawyerrouter.post("/login")
def login_lawyer(credentials: LawyerLogin, db: Session = Depends(get_db)):
    lawyer = db.query(Lawyers).filter(Lawyers.email == credentials.email).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password (using auth_utils wrapper)
    if not verify_password(credentials.password, lawyer.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate Token
    # Important: Distinguish role if needed in token, or just rely on separate endpoints
    access_token = create_access_token(data={"sub": lawyer.email, "role": "lawyer", "id": lawyer.id})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "lawyer_id": lawyer.id,
        "name": lawyer.name,
        "email": lawyer.email,
        "status": lawyer.status
    }

# -----------------------------
# GET SINGLE LAWYER
# -----------------------------
@lawyerrouter.get("/{lawyer_id}")
def get_lawyer(lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("id")
    if int(token_user_id or 0) != int(lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this lawyer profile"
        )
    
    lawyer = db.query(Lawyers).filter(
        Lawyers.id == lawyer_id,
        Lawyers.is_active == True
    ).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")
    return lawyer

# -----------------------------
# GET ALL APPROVED LAWYERS (Public)
# -----------------------------
@lawyerrouter.get("/")
def get_all_lawyers(db: Session = Depends(get_db)):
    # Only return APPROVED lawyers
    return db.query(Lawyers).filter(
        Lawyers.is_active == True,
        Lawyers.status == "approved"
    ).all()

# -----------------------------
# SIGNUP / ADD LAWYER
# -----------------------------
@lawyerrouter.post("/", status_code=status.HTTP_201_CREATED)
def add_lawyer(
    name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    city: str = Form(None),
    state: str = Form(None),
    gender: str = Form(None),
    specialization: str = Form(None),
    years_of_experience: float = Form(...),
    fees_range: str = Form(...),
    password: str = Form(...),
    id_proof: UploadFile = File(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Email check
    if db.query(Lawyers).filter(Lawyers.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Password hash
    hashed_password = get_password_hash(password)

    # Phone validation
    if not re.match(r"^[6-9]\d{9}$", phone_number):
        raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits starting with 6-9")

    # Upload to Cloudinary
    try:
        result_id = cloudinary.uploader.upload(id_proof.file, folder="lawyers/id_proof")
        id_proof_url = result_id["secure_url"]

        result_photo = cloudinary.uploader.upload(photo.file, folder="lawyers/photo")
        photo_url = result_photo["secure_url"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")

    new_lawyer = Lawyers(
        name=name,
        email=email,
        phone_number=phone_number,
        city=city,
        state=state,
        gender=gender,
        specialization=specialization,
        years_of_experience=years_of_experience,
        fees_range=fees_range,
        id_proof_url=id_proof_url,
        photo_url=photo_url,
        password=hashed_password,
        status="pending" # Default status
    )

    db.add(new_lawyer)
    db.commit()
    db.refresh(new_lawyer)

    # Generate Token for Auto-Login
    access_token = create_access_token(data={"sub": new_lawyer.email, "role": "lawyer", "id": new_lawyer.id})

    return {
        "message": "Lawyer registered successfully. Please wait for admin approval.",
        "access_token": access_token,
        "token_type": "bearer",
        "lawyer_id": new_lawyer.id,
        "name": new_lawyer.name,
        "email": new_lawyer.email,
        "status": new_lawyer.status
    }

# -----------------------------
# UPDATE LAWYER
# -----------------------------
@lawyerrouter.put("/{lawyer_id}")
def update_lawyer(
    lawyer_id: int,
    name: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    state: Optional[str] = Form(None),
    specialization: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    fees_range: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    years_of_experience: Optional[float] = Form(None),
    password: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    token_user_id = current_user.get("id")
    if int(token_user_id or 0) != int(lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this lawyer profile"
        )
    
    lawyer = db.query(Lawyers).filter(
        Lawyers.id == lawyer_id,
        Lawyers.is_active == True
    ).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    if name:
        lawyer.name = name
    if city:
        lawyer.city = city
    if state:
        lawyer.state = state
    if specialization:
        lawyer.specialization = specialization
    if gender:
        lawyer.gender = gender
    if fees_range:
        lawyer.fees_range = fees_range
    if phone_number:
        if not re.match(r"^[6-9]\d{9}$", phone_number):
            raise HTTPException(status_code=400, detail="Phone number must be exactly 10 digits starting with 6-9")
        lawyer.phone_number = phone_number
    if years_of_experience is not None:
        lawyer.years_of_experience = years_of_experience
 
    if password:
        lawyer.password = get_password_hash(password)

    if photo:
        result = cloudinary.uploader.upload(
            photo.file,
            folder="lawyers/photo"
        )
        lawyer.photo_url = result["secure_url"]

    db.commit()
    return {"message": "Profile updated successfully"}

# -----------------------------
# DELETE LAWYER (SOFT)
# -----------------------------
@lawyerrouter.delete("/{lawyer_id}")
def delete_lawyer(lawyer_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("id")
    if int(token_user_id or 0) != int(lawyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this lawyer profile"
        )
    
    lawyer = db.query(Lawyers).filter(
        Lawyers.id == lawyer_id,
        Lawyers.is_active == True
    ).first()

    if not lawyer:
        raise HTTPException(status_code=404, detail="Lawyer not found")

    lawyer.is_active = False
    db.commit()
    return {"message": "Lawyer deleted successfully"}
