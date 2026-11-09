# AGENTS.md — Luật làm việc chung (người và AI)

> Áp dụng cho cả ba thành viên và mọi trợ lý AI làm việc trong repo này. `CLAUDE.md` trỏ tới file này.

## 1. Dự án

- **CampusHub v3:** cổng học tập (LMS kết hợp học vụ) cho Admin, Giảng viên, Sinh viên.
- `api/`: FastAPI, Python 3.9, SQLAlchemy 2, MySQL 8. `web/`: Next.js 16, React 19, Tailwind v4.
- **Tài liệu nguồn:** `docs/plan/`. Đọc `00-INDEX.md` trước. Rule nghiệp vụ trong `03-BUSINESS-RULES.md` là chuẩn: code nào mâu thuẫn với 03 là lỗi của code.
- Với code Next.js, đọc thêm `web/AGENTS.md`: Next.js 16 khác tài liệu cũ, phải xem `web/node_modules/next/dist/docs/` trước khi viết.

## 2. Quy trình

Khảo sát → hiểu code hiện có → lập kế hoạch → **duyệt** → code → kiểm tra → review → cập nhật tài liệu.

- Việc không nhỏ thì nêu kế hoạch ngắn và chờ Lead duyệt trước khi sửa.
- **Bắt buộc duyệt trước:** đổi schema hoặc thêm migration, đổi cơ chế xác thực, thêm/nâng thư viện, xóa nhiều code, mọi thao tác xóa dữ liệu.
- Làm đúng phạm vi của task (10-TASKS). Ý tưởng ngoài phạm vi thì ghi lại và báo Lead, không tự làm.
- Ưu tiên sửa code có sẵn và dùng lại component/service có sẵn; không tạo bản thứ hai của một chức năng đã có.

## 3. Lệnh thường dùng

**Backend** (chạy trong `api/`):

```bash
docker compose up -d                       # MySQL local
source venv/bin/activate
uvicorn src.main:app --reload --port 5001  # API tại http://localhost:5001/api, tài liệu tại /docs
```

Sau khi xong giai đoạn P0 (09-ROADMAP) sẽ có thêm: `alembic upgrade head`, `python scripts/seed.py`, `pytest -q`.
**Lưu ý:** trước khi xong P0, file `seed.py` hiện tại **xóa sạch DB** rồi tạo lại. Chỉ chạy khi chấp nhận mất dữ liệu.

**Frontend** (chạy trong `web/`):

```bash
npm run dev          # http://localhost:3000, gọi API ở http://localhost:5001/api
npm run lint
npx tsc --noEmit
npm run build
```

## 4. Quy ước code

**Backend**
- Viết cho Python 3.9: dùng `Optional[X]`, không viết `X | None` trong model Pydantic, không dùng `match`.
- Phân tầng theo 06-ARCHITECTURE §2.2: router mỏng; service kiểm tra quyền và BR, quản lý transaction; repository không commit; logic thuần đặt ở `src/domain`.
- Báo lỗi bằng `AppError(code, params)`. Mã lỗi phải có trong 03 §8; thêm mã mới thì cập nhật 03.
- Thời gian dùng UTC: `datetime.now(timezone.utc)`, không dùng `datetime.utcnow()`.
- Điểm và GPA dùng `Decimal`, làm tròn `ROUND_HALF_UP` và chỉ làm tròn ở kết quả cuối (BR-TRN-06).
- Mỗi BR thêm mới hoặc sửa đều có test (08-TEST-PLAN).

**Frontend**
- Không gán cứng chuỗi giao diện: dùng `t("...")` và thêm khóa vào `vi.json` (và `en.json`).
- Dùng component trong `components/ui`; không dùng `alert()`; trang có đủ trạng thái đang tải, rỗng, lỗi, 403.
- Không import sâu sang feature khác; chỉ import qua `@/features/<tên>`.
- Gọi API qua `lib/api/client.ts`; hiển thị lỗi theo `error.code`.
- Ngày giờ hiển thị theo `Asia/Ho_Chi_Minh` qua `lib/format.ts`.

## 5. Git

- Repo: `https://github.com/kitalikedev/CampusHub`, nhánh chính `main`.
- Nhánh làm việc: `feat/T-xx-mo-ta-ngan`, `fix/...`, `docs/...`. Không commit thẳng vào `main`; merge qua PR do Lead duyệt.
- Commit message: `<type>(<phạm vi>): <mô tả ngắn>`, với type là `feat`, `fix`, `docs`, `refactor`, `test`, `chore`. Ví dụ: `feat(enrollments): chặn đăng ký trùng lịch (BR-ENR-04)`.
- Commit đầu tiên của repo là `Initial Commit`.
- PR ghi mã task, các FR/BR liên quan, cách đã kiểm tra, ảnh chụp nếu có sửa giao diện, và phải đạt Definition of Done (08 §4).
- **Hiện tại:** repo chỉ có tài liệu kế hoạch. Code sẽ được đẩy lên sau khi có bản demo sơ bộ (mốc M-3).

## 6. Điều cấm

- Commit `.env`, `venv/`, `node_modules/`, `.next/`, `api/storage/` hoặc bất kỳ file chứa mật khẩu thật.
- Push thẳng vào `main`, force push, xóa nhánh của người khác, viết lại lịch sử.
- Xóa DB/volume Docker, hoặc chạy seed/reset có xóa dữ liệu khi chưa hỏi.
- Tắt kiểm tra quyền, hoặc sửa test cho "qua", để né lỗi.
- Code một rule nghiệp vụ chưa có trong 03, hoặc sửa rule mà không cập nhật 03.
- Tự thêm thư viện khi chưa hỏi Lead.
- (AI) Đọc hoặc sửa bất cứ thứ gì nằm ngoài thư mục dự án.

## 7. Khi không chắc

- **Nghiệp vụ:** thêm câu hỏi vào bảng OQ (00 §5) và hỏi Lead. Không đoán.
- **Kỹ thuật:** nêu các phương án, đề xuất một, chờ duyệt nếu thuộc nhóm phải duyệt ở §2.
- **Báo cáo khi xong việc:** đã sửa gì · vì sao · đã kiểm tra bằng lệnh nào · kết quả · rủi ro còn lại · bước tiếp theo. Không nói "đã test" khi chưa chạy.
