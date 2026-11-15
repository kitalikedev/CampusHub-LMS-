"""Nộp bài (BR-SUB-01…08) và file đính kèm (BR-SUB-02, NFR-SEC-04)."""
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.errors import AppError
from src.core.permissions import ensure_enrolled, ensure_not_locked
from src.core.time import utcnow
from src.domain.submission_policy import PolicyViolation, decide
from src.modules.assignments import service as assignments
from src.modules.grading.models import Grade
from src.modules.submissions.models import StoredFile, Submission
from src.modules.users.models import Role, User

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".zip", ".rar", ".txt"}  # ĐỀ XUẤT


def _save_upload(user: User, upload: UploadFile) -> StoredFile:
    name = Path(upload.filename or "file").name
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AppError("FILE_TYPE_NOT_ALLOWED", {"allowed": sorted(ALLOWED_EXTENSIONS)})
    limit = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = upload.file.read(limit + 1)
    if len(data) > limit:
        raise AppError("FILE_TOO_LARGE", {"max_mb": settings.MAX_UPLOAD_MB})
    now = utcnow()
    relative = Path(f"{now:%Y}") / f"{now:%m}" / f"{uuid.uuid4().hex}{ext}"
    target = settings.UPLOAD_DIR / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return StoredFile(uploaded_by=user.id, original_name=name, stored_path=str(relative),
                      mime_type=upload.content_type or "application/octet-stream", size_bytes=len(data))


def _remove_file(db: Session, stored: Optional[StoredFile]) -> None:
    if stored is None:
        return
    path = settings.UPLOAD_DIR / stored.stored_path
    db.delete(stored)
    try:
        path.unlink()
    except OSError:
        pass


def submit(db: Session, student: User, assignment_id: int, content_url: Optional[str],
           upload: Optional[UploadFile]) -> Submission:
    assignment = assignments.get_assignment(db, assignment_id)
    section = assignments.section_of(db, assignment)
    ensure_enrolled(db, section, student)  # BR-SUB-01
    ensure_not_locked(section)
    url = (content_url or "").strip() or None
    if url and not (url.startswith("http://") or url.startswith("https://")):
        raise AppError("VALIDATION_ERROR", {"field": "content_url", "reason": "INVALID_URL"})
    has_file = upload is not None and bool(upload.filename)
    if url is None and not has_file:
        if assignment.submission_mode != "OFFLINE":
            raise AppError("SUBMISSION_EMPTY")
    attempts = db.query(Submission).filter(Submission.assignment_id == assignment.id,
                                           Submission.student_id == student.id) \
        .order_by(Submission.attempt_no).all()
    has_grade = db.query(Grade.id).filter(Grade.assignment_id == assignment.id,
                                          Grade.student_id == student.id).first() is not None
    now = utcnow()
    try:
        decision = decide(assignment.submission_mode, assignment.max_attempts, assignment.due_at,
                          assignment.late_policy, now, len(attempts), has_grade)
    except PolicyViolation as violation:
        raise AppError(violation.code, {"max_attempts": assignment.max_attempts})
    stored = _save_upload(student, upload) if has_file else None  # type: ignore[arg-type]
    try:
        if stored is not None:
            db.add(stored)
            db.flush()
        if decision.overwrite:
            submission = attempts[0]
            old_file = submission.file
            submission.content_url, submission.file_id = url, stored.id if stored else None
            submission.is_late, submission.submitted_at = decision.is_late, now
            db.flush()
            if old_file is not None and (stored is None or old_file.id != stored.id):
                _remove_file(db, old_file)
        else:
            submission = Submission(assignment_id=assignment.id, student_id=student.id,
                                    attempt_no=decision.attempt_no, content_url=url,
                                    file_id=stored.id if stored else None, is_late=decision.is_late,
                                    submitted_at=now)
            db.add(submission)
        db.commit()
    except Exception:
        db.rollback()
        if stored is not None:
            (settings.UPLOAD_DIR / stored.stored_path).unlink(missing_ok=True)
        raise
    db.refresh(submission)
    return submission


def my_attempts(db: Session, student: User, assignment_id: int) -> List[Submission]:
    assignment = assignments.get_assignment(db, assignment_id)
    ensure_enrolled(db, assignments.section_of(db, assignment), student)
    return db.query(Submission).filter(Submission.assignment_id == assignment_id,
                                       Submission.student_id == student.id) \
        .order_by(Submission.attempt_no.desc()).all()


def latest_by_student(db: Session, assignment_id: int) -> dict:
    """Lần nộp mới nhất và số lần nộp của từng SV (bản được chấm, BR-SUB-06)."""
    result: dict = {}
    for sub in db.query(Submission).filter(Submission.assignment_id == assignment_id) \
            .order_by(Submission.student_id, Submission.attempt_no):
        result[sub.student_id] = (sub, result.get(sub.student_id, (None, 0))[1] + 1)
    return result


def file_for_download(db: Session, user: User, file_id: int) -> Tuple[Path, StoredFile]:
    stored = db.get(StoredFile, file_id)
    if stored is None:
        raise AppError("NOT_FOUND")
    allowed = user.role == Role.ADMIN or stored.uploaded_by == user.id
    if not allowed and user.role == Role.INSTRUCTOR:
        sub = db.query(Submission).filter(Submission.file_id == stored.id).first()
        if sub is not None:
            section = assignments.section_of(db, assignments.get_assignment(db, sub.assignment_id))
            allowed = section.instructor_id == user.id
    if not allowed:
        raise AppError("FORBIDDEN")
    path = settings.UPLOAD_DIR / stored.stored_path
    if not path.is_file():
        raise AppError("NOT_FOUND")
    return path, stored
