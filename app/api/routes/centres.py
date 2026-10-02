from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
import math

from app.api.deps import get_db, get_current_admin_user
from app.models.user import User
from app.schemas.centre import (
    DiagnosticCentreResponse,
    DiagnosticCentreDetailResponse,
    PaginatedDiagnosticCentreResponse,
    DiagnosticCentreCreate,
    DiagnosticCentreUpdate,
    CentreTestCreate,
    CentreTestResponse
)
from app.services.catalogue_service import CatalogueService

router = APIRouter()

@router.get("", response_model=PaginatedDiagnosticCentreResponse)
def list_centres(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    active_only: bool = True
):
    items, total = CatalogueService.get_centres(db, page, page_size, search, active_only)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/{centre_id}", response_model=DiagnosticCentreDetailResponse)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    return CatalogueService.get_centre(db, centre_id)

@router.post("", response_model=DiagnosticCentreResponse, status_code=status.HTTP_201_CREATED)
def create_centre(
    centre_in: DiagnosticCentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return CatalogueService.create_centre(db, centre_in)

@router.patch("/{centre_id}", response_model=DiagnosticCentreResponse)
def update_centre(
    centre_id: int,
    centre_in: DiagnosticCentreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return CatalogueService.update_centre(db, centre_id, centre_in)

@router.delete("/{centre_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_centre(
    centre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Soft delete
    update_data = DiagnosticCentreUpdate(is_active=False)
    CatalogueService.update_centre(db, centre_id, update_data)
    return None

@router.post("/{centre_id}/tests", response_model=CentreTestResponse, status_code=status.HTTP_201_CREATED)
def add_test_to_centre(
    centre_id: int,
    centre_test_in: CentreTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return CatalogueService.add_centre_test(db, centre_id, centre_test_in)
