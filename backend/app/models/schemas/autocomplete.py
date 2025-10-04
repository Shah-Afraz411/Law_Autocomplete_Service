from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from ..enums.language_code import LanguageCode

class AutocompleteRequest(BaseModel):
    input: str = Field(..., min_length=1, description="User's free-text input")
    max_predictions: int = Field(5, ge=1, le=20, description="Max completions to return")
    categories: Optional[List[str]] = Field(None, description="Optional category filters")
    output_language: Optional[str] = Field(
        None,
        description="ISO 639-1 code of target language (default fallback 'en')",
    )

    @field_validator("input")
    @classmethod
    def validate_input(cls, v: str):
        if not v or not v.strip():
            raise ValueError("input must be a non-empty, non-whitespace string.")
        return v.strip()

    @field_validator("output_language")
    @classmethod
    def validate_output_language(cls, v: Optional[str]):
        if v is None:
            return v
        v = v.lower()
        valid = [c.value for c in LanguageCode]
        if v not in valid:
            raise ValueError(f"output_language must be one of: {valid}")
        return v

class Suggestion(BaseModel):
    text: str = Field(..., description="One autocomplete suggestion (includes original input)")
    category: Optional[str] = Field(None, description="Matched category")

class SuggestionList(BaseModel):
    suggestions: List[Suggestion]
    