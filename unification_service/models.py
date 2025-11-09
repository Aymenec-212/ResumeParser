# unification_service/models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class UnifiedContactInfo(BaseModel):
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    website: Optional[str] = None


class UnifiedWorkExperience(BaseModel):
    job_title: str
    company_name: str
    description: Optional[str] = None
    # Add other fields like dates later if needed


class UnifiedProject(BaseModel):
    project_name: str
    description: Optional[str] = None
    source: str  # e.g., "CV", "GitHub", "LinkedIn"


class UnifiedProfile(BaseModel):
    """
    The "Golden Record". A single, coherent profile created by merging data
    from multiple sources like CV, LinkedIn, and GitHub.
    """
    profile_id: str = Field(description="The unique ID for this unified profile.")

    contact_info: UnifiedContactInfo
    full_name: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None

    skills: List[str] = Field(default=[], description="A de-duplicated list of all skills.")
    work_experience: List[UnifiedWorkExperience] = Field(default=[])
    projects: List[UnifiedProject] = Field(default=[])

    # Store the original data for reference and debugging
    source_data: dict = Field(default={}, description="Raw JSON from the original sources.")