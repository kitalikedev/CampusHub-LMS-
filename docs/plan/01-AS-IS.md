# 01 — Hiện trạng hệ thống (as-is)

> Khảo sát ngày 2026-11-09 trên mã nguồn trong thư mục dự án. Đây là đầu vào cho bộ sơ đồ as-is (07-DIAGRAMS §3) và là căn cứ để giải thích "vì sao phải thiết kế lại" khi bảo vệ.

## 1. Tổng quan

- **Backend `api/`:** FastAPI, SQLAlchemy 2, MySQL 8 (chạy bằng `docker-compose`), JWT (python-jose) + bcrypt. Mã chia lớp `routers → services → repositories`. Bảng được tạo bằng `Base.metadata.create_all`, chưa có migration. Python 3.9 (venv).
- **Frontend `web/`:** Next.js 16.3.2, React 19, Tailwind v4, axios. Toàn bộ trang là client component; token lưu trong `localStorage`.
- **Lịch sử:** 2026-08-23 làm nền tảng (auth, khóa học, thông báo); 2026-09-28 thêm bài tập có trọng số, nộp/chấm bài, lịch học, bảng điểm, seed. Không có thay đổi nào từ đó.
- **Git:** chỉ `web/` có git, với 1 commit khởi tạo của create-next-app; `api/` chưa có git.
- **Kiểm tra đã chạy:** backend import và seed chạy được (trên SQLite tạm); `tsc --noEmit` và `npm run build` qua; `npm run lint` báo 18 lỗi, 12 cảnh báo; chưa có test tự động.

## 2. Tác nhân và chức năng hiện có

| Tác nhân | Chức năng hiện có |
|---|---|
| Khách | Tự đăng ký tài khoản và **tự chọn vai trò** (gọi API thẳng thì chọn được cả ADMIN); đăng nhập |
| Sinh viên | Xem mọi khóa học, đăng ký học bất kỳ lúc nào, xem thông báo và bài tập, nộp bài bằng link, xem lịch học, xem bảng điểm |
| Giảng viên | Tạo khóa học, đăng thông báo, tạo bài tập có trọng số, xem bài nộp, chấm điểm (thang 0–100) và nhận xét; thêm lịch học (chỉ có API, chưa có UI) |
| Admin | Gần giống giảng viên, không có trang quản trị riêng |

## 3. API hiện có (18 endpoint, tiền tố `/api`)

| Nhóm | Endpoint | Quyền |
|---|---|---|
| auth | `POST /auth/register`, `POST /auth/login` | Công khai |
| users | `GET /users/me` | Đã đăng nhập |
| courses | `POST /courses` | GV, Admin |
| | `GET /courses`, `GET /courses/{id}` | Đã đăng nhập |
| | `POST /courses/{id}/enroll` | SV |
| | `GET /courses/{id}/students` | GV, Admin |
| assignments | `POST /courses/{course_id}/assignments` | GV |
| | `GET /courses/{course_id}/assignments` | Đã đăng nhập |
| | `POST /assignments/{id}/submit` | SV |
| | `GET /assignments/{id}/submissions` | GV |
| | `POST /submissions/{id}/grade` | GV, Admin |
| announcements | `POST /courses/{course_id}/announcements` | GV, Admin |
| | `GET /courses/{course_id}/announcements` | Đã đăng nhập |
| schedules | `GET /schedules/my-schedule` | Đã đăng nhập |
| | `POST /courses/{id}/schedules` | GV, Admin |
| grades | `GET /grades/my-transcript` | Đã đăng nhập |

Frontend dùng 16/18 endpoint. `GET /courses/{id}/students` và `POST /courses/{id}/schedules` chưa có giao diện.

## 4. Dữ liệu hiện có (7 bảng)

```
users(id PK, name, email UQ, password_hash, role ENUM(ADMIN, INSTRUCTOR, STUDENT), created_at, updated_at)
courses(id PK, instructor_id FK→users, title, description, created_at, updated_at)
enrollments(student_id FK→users, course_id FK→courses, enrolled_at)      PK(student_id, course_id)
assignments(id PK, course_id FK→courses, title, description, due_date, weight INT DEFAULT 20, created_at)
submissions(id PK, assignment_id FK→assignments, student_id FK→users, content_url, grade INT NULL, feedback NULL, submitted_at)
announcements(id PK, course_id FK→courses, author_id FK→users, title, content, created_at)
schedules(id PK, course_id FK→courses, day_of_week VARCHAR("Thứ 2"…), start_time VARCHAR, end_time VARCHAR, room VARCHAR)
```

Điểm yếu của mô hình: không có học kỳ, mã môn, tín chỉ; điểm gắn vào từng bài nộp nên bài nộp trùng làm điểm "lạc"; `submissions` không có ràng buộc duy nhất; giờ học lưu dạng chuỗi; phòng học chỉ là chuỗi tự do.

## 5. Logic tính điểm hiện tại

