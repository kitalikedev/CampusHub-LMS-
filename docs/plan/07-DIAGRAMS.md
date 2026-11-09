# 07 — Kế hoạch sơ đồ (as-is và to-be)

> Phiên bản 0.1 · 2026-11-09 · Trọng tâm của môn System Design (DEC-B1, B2). Phụ trách chính: TV1, TV2; Lead vẽ Sequence/Class và duyệt tất cả.

## 1. Công cụ và chuẩn ký hiệu

| Loại | Chuẩn | Công cụ | Định dạng nộp |
|---|---|---|---|
| Use Case, Activity, Sequence, Class | UML 2.5 | draw.io (thư viện shape UML) | `.drawio` + ảnh `.png` |
| BPMN | BPMN 2.0 | draw.io (thư viện BPMN) **và** Camunda Modeler hoặc bpmn.io | `.drawio` + `.bpmn` (BPMN 2.0 XML) + `.png`, cho tới khi GV chốt OQ-02 |
| ERD | Crow's foot | draw.io (thư viện Entity Relation) | `.drawio` + `.png` |
| Lược đồ quan hệ | Gạch chân khóa chính, `#` cho khóa ngoại | draw.io hoặc bảng trong báo cáo | `.drawio` + `.png` |

Mỗi thành viên tự cài công cụ trên máy mình. AI có thể sinh **bản nháp** `.drawio`/`.bpmn` từ tài liệu này khi được yêu cầu; người vẽ chỉnh bố cục và chịu trách nhiệm nội dung.

## 2. Thư mục và quy ước đặt tên

```
docs/diagrams/
├── as-is/     UC-ASIS-01.drawio, ACT-ASIS-01.drawio, SEQ-ASIS-01.drawio, CLS-ASIS-01.drawio, ERD-ASIS-01.drawio, BPMN-ASIS-01.(drawio|bpmn)
├── to-be/     UC-01.drawio, ACT-01…06.drawio, SEQ-01…06.drawio, CLS-01…02.drawio, BPMN-01…03.(drawio|bpmn), ERD-01.drawio, REL-01.drawio
└── export/    ảnh .png (xuất ở tỉ lệ 2x) để chèn báo cáo và slide
```

- Tên file là mã sơ đồ; một file có thể chứa nhiều trang (ví dụ UC-01 gồm trang tổng quát và các trang theo tác nhân).
- Góc mỗi sơ đồ có **khung thông tin**: mã, tên, phiên bản, người vẽ, ngày, các BR/FR liên quan.
- Tên tác nhân, thực thể, thông điệp dùng đúng **bảng thuật ngữ** ở 00 §6, đúng tên endpoint ở 06 §3.2 và đúng tên bảng ở 05 §2.

## 3. Bộ sơ đồ as-is (vẽ trước, để học hệ thống hiện tại)

Nguồn: 01-AS-IS và chạy thử app với dữ liệu seed hiện tại.

| Mã | Sơ đồ | Nội dung cần thể hiện | Người vẽ |
|---|---|---|---|
| UC-ASIS-01 | Use case hiện tại | 4 tác nhân: Khách, SV, GV, Admin; khoảng 12 use case; ghi chú ISS-01 ở "Đăng ký tài khoản" | TV1 |
| ACT-ASIS-01 | Activity: nộp – chấm – xem điểm | Swimlane SV, GV, Hệ thống; chỉ ra chỗ tạo bản ghi trùng (ISS-03) và chỗ hiện sai trạng thái (ISS-04) | TV1 |
| BPMN-ASIS-01 | Quy trình học tập hiện tại | Đăng ký học tự do → nộp bài → chấm → xem bảng điểm; ghi chú các chỗ thiếu kiểm soát | TV2 |
| ERD-ASIS-01 | ERD hiện tại | 7 bảng ở 01 §4 | TV2 |
| SEQ-ASIS-01 | Sequence: chấm điểm | `POST /submissions/{id}/grade`: thiếu bước kiểm tra GV phụ trách (ISS-02) | Lead |
| CLS-ASIS-01 | Class hiện tại | 7 model và các Service/Repository dạng static | Lead |

## 4. Bộ sơ đồ to-be (vẽ sau mốc M-1 Design freeze)

### 4.1 Use Case — UC-01 (TV1)

Tác nhân: **Admin**, **Giảng viên**, **Sinh viên**, cùng tác nhân trừu tượng **Người dùng** (tổng quát hóa của cả ba) cho các use case dùng chung.

