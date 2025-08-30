from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import os

from ..database import get_db
from ..deps import get_current_active_user
from ..models import User
from ..schemas import UserOut, UserUpdate

router = APIRouter()

# Helpers for image saving
def _uploads_base_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

def save_user_photo(user_id: int, file: UploadFile, photo_type: str) -> Optional[str]:
    """Salva foto do usuário (profile ou cover)"""
    if not file:
        return None
    
    base_dir = _uploads_base_dir()
    upload_dir = os.path.join(base_dir, "user_photos", str(user_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{photo_type}{ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return "/uploads/" + "/".join(["user_photos", str(user_id), filename])

@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """Retorna o perfil do usuário logado"""
    return current_user

@router.put("/me", response_model=UserOut)
async def update_my_profile(
    profile_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza o perfil do usuário logado"""
    # Atualizar apenas os campos fornecidos
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    
    if profile_update.gender is not None:
        # Validar gênero
        valid_genders = ['Masculino', 'Feminino', 'Outro']
        if profile_update.gender not in valid_genders:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid gender. Must be one of: {', '.join(valid_genders)}"
            )
        current_user.gender = profile_update.gender
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/me/profile-photo", response_model=UserOut)
async def upload_profile_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload da foto de perfil do usuário"""
    # Validar tipo de arquivo
    if not photo.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Salvar foto
        photo_url = save_user_photo(current_user.id, photo, "profile")
        
        # Atualizar usuário
        current_user.profile_photo_url = photo_url
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")

@router.put("/me/cover-photo", response_model=UserOut)
async def upload_cover_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload da foto de capa do usuário"""
    # Validar tipo de arquivo
    if not photo.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Salvar foto
        photo_url = save_user_photo(current_user.id, photo, "cover")
        
        # Atualizar usuário
        current_user.cover_photo_url = photo_url
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading photo: {str(e)}")

@router.delete("/me/profile-photo", response_model=UserOut)
async def remove_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a foto de perfil do usuário"""
    if current_user.profile_photo_url:
        # Aqui você pode adicionar lógica para deletar o arquivo físico
        current_user.profile_photo_url = None
        db.commit()
        db.refresh(current_user)
    
    return current_user

@router.delete("/me/cover-photo", response_model=UserOut)
async def remove_cover_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a foto de capa do usuário"""
    if current_user.cover_photo_url:
        # Aqui você pode adicionar lógica para deletar o arquivo físico
        current_user.cover_photo_url = None
        db.commit()
        db.refresh(current_user)
    
    return current_user
