from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.lawyers import LawyerCreate, LawyerUpdate
from models.lawyers import Lawyers

lawyerrouter = APIRouter(
    prefix="/lawyers",
    tags=["Lawyers"]
)

@lawyerrouter.post("/", status_code=status.HTTP_201_CREATED)
def add_lawyer(lawyer: LawyerCreate, db: Session = Depends(get_db)):
    new_lawyer = Lawyers(
        name=lawyer.name,
        email=lawyer.email,
        phone_number=lawyer.phone_number,
        city=lawyer.city,
        specialization=lawyer.specialization,
        years_of_experience=lawyer.years_of_experience,
        fees_range=lawyer.fees_range,
        id_proof_file_url=lawyer.id_proof_file_url,  
        password=lawyer.password
    )

    db.add(new_lawyer)
    db.commit()
    db.refresh(new_lawyer)

    return {
        "message": "Lawyer registered successfully",
        "lawyer_id": new_lawyer.id
    }


@lawyerrouter.get("/")
def get_lawyers(db: Session = Depends(get_db)):
    return db.query(Lawyers).all()

@lawyerrouter.get("/{lawyer_id}")
def get_lawyer(lawyer_id: int,db: Session = Depends(get_db)):
    lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )
    
    return lawyer

@lawyerrouter.put("/{lawyer_id}")
def update_lawyer(lawyer_id: int,lawyer_update: LawyerUpdate,db: Session = Depends(get_db)):
    lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id).first()

    if not lawyer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Lawyer not found")

    if lawyer_update.phone_number is not None:
        lawyer.phone_number = lawyer_update.phone_number
    if lawyer_update.city is not None:
        lawyer.city = lawyer_update.city
    if lawyer_update.specialization is not None:
        lawyer.specialization = lawyer_update.specialization
    if lawyer_update.years_of_experience is not None:
       lawyer.years_of_experience = lawyer_update.years_of_experience
    if lawyer_update.fees_range is not None:
        lawyer.fees_range = lawyer_update.fees_range
    if lawyer_update.id_proof_file_url is not None:
        lawyer.id_proof_file_url = lawyer_update.id_proof_file_url  
    db.commit()
    db.refresh(lawyer)

    return {"message": "Lawyer updated successfully"}



@lawyerrouter.delete("/{lawyer_id}")
def delete_lawyer(lawyer_id: int,db: Session = Depends(get_db)):
    lawyer = db.query(Lawyers).filter(Lawyers.id == lawyer_id ).first()

    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found"
        )

    db.delete(lawyer)
    db.commit()

    return {"message": "Lawyer deleted successfully"}


