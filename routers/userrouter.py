from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.user import UserCreate, UserUpdate
from models.user import User

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate,db: Session = Depends(get_db)):
    new_user = User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }

@user_router.get("/{user_id}")
def get_user( user_id: int,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@user_router.put("/{user_id}")
def update_user(user_id: int,user_update: UserUpdate,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")

    user.name = user_update.name
    user.email = user_update.email

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}


@user_router.delete("/{user_id}")
def delete_user(
    user_id: int,db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
