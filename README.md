# CampusHub v3

Cổng học tập kết hợp quản lý học vụ cho Admin, Giảng viên và Sinh viên (đồ án môn Thiết kế hệ thống, VNUK).

- `api/`: FastAPI, Python 3.9, SQLAlchemy 2, MySQL 8.
- `web/`: Next.js 16, React 19, Tailwind v4.
- `docs/plan/`: tài liệu kế hoạch và quy tắc nghiệp vụ (đọc `00-INDEX.md` trước). `docs/PROGRESS.md`: tiến độ.
- Luật làm việc chung: [AGENTS.md](AGENTS.md).

## Yêu cầu

Docker, Python 3.9+, Node.js 20+.

## Chạy lần đầu

**1. Cơ sở dữ liệu** (MySQL 8 qua Docker, cổng 3306):

```bash
cd api
docker compose up -d
```

**2. Backend** (API tại http://localhost:5001/api, tài liệu tại http://localhost:5001/docs):

```bash
cd api
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # rồi điền JWT_SECRET (xem hướng dẫn trong file)
python scripts/init_db.py   # tạo database campushub_v3 và chạy migration
python scripts/seed.py      # nạp dữ liệu demo
uvicorn src.main:app --reload --port 5001
```

**3. Frontend** (http://localhost:3000):

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

Lần sau chỉ cần: `docker compose up -d`, chạy uvicorn, chạy `npm run dev`.

## Tài khoản demo

Mật khẩu chung: `Demo@12345` (chỉ dùng trên máy local).

| Vai trò | Email |
|---|---|
| Admin | `admin@campushub.edu.vn` |
| Giảng viên | `nam.dh@campushub.edu.vn`, `alex.smith@campushub.edu.vn`, `linh.pt@campushub.edu.vn` |
| Sinh viên | `an.nguyen@campushub.edu.vn` (SV demo chính), `binh.tran@...`, … |
| Sinh viên đăng nhập lần đầu (bị buộc đổi mật khẩu) | `sv.moi@campushub.edu.vn` |

Kịch bản demo chi tiết: `docs/plan/08-TEST-PLAN.md` §6 và `docs/plan/05-DATA-MODEL.md` §6.

## Lệnh thường dùng

```bash
cd api && source venv/bin/activate && pytest -q          # 76 test backend
cd api && python scripts/reset_db.py                      # xóa và nạp lại dữ liệu (hỏi xác nhận)
cd web && npm run lint && npx tsc --noEmit && npm run check:i18n && npm run build
```

## Lưu ý

- Không commit `.env`, `venv/`, `node_modules/`, `.next/`, `api/storage/`.
- `reset_db.py` **xóa sạch** database `campushub_v3`; chỉ chạy khi chấp nhận mất dữ liệu.
