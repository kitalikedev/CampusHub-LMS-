# 09 — Lộ trình, tiến độ, nợ kỹ thuật và rủi ro

> Phiên bản 0.1 · 2026-11-09 · Hạn chung khoảng **2026-11-23** (DEC-A1). Không chia việc theo từng ngày; các mốc dưới đây là mục tiêu để biết nhóm đang nhanh hay chậm.

## 1. Giai đoạn

| Giai đoạn | Phụ trách | Việc chính | Kết thúc ở |
|---|---|---|---|
| **P0 Chuẩn bị** | Lead | Tạo repo chung và đẩy tài liệu kế hoạch (commit `Initial Commit`); thêm `.gitignore` gốc; gộp `web/` vào repo chung (`web/.git` hiện chỉ có commit khởi tạo, cần Lead đồng ý trước khi bỏ); sửa `requirements.txt` (thêm `email-validator`; `alembic`, `pytest`, `httpx` phải hỏi trước, G4); `.env.example` đủ biến; README chạy local; khung test | M-0, trước M-1 |
| **P1 Chốt thiết kế** | Lead (cùng AI); TV đọc và hỏi | Duyệt 02, 03, 05, 06; chốt hoặc loại các mục ĐỀ XUẤT; trả lời OQ-05, 06, 07 | M-1 |
| **P2 Backend core** | Lead | Làm theo 06 §6: core → schema, migration, seed → auth/users → academics → sections và lịch → enrollments → assignments → submissions → grading/khóa sổ → transcripts → announcements; viết các test mức M ở 08 §2 | M-2 |
| **P2' Sơ đồ** (song song) | TV1, TV2; Lead | Bộ as-is làm ngay từ đầu (song song P0–P1); bộ to-be sau M-1; Lead vẽ Sequence/Class sau M-2 (07 §5) | M-3 (bản nháp đủ), M-4 (bản cuối) |
| **P3 Frontend** | Lead + TV | Bộ component, i18n, AppShell, API client; trang theo vai trò (10-TASKS) | M-3 → **push code** |
| **P4 Should** | Lead + TV | Import CSV, upload file, phúc khảo, thông báo hệ thống, ghi nhật ký, bản tiếng Anh | Trước M-4 |
| **P5 Hoàn thiện** | Cả nhóm | Chạy kịch bản demo trên MySQL; sửa lỗi; đồng bộ sơ đồ với code; xuất PNG; cập nhật tài liệu theo code thực tế (as-built); slide | M-4 |

## 2. Mốc

| Mốc | Mục tiêu | Điều kiện đạt |
|---|---|---|
| M-0 | 2026-11-09 | Bộ tài liệu kế hoạch 0.1 đã lên GitHub |
| M-1 Design freeze | khoảng 2026-11-12 | 02, 03, 05, 06 được duyệt; mọi ĐỀ XUẤT đã chốt hoặc loại; bản nháp sơ đồ as-is xong |
| M-2 Backend core | khoảng 2026-11-16 | Mọi endpoint mức Must chạy; test mức M ở 08 §2 pass; seed demo chạy được |
| M-3 Demo sơ bộ | khoảng 2026-11-19 | Kịch bản demo (08 §6) bước 1–7 và 9–11 chạy được trên giao diện; **push code** lên repo; có bản nháp đủ bộ sơ đồ to-be |
| M-4 Final | khoảng 2026-11-22 | Kịch bản demo chạy đầy đủ; sơ đồ khớp code; tài liệu as-built; slide sẵn sàng; còn 1 ngày dự phòng trước hạn |

## 3. PROGRESS (cập nhật khi xong mỗi việc)

Trạng thái: Chưa bắt đầu · Đang làm · Chờ duyệt · Xong · Bị chặn.

| Hạng mục | Phụ trách | Trạng thái | Ghi chú |
|---|---|---|---|
| Bộ tài liệu kế hoạch 00–10, AGENTS.md | Lead | Chờ duyệt | Bản 0.1, ngày 2026-11-09 |
| Repo chung + push tài liệu kế hoạch | Lead | Đang làm | Commit `Initial Commit`, chỉ gồm tài liệu |
| P0 Chuẩn bị (hạ tầng) | Lead | Chưa bắt đầu | |
| P1 Chốt thiết kế (M-1) | Lead | Chưa bắt đầu | |
| Sơ đồ as-is (T-01…T-03) | TV1, TV2, Lead | Chưa bắt đầu | |
| Backend core (T-10…T-18) | Lead | Chưa bắt đầu | |
| Sơ đồ to-be (T-04…T-09) | TV1, TV2, Lead | Chưa bắt đầu | Sau M-1 |
| Frontend (T-21…T-26) | Lead, TV1, TV2 | Chưa bắt đầu | |
| Should (T-27a…T-27f) | Lead, TV1, TV2 | Chưa bắt đầu | |
| Hoàn thiện, demo (T-29) | Cả nhóm | Chưa bắt đầu | |

