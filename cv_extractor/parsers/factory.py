# cv_extractor/parsers/factory.py
import os
from typing import Type
from .base_parser import BaseParser
from .pdf_parser import PdfParser
from .docx_parser import DocxParser


def get_parser(file_path: str) -> BaseParser:
    """
    Factory function to get the correct parser based on file extension.
    """
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == ".pdf":
        return PdfParser()
    elif extension == ".docx":
        return DocxParser()
    else:
        raise ValueError(f"Unsupported file type: {extension}")