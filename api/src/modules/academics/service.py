"""Học kỳ, môn học, tiên quyết, bảng quy đổi (BR-ACD-01, 02)."""
from typing import Dict, List, Optional, Set

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.time import to_naive_utc, utcnow
from src.domain.grading import ScaleRow
from src.modules.academics.models import GradeScale, Semester, Subject, subject_prerequisites
from src.modules.academics.schemas import (SemesterIn, SemesterOut, SemesterUpdate, SubjectBrief, SubjectIn,
                                           SubjectOut, SubjectUpdate)


# ---------- Học kỳ ----------

def is_registration_open(semester: Semester) -> bool:
    now = utcnow()
    return semester.registration_start_at <= now <= semester.registration_end_at


def semester_out(semester: Semester) -> SemesterOut:
    out = SemesterOut.model_validate(semester)
    out.is_registration_open = is_registration_open(semester)
    return out


def _check_semester(db: Session, s: Semester) -> None:
    if not (s.start_date < s.end_date and s.registration_start_at < s.registration_end_at
            and s.min_credits <= s.max_credits):
        raise AppError("VALIDATION_ERROR", {"reason": "INVALID_SEMESTER_RANGE"})
    overlap = db.query(Semester).filter(Semester.id != (s.id or 0), Semester.start_date <= s.end_date,
                                        Semester.end_date >= s.start_date).first()
    if overlap:
        raise AppError("VALIDATION_ERROR", {"reason": "SEMESTER_OVERLAP", "semester_code": overlap.code})


def get_semester(db: Session, semester_id: int) -> Semester:
    semester = db.get(Semester, semester_id)
    if semester is None:
        raise AppError("NOT_FOUND")
    return semester


def list_semesters(db: Session) -> List[Semester]:
    return db.query(Semester).order_by(Semester.start_date.desc()).all()


def create_semester(db: Session, data: SemesterIn) -> Semester:
    code = data.code.strip().upper()
    if db.query(Semester).filter(Semester.code == code).first():
        raise AppError("VALIDATION_ERROR", {"field": "code", "reason": "DUPLICATE"})
    semester = Semester(code=code, name=data.name.strip(), start_date=data.start_date, end_date=data.end_date,
                        registration_start_at=to_naive_utc(data.registration_start_at),
                        registration_end_at=to_naive_utc(data.registration_end_at),
                        min_credits=data.min_credits, max_credits=data.max_credits)
    _check_semester(db, semester)
    db.add(semester)
    db.commit()
    return semester


def update_semester(db: Session, semester_id: int, data: SemesterUpdate) -> Semester:
    semester = get_semester(db, semester_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is None:
            continue
        if field.startswith("registration_"):
            value = to_naive_utc(value)
        setattr(semester, field, value)
    _check_semester(db, semester)
    db.commit()
    return semester


# ---------- Môn học ----------

def prerequisite_map(db: Session) -> Dict[int, Set[int]]:
    graph: Dict[int, Set[int]] = {}
    for subject_id, prereq_id in db.execute(select(subject_prerequisites.c.subject_id,
                                                   subject_prerequisites.c.prerequisite_id)):
        graph.setdefault(subject_id, set()).add(prereq_id)
    return graph


def subject_out(db: Session, subject: Subject, graph: Optional[Dict[int, Set[int]]] = None) -> SubjectOut:
    graph = graph if graph is not None else prerequisite_map(db)
    ids = graph.get(subject.id, set())
    prereqs = db.query(Subject).filter(Subject.id.in_(ids)).order_by(Subject.code).all() if ids else []
    return SubjectOut(id=subject.id, code=subject.code, name=subject.name, credits=subject.credits,
                      is_graded=subject.is_graded, description=subject.description,
                      prerequisites=[SubjectBrief.model_validate(p) for p in prereqs])


def get_subject(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise AppError("NOT_FOUND")
    return subject


def list_subjects(db: Session) -> List[Subject]:
    return db.query(Subject).order_by(Subject.code).all()


def create_subject(db: Session, data: SubjectIn) -> Subject:
    code = data.code.strip().upper()
    if db.query(Subject).filter(Subject.code == code).first():
        raise AppError("VALIDATION_ERROR", {"field": "code", "reason": "DUPLICATE"})
    subject = Subject(code=code, name=data.name.strip(), credits=data.credits, is_graded=data.is_graded,
                      description=data.description)
    db.add(subject)
    db.commit()
    return subject


def update_subject(db: Session, subject_id: int, data: SubjectUpdate) -> Subject:
    subject = get_subject(db, subject_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None or field == "description":
            setattr(subject, field, value)
    db.commit()
    return subject


def _reaches(graph: Dict[int, Set[int]], start: int, target: int) -> bool:
    stack, seen = [start], set()
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in seen:
            continue
        seen.add(node)
        stack.extend(graph.get(node, set()))
    return False


def set_prerequisites(db: Session, subject_id: int, prerequisite_ids: List[int]) -> Subject:
    """Không tự tham chiếu, không tạo vòng lặp (BR-ACD-02)."""
    subject = get_subject(db, subject_id)
    ids = set(prerequisite_ids)
    if subject_id in ids:
        raise AppError("PREREQUISITE_CYCLE", {"subject_code": subject.code})
    if ids and db.query(Subject).filter(Subject.id.in_(ids)).count() != len(ids):
        raise AppError("NOT_FOUND")
    graph = prerequisite_map(db)
    graph[subject_id] = ids
    for prereq in ids:
        if _reaches(graph, prereq, subject_id):
            raise AppError("PREREQUISITE_CYCLE", {"subject_code": subject.code})
    db.execute(subject_prerequisites.delete().where(subject_prerequisites.c.subject_id == subject_id))
    for prereq in sorted(ids):
        db.execute(subject_prerequisites.insert().values(subject_id=subject_id, prerequisite_id=prereq))
    db.commit()
    return subject


# ---------- Bảng quy đổi ----------

def grade_scale_rows(db: Session) -> List[ScaleRow]:
    rows = db.query(GradeScale).order_by(GradeScale.min_score.desc()).all()
    return [ScaleRow(r.letter, r.min_score, r.grade_point, r.is_passing) for r in rows]


def list_grade_scales(db: Session) -> List[GradeScale]:
    return db.query(GradeScale).order_by(GradeScale.min_score.desc()).all()
