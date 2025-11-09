# cv_extractor/models/cv_models.py
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import Evidence

class Skill(BaseModel):
    name: str = Field(description="The normalized name of the skill.")
    evidence: List[Evidence] = Field(
        description="A list of text snippets from the CV that mention this skill."
    )

class WorkExperience(BaseModel):
    job_title: str
    company: str
    description: Optional[str] = None
    inferred_skills: List[str] = Field(
        default=[],
        description="Skills inferred by the LLM from the job description."
    )

# --- NEW MODEL ---
class Project(BaseModel):
    """
    Represents a project extracted from the CV.
    """
    project_name: str = Field(description="The name or title of the project.")
    description: Optional[str] = None
    inferred_skills: List[str] = Field(
        default=[],
        description="Skills inferred by the LLM from the project description."
    )

class ExtractedCV(BaseModel):
    """
    The root model representing all structured data extracted from a CV.
    """
    full_text: str = Field(description="The complete raw text extracted from the document.")
    skills: List[Skill] = Field(description="A list of all skills identified in the CV.")
    work_experience: List[WorkExperience] = Field(default=[])
    # --- ADDED FIELD ---
    projects: List[Project] = Field(default=[])