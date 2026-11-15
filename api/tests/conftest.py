"""Test chạy trên SQLite in-memory (ADR-15). Biến môi trường phải đặt trước khi import src."""
import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="campushub-test-")
os.environ["JWT_SECRET"] = "test-secret-test-secret-test-secret-0123456789"
os.environ["BCRYPT_ROUNDS"] = "4"

from datetime import time, timedelta  # noqa: E402
from decimal import Decimal  # noqa: E402
from typing import Dict, Optional, Sequence, Tuple  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import src.models  # noqa: E402,F401
from src.core.db import Base, SessionLocal, engine  # noqa: E402
from src.core.security import create_access_token, hash_password  # noqa: E402
from src.core.time import utcnow  # noqa: E402
from src.main import app  # noqa: E402
from src.modules.academics.models import GradeScale, Semester, Subject, subject_prerequisites  # noqa: E402
from src.modules.assignments.models import Assignment  # noqa: E402
from src.modules.enrollments.models import CourseResult, Enrollment  # noqa: E402
from src.modules.rooms.models import Room  # noqa: E402
from src.modules.sections.models import CourseSection, ScheduleSlot  # noqa: E402
from src.modules.users.models import User  # noqa: E402

SCALE = [("A+", "9.0", "4.0", True), ("A", "8.5", "3.7", True), ("B+", "8.0", "3.5", True),
         ("B", "7.0", "3.0", True), ("C+", "6.5", "2.5", True), ("C", "5.5", "2.0", True),
         ("D+", "5.0", "1.5", True), ("F", "0.0", "0.0", False)]


class Factory:
    """Tạo dữ liệu test nhanh (08 §1). Mỗi hàm commit ngay."""

    def __init__(self, db) -> None:
        self.db = db
        self.n = 0

    def _next(self) -> int:
        self.n += 1
        return self.n

    def user(self, role: str = "STUDENT", must_change: bool = False, password: str = "Password123",
             active: bool = True) -> Tuple[User, Dict[str, str]]:
        i = self._next()
        u = User(email=f"u{i}@test.vn", full_name=f"User {i}", role=role,
                 student_code=f"S{i:04d}" if role == "STUDENT" else None,
                 password_hash=hash_password(password), must_change_password=must_change, is_active=active)
        self.db.add(u)
        self.db.commit()
        return u, {"Authorization": f"Bearer {create_access_token(u.id, u.role)}"}

    def semester(self, open_: bool = True, max_credits: int = 24, min_credits: int = 0,
                 offset_days: int = 0) -> Semester:
        i, now = self._next(), utcnow()
        start = now.date() + timedelta(days=offset_days * 1000 + i * 200)
        s = Semester(code=f"T{i}", name=f"Term {i}", start_date=start, end_date=start + timedelta(days=120),
                     registration_start_at=now - timedelta(days=1) if open_ else now - timedelta(days=10),
                     registration_end_at=now + timedelta(days=1) if open_ else now - timedelta(days=5),
                     min_credits=min_credits, max_credits=max_credits)
        self.db.add(s)
        self.db.commit()
        return s

    def subject(self, credits: int = 3, graded: bool = True, prereqs: Sequence[Subject] = ()) -> Subject:
        i = self._next()
        s = Subject(code=f"SUB{i}", name=f"Subject {i}", credits=credits, is_graded=graded)
        self.db.add(s)
        self.db.flush()
        for p in prereqs:
            self.db.execute(subject_prerequisites.insert().values(subject_id=s.id, prerequisite_id=p.id))
        self.db.commit()
        return s

    def room(self, capacity: int = 50) -> Room:
        i = self._next()
        r = Room(code=f"R{i}", name=f"Room {i}", capacity=capacity)
        self.db.add(r)
        self.db.commit()
        return r

    def section(self, semester: Semester, subject: Subject, instructor: User, capacity: int = 30,
                slots: Sequence[Tuple[int, str, str]] = ((2, "08:00", "10:00"),), status: str = "PUBLISHED",
                room: Optional[Room] = None) -> CourseSection:
        i = self._next()
        sec = CourseSection(semester_id=semester.id, subject_id=subject.id, section_code=f"C{i}",
                            instructor_id=instructor.id, capacity=capacity, status=status)
        self.db.add(sec)
        self.db.flush()
        room = room or self.room(max(capacity, 50))
        for day, start, end in slots:
            h1, m1 = map(int, start.split(":"))
            h2, m2 = map(int, end.split(":"))
            self.db.add(ScheduleSlot(section_id=sec.id, room_id=room.id, day_of_week=day,
                                     start_time=time(h1, m1), end_time=time(h2, m2)))
        self.db.commit()
        return sec

    def enroll(self, section: CourseSection, student: User) -> Enrollment:
        e = Enrollment(section_id=section.id, student_id=student.id, status="ENROLLED", source="SELF")
        self.db.add(e)
        self.db.commit()
        return e

    def passed(self, student: User, subject: Subject, instructor: User, passed: bool = True) -> None:
        """SV đã có kết quả môn (lớp đã khóa sổ ở kỳ trước)."""
        sec = self.section(self.semester(open_=False, offset_days=-1), subject, instructor, status="LOCKED")
        e = self.enroll(sec, student)
        self.db.add(CourseResult(enrollment_id=e.id, final_score_10=Decimal("8") if passed else Decimal("3"),
                                 letter_grade="B+" if passed else "F",
                                 grade_point=Decimal("3.5") if passed else Decimal("0"), is_passed=passed))
        self.db.commit()

    def assignment(self, section: CourseSection, weight: str = "100", mode: str = "SINGLE",
                   due_days: Optional[float] = 3, late: Optional[str] = "REJECT", attempts: Optional[int] = None,
                   visibility: str = "IMMEDIATE") -> Assignment:
        if mode == "OFFLINE":
            due_days, late = None, None
        a = Assignment(section_id=section.id, title=f"A{self._next()}", weight_percent=Decimal(weight),
                       submission_mode=mode, max_attempts=attempts if mode == "MULTIPLE" else None,
                       due_at=utcnow() + timedelta(days=due_days) if due_days is not None else None,
                       late_policy=late, grade_visibility=visibility, created_by=section.instructor_id)
        self.db.add(a)
        self.db.commit()
        return a


@pytest.fixture()
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    for letter, minimum, point, passing in SCALE:
        session.add(GradeScale(letter=letter, min_score=Decimal(minimum), grade_point=Decimal(point),
                               is_passing=passing))
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(db) -> TestClient:
    return TestClient(app)


@pytest.fixture()
def f(db) -> Factory:
    return Factory(db)


def code_of(response) -> str:
    return response.json().get("error", {}).get("code", "")
