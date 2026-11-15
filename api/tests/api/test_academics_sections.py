"""TC-ACD-*, phòng học (T-20)."""
from tests.conftest import code_of


def _slot(client, headers, section_id, room_id, day=2, start="08:00", end="10:00"):
    return client.post(f"/api/sections/{section_id}/schedule-slots", headers=headers,
                       json={"room_id": room_id, "day_of_week": day, "start_time": start, "end_time": end})


def test_room_conflict(client, f):  # TC-ACD-01
    _, admin = f.user("ADMIN")
    gv1, _ = f.user("INSTRUCTOR")
    gv2, _ = f.user("INSTRUCTOR")
    sem, room = f.semester(), f.room(60)
    first = f.section(sem, f.subject(), gv1, slots=(), status="DRAFT")
    other = f.section(sem, f.subject(), gv2, slots=(), status="DRAFT")
    assert _slot(client, admin, first.id, room.id).status_code == 201
    r = _slot(client, admin, other.id, room.id, start="09:00", end="11:00")
    assert code_of(r) == "SCHEDULE_ROOM_CONFLICT" and r.json()["error"]["params"]["section_code"] == first.section_code


def test_instructor_conflict(client, f):  # TC-ACD-02
    _, admin = f.user("ADMIN")
    gv, _ = f.user("INSTRUCTOR")
    sem = f.semester()
    f.section(sem, f.subject(), gv, slots=((3, "13:00", "15:00"),))
    other = f.section(sem, f.subject(), gv, slots=(), status="DRAFT")
    assert code_of(_slot(client, admin, other.id, f.room().id, day=3, start="14:00", end="16:00")) \
        == "SCHEDULE_INSTRUCTOR_CONFLICT"


def test_room_capacity_and_adjacent_slots(client, f):  # TC-ACD-03
    _, admin = f.user("ADMIN")
    gv, _ = f.user("INSTRUCTOR")
    sem = f.semester()
    section = f.section(sem, f.subject(), gv, capacity=40, slots=(), status="DRAFT")
    assert code_of(_slot(client, admin, section.id, f.room(30).id)) == "ROOM_CAPACITY_TOO_SMALL"
    room = f.room(50)
    assert _slot(client, admin, section.id, room.id, start="08:00", end="10:00").status_code == 201
    assert _slot(client, admin, section.id, room.id, start="10:00", end="12:00").status_code == 201
    assert code_of(_slot(client, admin, section.id, room.id, start="11:00", end="09:00")) == "INVALID_TIME_RANGE"


def test_prerequisite_cycle(client, f):  # TC-ACD-04
    _, admin = f.user("ADMIN")
    a = f.subject()
    b = f.subject(prereqs=[a])
    r = client.put(f"/api/subjects/{a.id}/prerequisites", headers=admin, json={"prerequisite_ids": [b.id]})
    assert code_of(r) == "PREREQUISITE_CYCLE"
    assert code_of(client.put(f"/api/subjects/{a.id}/prerequisites", headers=admin,
                              json={"prerequisite_ids": [a.id]})) == "PREREQUISITE_CYCLE"


def test_draft_hidden_until_published(client, f):  # TC-ACD-05
    _, admin = f.user("ADMIN")
    gv, _ = f.user("INSTRUCTOR")
    _, student = f.user("STUDENT")
    sem = f.semester()
    section = f.section(sem, f.subject(), gv, status="DRAFT")
    assert all(s["id"] != section.id for s in client.get("/api/sections", headers=student).json())
    assert client.post(f"/api/sections/{section.id}/publish", headers=admin).status_code == 200
    assert any(s["id"] == section.id for s in client.get("/api/sections", headers=student).json())
    assert code_of(client.post(f"/api/sections/{section.id}/publish", headers=admin)) == "INVALID_STATE_TRANSITION"


def test_instructor_sees_only_own_sections(client, f):
    gv1, h1 = f.user("INSTRUCTOR")
    gv2, _ = f.user("INSTRUCTOR")
    sem = f.semester()
    mine = f.section(sem, f.subject(), gv1)
    theirs = f.section(sem, f.subject(), gv2)
    assert [s["id"] for s in client.get("/api/sections", headers=h1).json()] == [mine.id]
    assert code_of(client.get(f"/api/sections/{theirs.id}", headers=h1)) == "NOT_SECTION_INSTRUCTOR"


def test_rooms_crud_and_in_use(client, f):  # T-20
    _, admin = f.user("ADMIN")
    _, student = f.user("STUDENT")
    assert client.post("/api/rooms", headers=student, json={"code": "x", "name": "x", "capacity": 1}).status_code == 403
    assert client.post("/api/rooms", headers=admin, json={"code": "x", "name": "x", "capacity": 0}).status_code == 422
    r = client.post("/api/rooms", headers=admin, json={"code": "lab9", "name": "Lab 9", "capacity": 30})
    assert r.status_code == 201 and r.json()["code"] == "LAB9"
    dup = client.post("/api/rooms", headers=admin, json={"code": "LAB9", "name": "x", "capacity": 3})
    assert code_of(dup) == "VALIDATION_ERROR"
    gv, _ = f.user("INSTRUCTOR")
    room = f.room()
    f.section(f.semester(), f.subject(), gv, room=room)
    assert code_of(client.delete(f"/api/rooms/{room.id}", headers=admin)) == "ROOM_IN_USE"
    assert client.delete(f"/api/rooms/{r.json()['id']}", headers=admin).status_code == 204
