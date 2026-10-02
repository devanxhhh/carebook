from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

class AuthService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        user = db.query(User).filter(User.email == user_in.email.lower()).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists."
            )
        
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            name=user_in.name,
            email=user_in.email.lower(),
            password_hash=hashed_password,
            role=UserRole.USER
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User | None:
        user = db.query(User).filter(User.email == email.lower()).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
