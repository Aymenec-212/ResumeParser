# github_extractor/api_client.py
import os
import re
import json
import base64
import requests
from dotenv import load_dotenv
from typing import Optional

# --- NEW: Import OpenAI and config ---
from openai import OpenAI
from cv_extractor.config import OPENAI_API_KEY

# Import our updated Pydantic models
from .models import GitHubProfile, GitHubRepository, ParsedReadme

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

        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_token}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"

        # --- NEW: The LLM README Parser Method ---
    def _parse_readme_with_llm(self, readme_content: str) -> Optional[ParsedReadme]:
            """
            Uses an LLM to parse unstructured README text into a structured
            ParsedReadme Pydantic model.
            """
            if not readme_content:
                return None

            output_schema = ParsedReadme.model_json_schema()

            prompt = f"""
            You are a highly intelligent data extraction bot. Your task is to analyze the following GitHub profile README markdown text and extract structured information.

            **README Content:**
            ---
            {readme_content}
            ---

            **Instructions:**
            1.  Analyze the text to identify the user's primary tech stack, personal projects, and a brief summary of their professional focus.
            2.  Do NOT invent any information. Only extract what is explicitly mentioned or clearly implied in the text.
            3.  For projects, extract the name, a description, and any mentioned technologies.
            4.  Your output MUST be a valid JSON object that strictly adheres to the following JSON Schema. Do not add any commentary.

            **JSON Schema:**
            {json.dumps(output_schema, indent=2)}
            """

            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system",
                         "content": "You are a data extractor that only outputs JSON conforming to a provided schema."},
                        {"role": "user", "content": prompt}
                    ]
                )
                parsed_data = json.loads(response.choices[0].message.content)
                # Validate the LLM's output against our Pydantic model
                return ParsedReadme(**parsed_data)
            except Exception as e:
                print(f"Error parsing GitHub README with LLM: {e}")
                return None  # Fail gracefully

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
        user_data = requests.get(f"{self.base_url}/users/{username}", headers=self.headers).json()

        # 2. Get repository data
        repos_url = f"{self.base_url}/users/{username}/repos"
        repos_resp = requests.get(repos_url, headers=self.headers, params={"per_page": 100})
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        # Pydantic will automatically validate this list of dictionaries
        repos_list = requests.get(f"{self.base_url}/users/{username}/repos", headers=self.headers).json()

        # 3. Get raw README content
        readme_content = self._get_user_named_repo_readme(username)

        # 4. Parse it with the LLM if it exists
        parsed_readme_data = self._parse_readme_with_llm(readme_content)

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
            repos=[{"repo_name": r.get("name"), "repo_description": r.get("description") or ""} for r in repos_list if r.get("name")],
            user_named_repo_readme=readme_content,
            parsed_readme=parsed_readme_data,
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