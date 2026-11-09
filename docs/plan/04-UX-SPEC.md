# 04 — Đặc tả giao diện (UX)

> Phiên bản 0.1 · 2026-11-09 · Liên quan: 02-PRD (FR), 03-BUSINESS-RULES (BR), 06-ARCHITECTURE §5 (cấu trúc frontend)

## 1. Nguyên tắc

1. **Rõ ràng trước, trang trí sau.** Mỗi chức năng có nhãn bằng chữ; không dùng icon thay cho chữ; không thêm icon trang trí.
2. **Giao diện chỉ hỗ trợ, không thay backend.** Ẩn nút khi không có quyền cho dễ dùng, nhưng mọi rule vẫn được backend kiểm tra (BR-GEN-02).
3. **Nói lý do khi chặn.** Bị chặn thì hiện đúng lý do từ mã lỗi (ví dụ "Trùng lịch với lớp CS302-01, Thứ Ba 08:00–10:00"), không chỉ ghi "Thất bại".
4. **Đủ trạng thái** cho mọi vùng dữ liệu: đang tải, rỗng, lỗi, không có quyền (§4).
5. **Tách giao diện khỏi logic** để sau này có thể thiết kế lại theo hướng tối giản mà không đổi nghiệp vụ (DEC-F2): token màu ở một chỗ, component dùng chung ở `components/ui`, trang chỉ ghép component và gọi hook dữ liệu.

## 2. Bố cục chung (AppShell)

- **Desktop:** thanh bên trái (sidebar) chứa menu theo vai trò, nhãn bằng chữ. Thanh trên (header) có tên trang, nút đổi ngôn ngữ Vi/En, chuông thông báo (Should) và menu tài khoản (Đổi mật khẩu, Đăng xuất).
- **Mobile (< 768 px):** sidebar thu thành ngăn kéo mở bằng nút "Menu"; bảng dữ liệu cuộn ngang trong khung riêng, trang không bị cuộn ngang.
- **Vùng nội dung:** tiêu đề trang, mô tả ngắn (nếu cần), nút hành động chính ở góc phải, rồi tới nội dung.
- Menu khai báo trong `src/config/navigation.ts`, là điểm thêm tính năng mới vào menu (06 §5.4).

| Vai trò | Menu |
|---|---|
| Sinh viên | Tổng quan · Đăng ký học phần · Lớp của tôi · Thời khóa biểu · Bảng điểm |
| Giảng viên | Tổng quan · Lớp phụ trách · Phúc khảo (S) · Lịch dạy |
| Admin | Tổng quan · Người dùng · Học kỳ · Môn học · Phòng học · Lớp học phần · Nhật ký (C) · Thống kê (C) |

## 3. Danh sách màn hình

### 3.1 Dùng chung

| Mã | Màn hình | Nội dung chính | Hành động | FR |
|---|---|---|---|---|
| SCR-C01 | Đăng nhập | Email, mật khẩu, thông báo lỗi chung | Đăng nhập | FR-AUTH-01 |
| SCR-C02 | Đổi mật khẩu bắt buộc | Lý do phải đổi, mật khẩu mới, nhập lại, gợi ý quy tắc | Đổi mật khẩu | FR-AUTH-02 |
| SCR-C03 | Tài khoản của tôi | Thông tin cá nhân (chỉ đọc), form đổi mật khẩu | Đổi mật khẩu | FR-AUTH-03 |
| SCR-C04 | Thông báo (S) | Danh sách thông báo hệ thống, lọc chưa đọc | Đánh dấu đã đọc / đọc tất cả, mở liên kết | FR-NOT-01 |
| SCR-C05 | Lỗi 403 / 404 | Thông điệp rõ ràng, nút quay lại Tổng quan | — | — |

### 3.2 Sinh viên

