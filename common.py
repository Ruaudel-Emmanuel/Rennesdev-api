# app/schemas/common.py
from datetime import datetime
from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"


class ResourceMeta(BaseModel):
    created_at: datetime | None = None
    updated_at: datetime | None = None