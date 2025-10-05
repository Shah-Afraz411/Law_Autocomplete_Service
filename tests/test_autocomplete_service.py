import pytest
from uuid import UUID
from backend.app.services.autocomplete_service import AutocompleteService

@pytest.mark.asyncio
async def test_basic_generation():
    svc = AutocompleteService()
    suggestions = await svc.get_autocomplete(
        user_id=UUID(int=1),
        input_text="contract termination",
        max_predictions=5,
        categories=["Contract Law"],
        output_language="en"
    )
    assert isinstance(suggestions, list)
    assert len(suggestions) >= 1
    assert all("text" in s for s in suggestions)
    