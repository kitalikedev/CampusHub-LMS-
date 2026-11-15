from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import require_roles
from src.core.schemas import Page
from src.modules.users import repository as repo
from src.modules.users import service
from src.modules.users.models import Role, User
from src.modules.users.schemas import (ImportRequest, ImportResult, UserCreate, UserOut, UserUpdate,
                                       UserWithPassword)

router = APIRouter(prefix="/admin/users", tags=["users"])
admin_only = require_roles(Role.ADMIN)


@router.get("", response_model=Page[UserOut])
def list_users(q: Optional[str] = None, role: Optional[str] = None, page: int = Query(1, ge=1),
               page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
               _admin: User = Depends(admin_only)):
    items, total = repo.search(db, q, role, page, page_size)
    return Page[UserOut](items=items, total=total)


@router.post("", response_model=UserWithPassword, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    user, temp = service.create_user(db, admin, data)
    return UserWithPassword(user=UserOut.model_validate(user), temp_password=temp)


@router.post("/import", response_model=ImportResult, status_code=201)
def import_users(data: ImportRequest, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    return ImportResult(created=service.import_csv(db, admin, data.csv_text))


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    return service.update_user(db, admin, user_id, data)


@router.post("/{user_id}/reset-password", response_model=UserWithPassword)
def reset_password(user_id: int, db: Session = Depends(get_db), admin: User = Depends(admin_only)):
    user, temp = service.reset_password(db, admin, user_id)
    return UserWithPassword(user=UserOut.model_validate(user), temp_password=temp)
