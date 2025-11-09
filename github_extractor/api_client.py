# github_extractor/api_client.py
import os
import re
import time
import base64
import requests
from dotenv import load_dotenv
from typing import List, Optional

# Import our new Pydantic models
from .models import GitHubProfile, GitHubRepository

# Load environment variables from .env file
load_dotenv()


class GitHubApiClient:
    """
    A client for fetching and processing data from the GitHub API.
    """

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN not found in .env file. Please add it.")

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"

    def _get_user_named_repo_readme(self, username: str) -> Optional[str]:
        """Fetches the content of the user's special profile README."""
        url = f"{self.base_url}/repos/{username}/{username}/readme"
        resp = requests.get(url, headers=self.headers)
        if resp.status_code == 200:
            content = resp.json().get("content")
            if content:
                try:
                    return base64.b64decode(content).decode("utf-8", errors="ignore")
                except (base64.binascii.Error, UnicodeDecodeError):
                    return None
        return None

    def get_profile_data(self, username: str) -> GitHubProfile:
        """
        Collects all GitHub profile data and returns it as a validated
        Pydantic model.
        """
        # 1. Get user data
        user_url = f"{self.base_url}/users/{username}"
        user_resp = requests.get(user_url, headers=self.headers)
        if user_resp.status_code != 200:
            raise Exception(f"GitHub user {username} not found ({user_resp.status_code})")
        user_data = user_resp.json()

        # 2. Get repository data
        repos_url = f"{self.base_url}/users/{username}/repos"
        repos_resp = requests.get(repos_url, headers=self.headers, params={"per_page": 100})
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        # Pydantic will automatically validate this list of dictionaries
        repos_list = [
            {"repo_name": r.get("name"), "repo_description": r.get("description") or ""}
            for r in repos if r.get("name")
        ]

        # 3. Get README content
        readme_content = self._get_user_named_repo_readme(username)

        # 4. Assemble and validate the data using our Pydantic model
        github_profile = GitHubProfile(
            user_id=str(user_data.get("id")),
            username=user_data.get("login"),
            name=user_data.get("name") or user_data.get("login"),
            bio=user_data.get("bio"),
            location=user_data.get("location"),
            email=user_data.get("email"),
            company=user_data.get("company"),
            website=user_data.get("blog"),
            repos=repos_list,
            user_named_repo_readme=readme_content,
        )

        return github_profile


def get_profile_from_github_url(url: str) -> GitHubProfile:
    """
    Parses a GitHub URL to get the username and fetches the profile data.
    This is the main entry point for this module.
    """
    match = re.search(r"github\.com/([\w\-\d]+)", url)
    if not match:
        raise ValueError("Invalid GitHub URL")
    username = match.group(1)

    client = GitHubApiClient()
    return client.get_profile_data(username)