# app/main.py
from fastapi import FastAPI
# from app.api import auth, profiles
from app.core.config import settings
from app.core import security # Ensure this import is present and correct

from app.core.db import Base, engine # Import Base and engine
from app.api import auth # <-- Import the new auth router


# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(
    title="AI Profile Enhancer API",
    description="An API to extract, unify, and enhance professional profiles.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# --- Include the new authentication router ---
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
# We will add the profiles router in the next step
# app.include_router(profiles.router, prefix=f"{settings.API_V1_STR}/profiles", tags=["Profiles"])

# --- Placeholder for future routers ---
# app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
# app.include_router(profiles.router, prefix=f"{settings.API_V1_STR}/profiles", tags=["Profiles"])


@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the AI Profile Enhancer API"}