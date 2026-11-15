"""Chấm điểm, công bố, sổ điểm, khóa/mở sổ (BR-GRD-01…06, BR-LCK-01…07)."""
import csv
import io
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.errors import AppError
from src.core.permissions import ensure_admin, ensure_enrolled, ensure_not_locked, ensure_section_instructor, is_enrolled
from src.core.time import utcnow
from src.domain import grading as calc
from src.modules.academics import service as academics
from src.modules.assignments.models import Assignment, GradeVisibility, SubmissionMode
from src.modules.audit import service as audit
from src.modules.audit.service import AuditAction
from src.modules.enrollments import service as enrollments
from src.modules.enrollments.models import CourseResult, Enrollment
from src.modules.grading.models import Grade
from src.modules.notifications import service as notifications
from src.modules.notifications.service import NotificationType
from src.modules.regrades.models import RegradeRequest, RegradeStatus
from src.modules.sections import service as sections
from src.modules.sections.models import CourseSection, SectionStatus
from src.modules.submissions import service as submissions
from src.modules.users.models import User


def parse_score(value: Any) -> Decimal:
    """0.00–10.00, tối đa 2 chữ số thập phân (BR-GRD-01)."""
    try:
        score = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise AppError("GRADE_OUT_OF_RANGE")
    if score.is_nan() or score < 0 or score > 10 or score != score.quantize(Decimal("0.01")):
        raise AppError("GRADE_OUT_OF_RANGE")
    return score


def _is_visible_mode(assignment: Assignment) -> bool:
    return assignment.grade_visibility == GradeVisibility.IMMEDIATE or assignment.grades_published_at is not None


def _notify_visible(db: Session, assignment: Assignment, section: CourseSection, student_ids: List[int]) -> None:
    if student_ids:
        notifications.notify(db, student_ids, NotificationType.GRADE_VISIBLE,
                             {"title": assignment.title, "section_code": section.section_code},
                             f"/student/assignments/{assignment.id}")  # BR-GRD-06


def reveal_grades(db: Session, assignment: Assignment, section: CourseSection) -> None:
    """Cho mọi điểm còn ẩn của bài bắt đầu hiện (không commit)."""
    now, revealed = utcnow(), []
    for grade in db.query(Grade).filter(Grade.assignment_id == assignment.id, Grade.visible_at.is_(None)):
        grade.visible_at = now
        revealed.append(grade.student_id)
    _notify_visible(db, assignment, section, revealed)


def _load(db: Session, assignment_id: int):
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise AppError("NOT_FOUND")
    return assignment, sections.get_section(db, assignment.section_id)


def put_grade(db: Session, instructor: User, assignment_id: int, student_id: int, score_value: Any,
              feedback: Optional[str]) -> Grade:
    assignment, section = _load(db, assignment_id)
    ensure_section_instructor(section, instructor)  # BR-GRD-03
    ensure_not_locked(section)
    if not is_enrolled(db, section.id, student_id):
        raise AppError("NOT_ENROLLED")
    score = parse_score(score_value)
    feedback = (feedback or "").strip() or None
    grade = db.query(Grade).filter(Grade.assignment_id == assignment.id, Grade.student_id == student_id).first()
    now = utcnow()
    if grade is None:
        grade = Grade(assignment_id=assignment.id, student_id=student_id, score=score, feedback=feedback,
                      graded_by=instructor.id, graded_at=now)
        db.add(grade)
    else:
        if grade.score != score:
            audit.log(db, instructor, AuditAction.GRADE_CHANGED, "grade", grade.id,
                      before={"score": grade.score}, after={"score": score})
        grade.score, grade.feedback, grade.graded_by = score, feedback, instructor.id
    if grade.visible_at is None and _is_visible_mode(assignment):
        grade.visible_at = now
        _notify_visible(db, assignment, section, [student_id])
    db.commit()
    return grade


def publish_grades(db: Session, instructor: User, assignment_id: int) -> Assignment:
    assignment, section = _load(db, assignment_id)
    ensure_section_instructor(section, instructor)
    ensure_not_locked(section)
    if assignment.grade_visibility != GradeVisibility.MANUAL:
        raise AppError("INVALID_STATE_TRANSITION", {"reason": "NOT_MANUAL"})
    assignment.grades_published_at = assignment.grades_published_at or utcnow()
    reveal_grades(db, assignment, section)
    audit.log(db, instructor, AuditAction.GRADES_PUBLISHED, "assignment", assignment.id)
    db.commit()
    return assignment


def _assignments(db: Session, section_id: int) -> List[Assignment]:
    return db.query(Assignment).filter(Assignment.section_id == section_id) \
        .order_by(Assignment.due_at.is_(None), Assignment.due_at, Assignment.id).all()


def _grades_by_student(db: Session, assignment_ids: List[int]) -> Dict[int, Dict[int, Grade]]:
    result: Dict[int, Dict[int, Grade]] = {}
    if assignment_ids:
        for grade in db.query(Grade).filter(Grade.assignment_id.in_(assignment_ids)):
            result.setdefault(grade.student_id, {})[grade.assignment_id] = grade
    return result


