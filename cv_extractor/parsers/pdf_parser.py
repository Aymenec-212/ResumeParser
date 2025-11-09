# cv_extractor/parsers/pdf_parser.py
import fitz  # PyMuPDF
from .base_parser import BaseParser

class PdfParser(BaseParser):
    """Parses plain text from PDF files."""
    def get_text(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text