import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi import status
from uuid import uuid4
from typing import Optional
import shutil
from ..deps import get_current_active_user
from ..models import User

router = APIRouter()

# Base upload directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp'
}

# Max file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def get_upload_path(file_type: str, filename: str) -> str:
    """Generate a file path for the uploaded file."""
    file_type_dir = os.path.join(UPLOAD_DIR, file_type)
    os.makedirs(file_type_dir, exist_ok=True)
    return os.path.join(file_type_dir, filename)

@router.post("/upload/company/logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a company logo."""
    return await handle_file_upload(file, "company_logos")

@router.post("/upload/company/cover")
async def upload_company_cover(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a company cover image."""
    return await handle_file_upload(file, "company_covers")

@router.post("/upload/profile")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload a user profile picture."""
    return await handle_file_upload(file, "profile_pictures")

async def handle_file_upload(file: UploadFile, file_type: str):
    """Handle file upload with validation and storage."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )

    # Check file type
    content_type = file.content_type
    if content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS.keys())}"
        )

    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {MAX_FILE_SIZE/1024/1024}MB"
        )
    file.file.seek(0)

    # Generate safe filename
    ext = ALLOWED_EXTENSIONS[content_type]
    safe_name = f"{uuid4().hex}{ext}"
    
    # Save file
    dest_path = get_upload_path(file_type, safe_name)
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Return relative URL
    return {
        "success": True,
        "url": f"/uploads/{file_type}/{safe_name}",
        "filename": safe_name
    }
