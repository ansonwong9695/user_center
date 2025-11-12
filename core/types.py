from typing import TypedDict, Optional


class ExceptionResponse(TypedDict):
    code: Optional[int]
    message: Optional[str]
    description: Optional[str]
