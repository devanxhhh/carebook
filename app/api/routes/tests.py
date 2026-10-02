from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.api.deps import get_db, get_current_admin_user
from app.models.user import User
from app.schemas.test import (
    DiagnosticTestResponse,
    PaginatedDiagnosticTestResponse,
    DiagnosticTestCreate,
    DiagnosticTestUpdate
)
from app.services.catalogue_service import CatalogueService

router = APIRouter()

@router.get("", response_model=PaginatedDiagnosticTestResponse)
def list_tests(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None
):
    items, total = CatalogueService.get_tests(db, page, page_size, search, category)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/{test_id}", response_model=DiagnosticTestResponse)
def get_test(test_id: int, db: Session = Depends(get_db)):
    return CatalogueService.get_test(db, test_id)

@router.post("", response_model=DiagnosticTestResponse, status_code=status.HTTP_201_CREATED)
def create_test(
    test_in: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return CatalogueService.create_test(db, test_in)

@router.patch("/{test_id}", response_model=DiagnosticTestResponse)
def update_test(
    test_id: int,
    test_in: DiagnosticTestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return CatalogueService.update_test(db, test_id, test_in)

@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    update_data = DiagnosticTestUpdate(is_active=False)
    CatalogueService.update_test(db, test_id, update_data)
    return None
