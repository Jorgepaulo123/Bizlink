from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_active_user
from ..models import User
from ..schemas import UserMeOut

router = APIRouter()

@router.get("/me", response_model=UserMeOut)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
