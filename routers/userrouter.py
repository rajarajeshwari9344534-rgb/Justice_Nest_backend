from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import get_db
from schemas.user import UserCreate, UserUpdate, UserLogin
from models.user import User
from auth_utils import verify_password, get_password_hash, create_access_token, get_current_user

user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# -------------------------
# SIGNUP
# -------------------------
@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash the password
        hashed_password = get_password_hash(user.password)

        new_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate JWT Token for Auto-Login
        access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id, "role": "user"})

        return {
            "message": "User registered successfully",
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
    except Exception as e:
        print(f"SIGNUP ERROR: {str(e)}")
        # If it's already an HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# -------------------------
# LOGIN
# -------------------------
@user_router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify hashed password
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT Token
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id, "role": "user"})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "name": user.name
    }

# -------------------------
# GET SINGLE USER
# -------------------------
@user_router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    if int(token_user_id or 0) != int(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

# -------------------------
# UPDATE USER
# -------------------------
@user_router.put("/{user_id}")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    if int(token_user_id or 0) != int(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.name = user_update.name
    user.email = user_update.email

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}

# -------------------------
# DELETE USER
# -------------------------
@user_router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    token_user_id = current_user.get("user_id") or current_user.get("id")
    if int(token_user_id or 0) != int(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
