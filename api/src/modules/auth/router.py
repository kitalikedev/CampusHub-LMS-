"""Đăng nhập, đổi mật khẩu, thông tin bản thân (FR-AUTH-01…03). Không có đăng ký công khai (BR-ACC-01)."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.db import get_db
from src.core.deps import get_current_user_allow_password_change
from src.core.schemas import Message
from src.modules.auth import service
from src.modules.users.models import User
from src.modules.users.schemas import UserOut

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    token, user = service.login(db, data.email, data.password)
    return LoginResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/auth/change-password", response_model=Message)
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db),
                    user: User = Depends(get_current_user_allow_password_change)):
    service.change_password(db, user, data.current_password, data.new_password)
    return Message()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user_allow_password_change)):
    return user
