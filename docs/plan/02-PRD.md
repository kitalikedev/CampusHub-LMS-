# 02 — PRD: CampusHub v3 (to-be)

> Phiên bản 0.1 · 2026-11-09 · Quyết định gốc: 00-INDEX §4 · Rule chi tiết: 03-BUSINESS-RULES

## 1. Bối cảnh và mục tiêu

CampusHub là cổng học tập (LMS kết hợp học vụ) cho ba vai trò: Phòng đào tạo (Admin), Giảng viên và Sinh viên. Bản v3 viết lại v2 trên FastAPI + Next.js. Đợt này có ba mục tiêu:

- **G-1** Có bộ tài liệu và sơ đồ (as-is, to-be) nhất quán với code để bảo vệ môn System Design.
- **G-2** Logic nghiệp vụ đúng và được kiểm chứng bằng test: đăng ký học, nộp bài, chấm điểm, khóa sổ, GPA.
- **G-3** Demo trọn vẹn luồng của cả ba vai trò trên máy local.

**Chỉ số thành công:** (1) mọi FR mức Must chạy được trong kịch bản demo (08 §6); (2) mọi BR mức Must có ít nhất một test tự động pass; (3) mỗi use case to-be chính có sơ đồ activity hoặc BPMN và sequence tương ứng; (4) không còn lỗi ISS mức P0/P1.

## 2. Persona

| Persona | Mô tả | Mục tiêu chính | Vấn đề ở hệ thống hiện tại |
|---|---|---|---|
| Admin (Phòng đào tạo) | Cán bộ quản lý học vụ | Tạo tài khoản hàng loạt, mở lớp, xếp lịch không trùng, kiểm soát việc sửa điểm | Không có trang quản trị; ai cũng tự tạo được tài khoản |
| Giảng viên | Dạy 1–3 lớp mỗi kỳ | Giao bài, chấm, công bố điểm, khóa sổ đúng quy chế | Không cấu hình được cách nộp; GV khác sửa được điểm lớp mình |
| Sinh viên | Học 15–24 tín chỉ mỗi kỳ | Đăng ký lớp hợp lệ, nộp bài đúng hạn, xem điểm và GPA chính xác | Trạng thái nộp sai; GPA bị kéo xuống vì môn chưa có điểm |

## 3. Luồng người dùng chính

- **J-1 Đầu kỳ (Admin):** tạo học kỳ và đợt đăng ký → tạo môn, phòng → mở lớp, phân công GV, xếp lịch → import tài khoản SV và tải danh sách mật khẩu → (tùy chọn) xếp SV vào lớp bắt buộc → công bố lớp.
- **J-2 Đăng ký học (SV):** đăng nhập lần đầu → đổi mật khẩu → xem lớp đang mở → đăng ký (hệ thống kiểm tra ràng buộc) → xem thời khóa biểu.
- **J-3 Trong kỳ (GV ↔ SV):** GV tạo bài (trọng số, hạn nộp, chế độ nộp, chính sách trễ, chế độ hiện điểm) → SV nộp → GV chấm → điểm hiện ngay hoặc khi GV công bố → SV phúc khảo nếu cần → GV xử lý.
- **J-4 Cuối kỳ (GV → hệ thống → SV):** GV xem checklist → khóa sổ → hệ thống chốt kết quả và cập nhật GPA → SV xem bảng điểm. Nếu có sai sót, Admin mở lại sổ kèm lý do.

## 4. Phạm vi (MoSCoW), hạn khoảng 2026-11-23

- **Must** (bắt buộc cho buổi bảo vệ): AUTH, USR (trừ import), ACD, ENR (trừ import danh sách lớp), ASG, SUB bằng link, GRD, LCK, TRN, ANN, DSH, hạ tầng i18n kèm bản tiếng Việt, sửa toàn bộ ISS mức P0/P1.
- **Should** (làm khi xong Must): import CSV tài khoản, upload file bài nộp, phúc khảo, thông báo hệ thống, ghi nhật ký thao tác, bản dịch tiếng Anh.
- **Could:** màn hình xem nhật ký, thống kê Admin, import danh sách lớp, docker compose cho cả hệ thống, sơ đồ state machine.
- **Won't** (không làm đợt này): học lại/cải thiện (OQ-01), gửi email, nhắc hạn tự động, deploy cloud, xuất PDF/Excel, đăng nhập SSO, thiết kế lại UI tối giản.

