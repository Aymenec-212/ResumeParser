# app/main.py
from fastapi import FastAPI
# We will create and import the routers later
# from app.api import auth, profiles
from app.core.config import settings

from app.core.db import Base, engine # Import Base and engine

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(
    title="AI Profile Enhancer API",
    description="An API to extract, unify, and enhance professional profiles.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- Placeholder for future routers ---
# app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
# app.include_router(profiles.router, prefix=f"{settings.API_V1_STR}/profiles", tags=["Profiles"])


@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the AI Profile Enhancer API"}