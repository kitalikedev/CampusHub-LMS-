"""Seed dữ liệu demo (05 §6). Mốc thời gian tính tương đối theo ngày chạy.

Chạy: python scripts/seed.py
Chạy lặp lại được: nếu DB đã có người dùng thì bỏ qua. Muốn làm lại từ đầu: python scripts/reset_db.py
"""
import sys
from datetime import time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

import src.models  # noqa: E402,F401
from src.core.db import SessionLocal  # noqa: E402
from src.core.security import hash_password  # noqa: E402
from src.core.time import utcnow  # noqa: E402
from src.modules.academics.models import GradeScale, Semester, Subject, subject_prerequisites  # noqa: E402
from src.modules.announcements.models import Announcement  # noqa: E402
from src.modules.assignments.models import Assignment  # noqa: E402
from src.modules.enrollments.models import Enrollment  # noqa: E402
from src.modules.grading import service as grading  # noqa: E402
from src.modules.grading.models import Grade  # noqa: E402
from src.modules.regrades.models import RegradeRequest  # noqa: E402
from src.modules.rooms.models import Room  # noqa: E402
from src.modules.sections.models import CourseSection, ScheduleSlot  # noqa: E402
from src.modules.submissions.models import Submission  # noqa: E402
from src.modules.users.models import User  # noqa: E402

DEMO_PASSWORD = "Demo@12345"  # chỉ dùng trên máy local (G5)
DOMAIN = "campushub.edu.vn"

GRADE_SCALE = [  # DEC-E2
    ("A+", "9.0", "4.0", True), ("A", "8.5", "3.7", True), ("B+", "8.0", "3.5", True), ("B", "7.0", "3.0", True),
    ("C+", "6.5", "2.5", True), ("C", "5.5", "2.0", True), ("D+", "5.0", "1.5", True), ("F", "0.0", "0.0", False),
]

INSTRUCTORS = [("nam.dh", "ThS. Đàm Huỳnh Hoài Nam"), ("alex.smith", "Dr. Alex Smith"),
               ("linh.pt", "TS. Phan Thùy Linh")]
STUDENTS = [("an.nguyen", "Nguyễn Văn An"), ("binh.tran", "Trần Thị Bình"), ("cuong.le", "Lê Quốc Cường"),
            ("dung.pham", "Phạm Minh Dũng"), ("em.vo", "Võ Thị Em"), ("giang.do", "Đỗ Hà Giang"),
            ("hai.bui", "Bùi Thanh Hải"), ("khanh.ngo", "Ngô Bảo Khánh"), ("lan.dang", "Đặng Thị Lan"),
            ("minh.ho", "Hồ Quang Minh"), ("nga.trinh", "Trịnh Thu Nga"), ("sv.moi", "Sinh Viên Mới")]

SUBJECTS = [  # code, tên, tín chỉ, tính điểm, tiên quyết
    ("CS101", "Lập trình cơ bản", 3, True, []),
    ("CS201", "Lập trình hướng đối tượng và CTDL", 4, True, ["CS101"]),
    ("CS210", "Kiến trúc máy tính", 3, True, []),
    ("CS220", "Mạng máy tính", 4, True, []),
    ("CS230", "Phân tích thiết kế hệ thống", 3, True, []),
    ("CS301", "Cơ sở dữ liệu", 3, True, ["CS101"]),
    ("CS302", "Phát triển ứng dụng Web Fullstack", 3, True, ["CS201"]),
    ("CS401", "Thiết kế hệ thống", 3, True, ["CS301", "CS302"]),
    ("MA101", "Toán rời rạc", 3, True, []),
    ("MA201", "Xác suất thống kê", 3, True, ["MA101"]),
    ("EN101", "Tiếng Anh học thuật", 2, True, []),
    ("EN102", "Tiếng Anh chuyên ngành", 2, True, []),
    ("PE101", "Giáo dục thể chất 1", 1, False, []),
    ("PE102", "Bóng chuyền", 1, False, []),
]

