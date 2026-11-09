# 10 — Đặc tả việc giao

> Phiên bản 0.1 · 2026-11-09 · Mỗi việc có mã T-xx; nhánh git đặt tên `feat/T-xx-<mô-tả-ngắn>` (AGENTS.md).

## 1. Thành viên

| Vai trò | Tên (điền) | Trách nhiệm chính |
|---|---|---|
| Lead | | Code phần lớn backend và frontend; vẽ Sequence/Class; duyệt mọi PR và sơ đồ; giữ tài liệu khớp code |
| TV1 | | Use Case, đặc tả use case, Activity; module thông báo lớp; thời khóa biểu; bản tiếng Anh |
| TV2 | | BPMN, ERD, lược đồ quan hệ; module phòng học; thông báo hệ thống; nhật ký thao tác |

## 2. Lộ trình làm quen cho TV1, TV2

1. Đọc 00-INDEX → 01-AS-IS → 03-BUSINESS-RULES (đặc biệt §3, §4, §7).
2. Chạy app trên máy mình theo AGENTS.md; đăng nhập thử bằng tài khoản seed ở cả ba vai trò.
3. Vẽ bộ sơ đồ as-is (T-01, T-02). Đây là cách nhanh nhất để hiểu hệ thống hiện tại.
4. Đọc 05-DATA-MODEL và 06-ARCHITECTURE §2, §4, rồi nhận việc code đầu tiên. TV2 làm T-20 (module mẫu); TV1 làm T-19 theo mẫu đó.
5. Gặp chỗ nghiệp vụ chưa rõ thì **không đoán**: ghi câu hỏi và hỏi Lead.

## 3. Mẫu đặc tả một việc

> **Mã – Tên** · Phụ trách · Giai đoạn · Cỡ (S ≤ nửa ngày, M ≤ 1 ngày, L ≤ 2 ngày)
> - **Phụ thuộc:** việc/mốc phải xong trước
> - **Thư mục:** nơi được sửa (ngoài thư mục này thì hỏi Lead)
> - **Hành vi mong muốn:** mô tả ngắn, dẫn chiếu FR/BR/AC
> - **Test cần có:** mã TC ở 08 §2
> - **Bàn giao:** file/PR, người duyệt

## 4. Danh sách việc

| Mã | Việc | Phụ trách | Giai đoạn | Phụ thuộc | Cỡ |
|---|---|---|---|---|---|
| T-01 | Sơ đồ as-is: UC-ASIS-01, ACT-ASIS-01 | TV1 | P2' | — | M |
| T-02 | Sơ đồ as-is: BPMN-ASIS-01, ERD-ASIS-01 | TV2 | P2' | — | M |
| T-03 | Sơ đồ as-is: SEQ-ASIS-01, CLS-ASIS-01 | Lead | P2' | — | S |
| T-04 | Use case to-be UC-01 và đặc tả use case | TV1 | P2' | M-1 | L |
| T-05 | Activity to-be ACT-01…06 | TV1 | P2' | T-04 | L |
| T-06 | BPMN to-be BPMN-01…03 (`.drawio` + `.bpmn`) | TV2 | P2' | M-1 | L |
| T-07 | ERD-01 và lược đồ quan hệ REL-01 | TV2 | P2' | M-1 | M |
| T-08 | Sequence SEQ-01…06, Class CLS-01, CLS-02 | Lead | P2' | M-2 | L |
| T-09 | Duyệt chéo sơ đồ, xuất PNG, cập nhật as-built | TV1, TV2 | P5 | T-04…T-08 | M |
| T-10 | P0: repo chung, `.gitignore`, `requirements.txt`, `.env.example`, README, khung test | Lead | P0 | — | M |
| T-11 | Backend core: config, errors, permissions, deps, time | Lead | P2 | T-10 | M |
| T-12 | Schema to-be: migration `0001_initial_schema` và seed demo (05 §6) | Lead | P2 | T-11, M-1 | L |
| T-13 | Module auth + users (bỏ register; tạo, reset, khóa, đổi vai trò) | Lead | P2 | T-12 | M |
| T-14 | Module academics: học kỳ, môn học, tiên quyết, bảng quy đổi | Lead | P2 | T-12 | M |
| T-15 | Module sections và lịch học (kiểm tra trùng phòng/GV) | Lead | P2 | T-14, T-20 | M |
| T-16 | Module enrollments (ràng buộc đăng ký, khóa dòng) | Lead | P2 | T-15 | L |
| T-17 | Module assignments + submissions (4 chế độ, nộp trễ, link) | Lead | P2 | T-16 | L |
| T-18 | Module grading + transcripts: chấm, công bố, sổ điểm, khóa/mở sổ, GPA | Lead | P2 | T-17 | L |
| T-19 | Module announcements theo cấu trúc mới | TV1 | P2 | T-15, T-20 | S |
| T-20 | Module rooms (việc mẫu để học cấu trúc backend) | TV2 | P2 | T-11, T-12 | S |
| T-21 | Frontend nền: `components/ui`, AppShell, `lib/api`, `lib/i18n`, auth guard, navigation | Lead | P3 | M-1 | L |
| T-22 | Trang Admin: người dùng, học kỳ, môn học, lớp học phần và lịch | Lead | P3 | T-21, T-13…T-16 | L |
| T-23 | Trang Admin: phòng học | TV2 | P3 | T-21, T-20 | S |
| T-24 | Trang SV: tổng quan, đăng ký học phần, lớp của tôi, chi tiết lớp/bài, nộp bài, bảng điểm | Lead | P3 | T-21, T-16…T-18 | L |
| T-25 | Trang GV: chi tiết lớp (các tab), chấm bài, khóa sổ | Lead | P3 | T-21, T-17, T-18 | L |
| T-26 | Thời khóa biểu/lịch dạy (lưới tuần) và tab Thông báo lớp | TV1 | P3 | T-21, T-15, T-19 | M |
| T-27a | (S) Thông báo hệ thống: backend + chuông thông báo | TV2 | P4 | T-21 | M |
| T-27b | (S) Phúc khảo | Lead | P4 | T-18 | M |
| T-27c | (S) Upload file bài nộp | Lead | P4 | T-17 | M |
| T-27d | (S) Import CSV tài khoản | Lead | P4 | T-13 | S |
| T-27e | (S) Bản dịch tiếng Anh | TV1 | P4 | T-21 | S |
| T-27f | (S/C) Ghi và xem nhật ký thao tác | TV2 | P4 | T-11 | M |
| T-29 | Chạy thử kịch bản demo, quay video dự phòng, làm slide | Cả nhóm | P5 | M-3 | M |

