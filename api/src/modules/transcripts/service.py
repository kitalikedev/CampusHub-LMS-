"""Bảng điểm/GPA (BR-TRN-01…07), lịch cá nhân, lớp của tôi, dashboard."""
from datetime import timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from src.core.time import utcnow
from src.domain import grading as calc
from src.modules.academics.models import Semester
from src.modules.announcements.models import Announcement
from src.modules.assignments.models import Assignment, SubmissionMode
from src.modules.enrollments.models import Enrollment, EnrollmentStatus
from src.modules.grading import service as grading
from src.modules.grading.models import Grade
from src.modules.regrades.models import RegradeRequest, RegradeStatus
from src.modules.sections import repository as sections_repo
from src.modules.sections import service as sections
from src.modules.sections.models import CourseSection, SectionStatus
from src.modules.submissions import service as submissions
from src.modules.users.models import Role, User


def current_semester(db: Session) -> Optional[Semester]:
    today = utcnow().date()
    current = db.query(Semester).filter(Semester.start_date <= today, Semester.end_date >= today).first()
    if current:
        return current
    upcoming = db.query(Semester).filter(Semester.start_date > today).order_by(Semester.start_date).first()
    return upcoming or db.query(Semester).order_by(Semester.start_date.desc()).first()


def my_section_models(db: Session, user: User, semester_id: Optional[int]) -> List[CourseSection]:
    query = db.query(CourseSection)
    if user.role == Role.STUDENT:
        query = query.join(Enrollment, Enrollment.section_id == CourseSection.id).filter(
            Enrollment.student_id == user.id, Enrollment.status == EnrollmentStatus.ENROLLED)
    elif user.role == Role.INSTRUCTOR:
        query = query.filter(CourseSection.instructor_id == user.id)
    if semester_id:
        query = query.filter(CourseSection.semester_id == semester_id)
    return query.order_by(CourseSection.semester_id.desc(), CourseSection.section_code).all()


def my_sections(db: Session, user: User, semester_id: Optional[int]):
    items = my_section_models(db, user, semester_id)
    counts = sections_repo.enrolled_counts(db, [s.id for s in items])
    return [sections.section_out(db, s, user, counts) for s in items]


def transcript(db: Session, student: User) -> Dict[str, Any]:
    enrollments = db.query(Enrollment).join(CourseSection, CourseSection.id == Enrollment.section_id) \
        .filter(Enrollment.student_id == student.id, Enrollment.status == EnrollmentStatus.ENROLLED).all()
    by_semester: Dict[int, Dict[str, Any]] = {}
    all_outcomes: List[calc.CourseOutcome] = []
    for e in enrollments:
        section = sections.get_section(db, e.section_id)
        subject, semester = section.subject, section.semester
        bucket = by_semester.setdefault(semester.id, {"semester": semester, "courses": [], "outcomes": []})
        course: Dict[str, Any] = {"section_id": section.id, "section_code": section.section_code,
                                  "subject_code": subject.code, "subject_name": subject.name,
                                  "credits": subject.credits, "is_graded": subject.is_graded}
        result = e.result
        if result is not None:  # BR-TRN-01: chỉ môn đã khóa sổ
            outcome = calc.CourseOutcome(subject.credits, subject.is_graded, result.final_score_10,
                                         result.grade_point, result.is_passed)  # BR-TRN-07
            bucket["outcomes"].append(outcome)
            all_outcomes.append(outcome)
            course.update(status="FINALIZED", score_10=calc.round_half_up(result.final_score_10),
                          letter_grade=result.letter_grade, grade_point=result.grade_point,
                          is_passed=result.is_passed, provisional_score=None, graded_weight=None)
        else:
            mine = grading.my_grades(db, student, section.id)
            course.update(status="IN_PROGRESS", score_10=None, letter_grade=None, grade_point=None,
                          is_passed=None, provisional_score=mine["provisional_score"],
                          graded_weight=mine["graded_weight"])
        bucket["courses"].append(course)
    semesters = []
    for bucket in sorted(by_semester.values(), key=lambda b: b["semester"].start_date):
        summary = calc.summarize(bucket["outcomes"])
        semesters.append({"semester": bucket["semester"], "courses": sorted(bucket["courses"],
                                                                            key=lambda c: c["subject_code"]),
                          "gpa": summary.gpa, "average_10": summary.average_10,
                          "gpa_credits": summary.gpa_credits, "earned_credits": summary.earned_credits})
    total = calc.summarize(all_outcomes)  # BR-TRN-04: tính lại trên toàn bộ môn
    return {"student": student, "semesters": semesters,
            "cumulative": {"gpa": total.gpa, "average_10": total.average_10,
                           "gpa_credits": total.gpa_credits, "earned_credits": total.earned_credits}}


def schedule(db: Session, user: User, semester_id: Optional[int]) -> Dict[str, Any]:
    semester = db.get(Semester, semester_id) if semester_id else current_semester(db)
    items = []
    if semester is not None:
        for section in my_section_models(db, user, semester.id):
            if user.role == Role.INSTRUCTOR and section.status == SectionStatus.DRAFT:
                continue
            for slot in section.slots:
                items.append({"section_id": section.id, "section_code": section.section_code,
                              "subject_code": section.subject.code, "subject_name": section.subject.name,
                              "instructor_name": section.instructor.full_name, "day_of_week": slot.day_of_week,
                              "start_time": slot.start_time, "end_time": slot.end_time,
                              "room_code": slot.room.code})
    items.sort(key=lambda i: (i["day_of_week"], i["start_time"]))
    return {"semester": semester, "items": items}


def dashboard(db: Session, user: User) -> Dict[str, Any]:
    semester = current_semester(db)
    mine = my_section_models(db, user, semester.id if semester else None)
    data: Dict[str, Any] = {"semester": semester, "sections": my_sections(db, user, semester.id if semester else None)}
    section_ids = [s.id for s in mine]
    data["announcements"] = db.query(Announcement).filter(Announcement.section_id.in_(section_ids or [0])) \
        .order_by(Announcement.created_at.desc()).limit(5).all()
    if user.role == Role.STUDENT:
        now = utcnow()
        upcoming = db.query(Assignment).filter(Assignment.section_id.in_(section_ids or [0]),
                                               Assignment.submission_mode != SubmissionMode.OFFLINE,
                                               Assignment.due_at >= now,
                                               Assignment.due_at <= now + timedelta(days=7)) \
            .order_by(Assignment.due_at).all()
        codes = {s.id: s.section_code for s in mine}
        rows = []
        for a in upcoming:
            latest, _count = submissions.latest_by_student(db, a.id).get(user.id, (None, 0))
            grade = db.query(Grade).filter(Grade.assignment_id == a.id, Grade.student_id == user.id).first()
            info = grading.assignment_status(a, latest, grade, False)
            rows.append({"assignment": a, "section_code": codes.get(a.section_id, ""), "status": info["status"]})
        data["upcoming"] = rows
        data["pending_grading"] = None
        data["pending_regrades"] = None
    else:
        data["upcoming"] = []
        data["pending_grading"] = sum(grading.pending_grading_count(db, sid) for sid in section_ids)
        data["pending_regrades"] = db.query(RegradeRequest).join(Grade, Grade.id == RegradeRequest.grade_id) \
            .join(Assignment, Assignment.id == Grade.assignment_id) \
            .filter(Assignment.section_id.in_(section_ids or [0]),
                    RegradeRequest.status == RegradeStatus.PENDING).count()
    return data
