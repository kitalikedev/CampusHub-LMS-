# PROGRESS — Tiến độ dự án CampusHub v3

> Cập nhật lần cuối: **2026-11-15** · Hạn chung (tài liệu, sơ đồ, demo): khoảng **2026-11-23**
>
> Đây là **file tiến độ duy nhất**. Mỗi người tự cập nhật dòng việc của mình khi đổi trạng thái, rồi ghi ngày ở dòng "Cập nhật lần cuối". Kế hoạch và mốc nằm ở `plan/09-ROADMAP.md`; đặc tả từng việc nằm ở `plan/10-TASKS.md`.

Trạng thái: **Chưa bắt đầu** · **Đang làm** · **Chờ duyệt** · **Xong** · **Bị chặn**.

## 1. Tình hình hiện tại (đọc phần này trước)

- **Code đã xong bản demo đầy đủ** (backend + frontend) trên máy Lead, **chưa đưa lên repo** (chờ Lead duyệt demo, theo quy ước "xong demo sơ bộ mới đẩy code"). Backend: 14 module, migration `0001_initial_schema`, **76 test pytest đều qua**. Frontend: đủ trang ba vai trò, đổi Vi/En, giao diện "Học thuật cổ điển" theo màu VNUK; `tsc`, `eslint`, `check:i18n`, `build` đều qua.
- **Chạy trên MySQL 8 (Docker)**, DB `campushub_v3`. Dữ liệu demo: mật khẩu chung `Demo@12345` (xem README).
- **Báo cáo Word** (`ĐỀ TÀI_ HỆ THỐNG CỔNG THÔNG TIN HỌC TẬP VÀ QUẢN LÝ ĐÀO TẠO (CAMPUSHUB).docx`): đã viết lại Chương 2 và Chương 3 theo code, giữ nguyên Chương 1; còn **29 khung chờ hình** để nhóm tự vẽ và chèn.
- **Sơ đồ:** nhóm tự vẽ theo quy tắc của thầy (ERD ký hiệu Chen, class có bội số, DBMS + lược đồ quan hệ). Bản nháp `docs/diagrams/*/ERD*.drawio` dùng crow's foot nên **không dùng cho báo cáo**.
- **Việc còn lại chính:** vẽ và chèn sơ đồ vào báo cáo; đặc tả 15 use case còn lại; duyệt demo rồi dọn repo và mở PR đẩy code.

## 2. Bảng tiến độ

| Mã | Hạng mục | Phụ trách | Trạng thái | Cập nhật | Ghi chú |
|---|---|---|---|---|---|
| — | Bộ tài liệu kế hoạch `plan/00`…`10`, `AGENTS.md` | Lead | Chờ duyệt | 2026-11-15 | Bản 0.2, đã cập nhật theo code |
| — | Repo chung, đẩy tài liệu kế hoạch | Lead | Xong | 2026-11-09 | Chỉ có tài liệu và `.gitignore` |
| T-10 | P0: `.gitignore`, `requirements.txt`, `.env.example`, README, khung test | Lead | Xong | 2026-11-15 | Còn gộp `web/` vào repo chung (khi đẩy code) |
| — | **M-1**: duyệt 02, 03, 05, 06; chốt các mục ĐỀ XUẤT và OQ-05…07 | Lead | Chờ duyệt | | Code đang áp dụng các mục ĐỀ XUẤT |
| T-01…T-09 | Sơ đồ as-is và to-be | TV1, TV2, Lead | Đang làm | 2026-11-15 | Vẽ theo quy tắc của thầy; mô tả và khung chờ đã có trong báo cáo |
| T-11…T-18 | Backend core (auth, học vụ, đăng ký, bài nộp, chấm điểm, khóa sổ, GPA) | Lead | Xong | 2026-11-15 | 76 test qua |
| T-19, T-20 | Module announcements, rooms | Lead | Xong | 2026-11-15 | |
| T-21…T-26 | Frontend | Lead | Xong | 2026-11-15 | Đã thiết kế lại giao diện theo VNUK |
| T-27a…g | Tính năng Should (thông báo, phúc khảo, upload, import CSV, tiếng Anh, nhật ký, xuất sổ điểm CSV) | Lead | Xong | 2026-11-15 | |
| T-29 | Chạy thử kịch bản demo, quay video dự phòng, slide | Cả nhóm | Đang làm | 2026-11-15 | Kịch bản chạy tay đã kiểm trên trình duyệt; chưa quay video |
| — | Báo cáo môn System Design | Cả nhóm | Đang làm | 2026-11-15 | Xem §1; chưa có rubric (OQ-03) |

## 3. Mốc

| Mốc | Dự kiến | Trạng thái |
|---|---|---|
| M-0 Tài liệu kế hoạch 0.1 lên GitHub | 2026-11-09 | **Xong** |
| M-1 Design freeze | ~2026-11-12 | Chờ Lead duyệt |
| M-2 Backend core | ~2026-11-16 | **Xong** (2026-11-15) |
| M-3 Demo sơ bộ, đẩy code lên repo | ~2026-11-19 | Demo xong, chờ duyệt để đẩy code |
| M-4 Final | ~2026-11-22 | Chưa đạt |

