from fastapi import Depends, HTTPException
from uuid import UUID
from ...services.autocomplete_service import AutocompleteService
from .auth import authenticate

_service_singleton = AutocompleteService()

def get_autocomplete_service(user_id: UUID = Depends(authenticate)) -> AutocompleteService:
    """
    Dependency that ensures the user is authenticated, extracts their UUID,
    and returns an OperationsService scoped to that user.
    """
    try:
        # user_id is set on each request
        _service_singleton.user_id = user_id
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID in token.")
    return _service_singleton

singleton_ops = AutocompleteService()
