# cv_extractor/extractors/hybrid_manager.py
from .nlp_skill_extractor import NlpSkillExtractor
from .llm_data_extractor import LlmDataExtractor
from ..models.cv_models import ExtractedCV, Skill


class HybridManager:
    def __init__(self):
        self.nlp_extractor = NlpSkillExtractor()
        self.llm_extractor = LlmDataExtractor()

    def extract(self, text: str) -> ExtractedCV:
        print("2a. Running NLP skill extraction...")
        nlp_skills = self.nlp_extractor.extract(text)

        nlp_evidence_map = {skill.name: skill.evidence for skill in nlp_skills}

        print("2b. Running LLM for verification and contextual extraction...")
        llm_output = self.llm_extractor.extract(text, nlp_skills)

        final_skills = []
        if llm_output.get("skills"):
            llm_skill_names = [s.get("name").lower() for s in llm_output["skills"] if s.get("name")]

            for skill_name in set(llm_skill_names):
                evidence = nlp_evidence_map.get(skill_name, [])
                final_skills.append(Skill(name=skill_name, evidence=evidence))

        # --- UPDATE THIS BLOCK ---
        final_cv_data = ExtractedCV(
            full_text=text,
            summary=llm_output.get("summary"), # <-- Add this line to pass the summary
            skills=final_skills,
            work_experience=llm_output.get("work_experience", []),
            projects=llm_output.get("projects", [])
        )

        return final_cv_data