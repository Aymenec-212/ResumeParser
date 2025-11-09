# cv_extractor/models/common.py
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    """
    A model to store the exact text snippet from the CV that justifies
    an extraction, providing traceability.
    """
    text_snippet: str = Field(
        description="The exact text from the CV that supports the extraction."
    )
    # context: str | None = Field(
    #     default=None,
    #     description="A slightly larger block of text for context."
    # )