| Mã | Màn hình | Nội dung chính | Hành động | FR |
|---|---|---|---|---|
| SCR-S01 | Tổng quan | Lớp đang học kỳ này; bài đến hạn trong 7 ngày (kèm trạng thái nộp); thông báo lớp mới nhất | Mở lớp / mở bài | FR-DSH-01 |
| SCR-S02 | Đăng ký học phần | Học kỳ và thời gian đợt đăng ký; tổng tín chỉ đã đăng ký / tối đa; bảng lớp mở (mã môn, tên, TC, GV, lịch, phòng, chỗ còn, tiên quyết) | Đăng ký, hủy; lý do bị chặn hiện ngay trên dòng | FR-ENR-01…03 |
| SCR-S03 | Lớp của tôi | Danh sách lớp theo học kỳ, trạng thái (Đang học / Đã có kết quả) | Mở lớp | FR-ENR-02 |
| SCR-S04 | Chi tiết lớp | Tab **Thông báo** · **Bài tập** (hạn, trọng số, trạng thái nộp, điểm nếu đã hiện) · **Điểm** (điểm từng bài, điểm tạm tính, % trọng số đã có điểm) | Mở bài | FR-ANN-01, FR-GRD-04 |
| SCR-S05 | Chi tiết bài tập | Mô tả, hạn nộp, chế độ nộp, chính sách trễ; khung nộp (link/file); lịch sử lần nộp (MULTIPLE); điểm, nhận xét; phúc khảo (S) | Nộp / nộp lại; gửi phúc khảo | FR-SUB-01…03, FR-REG-01 |
| SCR-S06 | Thời khóa biểu | Lưới tuần Thứ Hai–Chủ nhật × giờ; mỗi ô có môn, lớp, phòng; chọn học kỳ | Mở lớp | FR-TRN-02 |
| SCR-S07 | Bảng điểm | Theo từng học kỳ: bảng môn (TC, hệ 10, chữ, hệ 4, Đạt); GPA/TBC kỳ; khối tích lũy (GPA, TBC, TC tích lũy); môn đang học hiện "Đang học" | Mở lớp | FR-TRN-01 |

### 3.3 Giảng viên

| Mã | Màn hình | Nội dung chính | Hành động | FR |
|---|---|---|---|---|
| SCR-I01 | Tổng quan | Lớp được giao; số bài nộp chờ chấm; phúc khảo chờ (S) | Mở lớp, mở hàng chờ chấm | FR-DSH-02 |
| SCR-I02 | Lớp phụ trách | Danh sách lớp theo học kỳ, trạng thái lớp | Mở lớp | FR-ENR-06 |
| SCR-I03 | Chi tiết lớp | Tab **Thông báo** · **Bài tập & trọng số** (tổng % hiện rõ, cảnh báo khi ≠ 100%) · **Sổ điểm** (SV × bài, tạm tính) · **Sinh viên** · **Khóa sổ** (checklist BR-LCK-01, nút Khóa sổ) | Tạo/sửa/xóa bài; đăng thông báo; khóa sổ | FR-ASG-01, 02, FR-GRD-03, FR-LCK-01, FR-ANN-01 |
| SCR-I04 | Chấm bài | Danh sách SV của lớp với bài nộp mới nhất, nhãn trễ, số lần nộp; ô điểm 0–10 và nhận xét; với bài MANUAL có nút "Công bố điểm" | Lưu điểm, công bố | FR-SUB-04, FR-GRD-01, 02 |
| SCR-I05 | Phúc khảo (S) | Danh sách yêu cầu theo trạng thái; chi tiết: điểm cũ, lý do của SV | Chấp nhận (nhập điểm mới) / Từ chối (nhập lý do) | FR-REG-02 |
| SCR-I06 | Lịch dạy | Lưới tuần như SCR-S06 | — | FR-TRN-02 |

### 3.4 Admin

| Mã | Màn hình | Nội dung chính | Hành động | FR |
|---|---|---|---|---|
| SCR-A01 | Tổng quan | Lối tắt tới các việc đầu kỳ; (C) số liệu thống kê | — | FR-STA-01 |
| SCR-A02 | Người dùng | Bảng người dùng (lọc theo vai trò, tìm theo email/tên); hộp hiện mật khẩu tạm **một lần** | Tạo, import CSV (S), reset mật khẩu, khóa/mở khóa, đổi vai trò | FR-USR-01…05 |
| SCR-A03 | Học kỳ | Mã, ngày học, đợt đăng ký, giới hạn tín chỉ | Tạo, sửa | FR-ACD-01 |
| SCR-A04 | Môn học | Mã, tên, TC, Non-Graded, môn tiên quyết | Tạo, sửa, chọn môn tiên quyết | FR-ACD-02 |
| SCR-A05 | Phòng học | Mã, tên, sức chứa | Tạo, sửa | FR-ACD-03 |
| SCR-A06 | Lớp học phần | Danh sách theo học kỳ; chi tiết gồm thông tin, lịch học (báo trùng ngay khi thêm), danh sách SV, trạng thái | Tạo, phân công GV, thêm buổi học, công bố, xếp/hủy SV (nhập lý do khi vượt), mở lại sổ | FR-ACD-04, 05, FR-ENR-04, FR-LCK-02 |
| SCR-A07 | Nhật ký (C) | Bảng sự kiện, lọc theo người làm, loại, thời gian | — | FR-AUD-02 |
| SCR-A08 | Thống kê (C) | Số SV/GV/lớp, tỉ lệ đạt theo môn, phân bố điểm chữ | — | FR-STA-01 |

