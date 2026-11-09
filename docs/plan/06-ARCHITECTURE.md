# 06 — Kiến trúc hệ thống (to-be)

> Phiên bản 0.1 · 2026-11-09 · Liên quan: 03 (BR), 05 (dữ liệu), 07 (sơ đồ Class/Sequence/Component)

## 1. Tổng quan

```
Trình duyệt ──► Next.js 16 (client components, i18n, gọi API bằng axios)
                    │  HTTPS/JSON, header Authorization: Bearer <JWT>
                    ▼
               FastAPI (router → service → domain/repository)
                    │  SQLAlchemy 2 (transaction do service quản lý)
                    ▼
               MySQL 8 (InnoDB)          Ổ đĩa local: api/storage/uploads (file bài nộp)
```

- Một backend dạng monolith chia module theo tính năng; không dùng microservice (đúng quy mô đồ án).
- Frontend chỉ gọi API, không truy cập DB trực tiếp.
- Mọi rule nghiệp vụ nằm ở backend: tính toán thuần ở `src/domain`, điều phối và kiểm tra quyền ở service.

## 2. Backend

### 2.1 Cấu trúc thư mục

```
api/
├── alembic.ini
├── migrations/                 # Alembic: env.py, versions/0001_initial_schema.py, …
├── scripts/
│   ├── seed.py                 # seed dữ liệu demo, chạy lặp lại được
│   └── reset_db.py             # chỉ dùng cho dev: xóa và tạo lại DB (phải xác nhận)
├── storage/uploads/            # file bài nộp (không commit)
├── src/
│   ├── main.py                 # tạo app, đăng ký router của các module (điểm cắm module)
│   ├── core/
│   │   ├── config.py           # Settings; bắt buộc có JWT_SECRET, không có giá trị mặc định
│   │   ├── db.py               # engine, SessionLocal, Base, get_db
│   │   ├── security.py         # bcrypt, JWT, sinh mật khẩu tạm
│   │   ├── deps.py             # get_current_user (kiểm tra is_active, must_change_password)
│   │   ├── permissions.py      # ensure_admin, ensure_section_instructor, ensure_enrolled, ensure_section_member
│   │   ├── errors.py           # AppError, bộ xử lý lỗi, danh mục mã lỗi (03 §8)
│   │   └── time.py             # utcnow(), chuẩn hóa và serialize UTC kèm "Z"
│   ├── domain/                 # logic thuần, không đụng DB (ADR-04)
│   │   ├── grading.py          # điểm môn, quy đổi chữ/hệ 4, GPA, TBC, làm tròn Decimal
│   │   ├── schedule.py         # kiểm tra hai buổi học có trùng không
│   │   └── submission_policy.py# quyết định được nộp không, có trễ không, là lần nộp thứ mấy
│   └── modules/
│       ├── auth/               # đăng nhập, đổi mật khẩu
│       ├── users/              # quản lý tài khoản, import CSV
│       ├── academics/          # học kỳ, môn học, tiên quyết, bảng quy đổi
│       ├── rooms/              # phòng học (module mẫu cho thành viên mới, T-20)
│       ├── sections/           # lớp học phần, lịch học
│       ├── enrollments/        # đăng ký học, kết quả môn (course_results)
│       ├── assignments/        # bài tập/cột điểm
│       ├── submissions/        # bài nộp, file
│       ├── grading/            # điểm, công bố, sổ điểm, khóa/mở sổ
│       ├── transcripts/        # bảng điểm, GPA, thời khóa biểu cá nhân, dashboard
│       ├── regrades/           # phúc khảo
│       ├── announcements/      # thông báo lớp
│       ├── notifications/      # thông báo hệ thống
│       ├── audit/              # nhật ký thao tác
│       └── stats/              # thống kê cho Admin
│           (mỗi module gồm: models.py, schemas.py, repository.py, service.py, router.py)
└── tests/
    ├── conftest.py             # SQLite in-memory, TestClient, hàm tạo dữ liệu mẫu
    ├── unit/                   # test domain/ (tính điểm, trùng lịch, chính sách nộp)
    └── api/                    # test theo BR qua HTTP
```

### 2.2 Quy tắc phân tầng