## 5. Yêu cầu chức năng (FR)

| Mã | Mô tả | Vai trò | Ưu tiên | BR liên quan |
|---|---|---|---|---|
| FR-AUTH-01 | Đăng nhập bằng email và mật khẩu | Tất cả | M | BR-ACC-02, 06 |
| FR-AUTH-02 | Bắt buộc đổi mật khẩu ở lần đăng nhập đầu và sau khi bị reset | Tất cả | M | BR-ACC-04, 05 |
| FR-AUTH-03 | Tự đổi mật khẩu | Tất cả | M | BR-ACC-05 |
| FR-AUTH-04 | Đăng xuất | Tất cả | M | — |
| FR-USR-01 | Tạo từng tài khoản; mật khẩu tạm hiển thị đúng một lần | Admin | M | BR-ACC-01, 02, 03, 08 |
| FR-USR-02 | Import CSV tạo tài khoản hàng loạt; tải file email + mật khẩu tạm | Admin | S | BR-ACC-01, 03, 10 |
| FR-USR-03 | Xem, tìm, lọc danh sách người dùng | Admin | M | — |
| FR-USR-04 | Khóa/mở khóa tài khoản, đổi vai trò | Admin | M | BR-ACC-06, 07, 09 |
| FR-USR-05 | Reset mật khẩu | Admin | M | BR-ACC-03, 04 |
| FR-ACD-01 | Quản lý học kỳ: ngày học, đợt đăng ký, giới hạn tín chỉ | Admin | M | BR-ACD-01 |
| FR-ACD-02 | Quản lý môn học: mã, tín chỉ, Non-Graded, môn tiên quyết | Admin | M | BR-ACD-02 |
| FR-ACD-03 | Quản lý phòng học | Admin | M | BR-ACD-06 |
| FR-ACD-04 | Mở lớp học phần, phân công GV, đặt sĩ số, công bố lớp | Admin | M | BR-ACD-03, 04 |
| FR-ACD-05 | Xếp lịch học, kiểm tra trùng phòng/trùng GV và sức chứa phòng | Admin | M | BR-ACD-05 |
| FR-ENR-01 | Xem danh sách lớp đang mở đăng ký | SV | M | BR-ENR-01 |
| FR-ENR-02 | Đăng ký lớp, hệ thống kiểm tra các ràng buộc | SV | M | BR-ENR-01, 03–07, 09 |
| FR-ENR-03 | Hủy đăng ký trong đợt | SV | M | BR-ENR-02 |
| FR-ENR-04 | Xếp/hủy SV vào lớp; được vượt ràng buộc nếu ghi lý do | Admin | M | BR-ENR-01, 08 |
| FR-ENR-05 | Import danh sách lớp từ CSV | Admin | C | BR-ENR-08 |
| FR-ENR-06 | Xem danh sách SV của lớp mình | GV | M | — |
| FR-ASG-01 | Tạo/sửa/xóa bài: trọng số, hạn nộp, chế độ nộp, chính sách trễ, chế độ hiện điểm | GV | M | BR-ASG-01…08 |
| FR-ASG-02 | Hiển thị tổng trọng số hiện tại và cảnh báo khi chưa đủ 100% | GV | M | BR-ASG-02 |
| FR-SUB-01 | Nộp bài bằng link | SV | M | BR-SUB-01, 03…08 |
| FR-SUB-02 | Nộp bài bằng file | SV | S | BR-SUB-02 |
| FR-SUB-03 | Xem trạng thái nộp, lịch sử các lần nộp, nhãn trễ | SV | M | BR-SUB-03…06 |
| FR-SUB-04 | Xem bài nộp theo từng bài (lần nộp, nhãn trễ), tải file | GV | M | BR-SUB-06 |
| FR-GRD-01 | Chấm điểm và nhận xét cho từng SV (kể cả SV không nộp, bài offline) | GV | M | BR-GRD-01, 02, 03 |
| FR-GRD-02 | Công bố điểm của bài ở chế độ ẩn | GV | M | BR-GRD-04 |
| FR-GRD-03 | Sổ điểm của lớp: SV × bài, điểm tạm tính | GV | M | BR-GRD-05 |
| FR-GRD-04 | Xem điểm, nhận xét từng bài và điểm tạm tính của môn | SV | M | BR-GRD-04, 05 |
| FR-LCK-01 | Khóa sổ theo checklist điều kiện | GV | M | BR-LCK-01…05, 07 |
| FR-LCK-02 | Mở lại sổ, bắt buộc ghi lý do | Admin | M | BR-LCK-06 |
| FR-TRN-01 | Bảng điểm theo học kỳ: hệ 10, điểm chữ, hệ 4, GPA/TBC học kỳ và tích lũy, tín chỉ tích lũy | SV | M | BR-TRN-01…07 |
| FR-TRN-02 | Thời khóa biểu tuần (SV) và lịch dạy (GV) | SV, GV | M | BR-ACD-05 |
| FR-REG-01 | Gửi yêu cầu phúc khảo | SV | S | BR-REG-01, 02 |
| FR-REG-02 | Xử lý phúc khảo | GV | S | BR-REG-03, 04 |
| FR-ANN-01 | Đăng/sửa/xóa thông báo lớp; SV của lớp xem | GV, SV | M | BR-ANN-01 |
| FR-NOT-01 | Chuông thông báo, đếm chưa đọc, đánh dấu đã đọc | Tất cả | S | BR-NOT-01 |
| FR-AUD-01 | Ghi nhật ký các thao tác nhạy cảm | Hệ thống | S | BR-AUD-01 |
| FR-AUD-02 | Xem và lọc nhật ký | Admin | C | BR-AUD-01 |
| FR-STA-01 | Dashboard thống kê toàn hệ thống | Admin | C | — |
| FR-DSH-01 | Dashboard SV: lớp đang học, bài sắp đến hạn, thông báo mới | SV | M | — |
| FR-DSH-02 | Dashboard GV: lớp được giao, bài chờ chấm, phúc khảo chờ xử lý | GV | M | — |
| FR-I18N-01 | Đổi ngôn ngữ Vi/En và nhớ lựa chọn | Tất cả | S (hạ tầng: M) | — |

