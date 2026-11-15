"""TC-ASG-*, TC-SUB-*."""
from datetime import timedelta

from src.core.time import utcnow
from src.modules.submissions.models import Submission
from tests.conftest import code_of


def _setup(f, **kwargs):
    gv, gvh = f.user("INSTRUCTOR")
    student, svh = f.user("STUDENT")
    section = f.section(f.semester(), f.subject(), gv)
    f.enroll(section, student)
    assignment = f.assignment(section, **kwargs) if kwargs is not None else None
    return section, assignment, (gv, gvh), (student, svh)


def _submit(client, headers, assignment, url="https://github.com/x/y"):
    return client.post(f"/api/assignments/{assignment.id}/submissions", headers=headers, data={"content_url": url})


ASSIGNMENT = {"title": "BT", "weight_percent": 30, "submission_mode": "SINGLE", "late_policy": "REJECT"}


def test_only_section_instructor_creates(client, f):  # TC-ASG-01
    section, _, (_, gvh), _ = _setup(f, weight="10")
    _, other = f.user("INSTRUCTOR")
    body = dict(ASSIGNMENT, due_at=(utcnow() + timedelta(days=3)).isoformat() + "Z")
    assert code_of(client.post(f"/api/sections/{section.id}/assignments", headers=other, json=body)) \
        == "NOT_SECTION_INSTRUCTOR"
    assert client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=body).status_code == 201


def test_weight_total_cannot_exceed_100(client, f):  # TC-ASG-02
    section, _, (_, gvh), _ = _setup(f, weight="80")
    body = dict(ASSIGNMENT, due_at=(utcnow() + timedelta(days=3)).isoformat() + "Z")
    r = client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=body)
    assert code_of(r) == "ASSIGNMENT_WEIGHT_EXCEEDED" and r.json()["error"]["params"]["current_total"] == 80


def test_mode_validation(client, f):  # TC-ASG-03
    section, _, (_, gvh), _ = _setup(f, weight="10")
    offline = dict(ASSIGNMENT, submission_mode="OFFLINE", due_at=utcnow().isoformat() + "Z")
    assert code_of(client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=offline)) \
        == "VALIDATION_ERROR"
    multiple = dict(ASSIGNMENT, submission_mode="MULTIPLE", due_at=(utcnow() + timedelta(days=1)).isoformat() + "Z")
    assert code_of(client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=multiple)) \
        == "VALIDATION_ERROR"
    ok = {"title": "Thi", "weight_percent": 50, "submission_mode": "OFFLINE"}
    assert client.post(f"/api/sections/{section.id}/assignments", headers=gvh, json=ok).status_code == 201


def test_locked_rules_after_submission(client, f, db):  # TC-ASG-04
    _, assignment, (_, gvh), (_, svh) = _setup(f, weight="50", late="ACCEPT_MARK_LATE")
    assert _submit(client, svh, assignment).status_code == 201
    url = f"/api/assignments/{assignment.id}"
    assert code_of(client.patch(url, headers=gvh, json={"submission_mode": "MULTIPLE", "max_attempts": 2})) \
        == "ASSIGNMENT_HAS_SUBMISSIONS"
    assert code_of(client.delete(url, headers=gvh)) == "ASSIGNMENT_HAS_SUBMISSIONS"
    past = (utcnow() - timedelta(days=1)).isoformat() + "Z"
    assert client.patch(url, headers=gvh, json={"due_at": past}).status_code == 200
    db.expire_all()
    assert db.query(Submission).filter(Submission.assignment_id == assignment.id).one().is_late is True


def test_single_mode(client, f):  # TC-SUB-01
    _, a, _, (_, svh) = _setup(f, mode="SINGLE")
    assert _submit(client, svh, a).status_code == 201
    assert code_of(_submit(client, svh, a)) == "SUBMISSION_LIMIT_REACHED"


def test_overwrite_mode_keeps_one(client, f, db):  # TC-SUB-02, ISS-03
    _, a, _, (student, svh) = _setup(f, mode="OVERWRITE")
    assert _submit(client, svh, a, "https://v1.example").status_code == 201
    assert _submit(client, svh, a, "https://v2.example").status_code == 201
    rows = db.query(Submission).filter(Submission.assignment_id == a.id, Submission.student_id == student.id).all()
    assert len(rows) == 1 and rows[0].content_url == "https://v2.example"


