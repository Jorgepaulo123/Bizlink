from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os

from ..database import get_db
from ..deps import get_current_active_user
from ..models import Service, Company, User
from ..schemas import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter()

# Helpers for image saving (reuse uploads dir mounted at /uploads)
from ..routers.companies import _uploads_base_dir as _uploads_base

def save_service_image(service_id: int, file: UploadFile) -> Optional[str]:
    if not file:
        return None
    base_dir = _uploads_base()
    upload_dir = os.path.join(base_dir, "service_images", str(service_id))
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    filename = f"image{ext}"
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    return "/uploads/" + "/".join(["service_images", str(service_id), filename])

@router.post("/", response_model=ServiceOut)
async def create_service(
    company_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Will be converted to list[str]
    status: Optional[str] = Form("Ativo"),
    is_promoted: Optional[bool] = Form(False),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # Convert tags string to list if provided
    tags_list = None
    if tags:
        tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    service = Service(
        company_id=company_id,
        title=title,
        description=description,
        price=price,
        category=category,
        tags=tags_list,
        status=status or "Ativo",
        is_promoted=bool(is_promoted),
    )
    db.add(service)
    db.commit()
    db.refresh(service)

    if image:
        try:
            service.image_url = save_service_image(service.id, image)
            db.commit()
            db.refresh(service)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

    return service

@router.get("/company/{company_id}", response_model=list[ServiceOut])
async def list_services_by_company(company_id: int, db: Session = Depends(get_db)):
    """Busca todos os serviços de uma empresa específica"""
    return db.query(Service).filter(Service.company_id == company_id).all()

@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """Busca um serviço específico por ID"""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.put("/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Will be converted to list[str]
    status: Optional[str] = Form(None),
    is_promoted: Optional[bool] = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    company = db.get(Company, service.company_id)
    if not company or company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if title is not None:
        service.title = title
    if description is not None:
        service.description = description
    if price is not None:
        service.price = price
    if category is not None:
        service.category = category
    if tags is not None:
        # Convert tags string to list if provided
        tags_list = None
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        service.tags = tags_list
    if status is not None:
        service.status = status
    if is_promoted is not None:
        service.is_promoted = bool(is_promoted)

    if image:
        try:
            service.image_url = save_service_image(service.id, image)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

    db.commit()
    db.refresh(service)
    return service

@router.put("/{service_id}/image", response_model=ServiceOut)
async def upload_service_image(
    service_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    company = db.get(Company, service.company_id)
    if not company or company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    try:
        service.image_url = save_service_image(service.id, image)
        db.commit()
        db.refresh(service)
        return service
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@router.delete("/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    company = db.get(Company, service.company_id)
    if not company or company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(service)
    db.commit()
    return {"ok": True}
