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
    """
    Generate law-focused autocomplete suggestions for partial user input with their law categories for the given input..

      * Restrict suggestions to one or more categories of BGB law.
      * Request output in a target output_language (ISO 639-1 code).

        Invalid or unsupported languages will fall back to the authenticated user’s
        profile preference, and then to English.

    Args:
        request (AutocompleteRequest):  
            - input (str): non-empty partial text to complete.  
            - max_predictions (int): number of suggestions (1–20, default 5).  
            - categories (List[str], optional): list of law categories to bias suggestions.  
            - output_language (str, optional): ISO 639-1 code for the response language.
        operations_service (OperationsService):  
            Service layer dependency, automatically injected after authentication.

    Returns:
        ResponseModel:  
            On success (success=True), data.suggestions is a list of objects, each with:
              - text (str): the completion string.
              - category (str, optional): the law category, if assigned.

    Raises:
        HTTPException (422): if input is empty or whitespace.
        HTTPException (502): if LLM generation fails internally.

    """
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
    
