"""TC-ACC-*, TC-GEN-02."""
from tests.conftest import code_of


def test_admin_creates_student_with_temp_password(client, f):  # TC-ACC-01
    _, admin = f.user("ADMIN")
    r = client.post("/api/admin/users", headers=admin,
                    json={"email": "New.Student@Test.vn", "full_name": "Sinh Viên", "role": "STUDENT",
                          "student_code": "SV900"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["email"] == "new.student@test.vn" and body["user"]["must_change_password"]
    assert len(body["temp_password"]) == 12
    listed = client.get("/api/admin/users?q=new.student", headers=admin).json()
    assert listed["total"] == 1 and "temp_password" not in listed["items"][0]


def test_student_requires_code_and_email_unique(client, f):
    _, admin = f.user("ADMIN")
    payload = {"email": "x@test.vn", "full_name": "X", "role": "STUDENT"}
    assert code_of(client.post("/api/admin/users", headers=admin, json=payload)) == "VALIDATION_ERROR"
    payload["student_code"] = "SV1"
    assert client.post("/api/admin/users", headers=admin, json=payload).status_code == 201
    payload["student_code"] = "SV2"
    assert code_of(client.post("/api/admin/users", headers=admin, json=payload)) == "EMAIL_ALREADY_EXISTS"


def test_no_public_registration(client):  # TC-ACC-02
    r = client.post("/api/auth/register", json={"email": "a@b.vn", "password": "x", "role": "ADMIN"})
    assert r.status_code == 404


def test_login_case_insensitive_and_same_error(client, f):  # TC-ACC-03
    u, _ = f.user("STUDENT")
    assert client.post("/api/auth/login", json={"email": u.email.upper(), "password": "Password123"}).status_code == 200
    wrong = client.post("/api/auth/login", json={"email": u.email, "password": "nope"})
    missing = client.post("/api/auth/login", json={"email": "ghost@test.vn", "password": "nope"})
    assert code_of(wrong) == code_of(missing) == "AUTH_INVALID_CREDENTIALS"


def test_must_change_password_blocks_other_apis(client, f):  # TC-ACC-04
    _, headers = f.user("STUDENT", must_change=True)
    assert code_of(client.get("/api/me/sections", headers=headers)) == "PASSWORD_CHANGE_REQUIRED"
    assert client.get("/api/me", headers=headers).status_code == 200
    r = client.post("/api/auth/change-password", headers=headers,
                    json={"current_password": "Password123", "new_password": "NewPassword1"})
    assert r.status_code == 200
    assert client.get("/api/me/sections", headers=headers).status_code == 200


def test_password_policy(client, f):  # TC-ACC-05
    _, headers = f.user("STUDENT", must_change=True)
    for bad in ["short", "a" * 73, "Password123"]:
        r = client.post("/api/auth/change-password", headers=headers,
                        json={"current_password": "Password123", "new_password": bad})
        assert r.status_code == 422 and code_of(r) == "PASSWORD_POLICY_VIOLATION"
    long_login = client.post("/api/auth/login", json={"email": "u1@test.vn", "password": "a" * 100})
    assert code_of(long_login) == "AUTH_INVALID_CREDENTIALS"  # không còn lỗi 500 (ISS-07)


def test_disabled_account_token_rejected(client, f):  # TC-ACC-06
    _, admin = f.user("ADMIN")
    student, headers = f.user("STUDENT")
    assert client.patch(f"/api/admin/users/{student.id}", headers=admin, json={"is_active": False}).status_code == 200
    assert code_of(client.get("/api/me", headers=headers)) == "ACCOUNT_DISABLED"


def test_last_admin_protection(client, f):  # TC-ACC-07
    admin, headers = f.user("ADMIN")
    assert code_of(client.patch(f"/api/admin/users/{admin.id}", headers=headers,
                                json={"is_active": False})) == "LAST_ADMIN_REQUIRED"
    assert code_of(client.patch(f"/api/admin/users/{admin.id}", headers=headers,
                                json={"role": "INSTRUCTOR"})) == "LAST_ADMIN_REQUIRED"


def test_reset_password_requires_change(client, f):
    _, admin = f.user("ADMIN")
    student, _ = f.user("STUDENT")
    r = client.post(f"/api/admin/users/{student.id}/reset-password", headers=admin)
    assert r.status_code == 200 and r.json()["user"]["must_change_password"]
    login = client.post("/api/auth/login", json={"email": student.email, "password": r.json()["temp_password"]})
    assert login.status_code == 200


def test_import_csv_all_or_nothing(client, f):  # TC-ACC-08
    _, admin = f.user("ADMIN")
    bad = "email,full_name,role,student_code\na@t.vn,A,STUDENT,X1\nbad-email,B,STUDENT,X2\n"
    r = client.post("/api/admin/users/import", headers=admin, json={"csv_text": bad})
    assert code_of(r) == "IMPORT_INVALID_ROWS" and r.json()["error"]["params"]["rows"][0]["row"] == 3
    assert client.get("/api/admin/users?q=a@t.vn", headers=admin).json()["total"] == 0
    good = "email,full_name,role,student_code\na@t.vn,A,STUDENT,X1\ngv@t.vn,GV,INSTRUCTOR,\n"
    r = client.post("/api/admin/users/import", headers=admin, json={"csv_text": good})
    assert r.status_code == 201 and len(r.json()["created"]) == 2


def test_non_admin_cannot_manage_users(client, f):
    _, instructor = f.user("INSTRUCTOR")
    assert client.get("/api/admin/users", headers=instructor).status_code == 403


def test_auth_required_everywhere(client):  # TC-GEN-02
    for path in ["/api/me", "/api/sections", "/api/me/transcript", "/api/rooms", "/api/admin/users"]:
        r = client.get(path)
        assert r.status_code == 401 and code_of(r) == "AUTH_REQUIRED", path
