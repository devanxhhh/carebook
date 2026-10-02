from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.test import DiagnosticTestResponse

class CentreTestBase(BaseModel):
    test_id: int
    price: float = Field(gt=0)
    is_available: bool = True

class CentreTestCreate(CentreTestBase):
    pass

class CentreTestResponse(CentreTestBase):
    id: int
    test: DiagnosticTestResponse
    model_config = ConfigDict(from_attributes=True)

class DiagnosticCentreBase(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    description: str | None = None
    is_active: bool = True

class DiagnosticCentreCreate(DiagnosticCentreBase):
    pass

class DiagnosticCentreUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    description: str | None = None
    is_active: bool | None = None

class DiagnosticCentreResponse(DiagnosticCentreBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DiagnosticCentreDetailResponse(DiagnosticCentreResponse):
    centre_tests: List[CentreTestResponse] = []

class PaginatedDiagnosticCentreResponse(BaseModel):
    items: List[DiagnosticCentreResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
