# unification_service/unifier.py
from .models import UnifiedProfile, UnifiedWorkExperience, UnifiedProject, UnifiedContactInfo
from cv_extractor.models.cv_models import ExtractedCV
from linkedin_extractor.models import LinkedInProfile
from github_extractor.models import GitHubProfile
from typing import Union, List


class ProfileUnifier:
    """
    A service to merge data from various sources into a single, unified profile.
    """

    def unify(self, profile_id: str,
              *sources: List[Union[ExtractedCV, LinkedInProfile, GitHubProfile]]) -> UnifiedProfile:
        """
        Takes multiple data source objects and merges them into a UnifiedProfile.
        """
        all_skills = set()
        all_work_experience = []
        all_projects = []
        source_data = {}

        # --- Prioritized fields ---
        # We prioritize sources for single-value fields (e.g., name from LinkedIn > CV)
        full_name, summary, location = None, None, None
        contact_info = {"email": None, "linkedin_url": None, "github_url": None, "website": None}

        for source in sources:
            if isinstance(source, LinkedInProfile):
                source_data['linkedin'] = source.model_dump()
                full_name = source.fullName or full_name
                summary = source.summary or summary
                location = source.location or location
                contact_info['linkedin_url'] = source.profileUrl

                for skill in source.skills:
                    if skill.name: all_skills.add(skill.name.lower())
                for pos in source.positions:
                    all_work_experience.append(
                        {"company_name": pos.companyName, "job_title": pos.title, "description": pos.description})
                for proj in source.projects:
                    all_projects.append(
                        {"project_name": proj.title, "description": proj.description, "source": "LinkedIn"})

            elif isinstance(source, ExtractedCV):
                source_data['cv'] = source.model_dump()
                summary = summary or source.summary  # Use CV summary if LinkedIn's is missing
                for skill in source.skills:
                    all_skills.add(skill.name.lower())
                for exp in source.work_experience:
                    all_work_experience.append(
                        {"company_name": exp.company, "job_title": exp.job_title, "description": exp.description})
                for proj in source.projects:
                    all_projects.append(
                        {"project_name": proj.project_name, "description": proj.description, "source": "CV"})

            elif isinstance(source, GitHubProfile):
                source_data['github'] = source.model_dump()
                full_name = full_name or source.name
                summary = summary or source.bio
                location = location or source.location
                contact_info['github_url'] = f"https://github.com/{source.username}"
                contact_info['website'] = source.website
                contact_info['email'] = source.email
                for repo in source.repos:
                    all_projects.append(
                        {"project_name": repo.repo_name, "description": repo.repo_description, "source": "GitHub"})

        # --- De-duplication Logic (Simple version for PoC) ---
        unique_work_experience = {(exp['company_name'], exp['job_title']): exp for exp in all_work_experience}.values()

        # --- Assemble the UnifiedProfile ---
        unified_profile = UnifiedProfile(
            profile_id=profile_id,
            full_name=full_name,
            summary=summary,
            location=location,
            contact_info=UnifiedContactInfo(**contact_info),
            skills=sorted(list(all_skills)),
            work_experience=[UnifiedWorkExperience(**exp) for exp in unique_work_experience],
            projects=[UnifiedProject(**proj) for proj in all_projects],
            source_data=source_data
        )
        return unified_profile