from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.db.database import get_db
from app.db import models, crud
from app.core import security

router = APIRouter()

class MentorCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: Optional[int] = None
    bio: Optional[str] = None
    license_number: Optional[str] = None
    admin_secret: Optional[str] = None # Secret key required to register as admin

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=Token)
def register_mentor(mentor_in: MentorCreate, db: Session = Depends(get_db)):
    """Creates a new Mentor account in the SQL database. Requires approval."""
    user = crud.get_mentor_by_email(db, email=mentor_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Super simple "secret" to allow the first user to become an admin
    # Admins are auto-approved
    is_admin = (mentor_in.admin_secret == "supersecretjootrh")
    is_approved = is_admin 
    
    hashed_password = security.get_password_hash(mentor_in.password)
    new_mentor = models.Mentor(
        email=mentor_in.email, 
        hashed_password=hashed_password, 
        name=mentor_in.name,
        phone_number=mentor_in.phone_number,
        specialization=mentor_in.specialization,
        experience_years=mentor_in.experience_years,
        bio=mentor_in.bio,
        license_number=mentor_in.license_number,
        is_approved=is_approved,
        is_admin=is_admin
    )
    
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    
    # We DON'T auto-login if they aren't approved yet
    if not is_approved:
        # Return a special "Success but pending" response or just raise a 201 with message
        # But we'll follow the token schema to keep it simple, just return an empty token or error
        raise HTTPException(
            status_code=201, 
            detail="Account created successfully. Your profile is now under review by our administration. We will contact you shortly."
        )
        
    access_token = security.create_access_token(data={"sub": new_mentor.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticates a mentor and returns a JWT Bearer token."""
    user = crud.get_mentor_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is currently pending administrative review. Please try again later."
        )

    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_mentor: models.Mentor = Depends(security.get_current_mentor)):
    """Returns details of the currently authenticated mentor for the frontend."""
    return {"name": current_mentor.name, "email": current_mentor.email, "is_admin": current_mentor.is_admin}
