from sqlalchemy import Boolean, Column, DateTime, Enum, String

from src.core.db import Base, IdType
from src.core.time import utcnow


class Role:
    ADMIN = "ADMIN"
    INSTRUCTOR = "INSTRUCTOR"
    STUDENT = "STUDENT"
    ALL = (ADMIN, INSTRUCTOR, STUDENT)


class User(Base):
    __tablename__ = "users"

    id = Column(IdType, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)  # lưu chữ thường (BR-ACC-02)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(*Role.ALL, name="user_role"), nullable=False)
    student_code = Column(String(20), nullable=True, unique=True)  # BR-ACC-08
    password_hash = Column(String(255), nullable=False)
    must_change_password = Column(Boolean, nullable=False, default=True)  # BR-ACC-04
    is_active = Column(Boolean, nullable=False, default=True)  # BR-ACC-06
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