## 6. Tiêu chí chấp nhận (AC) cho FR mức Must

**Tài khoản**
- **AC-AUTH-01.1** Email (không phân biệt hoa/thường) và mật khẩu đúng → vào dashboard đúng vai trò.
- **AC-AUTH-01.2** Sai email hoặc sai mật khẩu → cùng một thông báo `AUTH_INVALID_CREDENTIALS`, không tiết lộ email có tồn tại hay không.
- **AC-AUTH-01.3** Tài khoản bị khóa → `ACCOUNT_DISABLED`.
- **AC-AUTH-02.1** Tài khoản đang phải đổi mật khẩu → mọi trang chuyển tới màn hình đổi mật khẩu; các API khác trả `PASSWORD_CHANGE_REQUIRED`.
- **AC-AUTH-02.2** Mật khẩu mới dưới 8 ký tự, quá 72 byte, hoặc trùng mật khẩu tạm → `PASSWORD_POLICY_VIOLATION` (không phải lỗi 500).
- **AC-USR-01.1** Tạo tài khoản → mật khẩu tạm hiển thị đúng một lần, có nút sao chép; tải lại trang thì không xem lại được.
- **AC-USR-01.2** Email đã tồn tại → `EMAIL_ALREADY_EXISTS`; tạo SV mà thiếu mã SV → `VALIDATION_ERROR`.
- **AC-USR-01.3** Không còn API đăng ký công khai: `POST /api/auth/register` trả 404.
- **AC-USR-04.1** Khóa tài khoản → người đó không đăng nhập được, token cũ bị từ chối ngay ở request kế tiếp.
- **AC-USR-04.2** Admin không tự khóa hay tự hạ quyền chính mình, không hạ quyền Admin cuối cùng.
- **AC-USR-05.1** Reset → mật khẩu tạm mới hiển thị một lần; tài khoản chuyển về trạng thái phải đổi mật khẩu.

