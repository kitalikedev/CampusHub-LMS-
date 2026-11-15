"""TC-ENR-01…09."""
from src.modules.audit.models import AuditLog
from tests.conftest import code_of


def _enroll(client, headers, section):
    return client.post(f"/api/sections/{section.id}/enrollments/self", headers=headers)


def test_period_closed(client, f):  # TC-ENR-01
    gv, _ = f.user("INSTRUCTOR")
    _, sv = f.user("STUDENT")
    section = f.section(f.semester(open_=False), f.subject(), gv)
    assert code_of(_enroll(client, sv, section)) == "ENROLL_PERIOD_CLOSED"


def test_section_full(client, f):  # TC-ENR-02
    gv, _ = f.user("INSTRUCTOR")
    other, _ = f.user("STUDENT")
    _, sv = f.user("STUDENT")
    section = f.section(f.semester(), f.subject(), gv, capacity=1)
    f.enroll(section, other)
    assert code_of(_enroll(client, sv, section)) == "SECTION_FULL"


def test_schedule_conflict(client, f):  # TC-ENR-03
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    sem = f.semester()
    a = f.section(sem, f.subject(), gv, slots=((2, "08:00", "10:30"),))
    b = f.section(sem, f.subject(), gv, slots=((2, "09:00", "11:00"),))
    f.enroll(a, student)
    r = _enroll(client, sv, b)
    assert code_of(r) == "SCHEDULE_CONFLICT" and r.json()["error"]["params"]["section_code"] == a.section_code


def test_prerequisite(client, f):  # TC-ENR-04
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    base = f.subject()
    advanced = f.subject(prereqs=[base])
    sem = f.semester()
    section = f.section(sem, advanced, gv, slots=((5, "08:00", "10:00"),))
    r = _enroll(client, sv, section)
    assert code_of(r) == "PREREQUISITE_NOT_MET" and r.json()["error"]["params"]["missing"] == [base.code]
    f.enroll(f.section(sem, base, gv, slots=((3, "08:00", "10:00"),)), student)  # đang học cùng kỳ: chưa tính
    assert code_of(_enroll(client, sv, section)) == "PREREQUISITE_NOT_MET"
    f.passed(student, base, gv)
    assert _enroll(client, sv, section).status_code == 201


def test_credit_limit_and_warning(client, f):  # TC-ENR-05
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    sem = f.semester(max_credits=6, min_credits=5)
    a = f.section(sem, f.subject(credits=3), gv, slots=((2, "08:00", "10:00"),))
    b = f.section(sem, f.subject(credits=4), gv, slots=((3, "08:00", "10:00"),))
    r = _enroll(client, sv, a)
    assert r.status_code == 201 and r.json()["warnings"] == ["BELOW_MIN_CREDITS"]
    r = _enroll(client, sv, b)
    assert code_of(r) == "CREDIT_LIMIT_EXCEEDED" and r.json()["error"]["params"] == {"current": 3, "adding": 4, "max": 6}


def test_subject_already_taken(client, f):  # TC-ENR-06
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    subject = f.subject()
    sem = f.semester()
    f.enroll(f.section(sem, subject, gv, slots=((2, "08:00", "10:00"),)), student)
    other = f.section(sem, subject, gv, slots=((4, "08:00", "10:00"),))
    assert code_of(_enroll(client, sv, other)) == "SUBJECT_ALREADY_TAKEN"
    student2, sv2 = f.user("STUDENT")
    f.passed(student2, subject, gv, passed=False)  # đã có kết quả F
    assert code_of(_enroll(client, sv2, other)) == "SUBJECT_ALREADY_TAKEN"


def test_drop_in_and_out_of_period(client, f):  # TC-ENR-07
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    open_section = f.section(f.semester(), f.subject(), gv)
    assert _enroll(client, sv, open_section).status_code == 201
    assert client.delete(f"/api/sections/{open_section.id}/enrollments/self", headers=sv).status_code == 204
    closed = f.section(f.semester(open_=False), f.subject(), gv)
    f.enroll(closed, student)
    assert code_of(client.delete(f"/api/sections/{closed.id}/enrollments/self", headers=sv)) == "ENROLL_PERIOD_CLOSED"


def test_admin_override_lists_all_violations(client, f, db):  # TC-ENR-08
    _, admin = f.user("ADMIN")
    gv, _ = f.user("INSTRUCTOR")
    other, _ = f.user("STUDENT")
    student, _ = f.user("STUDENT")
    section = f.section(f.semester(), f.subject(prereqs=[f.subject()]), gv, capacity=1)
    f.enroll(section, other)
    url = f"/api/sections/{section.id}/enrollments"
    r = client.post(url, headers=admin, json={"student_id": student.id})
    assert code_of(r) == "ENROLLMENT_RULES_VIOLATED"
    assert {v["code"] for v in r.json()["error"]["params"]["violations"]} == {"SECTION_FULL", "PREREQUISITE_NOT_MET"}
    r = client.post(url, headers=admin, json={"student_id": student.id, "override_reason": "Duyệt đặc cách"})
    assert r.status_code == 201 and r.json()["source"] == "ADMIN"
    assert db.query(AuditLog).filter(AuditLog.action == "ENROLLMENT_ADDED_BY_ADMIN").count() == 1


def test_reenroll_reuses_record(client, f, db):  # TC-ENR-09
    from src.modules.enrollments.models import Enrollment
    gv, _ = f.user("INSTRUCTOR")
    student, sv = f.user("STUDENT")
    section = f.section(f.semester(), f.subject(), gv)
    assert _enroll(client, sv, section).status_code == 201
    assert client.delete(f"/api/sections/{section.id}/enrollments/self", headers=sv).status_code == 204
    assert _enroll(client, sv, section).status_code == 201
    rows = db.query(Enrollment).filter(Enrollment.section_id == section.id).all()
    assert len(rows) == 1 and rows[0].status == "ENROLLED"
    assert code_of(_enroll(client, sv, section)) == "ALREADY_ENROLLED"
