# enhancement_service/enhancer.py
import json
from openai import OpenAI
from unification_service.models import UnifiedProfile
from cv_extractor.config import OPENAI_API_KEY  # Re-use the existing config


class ProfileEnhancer:
    """
    Uses an LLM to refine and enhance a unified profile, focusing on
    consistency, coherence, and professional presentation.
    """

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def enhance(self, profile: UnifiedProfile) -> UnifiedProfile:
        """
        Takes a UnifiedProfile object, sends it to an LLM for refinement,
        and returns the enhanced UnifiedProfile.
        """
        profile_json = profile.model_dump_json(indent=2)
        output_schema_json = UnifiedProfile.model_json_schema(by_alias=False)

        # This prompt is the most critical part of this service.
        # It strictly instructs the LLM to edit, not invent.
        prompt = f"""
        You are a world-class professional resume editor and career coach.
        Your task is to refine the following unified profile data, which has been aggregated from multiple sources (CV, LinkedIn, GitHub).

        **CRITICAL INSTRUCTIONS:**
        1.  **DO NOT ADD NEW INFORMATION:** You must not invent any new skills, experiences, projects, or details. Your sole purpose is to improve the presentation of the EXISTING data.
        2.  **CREATE A PROFESSIONAL SUMMARY:** Write a concise, powerful professional summary (2-4 sentences) that synthesizes the candidate's key strengths based *only* on the provided skills, experience, and projects.
        3.  **REFINE WORK EXPERIENCE:** For each job, rewrite the description to be more professional and action-oriented. Use clear, impactful language. If descriptions are messy, structure them into bullet points starting with action verbs.
        4.  **STANDARDIZE SKILLS:** Review the skill list. Correct capitalization (e.g., "python" -> "Python", "javascript" -> "JavaScript"). Ensure consistency.
        5.  **ENSURE COHERENCE:** Make sure the entire profile reads like a single, coherent document, not a patchwork of different sources.

        **Unified Profile Data to Refine:**
        ---
        {profile_json}
        ---

        Your final output MUST be a valid JSON object that strictly follows this JSON schema. Do not add any extra text or explanations.

        **Output Schema:**
        {json.dumps(output_schema_json, indent=2)}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a resume editor that outputs perfectly structured JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        try:
            enhanced_data = json.loads(response.choices[0].message.content)
            # Validate the LLM's output by creating a new UnifiedProfile object.
            # This ensures the data structure is correct before returning.
            return UnifiedProfile(**enhanced_data)
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error parsing LLM response for enhancement: {e}")
            # In case of an error, return the original profile to prevent data loss.
            return profile