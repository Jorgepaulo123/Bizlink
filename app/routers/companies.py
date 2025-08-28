from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_active_user
from ..models import Company, User
from ..schemas import CompanyCreate, CompanyOut

router = APIRouter()

@router.post("/", response_model=CompanyOut)
def create_company(data: CompanyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    existing = db.query(Company).filter(Company.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company name already exists")
    company = Company(name=data.name, description=data.description, owner_id=current_user.id)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

@router.get("/", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(company)
    db.commit()
    return {"ok": True}
