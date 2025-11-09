# cv_extractor/parsers/base_parser.py
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Abstract base class for all file parsers."""
    @abstractmethod
    def get_text(self, file_path: str) -> str:
        """Extracts plain text from a given file."""
        pass