**Sơ đồ cần sửa do code thay đổi:** (ghi mã sơ đồ và lý do mỗi khi một PR đổi hành vi)

| Sơ đồ | Lý do | PR | Đã sửa? |
|---|---|---|---|
| — | — | — | — |

## 4. Kế hoạch cắt giảm khi trễ

- **M-2 trễ hơn 1 ngày:** bỏ toàn bộ mục Could; nộp file chỉ còn nộp bằng link; trang Admin cho học kỳ/môn/phòng chỉ còn danh sách (dữ liệu từ seed); bản tiếng Anh để sau.
- **M-3 trễ:** dừng thêm tính năng; dồn sức cho sơ đồ, tài liệu và các luồng Must trong kịch bản demo, vì đây là phần được chấm chính.
- **Không bao giờ cắt:** sửa các lỗi ISS mức P0; test cho các nhóm BR-ENR, SUB, GRD, LCK, TRN; bộ sơ đồ Use Case, Activity, Sequence, Class, BPMN, ERD.

## 5. Nợ kỹ thuật (ghi nhận, không xử lý trong đợt này)

| Nợ | Rủi ro | Hướng xử lý sau |
|---|---|---|
| JWT trong `localStorage` (ADR-13) | Lộ token nếu bị XSS | Cookie httpOnly + refresh token |
| Python 3.9 đã hết hỗ trợ (ADR-14) | Thư viện mới bỏ hỗ trợ | Nâng lên 3.12 khi được phép cài |
| Chưa có CI | Lỗi lọt vào nhánh `main` | GitHub Actions chạy pytest + lint (Could) |
| Test chạy trên SQLite (ADR-15) | Khác biệt so với MySQL | Thêm job test trên MySQL |
| Thông báo dạng polling (ADR-11) | Trễ tối đa 60 giây | Chuyển sang SSE |
| File lưu trên đĩa local (ADR-12) | Không dùng được khi chạy nhiều máy chủ | Object storage |
| Chưa giới hạn số lần đăng nhập sai | Dò mật khẩu | Rate limit, khóa tạm |
| Chưa có quy tắc học lại (OQ-01) | Chặn SV học lại | Bổ sung khi chủ dự án chốt |

## 6. Rủi ro

| Mã | Rủi ro | Khả năng | Ảnh hưởng | Cách giảm |
|---|---|---|---|---|
| R-1 | Không đủ thời gian trong 2 tuần | Cao | Cao | Ưu tiên MoSCoW; kế hoạch cắt giảm §4; theo dõi mốc M-x |
| R-2 | Hai thành viên làm quen dự án chậm | Trung bình | Trung bình | Vẽ sơ đồ as-is để học; việc nhỏ có mẫu sẵn (module Rooms); đặc tả việc chi tiết ở 10 |
| R-3 | Next.js 16 khác tài liệu cũ | Trung bình | Trung bình | Đọc `node_modules/next/dist/docs`; giữ cách làm client component như hiện tại |
| R-4 | Thư viện mới không hỗ trợ Python 3.9 | Trung bình | Trung bình | Kiểm tra phiên bản trước khi cài; ghim phiên bản trong `requirements.txt` |
| R-5 | Các câu hỏi mở chưa được trả lời | Trung bình | Cao | Cách xử lý tạm ở 00 §5; ngưỡng điểm và làm tròn để ở dạng cấu hình |
| R-6 | Sơ đồ lệch với code | Cao | Cao | DoD bắt buộc cập nhật; Sequence/Class vẽ sau M-2; rà soát as-built ở P5 |
| R-7 | Repo GitHub đã có code v2 (G3) | Thấp | Trung bình | Kiểm tra trước khi push; không bao giờ force push |
| R-8 | Docker/MySQL gặp sự cố lúc demo | Thấp | Cao | Chạy thử trước 1 ngày; seed chạy lặp lại được; quay video demo dự phòng |