- Điểm môn = Σ(điểm bài × weight) / Σ(weight của các bài **đã chấm**) / 10, làm tròn 1 chữ số.
- Điểm chữ 5 bậc: A ≥ 8.5 (4.0), B ≥ 7.0 (3.0), C ≥ 5.5 (2.0), D ≥ 4.0 (1.0), còn lại F.
- GPA = trung bình cộng hệ 4 của các môn, không theo tín chỉ. Tổng tín chỉ = số môn × 3.
- Môn chưa có bài nào được chấm bị tính 0.0 và F.

## 6. Lỗi và điểm yếu đã xác nhận

| Mã | Mức | Mô tả | Cách xác nhận | Hướng xử lý to-be |
|---|---|---|---|---|
| ISS-01 | P0 | Ai cũng tự đăng ký được tài khoản ADMIN/INSTRUCTOR (`schemas/auth.py` nhận `role` từ client) | Chạy thử | BR-ACC-01 |
| ISS-02 | P0 | Không kiểm tra giảng viên có phụ trách lớp: GV bất kỳ chấm điểm, tạo bài, đăng thông báo ở lớp của người khác | Chạy thử: GV khác chấm 0 điểm thành công | BR-GEN-02, BR-ASG-03, BR-GRD-03 |
| ISS-03 | P0 | Nộp lại tạo bản ghi trùng; bảng điểm đọc bản cũ nên điểm vừa chấm bị "mất" | Chạy thử | BR-SUB-04…08, BR-GRD-02 |
| ISS-04 | P1 | Trang lớp hiện "Đã nộp • Chờ chấm" cho cả bài chưa nộp | Chạy thử | FR-SUB-03 |
| ISS-05 | P1 | Môn chưa có điểm bị tính F vào GPA | Chạy thử: seed cho GPA 1.0 và 1.33 | BR-TRN-01, BR-GRD-05 |
| ISS-06 | P1 | Không chặn nộp sau hạn | Đọc code | BR-SUB-03 |
| ISS-07 | P1 | Mật khẩu dài hơn 72 byte gây lỗi 500 (bcrypt 5) | Chạy thử | BR-ACC-05, NFR-SEC-02 |
| ISS-08 | P1 | Lệch múi giờ: thời gian trả về không kèm `Z`, trình duyệt hiểu là giờ địa phương | Đọc code + kiểm PyMySQL | BR-GEN-01 |
| ISS-09 | P1 | Admin thấy nút tạo bài/xem bài nộp nhưng API trả 403 | Đọc code | 05-DATA-MODEL §5 |
| ISS-10 | P2 | `api/` không có git; `web/` chưa commit công sức | Kiểm tra git | DEC-F4 |
| ISS-11 | P2 | `requirements.txt` thiếu `email-validator` | Suy luận | 09-ROADMAP P0 |
| ISS-12 | P2 | `.env.example` lệch config; `JWT_SECRET` có giá trị mặc định | Đọc code | NFR-SEC-01 |
| ISS-13 | P2 | `seed.py` chạy `drop_all`, xóa sạch DB; không có migration | Đọc code | NFR-DAT-02 |
| ISS-14 | P2 | Trang lớp quay mãi khi chưa đăng nhập; màu `navy-50/100/200` chưa định nghĩa; dùng `alert()` | Đọc code | 04-UX-SPEC |
| ISS-15 | P2 | Lint 18 lỗi, 12 cảnh báo; chưa có test tự động | Chạy lint | 08-TEST-PLAN |
| ISS-16 | P2 | Dashboard gán cứng số 0; "Khóa học của tôi" hiện mọi khóa; chỉ hiện `#id` thay vì tên người | Đọc code | 04-UX-SPEC |

## 7. So với CampusHub v2 (Spring Boot + React)

- **v2 có, v3 chưa có:** chặn nộp sau hạn; mỗi sinh viên 1 bài nộp cho mỗi bài (unique); giảng viên chỉ quản lý lớp mình (Admin được bỏ qua); mã môn duy nhất; test tự động; admin dashboard; "lớp của tôi", "bài nộp của tôi".
- **v3 có, v2 chưa có:** thông báo lớp, lịch học, bảng điểm có trọng số và GPA.

## 8. Gợi ý cho bộ sơ đồ as-is

- **Use case as-is:** 4 tác nhân (Khách, SV, GV, Admin). Đánh dấu ISS-01 trên use case "Đăng ký tài khoản".
- **Activity/BPMN as-is:** luồng Nộp bài → Chấm → Xem điểm, chỉ rõ chỗ phát sinh ISS-03 và ISS-04.
- **Sequence as-is:** `POST /submissions/{id}/grade`, cho thấy thiếu bước kiểm tra giảng viên phụ trách (ISS-02).
- **Class as-is:** 7 model cùng các Service/Repository dạng static method.
- **ERD as-is:** 7 bảng ở §4.
