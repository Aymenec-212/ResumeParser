# cv_extractor/pipeline.py
from .models.cv_models import ExtractedCV
from .parsers.factory import get_parser
# from .extractors.nlp_skill_extractor import NlpSkillExtractor
from .extractors.hybrid_manager import HybridManager # Import the new manager



def extract_cv_data(file_path: str) -> ExtractedCV:
    """
    The main orchestration function.

    1. Selects the correct parser for the file type.
    2. Extracts the full text from the file.
    3. Uses the NLP extractor to find skills with evidence.
    4. Populates and returns a structured ExtractedCV object.

    Args:
        file_path (str): The path to the CV file (PDF or DOCX).

    Returns:
        ExtractedCV: A Pydantic model containing the extracted data.
    """
    print("1. Parsing document...")
    parser = get_parser(file_path)
    full_text = parser.get_text(file_path)

    # The manager now handles the entire extraction process
    manager = HybridManager()
    cv_data = manager.extract(full_text)

    print("3. Finalizing structured output...")
    return cv_data