## 5. Đặc tả chi tiết các việc của TV1, TV2

### Sơ đồ

**T-01 – Sơ đồ as-is: Use case và Activity** · TV1 · P2' · M
- **Phụ thuộc:** không. **Thư mục:** `docs/diagrams/as-is/`.
- **Hành vi:** vẽ UC-ASIS-01 và ACT-ASIS-01 đúng nội dung ở 07 §3; dữ liệu lấy từ 01-AS-IS và chạy thử app.
- **Bàn giao:** `.drawio` + `.png`; đạt checklist 07 §6; Lead duyệt.

**T-02 – Sơ đồ as-is: BPMN và ERD** · TV2 · P2' · M
- **Phụ thuộc:** không. **Thư mục:** `docs/diagrams/as-is/`.
- **Hành vi:** BPMN-ASIS-01 (cả `.drawio` và `.bpmn`) và ERD-ASIS-01 (7 bảng ở 01 §4).
- **Bàn giao:** như T-01.

**T-04 – Use case to-be và đặc tả** · TV1 · P2' · L
- **Phụ thuộc:** M-1. **Thư mục:** `docs/diagrams/to-be/`.
- **Hành vi:** UC-01 gồm trang tổng quát và các trang theo tác nhân (07 §4.1, đủ 26 use case, có «include»/«extend»); đặc tả cho 10 use case bắt buộc, luồng ngoại lệ lấy từ cột "Mã lỗi" ở 03.
- **Bàn giao:** `UC-01.drawio` + PNG; đặc tả đặt ở `docs/diagrams/to-be/UC-specs.md`.

**T-05 – Activity to-be** · TV1 · P2' · L
- **Phụ thuộc:** T-04. **Thư mục:** `docs/diagrams/to-be/`.
- **Hành vi:** ACT-01…06 theo 07 §4.2; mỗi điểm rẽ nhánh ghi mã BR; ACT-02 theo đúng thứ tự kiểm tra ở 03 §3.

**T-06 – BPMN to-be** · TV2 · P2' · L
- **Phụ thuộc:** M-1. **Thư mục:** `docs/diagrams/to-be/`.
- **Hành vi:** BPMN-01…03 theo 07 §4.5 (pool/lane, timer event, gateway); làm cả `.drawio` và `.bpmn` cho tới khi chốt OQ-02.

