from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
from typing import Optional, Annotated

from ..database import get_db
from ..deps import get_current_active_user
from ..models import Company, User
from ..schemas import CompanyCreate, CompanyOut, CompanyUpdate

router = APIRouter()

def _uploads_base_dir() -> str:
    """Absolute path to app/uploads directory (the one mounted at /uploads)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

def save_company_logo(company_id: int, file: UploadFile) -> Optional[str]:
    """Save company logo and return the URL path under /uploads."""
    if not file:
        return None

    base_dir = _uploads_base_dir()
    upload_dir = os.path.join(base_dir, "company_logos", str(company_id))
    os.makedirs(upload_dir, exist_ok=True)

    # Generate a safe filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"logo{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Public URL relative to /uploads
    return "/uploads/" + "/".join(["company_logos", str(company_id), filename])

def save_company_cover(company_id: int, file: UploadFile) -> Optional[str]:
    """Save company cover and return the URL path under /uploads."""
    if not file:
        return None

    base_dir = _uploads_base_dir()
    upload_dir = os.path.join(base_dir, "company_covers", str(company_id))
    os.makedirs(upload_dir, exist_ok=True)

    # Generate a safe filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"cover{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # Public URL relative to /uploads
    return "/uploads/" + "/".join(["company_covers", str(company_id), filename])


@router.post("/", response_model=CompanyOut, status_code=status.HTTP_201_CREATED)
async def create_company(
    name: str = Form(...),
    description: str = Form(...),
    logo: UploadFile = File(None),
    cover: UploadFile = File(None),
    nuit: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    province: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    whatsapp: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if company name already exists
    existing = db.query(Company).filter(Company.name == name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name already exists"
        )
    
    # Create company first to get the ID
    company = Company(
        name=name,
        description=description,
        owner_id=current_user.id,
        nuit=nuit,
        nationality=nationality,
        province=province,
        district=district,
        address=address,
        website=website,
        email=email,
        whatsapp=whatsapp,
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    # Handle file uploads after company is created
    try:
        if logo:
            company.logo_url = save_company_logo(company.id, logo)
        if cover:
            company.cover_url = save_company_cover(company.id, cover)
        db.commit()
        db.refresh(company)
    except Exception as e:
        # If file upload fails, delete the company
        db.delete(company)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )
    
    return company

@router.get("/", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()

@router.put("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None),
    cover: Optional[UploadFile] = File(None),
    nuit: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    province: Optional[str] = Form(None),
    district: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    whatsapp: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if user is the owner
    if company.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this company"
        )
    
    # Update fields if provided
    if name is not None:
        company.name = name
    if description is not None:
        company.description = description
    if nuit is not None:
        company.nuit = nuit
    if nationality is not None:
        company.nationality = nationality
    if province is not None:
        company.province = province
    if district is not None:
        company.district = district
    if address is not None:
        company.address = address
    if website is not None:
        company.website = website
    if email is not None:
        company.email = email
    if whatsapp is not None:
        company.whatsapp = whatsapp
    
    # Handle file uploads
    try:
        if logo:
            company.logo_url = save_company_logo(company.id, logo)
        if cover:
            company.cover_url = save_company_cover(company.id, cover)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}"
        )
    
    db.commit()
    db.refresh(company)
    return company

@router.put("/{company_id}/logo", response_model=CompanyOut)
async def update_company_logo(
    company_id: int,
    logo: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        company.logo_url = save_company_logo(company.id, logo)
        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading logo: {str(e)}")

@router.put("/{company_id}/cover", response_model=CompanyOut)
async def update_company_cover(
    company_id: int,
    cover: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        company.cover_url = save_company_cover(company.id, cover)
        db.commit()
        db.refresh(company)
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading cover: {str(e)}")

@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
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
