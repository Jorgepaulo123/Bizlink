from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None

# Users
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Companies
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# Services
class ServiceBase(BaseModel):
    name: str
    price: Optional[float] = None
    description: Optional[str] = None

class ServiceCreate(ServiceBase):
    company_id: int

class ServiceOut(ServiceBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True