**T-07 – ERD và lược đồ quan hệ** · TV2 · P2' · M
- **Phụ thuộc:** M-1. **Thư mục:** `docs/diagrams/to-be/`.
- **Hành vi:** ERD-01 (18 bảng, crow's foot, PK/FK, UQ chính) và REL-01, khớp đúng 05 §2.

**T-09 – Duyệt chéo và as-built** · TV1, TV2 · P5 · M
- **Phụ thuộc:** T-04…T-08. **Hành vi:** TV1 duyệt BPMN/ERD, TV2 duyệt Use Case/Activity theo checklist 07 §6; sửa các sơ đồ ghi ở 09 §3; xuất toàn bộ PNG vào `docs/diagrams/export/`.

### Code

**T-20 – Module rooms (việc mẫu)** · TV2 · P2 · S
- **Phụ thuộc:** T-11, T-12. **Thư mục:** `api/src/modules/rooms/`, `api/tests/api/test_rooms.py`.
- **Hành vi:** `GET /api/rooms` (đã đăng nhập), `POST /api/rooms`, `PATCH /api/rooms/{id}`, `DELETE /api/rooms/{id}` (Admin). Mã phòng duy nhất, lưu chữ hoa; sức chứa > 0; không xóa phòng đang có lịch → `ROOM_IN_USE` (BR-ACD-06, FR-ACD-03). Làm đúng phân tầng ở 06 §2.2: router mỏng, service kiểm tra rule, repository không commit.
- **Test cần có:** tạo hợp lệ; SV/GV tạo → 403; sức chứa 0 → 422; trùng mã → 422; xóa phòng đang dùng → 409.
- **Bàn giao:** PR `feat/T-20-rooms`; Lead review. Module này sẽ là mẫu cho các module khác.

**T-19 – Module announcements** · TV1 · P2 · S
- **Phụ thuộc:** T-15, T-20 (làm theo mẫu). **Thư mục:** `api/src/modules/announcements/`, `api/tests/api/test_announcements.py`.
- **Hành vi:** endpoint ở 06 §3.2 (nhóm Thông báo lớp); quyền theo BR-ANN-01, dùng `ensure_section_instructor` và `ensure_section_member` trong `core/permissions.py`. Khi T-27a đã xong thì gọi service thông báo hệ thống để báo cho SV của lớp.
- **Test cần có:** TC-ANN-01, TC-ANN-02.

**T-23 – Trang Phòng học** · TV2 · P3 · S
- **Phụ thuộc:** T-21, T-20. **Thư mục:** `web/src/features/rooms/`, `web/src/app/(app)/admin/rooms/`, khóa dịch `rooms.*` trong `messages/*.json`.
- **Hành vi:** SCR-A05: bảng phòng, form tạo/sửa trong Dialog, xác nhận khi xóa; đủ trạng thái ở 04 §4; lỗi hiển thị theo mã (`ROOM_IN_USE`…); chỉ dùng component trong `components/ui`.
- **Kiểm tra:** `npm run lint`, `npx tsc --noEmit`, `npm run build`; checklist 08 §3.

**T-26 – Thời khóa biểu và tab Thông báo lớp** · TV1 · P3 · M
- **Phụ thuộc:** T-21, T-15, T-19. **Thư mục:** `web/src/features/schedule/`, `web/src/features/announcements/`, các trang `student/schedule`, `instructor/schedule`.
- **Hành vi:** component `WeeklyTimetable` (7 cột Thứ Hai–Chủ nhật × khung giờ) dùng cho SCR-S06 và SCR-I06, lấy dữ liệu từ `GET /api/me/schedule`. Giờ học là giờ địa phương, hiển thị nguyên văn, **không** quy đổi múi giờ. Tên thứ lấy từ bản dịch. Component danh sách và form thông báo lớp để Lead gắn vào tab của SCR-S04, SCR-I03.

**T-27a – Thông báo hệ thống** · TV2 · P4 · M
- **Phụ thuộc:** T-21. **Thư mục:** `api/src/modules/notifications/`, `web/src/components/layout/NotificationBell.tsx`, `web/src/features/notifications/`.
- **Hành vi:** service `notify(user_ids, type, params, link)` ghi trong cùng transaction với thao tác gốc; endpoint ở 06 §3.2; chuông thông báo đếm chưa đọc, polling 60 giây (ADR-11); trang SCR-C04. Lead gắn lời gọi `notify` vào các module của mình theo BR-NOT-01.
- **Test cần có:** TC-NOT-01; chỉ người nhận đọc được thông báo của mình.

**T-27e – Bản dịch tiếng Anh** · TV1 · P4 · S
- **Phụ thuộc:** T-21. **Thư mục:** `web/src/lib/i18n/messages/en.json`, `web/scripts/check-i18n.mjs`.
- **Hành vi:** dịch đủ mọi khóa; viết script nhỏ so sánh khóa giữa `vi.json` và `en.json`, báo khóa thiếu.

**T-27f – Nhật ký thao tác** · TV2 · P4 · M
- **Phụ thuộc:** T-11. **Thư mục:** `api/src/modules/audit/`, (C) `web/src/features/audit/`, `web/src/app/(app)/admin/audit-logs/`.
- **Hành vi:** `AuditService.log(actor, action, entity_type, entity_id, before, after, reason)` ghi trong cùng transaction; `GET /api/admin/audit-logs` lọc theo người làm, loại, thời gian; (C) màn hình SCR-A07. Danh sách sự kiện theo BR-AUD-01.
- **Test cần có:** TC-GRD-06; người không phải Admin gọi → 403.
