# github_extractor/models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class GitHubRepository(BaseModel):
    # ... (no changes here)
    repo_name: str
    repo_description: str = Field(default="")


# --- NEW MODELS for Parsed README Content ---
class ReadmeProject(BaseModel):
    """A project explicitly described in the GitHub README."""
    project_name: str
    description: str
    technologies: List[str] = Field(default=[])


class ParsedReadme(BaseModel):
    """Holds the structured data extracted from the user's profile README."""
    summary: Optional[str] = Field(default=None, description="A concise summary or bio extracted from the README.")
    tech_stack: List[str] = Field(default=[], description="A list of key technologies or skills mentioned.")
    projects: List[ReadmeProject] = Field(default=[])


# --- UPDATE the main GitHubProfile model ---
class GitHubProfile(BaseModel):
    """
    The main validated data model for a user's GitHub profile.
    """
    # ... (existing fields like user_id, username, repos, etc.)
    platform: str = "github"
    user_id: str
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    repos: List[GitHubRepository] = []
    user_named_repo_readme: Optional[str] = None  # We keep the raw text for reference

    # --- ADDED FIELD ---
    # This will hold the structured data extracted by the LLM from the README.
    parsed_readme: Optional[ParsedReadme] = Field(default=None)