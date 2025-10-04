from uuid import UUID
from fastapi import Depends, HTTPException, status

# Placeholder for auth. Replace with JWT / OAuth2 / Cognito integration.
def get_current_user_id() -> UUID:
    # In production: decode token, verify, extract sub claim.
    # Here: deterministic dummy user.
    return UUID(int=123456)

def authenticate(user_id: UUID = Depends(get_current_user_id)) -> UUID:
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_id