def gradebook(db: Session, user: User, section_id: int) -> Dict[str, Any]:
    section = sections.get_section(db, section_id)
    sections.ensure_can_view(db, section, user)
    if user.role == "STUDENT":
        raise AppError("FORBIDDEN")
    items = _assignments(db, section.id)
    grades = _grades_by_student(db, [a.id for a in items])
    results = {e.student_id: e.result for e in enrollments.section_roster(db, section.id)}
    rows = []
    for enrollment in enrollments.section_roster(db, section.id):
        mine = grades.get(enrollment.student_id, {})
        provisional, weight = calc.provisional_score(
            (mine[a.id].score if a.id in mine else None, a.weight_percent) for a in items)
        result = results.get(enrollment.student_id)
        rows.append({
            "student": enrollment.student,
            "scores": {a.id: (mine[a.id].score if a.id in mine else None) for a in items},
            "provisional_score": calc.round_half_up(provisional) if provisional is not None else None,
            "graded_weight": weight,
            "result": result,
        })
    return {"section_id": section.id, "status": section.status, "assignments": items,
            "weight_total": sum((a.weight_percent for a in items), Decimal(0)), "rows": rows}


def assignment_status(assignment: Assignment, latest, grade: Optional[Grade], locked: bool) -> Dict[str, Any]:
    """Đúng một trạng thái hiển thị cho mỗi bài (AC-SUB-03.1, ISS-04)."""
    visible = grade is not None and (grade.visible_at is not None or locked)
    if visible:
        status = "GRADED"
    elif assignment.submission_mode == SubmissionMode.OFFLINE:
        status = "OFFLINE"
    elif latest is not None:
        status = "LATE" if latest.is_late else "SUBMITTED"
    else:
        status = "NOT_SUBMITTED"
    return {"status": status, "visible": visible, "grade_hidden": grade is not None and not visible}


def my_grades(db: Session, student: User, section_id: int) -> Dict[str, Any]:
    section = sections.get_section(db, section_id)
    ensure_enrolled(db, section, student)
    locked = section.status == SectionStatus.LOCKED
    items = _assignments(db, section.id)
    mine = _grades_by_student(db, [a.id for a in items]).get(student.id, {})
    rows, visible_scores = [], []
    for a in items:
        latest, count = submissions.latest_by_student(db, a.id).get(student.id, (None, 0))
        grade = mine.get(a.id)
        info = assignment_status(a, latest, grade, locked)
        regrade = None
        if grade is not None and info["visible"]:
            regrade = db.query(RegradeRequest).filter(RegradeRequest.grade_id == grade.id).first()
        rows.append({"assignment": a, "attempts_count": count, "latest": latest, **info,
                     "grade": grade if info["visible"] else None, "regrade": regrade})
        visible_scores.append((grade.score if info["visible"] else None, a.weight_percent))
    provisional, weight = calc.provisional_score(visible_scores)
    enrollment = db.query(Enrollment).filter(Enrollment.section_id == section.id,
                                             Enrollment.student_id == student.id).first()
    return {"section_id": section.id, "status": section.status, "items": rows,
            "provisional_score": calc.round_half_up(provisional) if provisional is not None else None,
            "graded_weight": weight, "result": enrollment.result if enrollment else None}


def lock_checks(db: Session, section: CourseSection) -> List[Dict[str, Any]]:
    """Bốn điều kiện khóa sổ (BR-LCK-01)."""
    items = _assignments(db, section.id)
    total = sum((a.weight_percent for a in items), Decimal(0))
    roster = {e.student_id for e in enrollments.section_roster(db, section.id)}
    grades = _grades_by_student(db, [a.id for a in items])
    ungraded = []
    for a in items:
        missing = [sid for sid, _ in submissions.latest_by_student(db, a.id).items()
                   if sid in roster and a.id not in grades.get(sid, {})]
        if missing:
            ungraded.append({"assignment_id": a.id, "title": a.title, "count": len(missing)})
    pending = db.query(RegradeRequest).join(Grade, Grade.id == RegradeRequest.grade_id) \
        .filter(Grade.assignment_id.in_([a.id for a in items] or [0]),
                RegradeRequest.status == RegradeStatus.PENDING).count()
    return [
        {"key": "WEIGHT_TOTAL_100", "ok": total == Decimal(100), "params": {"total": float(total)}},
        {"key": "NO_UNGRADED_SUBMISSIONS", "ok": not ungraded,
         "params": {"count": sum(u["count"] for u in ungraded), "assignments": ungraded}},
        {"key": "NO_PENDING_REGRADES", "ok": pending == 0, "params": {"count": pending}},
        {"key": "SECTION_PUBLISHED", "ok": section.status == SectionStatus.PUBLISHED,
         "params": {"status": section.status}},
    ]


def lock_check(db: Session, user: User, section_id: int) -> Dict[str, Any]:
    section = sections.get_section(db, section_id)
    ensure_section_instructor(section, user)
    checks = lock_checks(db, section)
    return {"can_lock": all(c["ok"] for c in checks), "checks": checks}


