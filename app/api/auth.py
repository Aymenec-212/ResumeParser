# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
# --- CORRECTED IMPORT ---
from app.core import security # Use the corrected security functions
# --- remove passlib import if it was there ---
# from passlib.context import CryptContext # Remove this
from app.core.db import get_db
from app.models.user import User
from app.schemas import user as user_schema

router = APIRouter()


@router.post("/register", response_model=user_schema.UserPublic)
def register_user(
        *,
        db: Session = Depends(get_db),
        user_in: user_schema.UserCreate
):
    """
    Create a new user with robust database handling.
    """
    # 1. Check for existing user
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists in the system.",
        )

    # --- Corrected Call ---
    # This now calls the function that correctly handles hashing and truncation
    hashed_password = security.get_password_hash(user_in.password)

    # 3. Create the SQLAlchemy model instance
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_password
    )

    # 4. Use a try/except block for robust database transaction
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()  # Roll back the transaction in case of an error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error occurred: {e}",
        )

    return db_user


@router.post("/token", response_model=user_schema.Token)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(User).filter(User.email == form_data.username).first()

    # --- Corrected Call for Verification ---
    # Ensure consistency by passing the string directly, verify handles truncation.
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }