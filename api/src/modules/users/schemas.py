from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Literal

from src.core.schemas import ORMModel
from src.core.time import UTCDateTime

RoleLiteral = Literal["ADMIN", "INSTRUCTOR", "STUDENT"]


class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    role: str
    student_code: Optional[str]
    is_active: bool
    must_change_password: bool
    last_login_at: Optional[UTCDateTime]
    created_at: UTCDateTime


class UserBrief(ORMModel):
    id: int
    email: str
    full_name: str
    student_code: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: RoleLiteral
    student_code: Optional[str] = Field(default=None, max_length=20)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    role: Optional[RoleLiteral] = None
    student_code: Optional[str] = Field(default=None, max_length=20)
    is_active: Optional[bool] = None


class UserWithPassword(BaseModel):
    """Mật khẩu tạm chỉ trả về một lần (BR-ACC-03)."""

    user: UserOut
    temp_password: str


class ImportRequest(BaseModel):
    csv_text: str = Field(min_length=1)


class ImportedAccount(BaseModel):
    email: str
    full_name: str
    role: str
    student_code: Optional[str]
    temp_password: str


class ImportResult(BaseModel):
    created: List[ImportedAccount]