def lock(db: Session, instructor: User, section_id: int) -> CourseSection:
    section = sections.get_section(db, section_id)
    ensure_section_instructor(section, instructor)
    checks = lock_checks(db, section)
    failed = [c for c in checks if not c["ok"]]
    if failed:
        raise AppError("LOCK_PRECONDITION_FAILED", {"failed": failed})
    try:
        items = _assignments(db, section.id)
        grades = _grades_by_student(db, [a.id for a in items])
        scales = academics.grade_scale_rows(db)
        now = utcnow()
        roster = enrollments.section_roster(db, section.id)
        for enrollment in roster:
            mine = grades.get(enrollment.student_id, {})
            score = calc.final_score((mine[a.id].score if a.id in mine else None, a.weight_percent)
                                     for a in items)  # bài thiếu điểm tính 0 (BR-LCK-02)
            if section.subject.is_graded:
                row = calc.to_letter(score, scales)  # BR-LCK-03
                letter, point, passed = row.letter, row.grade_point, row.is_passing
            else:
                letter, point, passed = None, None, score >= calc.NON_GRADED_PASS_SCORE  # BR-LCK-05
            if enrollment.result is not None:
                db.delete(enrollment.result)
                db.flush()
            db.add(CourseResult(enrollment_id=enrollment.id, final_score_10=score.quantize(Decimal("0.000001")),
                                letter_grade=letter, grade_point=point, is_passed=passed, finalized_at=now))
        for a in items:  # lớp đã khóa: mọi điểm đều hiện (03 §7.4)
            for grade in db.query(Grade).filter(Grade.assignment_id == a.id, Grade.visible_at.is_(None)):
                grade.visible_at = now
        section.status, section.locked_at, section.locked_by = SectionStatus.LOCKED, now, instructor.id
        notifications.notify(db, [e.student_id for e in roster], NotificationType.RESULT_FINALIZED,
                             {"section_code": section.section_code, "subject_name": section.subject.name},
                             "/student/transcript")  # BR-LCK-07
        audit.log(db, instructor, AuditAction.SECTION_LOCKED, "section", section.id,
                  after={"students": len(roster)})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return section


def unlock(db: Session, admin: User, section_id: int, reason: str) -> CourseSection:
    """Chỉ Admin, bắt buộc lý do; xóa kết quả đã chốt (BR-LCK-06)."""
    ensure_admin(admin)
    section = sections.get_section(db, section_id)
    if section.status != SectionStatus.LOCKED:
        raise AppError("INVALID_STATE_TRANSITION", {"from": section.status, "to": SectionStatus.PUBLISHED})
    reason = (reason or "").strip()
    if not reason:
        raise AppError("UNLOCK_REASON_REQUIRED")
    enrollment_ids = [e.id for e in db.query(Enrollment.id).filter(Enrollment.section_id == section.id)]
    if enrollment_ids:
        db.query(CourseResult).filter(CourseResult.enrollment_id.in_(enrollment_ids)) \
            .delete(synchronize_session=False)
    section.status, section.locked_at, section.locked_by = SectionStatus.PUBLISHED, None, None
    audit.log(db, admin, AuditAction.SECTION_UNLOCKED, "section", section.id, reason=reason)
    db.commit()
    db.expire_all()
    return section


def pending_grading_count(db: Session, section_id: int) -> int:
    roster = {e.student_id for e in enrollments.section_roster(db, section_id)}
    items = _assignments(db, section_id)
    grades = _grades_by_student(db, [a.id for a in items])
    return sum(1 for a in items for sid in submissions.latest_by_student(db, a.id)
               if sid in roster and a.id not in grades.get(sid, {}))


def _csv_safe(value: Any) -> str:
    """Chống CSV injection: ô bắt đầu bằng = + - @ sẽ bị Excel hiểu là công thức (BR-GRD-07)."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def gradebook_csv(db: Session, user: User, section_id: int) -> "tuple[str, str]":
    """Xuất sổ điểm lớp ra CSV UTF-8 có BOM (BR-GRD-07). Trả về (tên file, nội dung)."""
    book = gradebook(db, user, section_id)
    section = sections.get_section(db, section_id)
    items = book["assignments"]
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(["student_code", "full_name", "email"]
                    + [_csv_safe("%s (%s%%)" % (a.title, format(a.weight_percent.normalize(), "f"))) for a in items]
                    + ["provisional_score", "graded_weight", "final_score_10", "letter_grade", "grade_point", "passed"])
    for row in book["rows"]:
        student, result = row["student"], row["result"]
        writer.writerow(
            [_csv_safe(student.student_code), _csv_safe(student.full_name), _csv_safe(student.email)]
            + [row["scores"][a.id] if row["scores"][a.id] is not None else "" for a in items]
            + [row["provisional_score"] if row["provisional_score"] is not None else "", row["graded_weight"],
               result.final_score_10 if result else "", (result.letter_grade or "") if result else "",
               result.grade_point if result and result.grade_point is not None else "",
               ("1" if result.is_passed else "0") if result else ""])
    filename = "gradebook_%s_%s.csv" % (section.subject.code, section.section_code)
    return filename, "\ufeff" + out.getvalue()
