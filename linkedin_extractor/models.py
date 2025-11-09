# linkedin_extractor/models.py
from typing import List, Optional, Any
from pydantic import BaseModel, Field

# Nested models for complex fields

class LinkedInSkill(BaseModel):
    name: Optional[str] = None

class LinkedInEducation(BaseModel):
    schoolName: Optional[str] = None
    degreeName: Optional[str] = None
    fieldOfStudy: Optional[str] = None
    # Add other fields as needed, e.g., startDate, endDate

class LinkedInProject(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    # Add other fields as needed, e.g., url

class LinkedInPosition(BaseModel):
    title: Optional[str] = None
    companyName: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    # Add other fields as needed, e.g., startDate, endDate

# The main root model for a LinkedIn profile

class LinkedInProfile(BaseModel):
    """
    A validated data model for a user's LinkedIn profile.
    """
    platform: str = "linkedin"
    fullName: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    profileUrl: Optional[str] = None
    profilePicture: Optional[str] = None

    skills: List[LinkedInSkill] = Field(default=[])
    education: List[LinkedInEducation] = Field(default=[])
    projects: List[LinkedInProject] = Field(default=[])
    positions: List[LinkedInPosition] = Field(default=[])

    # A field to store the original, unstructured data for flexibility
    raw_data: Optional[Any] = None