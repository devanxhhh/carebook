from pydantic import BaseModel, EmailStr, ConfigDict, Field
from app.models.user import UserRole
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    role: str | None = None
