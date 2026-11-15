"""TC-GRD-*, TC-LCK-*, TC-TRN-02/03/06, TC-REG-*, TC-ANN-*, TC-NOT-01, TC-GEN-01."""
from decimal import Decimal

from src.modules.academics.models import GradeScale
from src.modules.audit.models import AuditLog
from src.modules.notifications.models import Notification
from tests.conftest import code_of


def _class(f, students=1, **section_kwargs):
    gv, gvh = f.user("INSTRUCTOR")
    section = f.section(f.semester(), section_kwargs.pop("subject", None) or f.subject(), gv, **section_kwargs)
    people = []
    for _ in range(students):
        s, h = f.user("STUDENT")
        f.enroll(section, s)
        people.append((s, h))
    return section, (gv, gvh), people


def _grade(client, headers, assignment, student, score):
    return client.put(f"/api/assignments/{assignment.id}/grades/{student.id}", headers=headers, json={"score": score})


def test_other_instructor_cannot_grade(client, f):  # TC-GRD-01, ISS-02
    section, _, [(student, _)] = _class(f)
    a = f.assignment(section, mode="OFFLINE")
    _, other = f.user("INSTRUCTOR")
    assert code_of(_grade(client, other, a, student, 0)) == "NOT_SECTION_INSTRUCTOR"


def test_score_range(client, f):  # TC-GRD-02
    section, (_, gvh), [(student, _)] = _class(f)
    a = f.assignment(section, mode="OFFLINE")
    for bad in [10.5, -1, 8.123, "abc"]:
        assert code_of(_grade(client, gvh, a, student, bad)) == "GRADE_OUT_OF_RANGE"
    assert _grade(client, gvh, a, student, 8.25).status_code == 200


def test_grade_without_submission_and_offline(client, f):  # TC-GRD-03
    section, (_, gvh), [(student, _)] = _class(f)
    assert _grade(client, gvh, f.assignment(section, weight="50"), student, 7).status_code == 200
    assert _grade(client, gvh, f.assignment(section, weight="50", mode="OFFLINE"), student, 6).status_code == 200


def test_manual_visibility_and_notification(client, f, db):  # TC-GRD-04, TC-NOT-01
    section, (_, gvh), [(student, svh)] = _class(f)
    manual = f.assignment(section, weight="50", mode="OFFLINE", visibility="MANUAL")
    _grade(client, gvh, manual, student, 9)
    item = client.get(f"/api/sections/{section.id}/my-grades", headers=svh).json()["items"][0]
    assert item["grade"] is None and item["grade_hidden"] is True
    assert db.query(Notification).filter(Notification.type == "GRADE_VISIBLE").count() == 0
    assert client.post(f"/api/assignments/{manual.id}/publish-grades", headers=gvh).status_code == 200
    item = client.get(f"/api/sections/{section.id}/my-grades", headers=svh).json()["items"][0]
    assert item["grade"]["score"] == 9 and item["grade"]["visible_at"].endswith("Z")
    assert db.query(Notification).filter(Notification.user_id == student.id,
                                         Notification.type == "GRADE_VISIBLE").count() == 1


def test_provisional_score(client, f):  # TC-GRD-05 (Ex6)
    section, (_, gvh), [(student, svh)] = _class(f)
    weights = {"10": None, "20": 8.0, "30": 8.5, "40": None}
    for w, score in weights.items():
        a = f.assignment(section, weight=w, mode="OFFLINE")
        if score is not None:
            _grade(client, gvh, a, student, score)
    mine = client.get(f"/api/sections/{section.id}/my-grades", headers=svh).json()
    assert mine["provisional_score"] == 8.3 and mine["graded_weight"] == 50 and mine["result"] is None


def test_grade_change_is_audited(client, f, db):  # TC-GRD-06
    section, (_, gvh), [(student, _)] = _class(f)
    a = f.assignment(section, mode="OFFLINE")
    _grade(client, gvh, a, student, 5)
    _grade(client, gvh, a, student, 6)
    log = db.query(AuditLog).filter(AuditLog.action == "GRADE_CHANGED").one()
    assert log.before_data == {"score": 5.0} and log.after_data == {"score": 6.0}