| Mã | Use case | Tác nhân | Quan hệ | FR |
|---|---|---|---|---|
| UC-01 | Đăng nhập | Người dùng | «include» UC-02 khi phải đổi mật khẩu | FR-AUTH-01 |
| UC-02 | Đổi mật khẩu | Người dùng | | FR-AUTH-02, 03 |
| UC-03 | Quản lý tài khoản (tạo, import, khóa, reset, đổi vai trò) | Admin | | FR-USR-01…05 |
| UC-04 | Quản lý học kỳ và đợt đăng ký | Admin | | FR-ACD-01 |
| UC-05 | Quản lý môn học và môn tiên quyết | Admin | | FR-ACD-02 |
| UC-06 | Quản lý phòng học | Admin | | FR-ACD-03 |
| UC-07 | Mở lớp học phần và phân công GV | Admin | | FR-ACD-04 |
| UC-08 | Xếp lịch học | Admin | «include» Kiểm tra trùng phòng/GV | FR-ACD-05 |
| UC-09 | Xếp SV vào lớp | Admin | «include» UC-26; «extend» Vượt ràng buộc có lý do | FR-ENR-04 |
| UC-10 | Đăng ký học phần | Sinh viên | «include» UC-26 | FR-ENR-01, 02 |
| UC-11 | Hủy đăng ký | Sinh viên | | FR-ENR-03 |
| UC-12 | Quản lý bài tập / cột điểm | Giảng viên | | FR-ASG-01, 02 |
| UC-13 | Nộp bài | Sinh viên | «extend» Nộp trễ (khi quá hạn và bài cho phép) | FR-SUB-01…03 |
| UC-14 | Chấm điểm | Giảng viên | | FR-GRD-01, FR-SUB-04 |
| UC-15 | Công bố điểm | Giảng viên | | FR-GRD-02 |
| UC-16 | Gửi phúc khảo | Sinh viên | | FR-REG-01 |
| UC-17 | Xử lý phúc khảo | Giảng viên | | FR-REG-02 |
| UC-18 | Khóa sổ điểm | Giảng viên | «include» Tính kết quả môn | FR-LCK-01 |
| UC-19 | Mở lại sổ điểm | Admin | | FR-LCK-02 |
| UC-20 | Xem bảng điểm và GPA | Sinh viên | | FR-TRN-01 |
| UC-21 | Xem thời khóa biểu / lịch dạy | Sinh viên, Giảng viên | | FR-TRN-02 |
| UC-22 | Đăng và xem thông báo lớp | Giảng viên, Sinh viên | | FR-ANN-01 |
| UC-23 | Xem thông báo hệ thống | Người dùng | | FR-NOT-01 |
| UC-24 | Xem nhật ký thao tác | Admin | | FR-AUD-02 |
| UC-25 | Xem thống kê | Admin | | FR-STA-01 |
| UC-26 | Kiểm tra ràng buộc đăng ký (use case được include) | — | | BR-ENR-03…07 |

**Đặc tả use case** (dạng bảng: mã, tên, tác nhân, mô tả, tiền điều kiện, hậu điều kiện, luồng chính, luồng thay thế/ngoại lệ, BR liên quan) bắt buộc có cho: UC-03, UC-08, UC-10, UC-13, UC-14, UC-15, UC-16/17, UC-18, UC-20. Luồng ngoại lệ lấy từ cột "Mã lỗi" ở 03.

### 4.2 Activity — ACT-01…06 (TV1)

| Mã | Luồng | Swimlane | Điểm rẽ nhánh phải có (ghi mã BR) |
|---|---|---|---|
| ACT-01 | Tạo tài khoản và đăng nhập lần đầu | Admin · Hệ thống · Người dùng | Import hợp lệ? (BR-ACC-10); phải đổi mật khẩu? (BR-ACC-04); mật khẩu mới hợp lệ? (BR-ACC-05) |
| ACT-02 | Đăng ký học phần | Sinh viên · Hệ thống | Đúng thứ tự kiểm tra ở 03 §3: đợt đăng ký, trạng thái lớp, cùng môn, sĩ số, trùng lịch, tiên quyết, tín chỉ |
| ACT-03 | Nộp bài | Sinh viên · Hệ thống | Chế độ nộp (§7.2 của 03); quá hạn × chính sách trễ (§7.3); đã có điểm? |
| ACT-04 | Chấm và công bố điểm | Giảng viên · Hệ thống · Sinh viên | IMMEDIATE hay MANUAL (BR-GRD-04); gửi thông báo |
| ACT-05 | Phúc khảo | Sinh viên · Giảng viên · Hệ thống | Còn trong 7 ngày? (BR-REG-01); chấp nhận/từ chối (BR-REG-03) |
| ACT-06 | Khóa sổ và tổng kết | Giảng viên · Hệ thống · Admin · Sinh viên | Bốn điều kiện của BR-LCK-01; bài thiếu điểm tính 0; mở lại sổ (BR-LCK-06) |

### 4.3 Sequence — SEQ-01…06 (Lead, vẽ theo code thật sau mốc M-2)

Lifeline chuẩn: `Người dùng` → `Trang Next.js` → `API Router` → `Service` → `domain` → `Repository` → `MySQL`; thêm `NotificationService` và `AuditService` khi có.

