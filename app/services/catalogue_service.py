from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Tuple, List
from fastapi import HTTPException, status
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest, CentreTest
from app.schemas.centre import DiagnosticCentreCreate, DiagnosticCentreUpdate, CentreTestCreate
from app.schemas.test import DiagnosticTestCreate, DiagnosticTestUpdate

class CatalogueService:
    @staticmethod
    def get_centres(db: Session, page: int = 1, page_size: int = 10, search: str | None = None, active_only: bool = True) -> Tuple[List[DiagnosticCentre], int]:
        query = db.query(DiagnosticCentre)
        if active_only:
            query = query.filter(DiagnosticCentre.is_active == True)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                DiagnosticCentre.name.ilike(search_pattern),
                DiagnosticCentre.location.ilike(search_pattern)
            ))
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def create_centre(db: Session, centre_in: DiagnosticCentreCreate) -> DiagnosticCentre:
        centre = DiagnosticCentre(**centre_in.model_dump())
        db.add(centre)
        db.commit()
        db.refresh(centre)
        return centre

    @staticmethod
    def get_centre(db: Session, centre_id: int) -> DiagnosticCentre:
        centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
        if not centre:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Centre not found")
        return centre

    @staticmethod
    def update_centre(db: Session, centre_id: int, centre_in: DiagnosticCentreUpdate) -> DiagnosticCentre:
        centre = CatalogueService.get_centre(db, centre_id)
        update_data = centre_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(centre, field, value)
        db.commit()
        db.refresh(centre)
        return centre

    @staticmethod
    def get_tests(db: Session, page: int = 1, page_size: int = 10, search: str | None = None, category: str | None = None) -> Tuple[List[DiagnosticTest], int]:
        query = db.query(DiagnosticTest)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(or_(
                DiagnosticTest.name.ilike(search_pattern),
                DiagnosticTest.code.ilike(search_pattern)
            ))
        if category:
            query = query.filter(DiagnosticTest.category == category)
            
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    @staticmethod
    def create_test(db: Session, test_in: DiagnosticTestCreate) -> DiagnosticTest:
        existing = db.query(DiagnosticTest).filter(DiagnosticTest.code == test_in.code).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Test with this code already exists")
        
        test = DiagnosticTest(**test_in.model_dump())
        db.add(test)
        db.commit()
        db.refresh(test)
        return test

    @staticmethod
    def get_test(db: Session, test_id: int) -> DiagnosticTest:
        test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_id).first()
        if not test:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
        return test

    @staticmethod
    def update_test(db: Session, test_id: int, test_in: DiagnosticTestUpdate) -> DiagnosticTest:
        test = CatalogueService.get_test(db, test_id)
        update_data = test_in.model_dump(exclude_unset=True)
        
        if 'code' in update_data and update_data['code'] != test.code:
            existing = db.query(DiagnosticTest).filter(DiagnosticTest.code == update_data['code']).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Test with this code already exists")
                
        for field, value in update_data.items():
            setattr(test, field, value)
        db.commit()
        db.refresh(test)
        return test

    @staticmethod
    def add_centre_test(db: Session, centre_id: int, centre_test_in: CentreTestCreate) -> CentreTest:
        centre = CatalogueService.get_centre(db, centre_id)
        test = CatalogueService.get_test(db, centre_test_in.test_id)
        
        existing = db.query(CentreTest).filter(
            CentreTest.centre_id == centre_id,
            CentreTest.test_id == centre_test_in.test_id
        ).first()
        
        if existing:
            existing.price = centre_test_in.price
            existing.is_available = centre_test_in.is_available
            db.commit()
            db.refresh(existing)
            return existing
            
        new_ct = CentreTest(
            centre_id=centre_id,
            test_id=centre_test_in.test_id,
            price=centre_test_in.price,
            is_available=centre_test_in.is_available
        )
        db.add(new_ct)
        db.commit()
        db.refresh(new_ct)
        return new_ct
