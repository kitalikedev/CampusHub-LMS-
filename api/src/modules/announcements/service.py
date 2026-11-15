"""Thông báo lớp (BR-ANN-01). Vẫn đăng được khi lớp đã khóa sổ (BR-LCK-06)."""
from typing import List

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.permissions import ensure_section_instructor, ensure_section_member
from src.modules.announcements.models import Announcement
from src.modules.notifications import service as notifications
from src.modules.notifications.service import NotificationType
from src.modules.sections import service as sections
from src.modules.users.models import User


def list_for_section(db: Session, user: User, section_id: int) -> List[Announcement]:
    section = sections.get_section(db, section_id)
    ensure_section_member(db, section, user)
    return db.query(Announcement).filter(Announcement.section_id == section_id) \
        .order_by(Announcement.created_at.desc(), Announcement.id.desc()).all()


def create(db: Session, user: User, section_id: int, title: str, content: str) -> Announcement:
    section = sections.get_section(db, section_id)
    ensure_section_instructor(section, user)
    item = Announcement(section_id=section.id, author_id=user.id, title=title.strip(), content=content.strip())
    db.add(item)
    notifications.notify(db, sections.enrolled_student_ids(db, section.id), NotificationType.ANNOUNCEMENT_POSTED,
                         {"title": item.title, "section_code": section.section_code},
                         f"/student/classes/{section.id}")
    db.commit()
    return item


def _own(db: Session, user: User, announcement_id: int) -> Announcement:
    item = db.get(Announcement, announcement_id)
    if item is None:
        raise AppError("NOT_FOUND")
    ensure_section_instructor(sections.get_section(db, item.section_id), user)
    return item


def update(db: Session, user: User, announcement_id: int, title: str, content: str) -> Announcement:
    item = _own(db, user, announcement_id)
    item.title, item.content = title.strip(), content.strip()
    db.commit()
    return item


def delete(db: Session, user: User, announcement_id: int) -> None:
    db.delete(_own(db, user, announcement_id))
    db.commit()