**Học vụ**
- **AC-ACD-04.1** Lớp mới ở trạng thái DRAFT; SV chỉ thấy lớp sau khi Admin công bố (PUBLISHED).
- **AC-ACD-04.2** Mã lớp trùng trong cùng học kỳ → lỗi `VALIDATION_ERROR`.
- **AC-ACD-05.1** Thêm buổi học trùng phòng (cùng thứ, khoảng giờ giao nhau) với lớp khác trong kỳ → `SCHEDULE_ROOM_CONFLICT`, nêu tên lớp bị trùng.
- **AC-ACD-05.2** Trùng giờ dạy của cùng GV → `SCHEDULE_INSTRUCTOR_CONFLICT`.
- **AC-ACD-05.3** Sức chứa phòng nhỏ hơn sĩ số lớp → `ROOM_CAPACITY_TOO_SMALL`.
- **AC-ACD-05.4** Hai buổi 08:00–10:00 và 10:00–12:00 không bị coi là trùng.

**Đăng ký học**
- **AC-ENR-01.1** SV thấy các lớp PUBLISHED của học kỳ đang mở đăng ký, kèm mã môn, tên, tín chỉ, GV, lịch, phòng, số chỗ còn lại, môn tiên quyết.
- **AC-ENR-02.1** Ngoài đợt đăng ký → `ENROLL_PERIOD_CLOSED`.
- **AC-ENR-02.2** Lớp đủ sĩ số → `SECTION_FULL`. Hai SV cùng đăng ký chỗ cuối cùng một lúc → chỉ một người thành công.
- **AC-ENR-02.3** Trùng lịch với lớp đang học → `SCHEDULE_CONFLICT`, nêu lớp bị trùng.
- **AC-ENR-02.4** Chưa đạt môn tiên quyết → `PREREQUISITE_NOT_MET`, nêu môn còn thiếu.
- **AC-ENR-02.5** Vượt số tín chỉ tối đa của kỳ → `CREDIT_LIMIT_EXCEEDED`; dưới mức tối thiểu chỉ hiện cảnh báo.
- **AC-ENR-02.6** Đã có lớp khác cùng môn trong kỳ, hoặc đã có kết quả môn đó → `SUBJECT_ALREADY_TAKEN`.
- **AC-ENR-02.7** Đăng ký thành công → lớp hiện trong "Lớp của tôi" và trong thời khóa biểu.
- **AC-ENR-03.1** Hủy trong đợt → thành công; hủy ngoài đợt → `ENROLL_PERIOD_CLOSED`.
- **AC-ENR-04.1** Admin xếp SV vi phạm ràng buộc → hệ thống liệt kê vi phạm; Admin nhập lý do để vượt → thành công và được ghi nhật ký.

