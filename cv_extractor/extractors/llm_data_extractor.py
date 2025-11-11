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
               Your goal is to extract structured information, clean up the skill list, and infer new skills from the work experience.

               **Resume Text:**
               ---
               {cv_text}
               ---

               **Skills found by NLP Tool:**
               {nlp_skill_names}

               **Instructions:**
               1.  **Extract Summary:** Look for a "Summary", "Objective", or "Professional Profile" section at the top of the resume and extract its content. This is the `summary`.
               2.  **Analyze Work Experience:** Read through the resume text and extract the candidate's work history.
               3.  **Infer Skills:** For each job, identify skills from the description (e.g., "developed a REST API" implies "REST API").
               4.  **Verify NLP Skills:** Review the "Skills found by NLP Tool". Remove junk or non-skills.
               5.  **Combine Skills:** The final skill list should include verified NLP skills and inferred skills.
               6.  **Format Output:** Your final output MUST be a valid JSON object that strictly follows this JSON schema:
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