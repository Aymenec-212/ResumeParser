# cv_extractor/extractors/llm_data_extractor.py
import json
from openai import OpenAI
from ..config import OPENAI_API_KEY
from ..models.cv_models import ExtractedCV


class LlmDataExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def extract(self, cv_text: str, nlp_skills: list) -> dict:
        nlp_skill_names = [skill.name for skill in nlp_skills]
        output_schema = ExtractedCV.model_json_schema()

        # --- UPDATED PROMPT ---
        prompt = f"""
        You are an expert HR recruitment assistant. Your task is to analyze the following resume text and a list of skills found by an NLP tool.
        Your goal is to extract structured information, clean up the skill list, and infer new skills from work experience and projects.

        **Resume Text:**
        ---
        {cv_text}
        ---

        **Skills found by NLP Tool:**
        {nlp_skill_names}

        **Instructions:**
        1.  **Analyze Work Experience:** Read through the resume text and extract the candidate's work history. For each role, infer skills from the description (e.g., "developed a REST API" implies "REST API").
        2.  **Analyze Projects:** Look for a "Projects" section. For each project, extract its name, description, and infer relevant technologies or skills mentioned in its description.
        3.  **Verify NLP Skills:** Review the "Skills found by NLP Tool". Remove any junk, typos, or non-skills (e.g., 'com', 'and', 'experience'). The final skill list should be clean and professional.
        4.  **Combine All Skills:** The final list of skills should include the verified NLP skills AND all skills you inferred from BOTH work experience and projects. Ensure there are no duplicates.
        5.  **Format Output:** Your final output MUST be a valid JSON object that strictly follows this JSON schema. Do not add any extra text or explanations outside of the JSON object.
        Schema:
        {json.dumps(output_schema, indent=2)}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system",
                 "content": "You are an expert HR assistant outputting JSON according to the provided schema."},
                {"role": "user", "content": prompt}
            ]
        )

        try:
            return json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, IndexError):
            return {}