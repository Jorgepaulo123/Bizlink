from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

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

# Credit System
class CompanyCreditBase(BaseModel):
    balance: float
    total_earned: float
    total_spent: float

class CompanyCreditOut(CompanyCreditBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CreditTransactionBase(BaseModel):
    type: str  # 'earn', 'spend', 'bonus', 'deduction'
    amount: float
    description: Optional[str] = None

class CreditTransactionOut(CreditTransactionBase):
    id: int
    company_credit_id: int
    balance_before: float
    balance_after: float
    created_at: datetime

    class Config:
        from_attributes = True

class CreditTransactionCreate(CreditTransactionBase):
    pass

# Services
class ServiceBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = "Ativo"
    is_promoted: Optional[bool] = False

class ServiceCreate(ServiceBase):
    company_id: int

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    status: Optional[str] = None
    is_promoted: Optional[bool] = None

class ServiceOut(ServiceBase):
    id: int
    company_id: int
    image_url: Optional[str] = None
    views: int
    leads: int
    likes: int

    class Config:
        from_attributes = True
