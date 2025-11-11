# app/core/security.py
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt, JWTError # Keep jose for JWT
from .config import settings


# OAuth2 scheme for FastAPI to know how to get the token (e.g., from an "Authorization: Bearer <token>" header)
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed one using bcrypt.
    Ensures the plain password is truncated to 72 bytes before comparison,
    symmetrically matching the hashing logic.
    """
    plain_password_bytes = plain_password.encode('utf-8')
    # --- FIX: Explicitly truncate the input password ---
    truncated_password_bytes = plain_password_bytes[:72]

    hashed_password_bytes = hashed_password.encode('utf-8')

    # Compare the truncated input against the stored hash
    return bcrypt.checkpw(truncated_password_bytes, hashed_password_bytes)


# --- NEW: Adjusting for direct bcrypt usage ---
def get_password_hash(password: str) -> str:
    """
    Hashes a plain password using bcrypt.
    Ensures truncation to 72 bytes for compatibility.
    """
    # Encode the string to bytes
    password_bytes = password.encode('utf-8')
    # Truncate to 72 bytes as required by bcrypt
    truncated_password_bytes = password_bytes[:72]
    # Hash the bytes
    hashed_bytes = bcrypt.hashpw(truncated_password_bytes, bcrypt.gensalt())
    # Decode the resulting hash back to a string for storage
    return hashed_bytes.decode('utf-8')


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Creates a JWT access token.
    'subject' is the data to encode in the token (e.g., user's email or ID).
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt