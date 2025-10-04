from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from ...models.schemas.autocomplete import (
    AutocompleteRequest,
    SuggestionList
)
from ...models.schemas.common import ResponseModel, ErrorDetail
from ...services.autocomplete_service import AutocompleteService
from ..dependencies.services import get_autocomplete_service
from ..dependencies.auth import authenticate

router = APIRouter()

@router.post(
    "/autocomplete",
    response_model=ResponseModel[SuggestionList],
    status_code=status.HTTP_200_OK,
    summary="Intelligent text autocomplete",
    description="Generate up to N autocomplete suggestions (law-focused)."
)
async def autocomplete_endpoint(
    request: AutocompleteRequest,
    user_id: UUID = Depends(authenticate),
    service: AutocompleteService = Depends(get_autocomplete_service)
):
    try:
        suggestions = await service.get_autocomplete(
            user_id=user_id,
            input_text=request.input,
            max_predictions=request.max_predictions,
            categories=request.categories,
            output_language=request.output_language
        )
        return ResponseModel(
            success=True,
            message="Autocomplete suggestions generated successfully.",
            data=SuggestionList(suggestions=suggestions)
        )
    except HTTPException as e:
        return ResponseModel(
            success=False,
            message=str(e.detail),
            errors=[ErrorDetail(message=str(e.detail))]
        )
    except Exception as e:
        return ResponseModel(
            success=False,
            message="Failed to generate Autocomplete suggestions.",
            errors=[ErrorDetail(message=str(e))]
        )
    