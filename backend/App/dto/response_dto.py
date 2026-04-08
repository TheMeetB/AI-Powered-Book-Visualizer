from typing import Any

from pydantic import BaseModel


class StandardResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Any | None = None
