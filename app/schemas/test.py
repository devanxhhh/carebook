from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class DiagnosticTestBase(BaseModel):
    name: str = Field(min_length=1)
    code: str = Field(min_length=1)
    description: str | None = None
    category: str | None = None
    is_active: bool = True

class DiagnosticTestCreate(DiagnosticTestBase):
    pass

class DiagnosticTestUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    category: str | None = None
    is_active: bool | None = None

class DiagnosticTestResponse(DiagnosticTestBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaginatedDiagnosticTestResponse(BaseModel):
    items: List[DiagnosticTestResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