## 4. Trạng thái giao diện

| Trạng thái | Cách hiển thị |
|---|---|
| Đang tải | Khung xương (skeleton) đúng hình dạng nội dung; không dùng spinner toàn trang, trừ lúc kiểm tra đăng nhập |
| Rỗng | Một câu nói rõ vì sao rỗng, kèm hành động tiếp theo nếu có (ví dụ "Chưa có bài tập. Tạo bài tập đầu tiên") |
| Lỗi | Thông điệp dịch từ mã lỗi và nút "Thử lại"; lỗi nhập liệu hiện ngay dưới trường tương ứng |
| Không có quyền | SCR-C05 (403); không để trang trắng hoặc quay vòng mãi (sửa ISS-14) |
| Thành công | Toast ngắn ở góc màn hình; không dùng `alert()` |
| Hành động nguy hiểm | Hộp xác nhận nêu rõ hậu quả (ví dụ khóa sổ: "Bài chưa có điểm sẽ được tính 0. Sau khi khóa chỉ Admin mở lại được.") |

**Nhãn trạng thái dùng chung:**

| Nhãn | Màu |
|---|---|
| Chưa nộp | Xám |
| Đã nộp | Xanh navy |
| Nộp trễ | Vàng cam (warning) |
| Đã chấm | Xanh lá (success) |
| Điểm đang ẩn | Viền xám |
| Không cần nộp | Viền xám |
| Đã khóa sổ | Viền đỏ crimson |
| Đang học | Xanh navy nhạt |

## 5. Design token

Khai báo trong `web/src/app/globals.css` (khối `@theme` của Tailwind v4). Giữ tông navy/crimson hiện tại và **bổ sung các màu đang dùng nhưng chưa định nghĩa** (sửa ISS-14).

| Nhóm | Token | Giá trị |
|---|---|---|
| Thương hiệu | `navy-900` / `navy-800` / `navy-700` | #0B2545 / #13315C / #134074 (giữ nguyên) |
| | `navy-200` / `navy-100` / `navy-50` | #B9C8DE / #DCE4F0 / #EEF2F8 (thêm mới) |
| | `crimson-700` / `crimson-600` | #8B0000 / #A31D1D (giữ nguyên) |
| Nền | `surface` / `card` | #F8FAFC / #FFFFFF |
| Ngữ nghĩa | `success` / `warning` / `danger` / `info` | #15803D / #B45309 / #A31D1D / #134074 |
| Chữ | `text` / `text-muted` | #0B2545 / #475569 |
| Viền | `border` | #E2E8F0 |

- **Chữ:** font hệ thống (system-ui), không thêm font ngoài. Cỡ chữ 12 / 14 / 16 / 20 / 24 / 30 px; nội dung chính 14–16 px.
- **Khoảng cách:** thang 4 px của Tailwind; khoảng cách giữa các khối 24 px, trong thẻ 16 px.
- **Bo góc:** 6 px cho input/nút, 10 px cho thẻ và hộp thoại.
- **Đổ bóng:** chỉ một mức nhẹ cho thẻ và hộp thoại; không dùng gradient.
- **Chuyển động:** 150 ms ease-out cho hover và mở hộp thoại; tôn trọng `prefers-reduced-motion`; bỏ hiệu ứng trang trí (ví dụ chấm nhấp nháy `animate-pulse`).

## 6. Bộ component dùng chung (`web/src/components/ui`)

