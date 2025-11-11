# app/api/auth.py (Definitively Corrected)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
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

    # 2. Hash the password using the corrected security utility
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

    # The password passed to verify_password should also be truncated for consistency,
    # though verify handles this more gracefully. Let's make it explicit.
    password_to_check = form_data.password[:72]

    if not user or not security.verify_password(password_to_check, user.hashed_password):
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