def test_lock_preconditions(client, f):  # TC-LCK-01, TC-LCK-02
    section, (_, gvh), [(student, svh)] = _class(f)
    a = f.assignment(section, weight="90")
    client.post(f"/api/assignments/{a.id}/submissions", headers=svh, data={"content_url": "https://x.y"})
    r = client.post(f"/api/sections/{section.id}/lock", headers=gvh)
    assert code_of(r) == "LOCK_PRECONDITION_FAILED"
    failed = {c["key"] for c in r.json()["error"]["params"]["failed"]}
    assert failed == {"WEIGHT_TOTAL_100", "NO_UNGRADED_SUBMISSIONS"}


def test_lock_computes_results_ex1_ex2(client, f):  # TC-LCK-03
    section, (_, gvh), [(s1, h1), (s2, _)] = _class(f, students=2)
    items = [f.assignment(section, weight=w, mode="OFFLINE") for w in ("10", "20", "30", "40")]
    for a, score in zip(items, [9.0, 8.0, 8.5, 8.9]):
        _grade(client, gvh, a, s1, score)
    for a, score in zip(items, [9.0, 8.0, None, 8.9]):
        if score is not None:
            _grade(client, gvh, a, s2, score)
    assert client.get(f"/api/sections/{section.id}/lock-check", headers=gvh).json()["can_lock"] is True
    assert client.post(f"/api/sections/{section.id}/lock", headers=gvh).status_code == 200
    rows = {r["student"]["id"]: r["result"] for r in
            client.get(f"/api/sections/{section.id}/gradebook", headers=gvh).json()["rows"]}
    assert (rows[s1.id]["final_score_10"], rows[s1.id]["letter_grade"], rows[s1.id]["grade_point"]) == (8.61, "A", 3.7)
    assert (rows[s2.id]["final_score_10"], rows[s2.id]["letter_grade"]) == (6.06, "C")
    transcript = client.get("/api/me/transcript", headers=h1).json()
    assert transcript["cumulative"]["gpa"] == 3.7


def test_locked_section_is_read_only(client, f):  # TC-LCK-04
    section, (_, gvh), [(student, svh)] = _class(f)
    a = f.assignment(section, mode="OFFLINE")
    _grade(client, gvh, a, student, 7)
    client.post(f"/api/sections/{section.id}/lock", headers=gvh)
    body = {"title": "x", "weight_percent": 1, "submission_mode": "OFFLINE"}
    assert code_of(client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=body)) == "SECTION_LOCKED"
    assert code_of(_grade(client, gvh, a, student, 9)) == "SECTION_LOCKED"
    ann = client.post(f"/api/sections/{section.id}/announcements", headers=gvh, json={"title": "t", "content": "c"})
    assert ann.status_code == 201


def test_unlock_rules(client, f, db):  # TC-LCK-05
    section, (_, gvh), [(student, _)] = _class(f)
    _grade(client, gvh, f.assignment(section, mode="OFFLINE"), student, 7)
    client.post(f"/api/sections/{section.id}/lock", headers=gvh)
    _, admin = f.user("ADMIN")
    assert client.post(f"/api/sections/{section.id}/unlock", headers=gvh, json={"reason": "x"}).status_code == 403
    assert code_of(client.post(f"/api/sections/{section.id}/unlock", headers=admin, json={})) \
        == "UNLOCK_REASON_REQUIRED"
    r = client.post(f"/api/sections/{section.id}/unlock", headers=admin, json={"reason": "Nhập sai điểm"})
    assert r.status_code == 200 and r.json()["status"] == "PUBLISHED"
    rows = client.get(f"/api/sections/{section.id}/gradebook", headers=gvh).json()["rows"]
    assert rows[0]["result"] is None
    assert db.query(AuditLog).filter(AuditLog.action == "SECTION_UNLOCKED").one().reason == "Nhập sai điểm"


def test_result_frozen_after_scale_change(client, f, db):  # TC-LCK-06
    section, (_, gvh), [(student, svh)] = _class(f)
    _grade(client, gvh, f.assignment(section, mode="OFFLINE"), student, 8.6)
    client.post(f"/api/sections/{section.id}/lock", headers=gvh)
    db.query(GradeScale).filter(GradeScale.letter == "A").update({GradeScale.min_score: Decimal("8.7")})
    db.commit()
    course = client.get("/api/me/transcript", headers=svh).json()["semesters"][0]["courses"][0]
    assert course["letter_grade"] == "A"


