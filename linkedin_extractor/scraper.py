# linkedin_extractor/scraper.py
import os
import requests
from dotenv import load_dotenv

# Import our new Pydantic model
from .models import LinkedInProfile

# Load environment variables from .env file
load_dotenv()


class LinkedInScraperClient:
    """
    A client for fetching LinkedIn data via the Scrapetable API.
    """

    def __init__(self):
        self.api_key = os.getenv("SCRAPETABLE_API_KEY")
        if not self.api_key:
            raise ValueError("SCRAPETABLE_API_KEY not found in .env file.")

        self.api_url = "https://v3.scrapetable.com/linkedin/people"
        self.headers = {"Content-Type": "application/json"}

    def get_profile_data(self, profile_url: str) -> LinkedInProfile:
        """
        Fetches LinkedIn profile data and returns it as a validated
        Pydantic model.
        """
        if not profile_url or "linkedin.com/in/" not in profile_url:
            raise ValueError("Invalid or missing LinkedIn profile URL")

        params = {"key": self.api_key, "profileUrl": profile_url}

        # Make API call
        response = requests.get(self.api_url, params=params, headers=self.headers, timeout=60)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        if not data.get("success"):
            raise Exception(f"Scrapetable API returned an error: {data}")

        person_data = data.get("person", {})

        # Assemble and validate the data using our Pydantic model
        # Pydantic will automatically handle the nested lists of objects.
        profile = LinkedInProfile(
            fullName=person_data.get("fullName"),
            headline=person_data.get("headline"),
            summary=person_data.get("summary"),
            location=person_data.get("geoFull"),  # Mapping 'geoFull' to 'location'
            skills=person_data.get("skills", []),
            education=person_data.get("education", []),
            projects=person_data.get("projects", []),
            positions=person_data.get("positions", []),
            profileUrl=person_data.get("profileUrl") or profile_url,
            profilePicture=person_data.get("profilePicture"),
            raw_data=person_data,
        )

        return profile


def collect_profile_from_linkedin_url(url: str) -> LinkedInProfile:
    """
    Parses a LinkedIn URL and fetches the profile data.
    This is the main public entry point for this module.
    """
    client = LinkedInScraperClient()
    return client.get_profile_data(url)