| Tầng | Được làm | Không được làm |
|---|---|---|
| `router.py` | Khai báo endpoint, kiểm tra schema đầu vào, gọi một hàm service, chọn status code | Chứa rule nghiệp vụ, truy vấn DB |
| `service.py` | Kiểm tra quyền (`core/permissions`), kiểm tra BR, gọi `domain/`, gọi repository, **commit/rollback transaction**, gọi notifications/audit | Trả về object HTTP |
| `domain/*.py` | Hàm thuần: nhận dữ liệu, trả kết quả | Import SQLAlchemy, FastAPI |
| `repository.py` | Truy vấn và ghi bằng SQLAlchemy | Commit, kiểm tra quyền, rule nghiệp vụ |

**Phụ thuộc giữa module chỉ đi một chiều:**
`users → academics, rooms → sections → enrollments → assignments → submissions → grading → transcripts`; `regrades` dựa trên `grading`; `announcements` dựa trên `sections` và `enrollments`. Riêng `notifications` và `audit` là module lá: module khác gọi vào, còn hai module này không gọi ngược ra.
Module chỉ gọi **service** của module khác, không gọi repository của module khác.

### 2.3 Luồng một request (ví dụ SV đăng ký lớp, dùng để vẽ SEQ-02)

1. `POST /api/sections/{id}/enrollments/self` → `enrollments/router.py`.
2. `get_current_user` giải mã JWT, tải user, chặn nếu bị khóa (BR-ACC-06) hoặc phải đổi mật khẩu (BR-ACC-04).
3. `EnrollmentService.self_enroll(user, section_id)` mở transaction, khóa dòng lớp bằng `SELECT … FOR UPDATE`.
4. Service kiểm tra lần lượt theo thứ tự ở 03 §3, gọi `domain/schedule.py` để xét trùng lịch.
5. Hợp lệ thì repository ghi `enrollments` và service commit; không hợp lệ thì ném `AppError(code, params)` và rollback.
6. Bộ xử lý lỗi chuyển `AppError` thành JSON (§3.1). Router trả 201 kèm thông tin đăng ký.

### 2.4 Transaction và xử lý đồng thời

- Service là "unit of work": một thao tác nghiệp vụ là một transaction; repository chỉ `add`/`flush`, không `commit` (sửa cách làm hiện tại, nơi mỗi repository tự commit).
- Đăng ký học khóa dòng `course_sections` để không vượt sĩ số (BR-ENR-03).
- Khóa sổ chạy trong một transaction: tính kết quả → ghi `course_results` → đổi trạng thái lớp → tạo thông báo → ghi nhật ký. Lỗi ở bất kỳ bước nào thì rollback toàn bộ.
- Notifications và audit được ghi trong **cùng transaction** với thao tác gốc, nên không có trường hợp thao tác thành công mà thiếu nhật ký.

### 2.5 Lỗi

```json
{ "error": { "code": "SCHEDULE_CONFLICT", "message": "Trùng lịch với lớp CS302-01", "params": { "section_code": "CS302-01", "day": 2, "start": "08:00", "end": "10:30" } } }
```

- `code` là hợp đồng với frontend (03 §8). `message` chỉ để debug; giao diện hiển thị bản dịch theo `code` và `params`.
- Lỗi validation của FastAPI được chuyển về cùng dạng, với `code = VALIDATION_ERROR` và `params.fields`.
- Lỗi không lường trước trả 500 với `code = INTERNAL_ERROR`, không lộ stack trace.

### 2.6 Xác thực và phân quyền

- Đăng nhập bằng email + mật khẩu → JWT HS256 (`sub` = user id, `role`, `exp` = 1 ngày).
- Mỗi request đều tải lại user từ DB, nên khóa tài khoản hay đổi vai trò có hiệu lực ngay.
- Phân quyền hai lớp: theo vai trò (`require_roles`) và theo tài nguyên (`core/permissions.py`), theo ma trận ở 05 §5.

### 2.7 Thời gian

- Python dùng `datetime.now(timezone.utc)`; DB lưu `DATETIME` theo UTC; Pydantic serialize kèm `Z` (sửa ISS-08).
- Frontend gửi thời gian dạng ISO kèm `Z` (dùng `toISOString()`) và hiển thị theo `Asia/Ho_Chi_Minh`.
- Ngoại lệ: giờ học trong lịch (`schedule_slots.start_time`, `end_time`, kiểu TIME) là giờ địa phương theo lịch trường, lưu và hiển thị nguyên văn, không quy đổi múi giờ.

### 2.8 File bài nộp

- Nhận bằng `multipart/form-data`; kiểm tra phần mở rộng, MIME, dung lượng (BR-SUB-02).
- Lưu vào `api/storage/uploads/<năm>/<tháng>/<uuid>` (tên gốc lưu trong DB); không phục vụ file tĩnh.
- Tải về qua `GET /api/files/{id}`; chỉ người nộp, GV phụ trách lớp và Admin được tải.

