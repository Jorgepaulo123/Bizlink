from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_active_user
from ..models import Service, Company, User
from ..schemas import ServiceCreate, ServiceOut

router = APIRouter()

@router.post("/", response_model=ServiceOut)
def create_service(data: ServiceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    company = db.get(Company, data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    service = Service(company_id=data.company_id, name=data.name, price=data.price, description=data.description)
    db.add(service)
    db.commit()
    db.refresh(service)
    return service

@router.get("/company/{company_id}", response_model=list[ServiceOut])
def list_services_by_company(company_id: int, db: Session = Depends(get_db)):
    return db.query(Service).filter(Service.company_id == company_id).all()

@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    company = db.get(Company, service.company_id)
    if not company or company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(service)
    db.commit()
    return {"ok": True}
