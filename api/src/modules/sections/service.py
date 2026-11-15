"""Lớp học phần, lịch học (BR-ACD-03…05), vòng đời lớp (03 §7.1)."""
from typing import Dict, List, Optional, Set

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.permissions import ensure_not_locked, is_enrolled
from src.domain.schedule import Slot, overlaps
from src.modules.academics import service as academics
from src.modules.academics.models import Semester, Subject
from src.modules.academics.schemas import SubjectBrief
from src.modules.enrollments.models import Enrollment, EnrollmentStatus
from src.modules.rooms.models import Room
from src.modules.sections import repository as repo
from src.modules.sections.models import CourseSection, ScheduleSlot, SectionStatus
from src.modules.sections.schemas import (InstructorBrief, SectionIn, SectionOut, SectionUpdate, SemesterBrief,
                                          SlotIn, SlotOut)
from src.modules.users.models import Role, User


def _slot(s: ScheduleSlot) -> Slot:
    return Slot(s.day_of_week, s.start_time, s.end_time)


def section_out(db: Session, section: CourseSection, viewer: Optional[User] = None,
                counts: Optional[Dict[int, int]] = None, graph: Optional[Dict[int, Set[int]]] = None) -> SectionOut:
    counts = counts if counts is not None else repo.enrolled_counts(db, [section.id])
    graph = graph if graph is not None else academics.prerequisite_map(db)
    prereq_ids = graph.get(section.subject_id, set())
    prereqs = db.query(Subject).filter(Subject.id.in_(prereq_ids)).order_by(Subject.code).all() if prereq_ids else []
    out = SectionOut(
        id=section.id, section_code=section.section_code, status=section.status, capacity=section.capacity,
        enrolled_count=counts.get(section.id, 0), semester=SemesterBrief.model_validate(section.semester),
        subject=SubjectBrief.model_validate(section.subject),
        prerequisites=[SubjectBrief.model_validate(p) for p in prereqs],
        instructor=InstructorBrief.model_validate(section.instructor),
        slots=[SlotOut.model_validate(s) for s in section.slots], locked_at=section.locked_at,
        registration_open=academics.is_registration_open(section.semester),
    )
    if viewer is not None and viewer.role == Role.STUDENT:
        out.is_enrolled = is_enrolled(db, section.id, viewer.id)
    return out


def get_section(db: Session, section_id: int) -> CourseSection:
    section = repo.get(db, section_id)
    if section is None:
        raise AppError("NOT_FOUND")
    return section


def ensure_can_view(db: Session, section: CourseSection, user: User) -> None:
    """05 §5: Admin mọi lớp; GV lớp mình; SV lớp mình hoặc lớp PUBLISHED đang mở đăng ký."""
    if user.role == Role.ADMIN:
        return
    if user.role == Role.INSTRUCTOR:
        if section.instructor_id != user.id:
            raise AppError("NOT_SECTION_INSTRUCTOR")
        return
    if is_enrolled(db, section.id, user.id):
        return
    if section.status == SectionStatus.PUBLISHED and academics.is_registration_open(section.semester):
        return
    raise AppError("NOT_ENROLLED")


def list_sections(db: Session, user: User, semester_id: Optional[int], status: Optional[str]) -> List[SectionOut]:
    query = db.query(CourseSection)
    if semester_id:
        query = query.filter(CourseSection.semester_id == semester_id)
    if status:
        query = query.filter(CourseSection.status == status)
    if user.role == Role.INSTRUCTOR:
        query = query.filter(CourseSection.instructor_id == user.id)
    sections = query.join(Subject, Subject.id == CourseSection.subject_id) \
        .order_by(Subject.code, CourseSection.section_code).all()
    if user.role == Role.STUDENT:
        visible = []
        for s in sections:
            open_ = s.status == SectionStatus.PUBLISHED and academics.is_registration_open(s.semester)
            if open_ or is_enrolled(db, s.id, user.id):
                visible.append(s)
        sections = visible
    counts = repo.enrolled_counts(db, [s.id for s in sections])
    graph = academics.prerequisite_map(db)
    return [section_out(db, s, user, counts, graph) for s in sections]


def _ensure_instructor(db: Session, instructor_id: int) -> User:
    instructor = db.get(User, instructor_id)
    if instructor is None or instructor.role != Role.INSTRUCTOR or not instructor.is_active:
        raise AppError("VALIDATION_ERROR", {"field": "instructor_id", "reason": "NOT_ACTIVE_INSTRUCTOR"})
    return instructor


def create_section(db: Session, data: SectionIn) -> CourseSection:
    if db.get(Semester, data.semester_id) is None or db.get(Subject, data.subject_id) is None:
        raise AppError("NOT_FOUND")
    _ensure_instructor(db, data.instructor_id)
    code = data.section_code.strip().upper()
    if db.query(CourseSection).filter(CourseSection.semester_id == data.semester_id,
                                      CourseSection.section_code == code).first():
        raise AppError("VALIDATION_ERROR", {"field": "section_code", "reason": "DUPLICATE"})
    section = CourseSection(semester_id=data.semester_id, subject_id=data.subject_id, section_code=code,
                            instructor_id=data.instructor_id, capacity=data.capacity, status=SectionStatus.DRAFT)
    db.add(section)
    db.commit()
    return section


