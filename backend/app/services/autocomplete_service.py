import re
from typing import List, Optional, ClassVar
from uuid import UUID
from fastapi import HTTPException, status
from ..models.enums.language_code import LanguageCode
from ..models.schemas.autocomplete import Suggestion, SuggestionList
from ..prompts.autocomplete import build_prompt
from ..api.dependencies.logger import get_logger
from ..core.config import get_settings

try:
    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class AutocompleteService:
    """
    Singleton-style service responsible for generating autocomplete suggestions.
    """

    _instance: ClassVar[Optional["AutocompleteService"]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()
        self.model = None
        self.user_id: Optional[UUID] = None
        self._init_model()

        # Example in-memory categories (replace with DB fetch)
        self._all_categories = [
            "Consumer Rights",
            "Contract Law",
            "Family Law",
            "Immigration",
            "Property Law",
            "Administrative Law",
            "Criminal Law"
        ]

    def _init_model(self):
        if self.settings.vertex_enabled():
            if not LANGCHAIN_AVAILABLE:
                self.logger.warning("LangChain/Vertex dependencies not installed. Falling back to mock.")
                return
            try:
                self.model = ChatVertexAI(
                    model=self.settings.VERTEX_MODEL_NAME,
                    project=self.settings.VERTEX_PROJECT,
                    location=self.settings.VERTEX_LOCATION,
                    temperature=0.0,
                    max_retries=2
                )
                self.logger.info("Vertex AI model initialized.")
            except Exception as e:
                self.logger.error(f"Failed to initialize Vertex AI model: {e}")
                self.model = None
        else:
            self.logger.info("Vertex AI disabled. Using mock generator.")

    async def warmup(self):
        if self.model:
            try:
                await self.generate_suggestions(
                    user_id=UUID(int=0),
                    input_text="contract",
                    max_predictions=1,
                    categories=None,
                    output_language="en"
                )
                self.logger.info("Model warm-up successful.")
            except Exception as e:
                self.logger.warning(f"Warm-up failed: {e}")

    def _spammy(self, text: str) -> bool:
        if len(text) > 64 and len(set(text)) < 4:
            return True
        patterns = [
            r"^[^a-zA-Z0-9]+$",
            r"^[a-zA-Z]{1,2}$",
            r"(.)\\1{5,}",
            r"[!@#$%^&*()_+=\\-]{6,}"
        ]
        return any(re.match(p, text.strip()) for p in patterns)

    def _mock_generate(self, input_text: str, max_predictions: int, categories: Optional[List[str]], language: str) -> List[Suggestion]:
        base = input_text.strip()
        if self._spammy(base):
            return []
        seeds = [
            f"{base} rights under BGB",
            f"{base} termination process",
            f"{base} legal obligations",
            f"{base} notice period",
            f"{base} dispute resolution"
        ]
        seeds = seeds[:max_predictions]
        cat_pool = categories if categories else self._all_categories
        suggestions: List[Suggestion] = []
        for idx, s in enumerate(seeds):
            cat = cat_pool[idx % len(cat_pool)] if cat_pool else "Other (Misc.)"
            suggestions.append(Suggestion(text=s, category=cat))
        return suggestions

    async def generate_suggestions(
        self,
        user_id: UUID,
        input_text: str,
        max_predictions: int = 5,
        categories: Optional[List[str]] = None,
        output_language: Optional[str] = None
    ) -> List[Suggestion]:
        self.user_id = user_id

        # Resolve language
        language = (output_language or LanguageCode.EN.value).lower()
        if language not in [c.value for c in LanguageCode]:
            language = LanguageCode.EN.value

        if self._spammy(input_text):
            return []

        if self.model:
            try:
                system_prompt = build_prompt(
                    all_categories=self._all_categories,
                    input_text=input_text,
                    categories=categories,
                    max_predictions=max_predictions,
                    language=language
                )
                # Build chat prompt via LangChain or simple fallback
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("user", input_text)
                ])
                chain = prompt | self.model
                raw = chain.invoke({"input": input_text})
                # Attempt to parse JSON from raw.content
                import json
                try:
                    data = json.loads(raw.content)
                    suggestions: List[Suggestion] = []
                    for item in data:
                        suggestions.append(
                            Suggestion(
                                text=item.get("text"),
                                category=item.get("category") or "Other (Misc.)"
                            )
                        )
                    return suggestions[:max_predictions]
                except Exception as e:
                    self.logger.warning(f"Failed to parse LLM output, falling back: {e}")
                    return self._mock_generate(input_text, max_predictions, categories, language)
            except Exception as e:
                self.logger.error(f"LLM generation failure: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Failed to generate completions from LLM."
                )
        else:
            return self._mock_generate(input_text, max_predictions, categories, language)

    async def get_autocomplete(
        self,
        user_id: UUID,
        input_text: str,
        max_predictions: int,
        categories: Optional[List[str]],
        output_language: Optional[str]
    ) -> List[dict]:
        suggestions = await self.generate_suggestions(
            user_id=user_id,
            input_text=input_text,
            max_predictions=max_predictions,
            categories=categories,
            output_language=output_language
        )
        # Normalize categories
        for s in suggestions:
            if not s.category or s.category not in self._all_categories:
                s.category = "Other (Misc.)"
        return [s.model_dump() for s in suggestions]
    