### 2.9 Lưu ý Python 3.9

Không dùng `match`; không viết `X | None` trong annotation mà Pydantic đọc lúc chạy (dùng `Optional[X]`); kiểm tra thư viện mới còn hỗ trợ 3.9 trước khi đề xuất cài.

## 3. Hợp đồng API

### 3.1 Quy ước

- Tiền tố `/api`; tên tài nguyên số nhiều; JSON dùng `snake_case`.
- Danh sách dài hỗ trợ `?page=&page_size=` (mặc định 20, tối đa 100) và trả `{ "items": [], "total": n }`.
- Status code: 200 đọc/sửa · 201 tạo · 204 xóa · 401 chưa đăng nhập · 403 không có quyền · 404 không tìm thấy · 409 vi phạm rule · 422 dữ liệu sai.
- Tài liệu OpenAPI tự sinh tại `/docs`; là nguồn để sinh type cho frontend (ADR-10).

### 3.2 Danh sách endpoint

| Nhóm | Phương thức và đường dẫn | Quyền | FR |
|---|---|---|---|
| Auth | `POST /auth/login` | Công khai | FR-AUTH-01 |
| | `POST /auth/change-password` | Đã đăng nhập (được gọi khi đang phải đổi mật khẩu) | FR-AUTH-02, 03 |
| | `GET /me` | Đã đăng nhập | FR-AUTH-01 |
| Người dùng | `GET /admin/users` · `POST /admin/users` | Admin | FR-USR-01, 03 |
| | `POST /admin/users/import` | Admin | FR-USR-02 |
| | `PATCH /admin/users/{id}` · `POST /admin/users/{id}/reset-password` | Admin | FR-USR-04, 05 |
| Học vụ | `GET/POST /semesters` · `PATCH /semesters/{id}` | Đọc: mọi người; ghi: Admin | FR-ACD-01 |
| | `GET/POST /subjects` · `PATCH /subjects/{id}` · `PUT /subjects/{id}/prerequisites` | Như trên | FR-ACD-02 |
| | `GET/POST /rooms` · `PATCH /rooms/{id}` · `DELETE /rooms/{id}` | Như trên | FR-ACD-03 |
| Lớp, lịch | `GET /sections?semester_id=&status=` | Lọc theo vai trò (05 §5) | FR-ACD-04, FR-ENR-01 |
| | `POST /sections` · `PATCH /sections/{id}` · `POST /sections/{id}/publish` | Admin | FR-ACD-04 |
| | `GET /sections/{id}` | Thành viên lớp, Admin | — |
| | `POST /sections/{id}/schedule-slots` · `DELETE /schedule-slots/{id}` | Admin | FR-ACD-05 |
| Đăng ký | `POST /sections/{id}/enrollments/self` · `DELETE /sections/{id}/enrollments/self` | SV | FR-ENR-02, 03 |
| | `GET /sections/{id}/enrollments` | GV phụ trách, Admin | FR-ENR-06 |
| | `POST /sections/{id}/enrollments` · `DELETE /sections/{id}/enrollments/{student_id}` | Admin | FR-ENR-04 |
| Bài tập | `GET/POST /sections/{id}/assignments` · `GET/PATCH/DELETE /assignments/{id}` | Đọc: thành viên lớp; ghi: GV phụ trách | FR-ASG-01, 02 |
| Nộp bài | `POST /assignments/{id}/submissions` (link và/hoặc file) | SV của lớp | FR-SUB-01, 02 |
| | `GET /assignments/{id}/submissions/mine` | SV | FR-SUB-03 |
| | `GET /assignments/{id}/submissions` | GV phụ trách, Admin | FR-SUB-04 |
| | `GET /files/{id}` | Người nộp, GV phụ trách, Admin | FR-SUB-02, 04 |
| Chấm điểm | `PUT /assignments/{id}/grades/{student_id}` | GV phụ trách | FR-GRD-01 |
| | `POST /assignments/{id}/publish-grades` | GV phụ trách | FR-GRD-02 |
| | `GET /sections/{id}/gradebook` | GV phụ trách, Admin | FR-GRD-03 |
| | `GET /sections/{id}/my-grades` | SV của lớp | FR-GRD-04 |
| Khóa sổ | `GET /sections/{id}/lock-check` · `POST /sections/{id}/lock` | GV phụ trách | FR-LCK-01 |
| | `POST /sections/{id}/unlock` (bắt buộc `reason`) | Admin | FR-LCK-02 |
| Cá nhân | `GET /me/transcript` | SV | FR-TRN-01 |
| | `GET /me/schedule?semester_id=` | SV, GV | FR-TRN-02 |
| | `GET /me/sections?semester_id=` | SV, GV | FR-ENR-02, 06 |
| | `GET /me/dashboard` | SV, GV | FR-DSH-01, 02 |
| Phúc khảo | `POST /grades/{id}/regrade-requests` | SV | FR-REG-01 |
| | `GET /regrade-requests?status=` | SV (của mình), GV (lớp mình) | FR-REG-01, 02 |
| | `POST /regrade-requests/{id}/resolve` | GV phụ trách | FR-REG-02 |
| Thông báo lớp | `GET/POST /sections/{id}/announcements` · `PATCH/DELETE /announcements/{id}` | Đọc: thành viên lớp; ghi: GV phụ trách | FR-ANN-01 |
| Thông báo hệ thống | `GET /me/notifications?unread=` · `POST /me/notifications/{id}/read` · `POST /me/notifications/read-all` | Người nhận | FR-NOT-01 |
| Quản trị | `GET /admin/audit-logs` · `GET /admin/stats?semester_id=` | Admin | FR-AUD-02, FR-STA-01 |