| Mã | Luồng | Điểm cần thể hiện |
|---|---|---|
| SEQ-01 | Đăng nhập và bắt buộc đổi mật khẩu | JWT; `get_current_user` chặn bằng `PASSWORD_CHANGE_REQUIRED` |
| SEQ-02 | Đăng ký học phần | Transaction, `SELECT … FOR UPDATE`, khung `alt` cho từng lỗi |
| SEQ-03 | Nộp bài | `submission_policy` quyết định lần nộp và nhãn trễ; lưu file |
| SEQ-04 | Chấm điểm và công bố | Kiểm tra GV phụ trách; `visible_at`; tạo thông báo |
| SEQ-05 | Khóa sổ | Kiểm tra điều kiện, `domain/grading` tính kết quả, ghi `course_results`, thông báo, nhật ký, tất cả trong một transaction |
| SEQ-06 | Xem bảng điểm | Đọc `course_results`, tính GPA kỳ và tích lũy |

### 4.4 Class — CLS-01, CLS-02 (Lead)

- **CLS-01 Mô hình miền:** 18 thực thể ở 05 §2, các enum, quan hệ có bội số khớp với ERD, một số phương thức nghiệp vụ tiêu biểu (`CourseSection.lock()`, `Assignment.canSubmit(student, now)`, `GradeScale.toLetter(score)`). User vẽ dạng tổng quát hóa với ba vai trò (về DB vẫn là một bảng).
- **CLS-02 Kiến trúc tầng của một module (enrollments):** `EnrollmentRouter` → `EnrollmentService` → `EnrollmentRepository`, cùng `PermissionGuard`, `AppError`, `domain.schedule`; thể hiện quan hệ phụ thuộc giữa các tầng.

### 4.5 BPMN — BPMN-01…03 (TV2)

| Mã | Quy trình | Pool / Lane | Phần tử bắt buộc |
|---|---|---|---|
| BPMN-01 | Mở lớp và đăng ký học phần | Pool "Trường": Phòng đào tạo (Admin), Sinh viên, Hệ thống CampusHub | Timer event mở/đóng đợt đăng ký; exclusive gateway cho từng ràng buộc; message flow khi xếp lớp |
| BPMN-02 | Giao bài, nộp, chấm, công bố, phúc khảo | Giảng viên, Sinh viên, Hệ thống | Timer event hạn nộp; gateway chế độ nộp và chính sách trễ; gateway hiện điểm ngay hay công bố sau |
| BPMN-03 | Tổng kết học kỳ | Giảng viên, Hệ thống, Admin, Sinh viên | Gateway điều kiện khóa sổ; tác vụ tính kết quả; luồng mở lại sổ có lý do |

### 4.6 ERD và lược đồ quan hệ — ERD-01, REL-01 (TV2)

- **ERD-01:** 18 bảng ở 05 §2, ghi đủ khóa chính, khóa ngoại, bội số crow's foot, các ràng buộc UQ quan trọng.
- **REL-01:** lược đồ quan hệ chép từ 05 §2, theo ký hiệu ở §1.

## 5. Thứ tự làm và phân công

1. Ngay từ đầu: TV1, TV2 đọc 00, 01, 03, chạy app, rồi vẽ bộ as-is (§3).
2. Sau M-1 (Design freeze): vẽ bộ to-be. TV1 làm Use Case, đặc tả UC và Activity; TV2 làm BPMN, ERD, REL.
3. Sau M-2 (backend xong phần chính): Lead vẽ Sequence và Class theo code thật.
4. Duyệt chéo: TV1 duyệt BPMN/ERD, TV2 duyệt Use Case/Activity, Lead duyệt tất cả theo checklist §6.
5. Trước M-4: xuất PNG, cập nhật cho khớp code (as-built), ghi phiên bản cuối.

## 6. Checklist duyệt một sơ đồ

- [ ] Đúng ký hiệu UML 2.5 / BPMN 2.0 / crow's foot (không trộn ký hiệu giữa các loại).
- [ ] Có khung thông tin: mã, tên, phiên bản, người vẽ, ngày, BR/FR liên quan.
- [ ] Tên dùng đúng bảng thuật ngữ (00 §6), đúng endpoint (06 §3.2) và bảng (05 §2).
- [ ] Mỗi điểm rẽ nhánh trong Activity/BPMN ghi mã BR tương ứng.
- [ ] Mọi use case to-be đều có FR trong 02; mọi FR mức Must đều có use case.
- [ ] Bội số trong Class/ERD khớp với 05.
- [ ] Sequence khớp với code (tên service, thứ tự gọi, transaction).
- [ ] Sơ đồ as-is ghi rõ các lỗi ISS mà nó minh họa.
- [ ] Đã xuất PNG vào `docs/diagrams/export/`.