ROOMS = [("A102", "Giảng đường A102", 60), ("B201", "Phòng B201", 40), ("LAB301", "Phòng máy Lab 301", 30),
         ("LAB402", "Phòng máy Lab 402", 30), ("LAB501", "Phòng máy Lab 501", 35)]


def t(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


class Seeder:
    def __init__(self) -> None:
        self.db = SessionLocal()
        self.now = utcnow().replace(microsecond=0)
        self.today = self.now.date()
        self.users: Dict[str, User] = {}
        self.subjects: Dict[str, Subject] = {}
        self.rooms: Dict[str, Room] = {}
        self.semesters: Dict[str, Semester] = {}
        self.sections: Dict[str, CourseSection] = {}

    # ---------- danh mục ----------
    def catalog(self) -> None:
        db = self.db
        for letter, minimum, point, passing in GRADE_SCALE:
            db.add(GradeScale(letter=letter, min_score=Decimal(minimum), grade_point=Decimal(point),
                              is_passing=passing))
        pw = hash_password(DEMO_PASSWORD)
        db.add(User(email=f"admin@{DOMAIN}", full_name="Phòng Đào tạo", role="ADMIN", password_hash=pw,
                    must_change_password=False))
        for key, name in INSTRUCTORS:
            self.users[key] = User(email=f"{key}@{DOMAIN}", full_name=name, role="INSTRUCTOR", password_hash=pw,
                                   must_change_password=False)
            db.add(self.users[key])
        for index, (key, name) in enumerate(STUDENTS, start=1):
            self.users[key] = User(email=f"{key}@{DOMAIN}", full_name=name, role="STUDENT",
                                   student_code=f"SV{index:03d}", password_hash=pw,
                                   must_change_password=(key == "sv.moi"))
            db.add(self.users[key])
        for code, name, credits, graded, _ in SUBJECTS:
            self.subjects[code] = Subject(code=code, name=name, credits=credits, is_graded=graded)
            db.add(self.subjects[code])
        for code, name, capacity in ROOMS:
            self.rooms[code] = Room(code=code, name=name, capacity=capacity)
            db.add(self.rooms[code])
        db.flush()
        for code, *_rest, prereqs in SUBJECTS:
            for prereq in prereqs:
                db.execute(subject_prerequisites.insert().values(subject_id=self.subjects[code].id,
                                                                 prerequisite_id=self.subjects[prereq].id))
        d = self.today
        self.semesters["2026-1"] = Semester(
            code="2026-1", name="Học kỳ 1 năm học 2026", start_date=d - timedelta(days=300),
            end_date=d - timedelta(days=160), registration_start_at=self.now - timedelta(days=330),
            registration_end_at=self.now - timedelta(days=310), min_credits=6, max_credits=24)
        self.semesters["2026-2"] = Semester(
            code="2026-2", name="Học kỳ 2 năm học 2026", start_date=d - timedelta(days=60),
            end_date=d + timedelta(days=60), registration_start_at=self.now - timedelta(days=90),
            registration_end_at=self.now - timedelta(days=62), min_credits=6, max_credits=24)
        self.semesters["2027-1"] = Semester(
            code="2027-1", name="Học kỳ 1 năm học 2027", start_date=d + timedelta(days=70),
            end_date=d + timedelta(days=190), registration_start_at=self.now - timedelta(days=7),
            registration_end_at=self.now + timedelta(days=14), min_credits=6, max_credits=9)
        for s in self.semesters.values():
            db.add(s)
        db.flush()

    def section(self, semester: str, code: str, subject: str, instructor: str, capacity: int,
                slots: List[tuple], status: str = "PUBLISHED") -> CourseSection:
        section = CourseSection(semester_id=self.semesters[semester].id, subject_id=self.subjects[subject].id,
                                section_code=code, instructor_id=self.users[instructor].id, capacity=capacity,
                                status=status)
        self.db.add(section)
        self.db.flush()
        for day, start, end, room in slots:
            self.db.add(ScheduleSlot(section_id=section.id, room_id=self.rooms[room].id, day_of_week=day,
                                     start_time=t(start), end_time=t(end)))
        self.sections[f"{semester}/{code}"] = section
        return section

    def enroll(self, section: CourseSection, students: List[str], days_ago: int = 0) -> None:
        for key in students:
            self.db.add(Enrollment(section_id=section.id, student_id=self.users[key].id, status="ENROLLED",
                                   source="SELF", enrolled_at=self.now - timedelta(days=days_ago)))
        self.db.flush()

    def assignment(self, section: CourseSection, title: str, weight: str, mode: str, *,
                   due_days: Optional[float] = None, late: Optional[str] = None, attempts: Optional[int] = None,
                   visibility: str = "IMMEDIATE", description: str = "") -> Assignment:
        item = Assignment(section_id=section.id, title=title, description=description or None,
                          weight_percent=Decimal(weight), submission_mode=mode, max_attempts=attempts,
                          due_at=self.now + timedelta(days=due_days) if due_days is not None else None,
                          late_policy=late, grade_visibility=visibility, created_by=section.instructor_id,
                          created_at=self.now - timedelta(days=30))
        self.db.add(item)
        self.db.flush()
        return item

    def submit(self, item: Assignment, student: str, days_ago: float, attempt: int = 1,
               url: Optional[str] = None) -> None:
        at = self.now - timedelta(days=days_ago)
        self.db.add(Submission(assignment_id=item.id, student_id=self.users[student].id, attempt_no=attempt,
                               content_url=url or f"https://github.com/{student}/{item.id}-v{attempt}",
                               is_late=item.due_at is not None and at > item.due_at, submitted_at=at))
        self.db.flush()

    def grade(self, item: Assignment, student: str, score: str, feedback: str = "") -> None:
        self.db.commit()
        section = self.db.get(CourseSection, item.section_id)
        grading.put_grade(self.db, section.instructor, item.id, self.users[student].id, score, feedback or None)

    # ---------- kịch bản ----------
    def past_semester(self) -> None:
        """2026-1 đã khóa sổ: có kết quả, có môn F, có môn Non-Graded."""
        students = ["an.nguyen", "binh.tran", "cuong.le", "dung.pham", "em.vo", "giang.do", "hai.bui",
                    "khanh.ngo"]
        cs101 = self.section("2026-1", "CS101-01", "CS101", "nam.dh", 40, [(2, "08:00", "10:30", "B201")])
        ma101 = self.section("2026-1", "MA101-01", "MA101", "alex.smith", 40, [(4, "08:00", "10:30", "B201")])
        pe101 = self.section("2026-1", "PE101-01", "PE101", "linh.pt", 60, [(6, "07:00", "09:00", "A102")])
        for s in (cs101, ma101, pe101):
            self.enroll(s, students, days_ago=320)
        scores = {  # (giữa kỳ, cuối kỳ)
            "CS101": [("8.5", "9.0"), ("7.0", "8.0"), ("6.0", "7.5"), ("9.0", "9.5"), ("5.0", "6.0"),
                      ("8.0", "8.5"), ("7.5", "7.0"), ("6.5", "8.0")],
            "MA101": [("8.0", "8.6"), ("7.5", "7.0"), ("4.0", "5.0"), ("8.5", "9.0"), ("6.0", "5.5"),
                      ("3.5", "4.0"), ("7.0", "8.0"), ("9.0", "9.5")],
            "PE101": [("8.0", "8.0"), ("7.0", "7.0"), ("6.0", "6.0"), ("9.0", "9.0"), ("4.0", "4.5"),
                      ("8.0", "8.0"), ("7.0", "7.0"), ("6.0", "6.0")],
        }
        for section, code in ((cs101, "CS101"), (ma101, "MA101"), (pe101, "PE101")):
            mid = self.assignment(section, "Thi giữa kỳ", "40", "OFFLINE")
            final = self.assignment(section, "Thi cuối kỳ", "60", "OFFLINE")
            for key, (m, f) in zip(students, scores[code]):
                self.grade(mid, key, m)
                self.grade(final, key, f)
            self.db.commit()
            grading.lock(self.db, section.instructor, section.id)

    def current_semester(self) -> None:
        """2026-2 đang học: đủ 4 chế độ nộp, 2 chính sách trễ, điểm ẩn, phúc khảo, lớp chờ khóa sổ."""
        cls = ["an.nguyen", "binh.tran", "cuong.le", "dung.pham", "em.vo", "giang.do"]
        cs201 = self.section("2026-2", "CS201-01", "CS201", "nam.dh", 30,
                             [(2, "08:00", "10:30", "LAB402"), (5, "13:30", "16:00", "LAB402")])
        self.enroll(cs201, cls, days_ago=70)
        attend = self.assignment(cs201, "Chuyên cần", "10", "OFFLINE")
        hw1 = self.assignment(cs201, "Bài tập 1 – Lớp và đối tượng", "15", "SINGLE", due_days=-10, late="REJECT",
                              description="Cài đặt lớp Student, Course và quan hệ giữa chúng.")
        hw2 = self.assignment(cs201, "Bài tập 2 – Cấu trúc dữ liệu", "15", "OVERWRITE", due_days=5,
                              late="ACCEPT_MARK_LATE", description="Cài đặt Stack, Queue và Binary Search Tree.")
        proj = self.assignment(cs201, "Bài tập 3 – Đồ án nhỏ", "20", "MULTIPLE", due_days=12, late="REJECT",
                               attempts=3, visibility="MANUAL",
                               description="Ứng dụng quản lý thư viện. Được nộp tối đa 3 lần, GV chấm bản cuối.")
        lab = self.assignment(cs201, "Lab 4 – Xử lý ngoại lệ", "10", "SINGLE", due_days=-1,
                              late="ACCEPT_MARK_LATE", description="Hạn đã qua; vẫn nhận bài nhưng gắn nhãn trễ.")
        self.assignment(cs201, "Thi giữa kỳ", "30", "OFFLINE")
        for key, score in zip(cls, ["9.0", "8.0", "7.5", "10", "6.0", "8.5"]):
            self.grade(attend, key, score)
        for key in ["binh.tran", "cuong.le", "dung.pham"]:
            self.submit(hw1, key, days_ago=12)
        self.grade(hw1, "binh.tran", "7.0", "Thiếu phần kiểm thử đơn vị.")
        self.grade(hw1, "cuong.le", "8.5")
        self.grade(hw1, "dung.pham", "9.0", "Thiết kế lớp rõ ràng.")
        self.submit(hw2, "binh.tran", days_ago=1)
        self.submit(proj, "binh.tran", days_ago=3, attempt=1)
        self.submit(proj, "binh.tran", days_ago=1, attempt=2)
        self.submit(proj, "an.nguyen", days_ago=2, attempt=1)
        self.grade(proj, "binh.tran", "8.0", "Đã cải thiện so với lần nộp đầu.")  # ẩn tới khi GV công bố
        self.submit(lab, "dung.pham", days_ago=2)
        self.db.commit()
        cuong_grade = self.db.query(Grade).filter(Grade.assignment_id == attend.id,
                                                  Grade.student_id == self.users["cuong.le"].id).one()
        self.db.add(RegradeRequest(grade_id=cuong_grade.id, old_score=cuong_grade.score,
                                   reason="Em có mặt đủ các buổi, xin thầy kiểm tra lại điểm chuyên cần."))

        cs301 = self.section("2026-2", "CS301-01", "CS301", "alex.smith", 40, [(3, "08:00", "10:30", "B201")])
        self.enroll(cs301, ["an.nguyen", "binh.tran", "cuong.le", "dung.pham"], days_ago=70)
        big = self.assignment(cs301, "Bài tập lớn – Thiết kế CSDL", "40", "SINGLE", due_days=-5, late="REJECT")
        exam = self.assignment(cs301, "Thi cuối kỳ", "60", "OFFLINE")
        for key, (b, e) in zip(["an.nguyen", "binh.tran", "cuong.le", "dung.pham"],
                               [("9.0", "8.4"), (None, "7.0"), ("6.0", "4.0"), ("8.0", "9.0")]):
            self.submit(big, key, days_ago=6)
            if b is not None:
                self.grade(big, key, b)
            self.grade(exam, key, e)

        en101 = self.section("2026-2", "EN101-01", "EN101", "linh.pt", 35, [(4, "13:30", "15:30", "LAB501")])
        self.enroll(en101, ["an.nguyen", "em.vo", "giang.do"], days_ago=70)
        essay = self.assignment(en101, "Essay 1 – Academic Writing", "30", "OVERWRITE", due_days=3, late="REJECT")
        self.assignment(en101, "Thi cuối kỳ", "70", "OFFLINE")
        self.submit(essay, "em.vo", days_ago=1)

        for section, title, content in [
            (cs201, "Lịch thi giữa kỳ", "Thi giữa kỳ vào tuần 9 tại phòng Lab 402. Mang theo thẻ sinh viên."),
            (cs301, "Chuẩn bị khóa sổ điểm", "Thầy sẽ khóa sổ điểm sau khi chấm xong bài tập lớn."),
            (en101, "Tài liệu tham khảo", "Đã cập nhật danh sách bài đọc cho Essay 1."),
        ]:
            self.db.add(Announcement(section_id=section.id, author_id=section.instructor_id, title=title,
                                     content=content, created_at=self.now - timedelta(days=2)))

    def registration_semester(self) -> None:
        """2027-1 đang mở đăng ký: đủ chỗ, trùng lịch, thiếu tiên quyết, vượt tín chỉ, trùng phòng."""
        ma201 = self.section("2027-1", "MA201-01", "MA201", "alex.smith", 40, [(2, "09:00", "11:00", "B201")])
        self.enroll(ma201, ["an.nguyen"], days_ago=3)
        self.section("2027-1", "CS210-01", "CS210", "nam.dh", 30, [(3, "13:30", "16:00", "LAB301")])
        self.section("2027-1", "CS220-01", "CS220", "linh.pt", 30, [(5, "08:00", "11:00", "LAB402")])
        en102 = self.section("2027-1", "EN102-01", "EN102", "linh.pt", 2, [(4, "08:00", "10:00", "A102")])
        self.enroll(en102, ["lan.dang", "minh.ho"], days_ago=2)
        self.section("2027-1", "PE102-01", "PE102", "linh.pt", 40, [(2, "10:00", "11:30", "A102")])
        self.section("2027-1", "CS401-01", "CS401", "nam.dh", 30, [(6, "08:00", "10:30", "LAB501")])
        self.section("2027-1", "CS302-01", "CS302", "nam.dh", 30, [(4, "13:30", "16:00", "LAB402")])
        self.section("2027-1", "CS230-01", "CS230", "alex.smith", 30, [], status="DRAFT")

    def run(self) -> None:
        db = self.db
        if db.query(User.id).first() is not None:
            print("DB đã có dữ liệu, bỏ qua seed. Muốn làm lại: python scripts/reset_db.py")
            return
        self.catalog()
        db.commit()
        self.past_semester()
        self.current_semester()
        self.registration_semester()
        db.commit()
        print("Seed xong. Mật khẩu demo cho mọi tài khoản:", DEMO_PASSWORD)
        print(f"  Admin: admin@{DOMAIN}")
        print(f"  Giảng viên: nam.dh@{DOMAIN}, alex.smith@{DOMAIN}, linh.pt@{DOMAIN}")
        print(f"  Sinh viên: an.nguyen@{DOMAIN} (SV demo chính), binh.tran@{DOMAIN}, …")
        print(f"  Đăng nhập lần đầu (phải đổi mật khẩu): sv.moi@{DOMAIN}")
        db.close()


if __name__ == "__main__":
    Seeder().run()