Endpoint bị bỏ so với as-is: `POST /auth/register` (BR-ACC-01). Các endpoint `/courses/...` cũ được thay bằng `/sections/...`.

## 4. Frontend

### 4.1 Cấu trúc thư mục

```
web/src/
├── app/
│   ├── login/page.tsx
│   ├── change-password/page.tsx
│   └── (app)/                       # layout chung: AppShell + kiểm tra đăng nhập
│       ├── student/{dashboard, registration, classes/[id], assignments/[id], schedule, transcript}
│       ├── instructor/{dashboard, classes/[id], assignments/[id], regrades, schedule}
│       └── admin/{dashboard, users, semesters, subjects, rooms, sections/[id], audit-logs, stats}
├── components/
│   ├── ui/                          # bộ component dùng chung (04 §6)
│   └── layout/                      # AppShell, Sidebar, Header, LanguageSwitch, NotificationBell
├── features/<tên>/                  # api.ts, hooks.ts, components/, index.ts (chỉ export qua index)
├── lib/
│   ├── api/client.ts                # axios: gắn token, chuẩn hóa lỗi thành { code, params }
│   ├── api/useApi.ts                # hook tải dữ liệu: { data, error, loading, reload }
│   ├── auth/                        # AuthProvider, RoleGate, chuyển trang khi phải đổi mật khẩu
│   ├── i18n/                        # I18nProvider, useT(), messages/vi.json, messages/en.json
│   └── format.ts                    # định dạng ngày giờ (Asia/Ho_Chi_Minh), số, điểm
├── config/navigation.ts             # menu theo vai trò (điểm cắm tính năng mới)
└── types/api.d.ts                   # sinh từ OpenAPI (ADR-10)
```

Trước khi viết code Next.js phải đọc `web/node_modules/next/dist/docs/` (Next.js 16 khác tài liệu cũ, xem `web/AGENTS.md`).

### 4.2 Ranh giới module

Trong cùng một feature dùng import tương đối. Feature khác chỉ được import qua `@/features/<tên>` (file `index.ts`). Rule ESLint thêm vào `web/eslint.config.mjs`:

```js
{
  files: ["src/**/*.{ts,tsx}"],
  rules: {
    "no-restricted-imports": ["error", {
      patterns: [{ group: ["@/features/*/*"], message: "Import tính năng khác qua index: @/features/<tên>" }],
    }],
  },
}
```

Nhờ vậy, ba người làm ba feature khác nhau ít khi sửa chung file.

### 4.3 Lấy dữ liệu và state

- Dữ liệu từ server lấy qua `useApi` (loading/error/data/reload). Hook này gom luôn cách xử lý lỗi, sửa cảnh báo lint `set-state-in-effect` hiện tại.
- State toàn cục chỉ có phiên đăng nhập (AuthProvider) và ngôn ngữ (I18nProvider). Không thêm thư viện quản lý state.

### 4.4 Điểm cắm (slot) khi thêm tính năng

- **Backend:** tạo `src/modules/<tên>/` theo mẫu, thêm một dòng `include_router` trong `main.py`.
- **Frontend:** tạo `src/features/<tên>/`, thêm route trong `app/(app)/<vai-trò>/`, thêm một mục trong `config/navigation.ts`, thêm khóa dịch vào `messages/*.json`.

