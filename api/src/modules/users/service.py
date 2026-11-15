"""Quản lý tài khoản (BR-ACC-01…10)."""
import csv
import io
from typing import Any, Dict, List, Optional, Tuple

from email_validator import EmailNotValidError, validate_email
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.security import generate_temp_password, hash_password
from src.modules.audit import service as audit
from src.modules.audit.service import AuditAction
from src.modules.enrollments.models import Enrollment
from src.modules.sections.models import CourseSection
from src.modules.users import repository as repo
from src.modules.users.models import Role, User
from src.modules.users.schemas import ImportedAccount, UserCreate, UserUpdate


def _validate_identity(db: Session, email: str, role: str, student_code: Optional[str],
                       exclude_id: Optional[int] = None) -> Optional[str]:
    """Trả mã lỗi hoặc None (BR-ACC-02, 08)."""
    existing = repo.get_by_email(db, email)
    if existing and existing.id != exclude_id:
        return "EMAIL_ALREADY_EXISTS"
    if role == Role.STUDENT:
        if not student_code:
            return "VALIDATION_ERROR"
        other = repo.get_by_student_code(db, student_code)
        if other and other.id != exclude_id:
            return "STUDENT_CODE_EXISTS"
    elif student_code:
        return "VALIDATION_ERROR"
    return None


def _new_user(email: str, full_name: str, role: str, student_code: Optional[str]) -> Tuple[User, str]:
    temp = generate_temp_password()
    user = User(email=repo.normalize_email(email), full_name=full_name.strip(), role=role,
                student_code=(student_code or None) if role == Role.STUDENT else None,
                password_hash=hash_password(temp), must_change_password=True, is_active=True)
    return user, temp


def create_user(db: Session, actor: User, data: UserCreate) -> Tuple[User, str]:
    code = (data.student_code or "").strip() or None
    error = _validate_identity(db, data.email, data.role, code)
    if error:
        raise AppError(error, {"field": "student_code" if error != "EMAIL_ALREADY_EXISTS" else "email"})
    user, temp = _new_user(data.email, data.full_name, data.role, code)
    repo.add(db, user)
    audit.log(db, actor, AuditAction.USER_CREATED, "user", user.id, after={"email": user.email, "role": user.role})
    db.commit()
    return user, temp


def import_csv(db: Session, actor: User, csv_text: str) -> List[ImportedAccount]:
    """Kiểm tra toàn bộ file trước; có dòng lỗi thì không tạo tài khoản nào (BR-ACC-10)."""
    reader = csv.DictReader(io.StringIO(csv_text.strip().lstrip("﻿")))
    required = {"email", "full_name", "role"}
    if not reader.fieldnames or not required.issubset({f.strip() for f in reader.fieldnames}):
        raise AppError("IMPORT_INVALID_ROWS", {"rows": [{"row": 1, "code": "MISSING_COLUMNS"}]})
    rows: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    seen_emails, seen_codes = set(), set()
    for index, raw in enumerate(reader, start=2):
        row = {k.strip(): (v or "").strip() for k, v in raw.items() if k}
        email, role, code = row.get("email", "").lower(), row.get("role", "").upper(), row.get("student_code") or None
        error = None
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError:
            error = "INVALID_EMAIL"
        if not error and role not in Role.ALL:
            error = "INVALID_ROLE"
        if not error and not row.get("full_name"):
            error = "MISSING_NAME"
        if not error and (email in seen_emails or (code and code in seen_codes)):
            error = "DUPLICATE_IN_FILE"
        if not error:
            error = _validate_identity(db, email, role, code)
        if error:
            errors.append({"row": index, "email": email, "code": error})
        seen_emails.add(email)
        if code:
            seen_codes.add(code)
        rows.append({"email": email, "full_name": row.get("full_name", ""), "role": role, "student_code": code})
    if not rows:
        raise AppError("IMPORT_INVALID_ROWS", {"rows": [{"row": 1, "code": "EMPTY_FILE"}]})
    if errors:
        raise AppError("IMPORT_INVALID_ROWS", {"rows": errors})
    created: List[ImportedAccount] = []
    for row in rows:
        user, temp = _new_user(row["email"], row["full_name"], row["role"], row["student_code"])
        repo.add(db, user)
        created.append(ImportedAccount(email=user.email, full_name=user.full_name, role=user.role,
                                       student_code=user.student_code, temp_password=temp))
    audit.log(db, actor, AuditAction.USERS_IMPORTED, "user", 0, after={"count": len(created)})
    db.commit()
    return created


def _has_role_data(db: Session, user: User) -> bool:
    if user.role == Role.INSTRUCTOR:
        return db.query(CourseSection.id).filter(CourseSection.instructor_id == user.id).first() is not None
    if user.role == Role.STUDENT:
        return db.query(Enrollment.id).filter(Enrollment.student_id == user.id).first() is not None
    return False


def update_user(db: Session, actor: User, user_id: int, data: UserUpdate) -> User:
    user = repo.get(db, user_id)
    if user is None:
        raise AppError("NOT_FOUND")
    before = {"full_name": user.full_name, "role": user.role, "is_active": user.is_active,
              "student_code": user.student_code}
    new_role = data.role or user.role
    deactivating = data.is_active is False and user.is_active
    demoting = user.role == Role.ADMIN and new_role != Role.ADMIN
    if user.id == actor.id and (deactivating or demoting):
        raise AppError("LAST_ADMIN_REQUIRED")  # BR-ACC-07: không tự khóa/tự hạ quyền
    if (deactivating or demoting) and user.role == Role.ADMIN and repo.count_active_admins(db) <= 1:
        raise AppError("LAST_ADMIN_REQUIRED")
    if new_role != user.role and _has_role_data(db, user):
        raise AppError("ROLE_CHANGE_NOT_ALLOWED")  # BR-ACC-09
    code = data.student_code.strip() if data.student_code is not None else user.student_code
    if new_role != Role.STUDENT:
        code = None
    error = _validate_identity(db, user.email, new_role, code, exclude_id=user.id)
    if error:
        raise AppError(error, {"field": "student_code"})
    if data.full_name is not None:
        user.full_name = data.full_name.strip()
    user.role, user.student_code = new_role, code
    if data.is_active is not None:
        user.is_active = data.is_active
    audit.log(db, actor, AuditAction.USER_UPDATED, "user", user.id, before=before,
              after={"full_name": user.full_name, "role": user.role, "is_active": user.is_active,
                     "student_code": user.student_code})
    db.commit()
    return user


def reset_password(db: Session, actor: User, user_id: int) -> Tuple[User, str]:
    user = repo.get(db, user_id)
    if user is None:
        raise AppError("NOT_FOUND")
    temp = generate_temp_password()
    user.password_hash = hash_password(temp)
    user.must_change_password = True
    audit.log(db, actor, AuditAction.PASSWORD_RESET, "user", user.id)
    db.commit()
    return user, temp