## 4. Độ ổn định của nội dung (để biết làm gì được ngay)

| Nội dung | Mức | Có làm ngay được không |
|---|---|---|
| Hệ thống hiện tại (`plan/01-AS-IS.md`) | Ổn định, mô tả code đang có | **Có**: vẽ toàn bộ sơ đồ as-is |
| Use case và FR (`plan/02` §5) | Ổn định ở mức chức năng; mục Should/Could có thể bị cắt nếu trễ | Có thể nháp |
| Các rule **đã chốt với chủ dự án** (cột Nguồn là `DEC-…` trong `plan/03`): đăng ký học, 4 chế độ nộp, nộp trễ, khóa sổ, quy đổi điểm, GPA | Đã chốt | **Có**: vẽ Activity, BPMN theo các rule này |
| Rule ghi **ĐỀ XUẤT** trong `plan/03` (ví dụ thang điểm 10 cho từng bài, phúc khảo 7 ngày, giới hạn file 20 MB, điều kiện khóa sổ "không còn phúc khảo chờ") | Chưa duyệt, có thể đổi ở M-1 | Nháp được, **đừng chốt bản cuối** trước M-1 |
| Học lại, học cải thiện (OQ-01) | Chưa chốt, đang ngoài phạm vi | **Không vẽ** |
| Định dạng BPMN XML (OQ-02) | Chờ hỏi giảng viên | Làm cả hai: `.drawio` và `.bpmn` |
| Sequence, Class | Phải khớp code thật | Chờ code (sau M-2), do Lead vẽ |

Khi một rule đổi, `plan/03` sẽ ghi vào mục "Lịch sử thay đổi", và bảng §6 dưới đây sẽ liệt kê sơ đồ nào cần sửa.

## 5. Việc TV1, TV2 làm ngay và dàn ý báo cáo

**TV1**
1. Đọc `plan/00-INDEX.md` → `plan/01-AS-IS.md` → `plan/03-BUSINESS-RULES.md` (§3, §4, §7).
2. Vẽ UC-ASIS-01 và ACT-ASIS-01 (T-01), đúng nội dung ở `plan/07-DIAGRAMS.md` §3.
3. Nháp Use Case to-be từ danh sách 26 use case ở `plan/07` §4.1, chưa chốt trước M-1.

**TV2**
1. Đọc như TV1, thêm `plan/05-DATA-MODEL.md`.
2. Soát bản nháp ERD-ASIS-01 với `plan/01` §4 và ERD-01 với `plan/05` §2; vẽ BPMN-ASIS-01 (T-02, T-07).
3. Làm quen BPMN (T-06), chưa chốt trước M-1.

**Dàn ý báo cáo (theo mục lục của môn, đã áp dụng trong file Word):** Mở đầu · Chương 1 Khảo sát hiện trạng (phỏng vấn, as-is, to-be) · Chương 2 Phân tích hệ thống (FR/NFR, Use case, đặc tả UC, Activity, Sequence, Class) · Chương 3 Thiết kế hệ thống (thiết kế CSDL: ERD Chen, lược đồ quan hệ, DBMS, chuẩn hóa; thiết kế GUI).

## 6. Sơ đồ cần sửa do thay đổi

Ghi vào đây mỗi khi một rule hoặc code đổi hành vi, để người vẽ biết sơ đồ nào lệch.

| Sơ đồ | Lý do | Liên quan | Đã sửa? |
|---|---|---|---|
| — | — | — | — |

## 7. Vấn đề đang chặn / cần quyết định

| Mã | Vấn đề | Ai quyết định | Ảnh hưởng |
|---|---|---|---|
| — | Duyệt các mục ĐỀ XUẤT (mốc M-1) | Lead (chủ dự án) | Chặn bản cuối của T-04…T-07 và toàn bộ phần code |
| OQ-02 | BPMN cần XML chuẩn (`.bpmn`) hay XML của draw.io | Giảng viên | Làm cả hai trong lúc chờ |
| OQ-03 | Rubric chấm của môn | Lead | Dàn ý báo cáo ở §5 chỉ là tạm |

## 8. Nhật ký cập nhật

| Ngày | Người | Nội dung |
|---|---|---|
| 2026-11-09 | Lead | Tạo file; ghi nhận bộ tài liệu kế hoạch 0.1 đã lên GitHub, đã có bản nháp ERD as-is và to-be |
| 2026-11-15 | Lead | Code đầy đủ, 76 test qua, giao diện VNUK, báo cáo Word chương 2–3, thêm xuất sổ điểm CSV (BR-GRD-07); cập nhật 02, 03, 04, 05, 08, 10 theo code |