### 4.5 Xác thực phía client

- Token lưu ở `localStorage` (ADR-13). `AuthProvider` gọi `GET /me` khi tải trang.
- Chưa đăng nhập → `/login`. Đang phải đổi mật khẩu → `/change-password`. Sai vai trò → trang 403. Trang không bao giờ quay vòng mãi (sửa ISS-14).

## 5. Quyết định kiến trúc (ADR)

| Mã | Quyết định | Phương án đã cân nhắc | Lý do chọn | Hệ quả |
|---|---|---|---|---|
| ADR-01 | Tách Học kỳ / Môn học / Lớp học phần | Giữ một bảng `courses` | Cần tín chỉ, tiên quyết, GPA theo kỳ, học lại về sau | Nhiều bảng hơn, nhưng ERD sát thực tế |
| ADR-02 | Bảng `grades` riêng | Điểm nằm trong `submissions` | Bài offline và SV không nộp vẫn có điểm; tránh điểm "lạc" (ISS-03) | Phải join khi hiển thị |
| ADR-03 | Lưu cố định kết quả môn khi khóa sổ | Luôn tính lại | Kết quả đã chốt không đổi theo cấu hình | Mở sổ phải xóa rồi tính lại |
| ADR-04 | Logic thuần ở `src/domain` | Viết thẳng trong service | Dễ unit test, dễ minh họa trong Class/Sequence | Thêm một thư mục |
| ADR-05 | Service quản lý transaction | Repository tự commit (như hiện tại) | Thao tác nhiều bước phải thành công hoặc hủy toàn bộ | Phải sửa toàn bộ repository |
| ADR-06 | Module theo tính năng, phụ thuộc một chiều | Giữ chia theo tầng (`routers/`, `services/`…) | Ba người làm song song, ít đụng file | Di chuyển code cũ |
| ADR-07 | Alembic | `create_all` + seed `drop_all` | Đổi schema an toàn, có lịch sử | Thêm thư viện (hỏi trước, G4) |
| ADR-08 | API trả mã lỗi, frontend dịch | API trả câu tiếng Việt | Cần UI Vi/En (DEC-F2) | Phải giữ danh mục mã lỗi đồng bộ |
| ADR-09 | i18n tự viết (context + JSON) | Thư viện `next-intl` | Không thêm phụ thuộc; nhu cầu đơn giản | Tự viết khoảng 60 dòng |
| ADR-10 | Sinh type TS từ OpenAPI bằng `openapi-typescript` (dev) — **ĐỀ XUẤT** | Viết type bằng tay | Tránh lệch hợp đồng API khi ba người cùng làm | Thêm một devDependency (hỏi trước) |
| ADR-11 | Thông báo hệ thống dạng polling 60 giây | WebSocket / SSE | Đơn giản, đủ cho demo | Trễ tối đa 60 giây |
| ADR-12 | Lưu file trên đĩa local | Cloud storage | Demo local (DEC-F3) | Khi deploy phải đổi nơi lưu |
| ADR-13 | Giữ JWT trong `localStorage` | Cookie httpOnly + refresh token | Ít thay đổi trong 2 tuần | Nợ kỹ thuật: rủi ro XSS (09 §5) |
| ADR-14 | Giữ Python 3.9 | Nâng lên 3.12 | Không cài phần mềm ngoài thư mục dự án | Hạn chế phiên bản thư viện |
| ADR-15 | Test chạy trên SQLite in-memory, cộng một lượt smoke test trên MySQL trước demo | Chỉ test trên MySQL | Nhanh, không cần Docker khi chạy test | SQLite không mô phỏng `FOR UPDATE`; kiểm tra tay trên MySQL |

## 6. Lộ trình chuyển từ code hiện tại

1. **Hạ tầng backend:** `core/` (config, errors, permissions, deps, time), Alembic, khung test.
2. **Schema mới:** migration `0001_initial_schema`, seed mới; bỏ `drop_all`.
3. **Chuyển module** từ `routers/ services/ repositories/` sang `modules/<tên>/` theo thứ tự phụ thuộc ở §2.2; xóa `POST /auth/register`.
4. **Frontend:** dựng `components/ui`, `lib/api`, `lib/i18n`, AppShell; chuyển trang cũ sang route theo vai trò; xóa trang `/register`.
5. **Dọn dẹp:** xóa code cũ không còn dùng; lint đạt 0 lỗi; cập nhật tài liệu cho khớp code (as-built).
