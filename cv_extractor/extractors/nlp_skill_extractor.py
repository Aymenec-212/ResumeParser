# cv_extractor/extractors/nlp_skill_extractor.py
import spacy
from spacy.matcher import PhraseMatcher
from typing import List

# Import from SkillNer
from skillNer.skill_extractor_class import SkillExtractor as SkillNerExtractor
from skillNer.general_params import SKILL_DB

# Import our Pydantic models
from cv_extractor.models.cv_models import Skill
from cv_extractor.models.common import Evidence


class NlpSkillExtractor:
    """
    A wrapper for the SkillNer library to extract skills and format them
    into our Pydantic models.
    """

    def __init__(self):
        # Initializes the spaCy model and the SkillNer extractor.
        # This setup can take a moment on first run.
        self.nlp = spacy.load("en_core_web_lg")
        self.skill_extractor = SkillNerExtractor(self.nlp, SKILL_DB, PhraseMatcher)

    def extract(self, text: str) -> List[Skill]:
        """
        Extracts skills from text using SkillNer and maps them to our
        internal Pydantic models with evidence.
        """
        annotations = self.skill_extractor.annotate(text)

        # --- Adapter Logic ---
        # Transforms SkillNer's dictionary output into our Pydantic objects
        extracted_skills = {}

        # Combine full and ngram matches for comprehensive coverage
        all_matches = annotations['results'].get('full_matches', []) + \
                      annotations['results'].get('ngram_scored', [])

        for match in all_matches:
            # SkillNer uses 'skill_id' for a normalized name (e.g., 'KS122Z36QK3N5097B5JH')
            # For readability, we can map this or use the matched value.
            # Let's use the matched text ('doc_node_value') as the skill name for now.
            skill_name = match['doc_node_value'].lower()
            evidence_text = match['doc_node_value']

            evidence = Evidence(text_snippet=evidence_text)

            if skill_name not in extracted_skills:
                extracted_skills[skill_name] = Skill(name=skill_name, evidence=[])

            extracted_skills[skill_name].evidence.append(evidence)

        return list(extracted_skills.values())