def _instructor_conflict(db: Session, section: CourseSection, instructor_id: int, new: Slot) -> Optional[str]:
    for other in repo.slots_in_semester(db, section.semester_id, exclude_section_id=section.id):
        if other.section.instructor_id == instructor_id and overlaps(new, _slot(other)):
            return other.section.section_code
    return None


def update_section(db: Session, section_id: int, data: SectionUpdate) -> CourseSection:
    section = get_section(db, section_id)
    ensure_not_locked(section)
    if data.section_code is not None:
        code = data.section_code.strip().upper()
        dup = db.query(CourseSection).filter(CourseSection.semester_id == section.semester_id,
                                             CourseSection.section_code == code, CourseSection.id != section.id).first()
        if dup:
            raise AppError("VALIDATION_ERROR", {"field": "section_code", "reason": "DUPLICATE"})
        section.section_code = code
    if data.capacity is not None:
        enrolled = repo.enrolled_counts(db, [section.id]).get(section.id, 0)
        if data.capacity < enrolled:
            raise AppError("VALIDATION_ERROR", {"field": "capacity", "reason": "BELOW_ENROLLED", "enrolled": enrolled})
        for slot in section.slots:
            if slot.room.capacity < data.capacity:
                raise AppError("ROOM_CAPACITY_TOO_SMALL", {"room_code": slot.room.code, "required": data.capacity})
        section.capacity = data.capacity
    if data.instructor_id is not None and data.instructor_id != section.instructor_id:
        _ensure_instructor(db, data.instructor_id)
        for slot in section.slots:
            other = _instructor_conflict(db, section, data.instructor_id, _slot(slot))
            if other:
                raise AppError("SCHEDULE_INSTRUCTOR_CONFLICT", {"section_code": other})
        section.instructor_id = data.instructor_id  # GV mới nhận toàn quyền (BR-ACD-03)
    db.commit()
    return section


def publish_section(db: Session, section_id: int) -> CourseSection:
    section = get_section(db, section_id)
    if section.status != SectionStatus.DRAFT:
        raise AppError("INVALID_STATE_TRANSITION", {"from": section.status, "to": SectionStatus.PUBLISHED})
    if not section.slots:
        raise AppError("INVALID_STATE_TRANSITION", {"reason": "NO_SCHEDULE"})
    section.status = SectionStatus.PUBLISHED
    db.commit()
    return section


def add_slot(db: Session, section_id: int, data: SlotIn) -> ScheduleSlot:
    """Không trùng phòng, không trùng GV, phòng đủ sức chứa (BR-ACD-05)."""
    section = get_section(db, section_id)
    ensure_not_locked(section)
    if not data.start_time < data.end_time:
        raise AppError("INVALID_TIME_RANGE")
    room = db.get(Room, data.room_id)
    if room is None:
        raise AppError("NOT_FOUND")
    if room.capacity < section.capacity:
        raise AppError("ROOM_CAPACITY_TOO_SMALL", {"room_code": room.code, "required": section.capacity})
    new = Slot(data.day_of_week, data.start_time, data.end_time)
    for other in section.slots:
        if overlaps(new, _slot(other)):
            raise AppError("SCHEDULE_INSTRUCTOR_CONFLICT", {"section_code": section.section_code})
    for other in repo.slots_in_semester(db, section.semester_id, exclude_section_id=section.id):
        if other.room_id == room.id and overlaps(new, _slot(other)):
            raise AppError("SCHEDULE_ROOM_CONFLICT", {"section_code": other.section.section_code,
                                                      "room_code": room.code})
    conflict = _instructor_conflict(db, section, section.instructor_id, new)
    if conflict:
        raise AppError("SCHEDULE_INSTRUCTOR_CONFLICT", {"section_code": conflict})
    slot = ScheduleSlot(section_id=section.id, room_id=room.id, day_of_week=data.day_of_week,
                        start_time=data.start_time, end_time=data.end_time)
    db.add(slot)
    db.commit()
    db.refresh(section)
    return slot


def delete_slot(db: Session, slot_id: int) -> None:
    slot = db.get(ScheduleSlot, slot_id)
    if slot is None:
        raise AppError("NOT_FOUND")
    ensure_not_locked(slot.section)
    db.delete(slot)
    db.commit()


def enrolled_student_ids(db: Session, section_id: int) -> List[int]:
    rows = db.query(Enrollment.student_id).filter(Enrollment.section_id == section_id,
                                                 Enrollment.status == EnrollmentStatus.ENROLLED).all()
    return [r[0] for r in rows]