Button (primary / secondary / danger / ghost; có trạng thái loading) · Input · Textarea · Select · Checkbox · FormField (nhãn + lỗi + gợi ý) · Table (sắp xếp, trạng thái rỗng) · Badge (nhãn §4) · Card · Tabs · Dialog · ConfirmDialog · Toast · Skeleton · EmptyState · ErrorState · PageHeader · DateTimeText (hiển thị theo giờ Việt Nam) · ScoreText (định dạng điểm theo locale).

Trang **không** được tự viết lại các thành phần trên; thiếu gì thì thêm vào `components/ui`.

## 7. Đa ngôn ngữ (i18n) và định dạng

- Mặc định tiếng Việt; có nút đổi sang tiếng Anh; lựa chọn được nhớ trong trình duyệt và đặt vào `<html lang>`.
- Mọi chuỗi nằm trong `web/src/lib/i18n/messages/{vi,en}.json`. Khóa đặt theo tính năng, ví dụ `enrollment.actions.register`, `errors.SECTION_FULL`.
- Lỗi từ API được dịch theo `errors.<MÃ_LỖI>`, có tham số (ví dụ `{section}` cho lớp bị trùng).
- Ngày giờ: `Intl.DateTimeFormat(locale, { timeZone: "Asia/Ho_Chi_Minh" })`.
- Số và điểm: `Intl.NumberFormat(locale)`; điểm môn và GPA hiện 2 chữ số thập phân (OQ-05). Theo locale `vi`, dấu thập phân là dấu phẩy (8,61) (ĐỀ XUẤT).
- Tên thứ trong tuần lấy từ bản dịch, không lưu chuỗi "Thứ 2" trong DB (BR-ACD-05 dùng số 1–7).

## 8. Khả năng truy cập

- Mọi input có `<label>`; lỗi gắn với input qua `aria-describedby`.
- Có viền focus nhìn thấy được; dùng được bằng bàn phím (Tab, Enter, Esc để đóng hộp thoại).
- Độ tương phản chữ/nền đạt WCAG AA.
- Không chỉ dùng màu để truyền trạng thái: nhãn luôn có chữ.

## 9. Phác thảo hai màn hình chính

**SCR-S02 Đăng ký học phần**

```
Đăng ký học phần — Học kỳ 2026-2          Đợt đăng ký: 10/11 08:00 – 20/11 17:00
Đã đăng ký: 9 / 24 tín chỉ (tối thiểu 12)  ⚠ Chưa đạt số tín chỉ tối thiểu
┌──────────┬─────────────────────┬────┬───────────┬───────────────────┬──────┬────────┬──────────────┐
│ Lớp      │ Môn                 │ TC │ Giảng viên│ Lịch              │ Phòng│ Còn chỗ│              │
├──────────┼─────────────────────┼────┼───────────┼───────────────────┼──────┼────────┼──────────────┤
│ CS401-01 │ Kiến trúc phần mềm  │ 3  │ Nam Đàm   │ T2 08:00–10:30    │ A102 │ 12/40  │ [Đăng ký]    │
│ CS402-01 │ Hệ phân tán         │ 3  │ Alex Smith│ T3 08:00–10:30    │ B201 │  0/40  │ Lớp đã đủ chỗ│
│ CS403-02 │ Học máy             │ 3  │ …         │ T2 09:00–11:00    │ Lab5 │  5/30  │ Trùng lịch CS401-01 │
└──────────┴─────────────────────┴────┴───────────┴───────────────────┴──────┴────────┴──────────────┘
```

**SCR-I03 Chi tiết lớp — tab Khóa sổ**

```
CS401-01 · Kiến trúc phần mềm · 2026-2            Trạng thái: Đang mở
Điều kiện khóa sổ
  ✓ Tổng trọng số = 100%
  ✗ Còn 3 bài nộp chưa chấm (Bài tập 2)          [Đi tới chấm bài]
  ✓ Không còn phúc khảo đang chờ
Khi khóa sổ: bài chưa có điểm được tính 0; sau khi khóa chỉ Admin mở lại được.
                                                 [Khóa sổ] (bị vô hiệu tới khi đủ điều kiện)
```

## 10. Hướng thiết kế lại tối giản (để sau, DEC-F2)

Khi nhóm quyết định thiết kế lại: chỉ đổi token (§5) và component (§6), giữ nguyên trang, hook dữ liệu và API. Định hướng: nền trắng, một màu nhấn, không gradient, không icon trang trí, tên chức năng hiện rõ, mật độ thông tin vừa phải.
