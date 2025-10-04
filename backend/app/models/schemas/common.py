from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, Field

T = TypeVar("T")

class ErrorDetail(BaseModel):
    message: str
    code: Optional[str] = None

class ResponseModel(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    errors: Optional[List[ErrorDetail]] = None
    