def test_multiple_mode_limit_and_latest(client, f):  # TC-SUB-03
    _, a, (_, gvh), (student, svh) = _setup(f, mode="MULTIPLE", attempts=3)
    for i in range(3):
        assert _submit(client, svh, a, f"https://v{i}.example").status_code == 201
    assert code_of(_submit(client, svh, a)) == "SUBMISSION_LIMIT_REACHED"
    rows = client.get(f"/api/assignments/{a.id}/submissions", headers=gvh).json()
    assert rows[0]["attempts_count"] == 3 and rows[0]["latest"]["content_url"] == "https://v2.example"


def test_offline_not_allowed(client, f):  # TC-SUB-04
    _, a, _, (_, svh) = _setup(f, mode="OFFLINE")
    assert code_of(_submit(client, svh, a)) == "SUBMISSION_NOT_ALLOWED"


def test_no_submit_after_graded(client, f):  # TC-SUB-05
    _, a, (_, gvh), (student, svh) = _setup(f, mode="OVERWRITE")
    assert _submit(client, svh, a).status_code == 201
    assert client.put(f"/api/assignments/{a.id}/grades/{student.id}", headers=gvh, json={"score": 8}).status_code == 200
    assert code_of(_submit(client, svh, a)) == "SUBMISSION_ALREADY_GRADED"


def test_late_policies(client, f):  # TC-SUB-06, TC-SUB-07
    _, reject, _, (_, svh) = _setup(f, mode="SINGLE", due_days=-1, late="REJECT")
    assert code_of(_submit(client, svh, reject)) == "SUBMISSION_PAST_DUE"
    _, accept, _, (_, svh2) = _setup(f, mode="SINGLE", due_days=-1, late="ACCEPT_MARK_LATE")
    r = _submit(client, svh2, accept)
    assert r.status_code == 201 and r.json()["is_late"] is True


def test_not_enrolled_and_empty(client, f):  # TC-SUB-08
    _, a, _, (_, svh) = _setup(f)
    _, outsider = f.user("STUDENT")
    assert code_of(_submit(client, outsider, a)) == "NOT_ENROLLED"
    r = client.post(f"/api/assignments/{a.id}/submissions", headers=svh, data={})
    assert code_of(r) == "SUBMISSION_EMPTY"


def test_file_upload_and_download(client, f):  # FR-SUB-02
    _, a, (_, gvh), (_, svh) = _setup(f)
    bad = client.post(f"/api/assignments/{a.id}/submissions", headers=svh,
                      files={"file": ("virus.exe", b"x", "application/octet-stream")})
    assert code_of(bad) == "FILE_TYPE_NOT_ALLOWED"
    r = client.post(f"/api/assignments/{a.id}/submissions", headers=svh,
                    files={"file": ("report.pdf", b"%PDF-1.4 demo", "application/pdf")})
    assert r.status_code == 201
    file_id = r.json()["file"]["id"]
    assert client.get(f"/api/files/{file_id}", headers=gvh).content == b"%PDF-1.4 demo"
    _, stranger = f.user("STUDENT")
    assert client.get(f"/api/files/{file_id}", headers=stranger).status_code == 403


def test_status_labels(client, f):  # TC-SUB-09, ISS-04
    section, _, (_, gvh), (student, svh) = _setup(f, weight="10")
    not_submitted = f.assignment(section, weight="10")
    submitted = f.assignment(section, weight="10")
    late = f.assignment(section, weight="10", due_days=-1, late="ACCEPT_MARK_LATE")
    graded = f.assignment(section, weight="10")
    offline = f.assignment(section, weight="10", mode="OFFLINE")
    _submit(client, svh, submitted)
    _submit(client, svh, late)
    _submit(client, svh, graded)
    client.put(f"/api/assignments/{graded.id}/grades/{student.id}", headers=gvh, json={"score": 9})
    items = {i["assignment"]["id"]: i["status"]
             for i in client.get(f"/api/sections/{section.id}/my-grades", headers=svh).json()["items"]}
    assert items[not_submitted.id] == "NOT_SUBMITTED" and items[submitted.id] == "SUBMITTED"
    assert items[late.id] == "LATE" and items[graded.id] == "GRADED" and items[offline.id] == "OFFLINE"
