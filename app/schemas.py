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

class UserMeOut(UserOut):
    companies: List["CompanyOut"] = []

# Companies
class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    nuit: Optional[str] = None
    nationality: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    nuit: Optional[str] = None
    nationality: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None

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
