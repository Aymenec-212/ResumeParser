# github_extractor/models.py
from typing import List, Optional
from pydantic import BaseModel, Field


class GitHubRepository(BaseModel):
    """
    Represents a single GitHub repository.
    """
    repo_name: str
    repo_description: str = Field(default="")


class GitHubProfile(BaseModel):
    """
    A validated data model for a user's GitHub profile, combining
    user info, repositories, and other relevant metadata.
    """
    platform: str = "github"
    user_id: str
    username: str
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None

    # Nested Pydantic model for repositories
    repos: List[GitHubRepository] = []

    # Optional field for the special profile README
    user_named_repo_readme: Optional[str] = None