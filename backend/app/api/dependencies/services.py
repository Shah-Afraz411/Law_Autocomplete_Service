from fastapi import Depends
from uuid import UUID
from ...services.autocomplete_service import AutocompleteService
from .auth import authenticate

_service_singleton = AutocompleteService()

def get_autocomplete_service(user_id: UUID = Depends(authenticate)) -> AutocompleteService:
    # user_id is set on each request
    _service_singleton.user_id = user_id
    return _service_singleton
