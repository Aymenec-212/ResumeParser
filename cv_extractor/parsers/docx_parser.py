# cv_extractor/parsers/docx_parser.py
import docx
from .base_parser import BaseParser

class DocxParser(BaseParser):
    """Parses plain text from DOCX files."""
    def get_text(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