def test_non_graded_and_in_progress(client, f):  # TC-TRN-04, TC-TRN-06
    pe = f.subject(credits=1, graded=False)
    section, (_, gvh), [(student, svh)] = _class(f, subject=pe)
    _grade(client, gvh, f.assignment(section, mode="OFFLINE"), student, 6)
    client.post(f"/api/sections/{section.id}/lock", headers=gvh)
    other_section = f.section(f.semester(), f.subject(), section.instructor)
    f.enroll(other_section, student)
    data = client.get("/api/me/transcript", headers=svh).json()
    statuses = {c["subject_code"]: (c["status"], c["is_passed"], c["letter_grade"])
                for s in data["semesters"] for c in s["courses"]}
    assert statuses[pe.code] == ("FINALIZED", True, None)
    assert data["cumulative"] == {"gpa": None, "average_10": None, "gpa_credits": 0, "earned_credits": 0}
    assert any(v[0] == "IN_PROGRESS" for v in statuses.values())


def test_regrade_flow(client, f, db):  # TC-REG-01…03
    section, (_, gvh), [(student, svh)] = _class(f)
    a = f.assignment(section, weight="50", mode="OFFLINE")
    grade = _grade(client, gvh, a, student, 6).json()
    url = f"/api/grades/{grade['id']}/regrade-requests"
    assert code_of(client.post(url, headers=svh, json={"reason": " "})) == "REGRADE_REASON_REQUIRED"
    r = client.post(url, headers=svh, json={"reason": "Xin chấm lại câu 3"})
    assert r.status_code == 201
    assert code_of(client.post(url, headers=svh, json={"reason": "lần 2"})) == "REGRADE_EXISTS"
    assert code_of(client.post(f"/api/sections/{section.id}/lock", headers=gvh)) == "LOCK_PRECONDITION_FAILED"
    rid = r.json()["request"]["id"]
    assert code_of(client.post(f"/api/regrade-requests/{rid}/resolve", headers=gvh, json={"accept": False})) \
        == "REGRADE_REASON_REQUIRED"
    r = client.post(f"/api/regrade-requests/{rid}/resolve", headers=gvh, json={"accept": True, "new_score": 7.5})
    assert r.status_code == 200 and r.json()["current_score"] == 7.5
    assert db.query(Notification).filter(Notification.type == "REGRADE_RESOLVED").count() == 1


def test_announcements_permissions(client, f):  # TC-ANN-01, TC-ANN-02
    section, (_, gvh), [(_, svh)] = _class(f)
    _, other_gv = f.user("INSTRUCTOR")
    _, outsider = f.user("STUDENT")
    url = f"/api/sections/{section.id}/announcements"
    assert client.post(url, headers=other_gv, json={"title": "t", "content": "c"}).status_code == 403
    assert client.post(url, headers=gvh, json={"title": "t", "content": "c"}).status_code == 201
    assert client.get(url, headers=outsider).status_code == 403
    assert len(client.get(url, headers=svh).json()) == 1
    notes = client.get("/api/me/notifications", headers=svh).json()
    assert notes["unread_count"] == 1 and notes["items"][0]["type"] == "ANNOUNCEMENT_POSTED"


def test_datetimes_end_with_z(client, f):  # TC-GEN-01
    section, _, [(_, svh)] = _class(f)
    f.assignment(section)
    a = client.get(f"/api/sections/{section.id}/assignments", headers=svh).json()[0]
    assert a["due_at"].endswith("Z") and a["created_at"].endswith("Z")


def test_gradebook_csv_export(client, f):  # TC-GRD-07 (BR-GRD-07)
    section, (_, gvh), [(s1, h1)] = _class(f)
    a = f.assignment(section, weight="100", mode="OFFLINE")
    a.title = "=HYPERLINK(x)"
    f.db.commit()
    _grade(client, gvh, a, s1, 8.5)
    assert client.get(f"/api/sections/{section.id}/gradebook.csv", headers=h1).status_code == 403
    other, ogh = f.user("INSTRUCTOR")
    assert client.get(f"/api/sections/{section.id}/gradebook.csv", headers=ogh).status_code == 403
    r = client.get(f"/api/sections/{section.id}/gradebook.csv", headers=gvh)
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    assert "attachment" in r.headers["content-disposition"]
    assert r.content.startswith(b"\xef\xbb\xbf")  # BOM UTF-8
    lines = r.content.decode("utf-8-sig").splitlines()
    assert lines[0].startswith("student_code,full_name,email,'=HYPERLINK(x)")  # chống công thức
    assert s1.email in lines[1] and "8.5" in lines[1]