**Bài tập và nộp bài**
- **AC-ASG-01.1** Chỉ GV phụ trách lớp thấy nút và gọi được API tạo/sửa/xóa bài; GV khác → 403 `NOT_SECTION_INSTRUCTOR`.
- **AC-ASG-01.2** Tổng trọng số vượt 100% → `ASSIGNMENT_WEIGHT_EXCEEDED`; giao diện luôn hiện tổng hiện tại.
- **AC-ASG-01.3** Bài OFFLINE không có hạn nộp và chính sách trễ; bài MULTIPLE bắt buộc có số lần nộp tối đa ≥ 1.
- **AC-ASG-01.4** Bài đã có bài nộp → không đổi được chế độ nộp/chính sách trễ và không xóa được.
- **AC-SUB-01.1** SINGLE: nộp lần hai → `SUBMISSION_LIMIT_REACHED`.
- **AC-SUB-01.2** OVERWRITE: nộp lại khi chưa có điểm → chỉ còn một bản, mang nội dung mới.
- **AC-SUB-01.3** MULTIPLE: mỗi lần nộp được lưu; vượt số lần tối đa → `SUBMISSION_LIMIT_REACHED`.
- **AC-SUB-01.4** OFFLINE: nộp bài → `SUBMISSION_NOT_ALLOWED`.
- **AC-SUB-01.5** Đã có điểm → mọi chế độ đều trả `SUBMISSION_ALREADY_GRADED`.
- **AC-SUB-01.6** Sau hạn: REJECT → `SUBMISSION_PAST_DUE`; ACCEPT_MARK_LATE → nhận và gắn nhãn LATE.
- **AC-SUB-01.7** SV chưa vào lớp → `NOT_ENROLLED`.
- **AC-SUB-03.1** Mỗi bài hiện đúng một trạng thái: Chưa nộp / Đã nộp / Nộp trễ / Đã chấm / Không cần nộp (sửa ISS-04).

**Chấm điểm**
- **AC-GRD-01.1** Điểm ngoài 0–10 hoặc quá 2 chữ số thập phân → `GRADE_OUT_OF_RANGE`.
- **AC-GRD-01.2** GV không phụ trách lớp chấm điểm → 403 `NOT_SECTION_INSTRUCTOR` (sửa ISS-02).
- **AC-GRD-01.3** Chấm được cho SV không nộp bài và cho bài OFFLINE.
- **AC-GRD-02.1** Bài ở chế độ ẩn: SV không thấy điểm trước khi công bố; sau khi công bố thấy toàn bộ.
- **AC-GRD-03.1** Sổ điểm hiển thị SV × bài, điểm tạm tính và % trọng số đã có điểm.
- **AC-GRD-04.1** SV thấy điểm môn "tạm tính" kèm % trọng số đã có điểm; chưa có điểm chữ/GPA cho tới khi khóa sổ (sửa ISS-05).

**Khóa sổ và bảng điểm**
- **AC-LCK-01.1** Checklist hiện từng điều kiện đạt/chưa đạt. Chưa đủ điều kiện thì nút khóa bị vô hiệu, API trả `LOCK_PRECONDITION_FAILED` kèm danh sách lý do.
- **AC-LCK-01.2** Khóa thành công → bài không có điểm tính 0; kết quả từng SV khớp các ví dụ ở 03 §5.
- **AC-LCK-01.3** Sau khi khóa: tạo/sửa bài, nộp, chấm, xếp/hủy SV đều trả `SECTION_LOCKED`.
- **AC-LCK-02.1** Chỉ Admin mở lại được, bắt buộc có lý do; lớp về PUBLISHED, kết quả đã chốt bị xóa, thao tác được ghi nhật ký.
- **AC-TRN-01.1** Bảng điểm nhóm theo học kỳ; mỗi môn có tín chỉ, điểm hệ 10, điểm chữ, hệ 4, Đạt/Không đạt; môn chưa khóa sổ hiện "Đang học".
- **AC-TRN-01.2** GPA học kỳ, TBC học kỳ, GPA tích lũy, TBC tích lũy và tín chỉ tích lũy khớp các ví dụ Ex4, Ex5 ở 03 §5.
- **AC-TRN-02.1** Thời khóa biểu hiển thị đúng thứ, giờ, phòng theo giờ Việt Nam.

**Thông báo lớp và dashboard**
- **AC-ANN-01.1** Chỉ GV phụ trách được đăng/sửa/xóa; SV không thuộc lớp không xem được (403).
- **AC-DSH-01.1** Dashboard SV hiện lớp đang học trong kỳ, bài đến hạn trong 7 ngày tới, thông báo lớp mới nhất, đều là số liệu thật.
- **AC-DSH-02.1** Dashboard GV hiện lớp được giao, số bài nộp chờ chấm và (khi có REG) số phúc khảo chờ xử lý.

## 7. Yêu cầu phi chức năng (NFR)

| Mã | Yêu cầu |
|---|---|
| NFR-SEC-01 | `JWT_SECRET` bắt buộc đọc từ biến môi trường, tối thiểu 32 ký tự, không có giá trị mặc định; token hết hạn sau 1 ngày |
| NFR-SEC-02 | Mật khẩu băm bằng bcrypt; kiểm tra độ dài trước khi băm, không để xảy ra lỗi 500 |
| NFR-SEC-03 | Phân quyền theo tài nguyên (ai sở hữu lớp, ai thuộc lớp) ở tầng service theo ma trận 05 §5; mỗi quy tắc có test |
| NFR-SEC-04 | File nộp được kiểm tra loại và dung lượng, lưu ngoài thư mục public, chỉ tải qua API có kiểm quyền |
| NFR-SEC-05 | CORS chỉ cho phép origin của frontend được cấu hình |
| NFR-SEC-06 | Không commit `.env`; `.env.example` liệt kê đủ biến cần thiết |
| NFR-DAT-01 | Rule toàn vẹn được bảo vệ bằng ràng buộc DB (unique, FK, check); thao tác nhiều bước chạy trong một transaction |
| NFR-DAT-02 | Schema quản lý bằng migration (Alembic); seed demo chạy lặp lại được, không xóa DB trừ khi chạy lệnh reset riêng |
| NFR-DAT-03 | Thời gian lưu theo UTC; API trả ISO 8601 kèm `Z`; giao diện hiển thị theo giờ Việt Nam |
| NFR-PERF-01 | Với dữ liệu demo (≤ 500 SV, ≤ 50 lớp), API phản hồi dưới 500 ms; bảng điểm không bị lỗi N+1 query |
| NFR-USA-01 | Mọi trang có đủ trạng thái đang tải / rỗng / lỗi / không có quyền; không dùng `alert()` |
| NFR-USA-02 | Nhãn chức năng ghi rõ bằng chữ; nút chỉ có icon phải có nhãn ẩn cho trình đọc màn hình |
| NFR-I18N-01 | Không gán cứng chuỗi giao diện; API trả mã lỗi để frontend dịch |
| NFR-MNT-01 | Backend chia module theo tính năng; mỗi module tách router / service / repository |
| NFR-MNT-02 | Code backend chạy được trên Python 3.9 |
| NFR-TST-01 | Có pytest cho mọi BR nghiệp vụ mức Must; frontend qua `tsc`, `lint` (0 lỗi) và `build` |
| NFR-OPS-01 | Chạy local theo hướng dẫn trong README/AGENTS; (Could) docker compose cho cả hệ thống |

## 8. Ngoài phạm vi

Thanh toán học phí, ứng dụng di động, chat/diễn đàn, chấm tự động, chống đạo văn, điểm danh bằng QR, đăng nhập SSO, gửi email/SMS, nhắc hạn tự động, học lại/cải thiện (OQ-01), deploy cloud, xuất PDF/Excel.

## 9. Rủi ro chính (chi tiết ở 09-ROADMAP §6)

- **R-1** Chỉ có 2 tuần cho cả tài liệu, sơ đồ và code.
- **R-2** Hai thành viên mới bắt đầu tìm hiểu dự án.
- **R-3** Next.js 16 có thay đổi so với tài liệu cũ; phải đọc `node_modules/next/dist/docs`.
- **R-4** Python 3.9 đã hết hạn hỗ trợ; một số thư viện mới có thể không còn hỗ trợ.
- **R-5** Một số rule chưa chốt (OQ-01…07).
- **R-6** Sơ đồ lệch với code nếu không cập nhật cùng lúc.
