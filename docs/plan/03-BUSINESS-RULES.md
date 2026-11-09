# 03 — Danh mục rule nghiệp vụ (Business Rules)

> Phiên bản 0.1 · 2026-11-09 · **Tài liệu quan trọng nhất của bộ kế hoạch.** Code, sơ đồ và test đều dẫn chiếu tới mã BR ở đây.

## 0. Cách đọc

- **Nguồn:** `DEC-xx` là quyết định của chủ dự án (00 §4); `ISS-xx` là rule sinh ra để sửa lỗi hiện tại (01 §6); `v2` là rule có sẵn ở CampusHub v2; **ĐỀ XUẤT** là rule do người soạn đề xuất, **cần duyệt**.
- **Thực thi:** `DB` = ràng buộc trong cơ sở dữ liệu; `Service` = kiểm tra ở tầng service của backend; `UI` = giao diện hỗ trợ (ẩn nút, hiện cảnh báo). UI **không bao giờ** là nơi thực thi duy nhất.
- **Mã lỗi:** mã backend trả về (danh mục ở §8). Frontend dịch mã này sang Vi/En.
- Muốn đổi rule: sửa file này, ghi vào §9, rồi cập nhật FR/AC, sơ đồ và test trong cùng một PR.

## 1. Tài khoản (ACC)

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-ACC-01 | Không có đăng ký công khai. Chỉ Admin tạo tài khoản, từng người hoặc import CSV. | DEC-C1, ISS-01 | Service (bỏ endpoint register) | — |
| BR-ACC-02 | Tên đăng nhập là email, duy nhất toàn hệ thống, lưu dạng chữ thường, so khớp không phân biệt hoa/thường. Áp dụng cho SV, GV và Admin. | DEC-C1 | DB (unique) + Service | EMAIL_ALREADY_EXISTS |
| BR-ACC-03 | Mật khẩu ban đầu và mật khẩu reset do hệ thống sinh ngẫu nhiên: 12 ký tự gồm chữ và số, bỏ các ký tự dễ nhầm (0/O, 1/l/I). Mật khẩu chỉ trả về **một lần** trong response tạo/reset/import. Hệ thống chỉ lưu bản băm bcrypt nên không ai xem lại được. | DEC-C1 | Service | — |
| BR-ACC-04 | Tài khoản mới hoặc vừa reset có cờ "phải đổi mật khẩu". Khi cờ bật, chỉ được đổi mật khẩu, xem thông tin bản thân và đăng xuất; mọi API khác trả lỗi. | DEC-C1 | Service + UI (chuyển trang) | PASSWORD_CHANGE_REQUIRED |
| BR-ACC-05 | Mật khẩu mới dài 8–72 byte và khác mật khẩu đang dùng. | ĐỀ XUẤT, ISS-07 | Service | PASSWORD_POLICY_VIOLATION |
| BR-ACC-06 | Tài khoản bị khóa không đăng nhập được; token đã cấp bị từ chối ngay ở request kế tiếp. | ĐỀ XUẤT | Service | ACCOUNT_DISABLED |
| BR-ACC-07 | Admin không tự khóa hay tự hạ quyền chính mình; hệ thống luôn còn ít nhất một Admin đang hoạt động. | ĐỀ XUẤT | Service | LAST_ADMIN_REQUIRED |
| BR-ACC-08 | Tài khoản SV có mã sinh viên duy nhất; GV và Admin không có mã SV. | ĐỀ XUẤT | DB (unique) + Service | STUDENT_CODE_EXISTS |
| BR-ACC-09 | Không xóa cứng tài khoản đã có dữ liệu học tập, chỉ khóa. Chỉ đổi vai trò khi tài khoản chưa gắn dữ liệu với vai trò cũ (GV đang phụ trách lớp, SV đang học). | ĐỀ XUẤT | Service | ROLE_CHANGE_NOT_ALLOWED |
| BR-ACC-10 | Import CSV gồm các cột `email, full_name, role, student_code`. Hệ thống kiểm tra toàn bộ file trước; có dòng lỗi thì **không tạo tài khoản nào** và trả danh sách lỗi theo số dòng. | ĐỀ XUẤT | Service | IMPORT_INVALID_ROWS |

## 2. Học vụ: học kỳ, môn, phòng, lớp, lịch (ACD)

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-ACD-01 | Học kỳ có mã duy nhất (ví dụ `2026-1`); ngày bắt đầu < ngày kết thúc; đợt đăng ký có thời điểm mở < đóng; tín chỉ tối thiểu ≤ tối đa. Các học kỳ không chồng ngày nhau. | DEC-C2, C4 | DB (check) + Service | VALIDATION_ERROR |
| BR-ACD-02 | Môn học có mã duy nhất, số tín chỉ nguyên từ 1 đến 10, cờ Non-Graded. Môn tiên quyết không được là chính nó và không tạo vòng lặp (A cần B, B cần A). | DEC-E5, C4 | DB + Service | PREREQUISITE_CYCLE |
| BR-ACD-03 | Lớp học phần thuộc đúng một môn và một học kỳ; mã lớp duy nhất trong học kỳ; có một GV phụ trách (vai trò INSTRUCTOR, đang hoạt động); sĩ số tối đa > 0. Chỉ Admin tạo, sửa, đổi GV. Đổi GV thì GV mới nhận toàn quyền với lớp. | DEC-C2 | DB + Service | VALIDATION_ERROR |
| BR-ACD-04 | Trạng thái lớp: DRAFT → PUBLISHED (Admin công bố) → LOCKED (GV khóa sổ) → PUBLISHED (chỉ Admin mở lại, bắt buộc lý do). Chi tiết ở §7.1. | DEC-E7 | Service | INVALID_STATE_TRANSITION |
| BR-ACD-05 | Buổi học gồm thứ (1 = Thứ Hai … 7 = Chủ nhật), giờ bắt đầu < giờ kết thúc và phòng. Hai buổi **trùng** khi cùng thứ và `a.start < b.end` và `b.start < a.end` (khoảng nửa mở, nên 08:00–10:00 và 10:00–12:00 không trùng). Trong cùng học kỳ: không trùng phòng, không trùng GV. Sức chứa phòng ≥ sĩ số lớp; khi sửa sĩ số cũng phải kiểm tra lại. | DEC-C2, C4 | Service | SCHEDULE_ROOM_CONFLICT, SCHEDULE_INSTRUCTOR_CONFLICT, ROOM_CAPACITY_TOO_SMALL, INVALID_TIME_RANGE |
| BR-ACD-06 | Phòng học có mã duy nhất và sức chứa > 0. Không xóa phòng đang có lịch. | DEC-F1 | DB + Service | ROOM_IN_USE |

## 3. Đăng ký học (ENR)

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-ENR-01 | SV vào lớp theo hai cách: (a) Admin xếp, khi lớp chưa khóa sổ; (b) SV tự đăng ký khi lớp đang PUBLISHED và thời điểm hiện tại nằm trong đợt đăng ký của học kỳ. | DEC-C3 | Service | ENROLL_PERIOD_CLOSED, SECTION_NOT_OPEN |
| BR-ENR-02 | SV chỉ tự hủy trong đợt đăng ký; ngoài đợt chỉ Admin hủy (có ghi nhật ký). Hủy không xóa bài nộp và điểm đã có, nhưng SV đã hủy không còn trong sổ điểm và không có kết quả môn. | DEC-C3, ĐỀ XUẤT | Service | ENROLL_PERIOD_CLOSED |
| BR-ENR-03 | Sĩ số: chỉ nhận khi số SV đang học < sĩ số tối đa. Việc kiểm tra và ghi chạy trong một transaction có khóa dòng của lớp (`SELECT … FOR UPDATE`), để hai người đăng ký cùng lúc không làm vượt sĩ số. | DEC-C4 | Service + DB | SECTION_FULL |
| BR-ENR-04 | Trùng lịch: không vào lớp có buổi học trùng (theo định nghĩa ở BR-ACD-05) với bất kỳ lớp nào SV đang học trong cùng học kỳ. | DEC-C4 | Service | SCHEDULE_CONFLICT |
| BR-ENR-05 | Tiên quyết: SV phải **đạt** mọi môn tiên quyết, tức là có kết quả đã khóa sổ ở mức Đạt (môn tính điểm: từ D+; môn Non-Graded: Đạt). Đang học môn tiên quyết trong cùng kỳ chưa tính là đạt. | DEC-C4 | Service | PREREQUISITE_NOT_MET |
| BR-ENR-06 | Giới hạn tín chỉ: tổng tín chỉ các lớp đang học trong kỳ cộng với lớp mới không vượt mức tối đa của học kỳ. Dưới mức tối thiểu chỉ cảnh báo, không chặn. Môn Non-Graded có tính vào giới hạn (ĐỀ XUẤT, OQ-07). | DEC-C4 | Service | CREDIT_LIMIT_EXCEEDED |
| BR-ENR-07 | Không đăng ký hai lớp của cùng một môn trong một học kỳ. Không đăng ký lại môn đã có kết quả (đạt hay F) cho tới khi chốt quy tắc học lại (OQ-01). | ĐỀ XUẤT | Service | SUBJECT_ALREADY_TAKEN |
| BR-ENR-08 | Khi Admin xếp SV vi phạm BR-ENR-03…07, hệ thống liệt kê **mọi** vi phạm; Admin chỉ vượt được khi nhập lý do, và thao tác được ghi nhật ký. Không ai vượt được việc lớp đã khóa sổ. | ĐỀ XUẤT | Service | ENROLLMENT_RULES_VIOLATED |
| BR-ENR-09 | Mỗi cặp (SV, lớp) chỉ có một bản ghi đăng ký; hủy rồi đăng ký lại thì cập nhật trạng thái của bản ghi cũ. | ĐỀ XUẤT | DB (unique) + Service | ALREADY_ENROLLED |

**Thứ tự kiểm tra khi SV tự đăng ký** (dùng để vẽ activity/BPMN; SV nhận lỗi đầu tiên gặp phải): đợt đăng ký → trạng thái lớp → đã đăng ký lớp này chưa → cùng môn / đã có kết quả → sĩ số → trùng lịch → tiên quyết → giới hạn tín chỉ → ghi đăng ký.

## 4. Bài tập, nộp bài, chấm điểm (ASG, SUB, GRD)

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-ASG-01 | Mỗi cột điểm là đúng một bài. Mỗi bài có trọng số % trong khoảng (0, 100], tối đa 2 chữ số thập phân. | DEC-E1 | DB (check) + Service | VALIDATION_ERROR |
| BR-ASG-02 | Tổng trọng số các bài của một lớp không được vượt 100%; phải đúng 100% mới khóa sổ được (BR-LCK-01). | DEC-E1, E7 | Service | ASSIGNMENT_WEIGHT_EXCEEDED |
| BR-ASG-03 | Chỉ GV phụ trách lớp được tạo/sửa/xóa bài, và chỉ khi lớp chưa khóa sổ. Admin chỉ xem. | DEC-C2, ISS-02 | Service | NOT_SECTION_INSTRUCTOR, SECTION_LOCKED |
| BR-ASG-04 | Mỗi bài chọn một chế độ nộp: SINGLE, OVERWRITE, MULTIPLE (bắt buộc `max_attempts` ≥ 1) hoặc OFFLINE. Chi tiết ở §7.2. | DEC-D1 | DB (enum) + Service | VALIDATION_ERROR |
| BR-ASG-05 | Bài không phải OFFLINE bắt buộc có hạn nộp và một chính sách trễ (REJECT hoặc ACCEPT_MARK_LATE). Bài OFFLINE không có hạn nộp và chính sách trễ. | DEC-D2 | Service | VALIDATION_ERROR |
| BR-ASG-06 | Khi bài đã có bài nộp: không đổi được chế độ nộp và chính sách trễ. Vẫn được đổi hạn nộp; khi đó nhãn trễ của các bài nộp được tính lại theo hạn mới. | ĐỀ XUẤT | Service | ASSIGNMENT_HAS_SUBMISSIONS |
| BR-ASG-07 | Không xóa bài đã có bài nộp hoặc đã có điểm. | ĐỀ XUẤT | Service | ASSIGNMENT_HAS_SUBMISSIONS |
| BR-ASG-08 | Mỗi bài chọn chế độ hiện điểm: IMMEDIATE (mặc định) hoặc MANUAL (ẩn tới khi GV công bố). | DEC-E6 | DB (enum) | — |
| BR-SUB-01 | Chỉ SV đang học trong lớp được nộp; lớp chưa khóa sổ; bài không phải OFFLINE. | v2, DEC-D1 | Service | NOT_ENROLLED, SECTION_LOCKED, SUBMISSION_NOT_ALLOWED |
| BR-SUB-02 | Mỗi lần nộp có ít nhất một trong hai: link (http/https) hoặc file. File cho phép pdf, docx, pptx, xlsx, zip, rar, txt; tối đa 20 MB (danh sách và dung lượng là ĐỀ XUẤT). | DEC-D3 | Service | SUBMISSION_EMPTY, FILE_TYPE_NOT_ALLOWED, FILE_TOO_LARGE |
| BR-SUB-03 | Nộp sau hạn: REJECT → từ chối; ACCEPT_MARK_LATE → nhận và gắn nhãn trễ, nhận cho tới khi lớp khóa sổ. So sánh thời gian theo UTC. Chi tiết ở §7.3. | DEC-D2, ISS-06 | Service | SUBMISSION_PAST_DUE |
| BR-SUB-04 | SINGLE: mỗi SV nộp đúng một lần. | DEC-D1 | Service + DB | SUBMISSION_LIMIT_REACHED |
| BR-SUB-05 | OVERWRITE: được thay bản cũ khi chưa có điểm; chỉ lưu bản mới nhất; thời điểm nộp và nhãn trễ lấy theo bản mới. | DEC-D1 | Service | SUBMISSION_ALREADY_GRADED |
| BR-SUB-06 | MULTIPLE: mỗi lần nộp là một bản ghi mới (lần 1…N), tối đa `max_attempts` lần; bản được chấm là lần nộp mới nhất. | DEC-D1 | Service + DB | SUBMISSION_LIMIT_REACHED |
| BR-SUB-07 | Khi SV đã có điểm cho một bài, SV không nộp thêm cho bài đó (mọi chế độ). | ĐỀ XUẤT | Service | SUBMISSION_ALREADY_GRADED |
| BR-SUB-08 | Ràng buộc DB `unique(assignment_id, student_id, attempt_no)`; SINGLE và OVERWRITE luôn có `attempt_no = 1`. | ISS-03 | DB | — |
| BR-GRD-01 | Điểm từng bài theo thang 10, từ 0.00 đến 10.00, tối đa 2 chữ số thập phân (thay cho thang 100 hiện tại). | ĐỀ XUẤT | DB (check) + Service | GRADE_OUT_OF_RANGE |
| BR-GRD-02 | Mỗi cặp (bài, SV) có tối đa một điểm, lưu ở bảng điểm riêng, không gắn vào bài nộp. GV chấm được cả khi SV không nộp và với bài OFFLINE. | DEC-E1, D1, ISS-03 | DB (unique) + Service | — |
| BR-GRD-03 | Chỉ GV phụ trách lớp được chấm/sửa điểm, khi lớp chưa khóa sổ. Sửa một điểm đã có thì ghi nhật ký (điểm cũ → điểm mới). | DEC-C2, F1, ISS-02 | Service | NOT_SECTION_INSTRUCTOR, SECTION_LOCKED |
| BR-GRD-04 | Hiển thị điểm: IMMEDIATE → SV thấy ngay khi điểm được lưu; MANUAL → SV thấy khi GV bấm công bố bài (công bố toàn bộ điểm của bài), sau đó mọi lần sửa đều hiện ngay. Khi lớp khóa sổ, mọi điểm đều hiện. Thời điểm điểm bắt đầu hiện được lưu lại để tính hạn phúc khảo. Chi tiết ở §7.4. | DEC-E6 | Service | — |
| BR-GRD-05 | Trước khi khóa sổ, điểm môn chỉ là **tạm tính** = Σ(điểm × trọng số) / Σ(trọng số các bài đã có điểm). Phía SV chỉ tính trên các điểm SV thấy được; phía GV tính trên mọi điểm. Luôn hiện kèm "đã có điểm X% trọng số" và **không** quy đổi điểm chữ/GPA. | ĐỀ XUẤT, ISS-05 | Service | — |
| BR-GRD-06 | Khi một điểm bắt đầu hiện với SV, hệ thống gửi thông báo cho SV đó. | DEC-F1 | Service | — |

## 5. Khóa sổ, kết quả môn và bảng điểm (LCK, TRN)

### 5.1 Khóa sổ

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-LCK-01 | GV phụ trách được khóa sổ khi đủ cả bốn điều kiện: (1) tổng trọng số = 100%; (2) không còn bài nộp chưa chấm (với MULTIPLE xét lần nộp mới nhất); (3) không còn phúc khảo đang chờ; (4) lớp đang PUBLISHED. | DEC-E7; (3) là ĐỀ XUẤT | Service | LOCK_PRECONDITION_FAILED |
| BR-LCK-02 | Khi khóa, với mỗi SV đang học: bài không có điểm tính 0; điểm môn hệ 10 = Σ(điểm × trọng số / 100), lưu điểm gốc, không làm tròn. | DEC-E1, E7 | Service | — |
| BR-LCK-03 | Quy đổi điểm chữ và hệ 4 theo bảng cấu hình `grade_scales`, so trực tiếp với điểm gốc: chọn bậc có ngưỡng dưới lớn nhất mà vẫn ≤ điểm. Không làm tròn trước khi quy đổi. | DEC-E2, E3 | Service | — |
| BR-LCK-04 | Kết quả môn (điểm gốc, điểm chữ, hệ 4, Đạt/Không đạt) được lưu cố định lúc khóa sổ. Sửa bảng quy đổi về sau không làm đổi kết quả đã chốt. | ĐỀ XUẤT, DEC-E3 | DB | — |
| BR-LCK-05 | Môn Non-Graded không có điểm chữ và hệ 4; kết quả là Đạt nếu điểm môn ≥ 5.0, ngược lại Không đạt (ĐỀ XUẤT, OQ-06). | DEC-E5 | Service | — |
| BR-LCK-06 | Sau khi khóa: không tạo/sửa/xóa bài, không nộp, không chấm, không xếp/hủy SV, không gửi phúc khảo; thông báo lớp vẫn đăng được. Chỉ Admin mở lại, bắt buộc có lý do. Mở lại thì xóa kết quả đã chốt; khóa lại thì tính lại từ đầu. | DEC-E7 | Service | SECTION_LOCKED, UNLOCK_REASON_REQUIRED |
| BR-LCK-07 | Khóa sổ gửi thông báo "đã có kết quả môn" cho từng SV của lớp, và được ghi nhật ký. | DEC-F1 | Service | — |

### 5.2 Bảng điểm và GPA

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-TRN-01 | Chỉ lớp đã khóa sổ mới được tính vào GPA, TBC và tín chỉ tích lũy. Lớp chưa khóa hiện "Đang học" kèm điểm tạm tính. | DEC-E3, ISS-05 | Service | — |
| BR-TRN-02 | GPA học kỳ = Σ(hệ 4 × tín chỉ) / Σ(tín chỉ), tính trên các môn tính điểm (không phải Non-Graded) đã khóa sổ trong kỳ; môn F tính với 0. | DEC-E4, E5 | Service | — |
| BR-TRN-03 | TBC hệ 10 học kỳ = Σ(điểm hệ 10 × tín chỉ) / Σ(tín chỉ), trên cùng tập môn với BR-TRN-02, dùng điểm gốc. | DEC-E4 | Service | — |
| BR-TRN-04 | GPA và TBC tích lũy tính lại từ toàn bộ môn đã khóa sổ của mọi học kỳ, **không** lấy trung bình các GPA học kỳ. | DEC-E4 | Service | — |
| BR-TRN-05 | Tín chỉ tích lũy = Σ tín chỉ các môn tính điểm đã đạt (từ D+). Môn F không được cộng. Môn Non-Graded không cộng vào tổng tín chỉ và không ảnh hưởng GPA. | DEC-E5 | Service | — |
| BR-TRN-06 | Chỉ làm tròn ở kết quả cuối: GPA và TBC hiển thị 2 chữ số thập phân, làm tròn half-up bằng `Decimal` (không dùng `round()` của Python vì hàm này làm tròn kiểu ngân hàng). Số chữ số là ĐỀ XUẤT (OQ-05). | DEC-E3 | Service | — |
| BR-TRN-07 | Khi môn đã có điểm chữ được chốt, GPA dùng trực tiếp hệ 4 của điểm chữ đó, không quy đổi lại từ điểm hệ 10. | DEC-E3 | Service | — |

### 5.3 Ví dụ tính điểm (dùng làm dữ liệu test)

**Ex1. Điểm môn.** Bốn cột: Chuyên cần 10% (9.0), Bài tập 20% (8.0), Giữa kỳ 30% (8.5), Cuối kỳ 40% (8.9).
`9.0×0.10 + 8.0×0.20 + 8.5×0.30 + 8.9×0.40 = 0.90 + 1.60 + 2.55 + 3.56 = 8.61` → **A (3.7)**.

**Ex2. Không nộp bài giữa kỳ** (khi khóa sổ tính 0):
`0.90 + 1.60 + 0 + 3.56 = 6.06` → **C (2.0)**.

**Ex3. Ngưỡng quy đổi** (không làm tròn trước): 8.4999 → **B+** (không được làm tròn lên 8.5 để thành A) · 4.9999 → **F** · 5.0 → **D+** · 10.0 → **A+**.

**Ex4. GPA học kỳ 2026-1.**

| Môn | Tín chỉ | Hệ 10 | Điểm chữ | Hệ 4 |
|---|---|---|---|---|
| CS301 | 3 | 8.61 | A | 3.7 |
| CS302 | 4 | 7.45 | B | 3.0 |
| MA201 | 3 | 4.80 | F | 0.0 |
| PE101 (Non-Graded) | 1 | — | Đạt | — |

- GPA = (3.7×3 + 3.0×4 + 0.0×3) / (3 + 4 + 3) = 23.1 / 10 = **2.31**
- TBC hệ 10 = (8.61×3 + 7.45×4 + 4.80×3) / 10 = 70.03 / 10 = 7.003 → **7.00**
- Tín chỉ tích lũy của kỳ = 3 + 4 = **7** (MA201 trượt; PE101 là Non-Graded nên không cộng)

**Ex5. GPA tích lũy.** Học kỳ 2026-2: CS401 3 TC, B+ (3.5); CS402 3 TC, A+ (4.0) → GPA kỳ 2 = (10.5 + 12.0) / 6 = **3.75**.
GPA tích lũy = (23.1 + 22.5) / (10 + 6) = 45.6 / 16 = **2.85**.
Nếu lấy trung bình hai kỳ thì được (2.31 + 3.75) / 2 = 3.03 → **sai**, không dùng (BR-TRN-04).

**Ex6. Điểm tạm tính** (trước khóa sổ): mới có Bài tập 20% (8.0) và Giữa kỳ 30% (8.5).
Tạm tính = (8.0×20 + 8.5×30) / (20 + 30) = 415 / 50 = **8.30**, hiện kèm "đã có điểm 50% trọng số", không có điểm chữ/GPA.

## 6. Phúc khảo, thông báo, nhật ký, quy tắc chung (REG, ANN, NOT, AUD, GEN)

| Mã | Rule | Nguồn | Thực thi | Mã lỗi |
|---|---|---|---|---|
| BR-REG-01 | SV gửi phúc khảo cho một điểm đang hiện với mình, khi lớp chưa khóa sổ, trong vòng 7 ngày (cấu hình được) kể từ lúc điểm bắt đầu hiện; bắt buộc ghi lý do. Thời hạn 7 ngày là ĐỀ XUẤT. | DEC-E8 | Service | REGRADE_WINDOW_CLOSED, REGRADE_REASON_REQUIRED |
| BR-REG-02 | Mỗi cặp (bài, SV) có tối đa một yêu cầu phúc khảo. | ĐỀ XUẤT | DB (unique) | REGRADE_EXISTS |
| BR-REG-03 | GV phụ trách xử lý: CHẤP NHẬN (nhập điểm mới, có thể giữ nguyên) hoặc TỪ CHỐI (bắt buộc ghi lý do). Lưu điểm cũ và điểm mới, ghi nhật ký, thông báo cho SV. | DEC-E8 | Service | REGRADE_REASON_REQUIRED |
| BR-REG-04 | Còn phúc khảo đang chờ thì lớp không khóa sổ được (xem BR-LCK-01). | ĐỀ XUẤT | Service | LOCK_PRECONDITION_FAILED |
| BR-ANN-01 | Chỉ GV phụ trách đăng/sửa/xóa thông báo lớp. SV đang học trong lớp, GV phụ trách và Admin được xem. Đăng thông báo tạo thông báo hệ thống cho SV của lớp. | DEC-C2, F1 | Service | NOT_SECTION_INSTRUCTOR, NOT_ENROLLED |
| BR-NOT-01 | Thông báo hệ thống sinh theo sự kiện: lớp có bài mới; điểm bắt đầu hiện; thông báo lớp mới; được Admin xếp vào lớp; phúc khảo được gửi (báo GV) hoặc được xử lý (báo SV); có kết quả môn. Chỉ người nhận xem và đánh dấu đã đọc. Không gửi email. | DEC-F1 | Service | — |
| BR-AUD-01 | Ghi nhật ký cho: tạo/import/khóa/mở khóa tài khoản, reset mật khẩu, đổi vai trò; Admin xếp/hủy SV (kể cả khi vượt ràng buộc); sửa điểm đã có; công bố điểm; khóa/mở sổ; xử lý phúc khảo. Nhật ký chỉ được thêm, không sửa/xóa; chỉ Admin xem. | DEC-F1 | Service + DB | — |
| BR-GEN-01 | Thời gian lưu theo UTC; API trả ISO 8601 kèm `Z`; giao diện hiển thị theo giờ Việt Nam (UTC+7); hạn nộp so sánh theo UTC. Riêng giờ học trong lịch (`start_time`, `end_time`) là giờ địa phương theo lịch trường, lưu và hiển thị nguyên văn, không quy đổi múi giờ. | ISS-08 | Service + UI | — |
| BR-GEN-02 | Mọi thao tác đọc/ghi đều kiểm tra quyền theo tài nguyên (ma trận 05 §5), không chỉ theo vai trò. | ISS-02, v2 | Service | FORBIDDEN, NOT_SECTION_INSTRUCTOR, NOT_ENROLLED |
| BR-GEN-03 | Không có quyền truy cập cho khách: mọi trang và API, trừ đăng nhập, đều yêu cầu đăng nhập. | ĐỀ XUẤT | Service + UI | AUTH_REQUIRED |

## 7. Bảng trạng thái và ma trận quyết định

### 7.1 Vòng đời lớp học phần

| Trạng thái | Ai thấy | Được làm gì | Chuyển sang | Điều kiện chuyển |
|---|---|---|---|---|
| DRAFT | Admin | Admin sửa thông tin, xếp lịch, xếp SV | PUBLISHED | Admin công bố; đã có GV và ít nhất một buổi học (ĐỀ XUẤT) |
| PUBLISHED | Admin, GV phụ trách; SV khi lớp mở đăng ký hoặc khi đã vào lớp | SV đăng ký trong đợt; GV quản lý bài, chấm, đăng thông báo | LOCKED | GV khóa sổ, đạt BR-LCK-01 |
| LOCKED | Như PUBLISHED | Chỉ đọc; vẫn đăng thông báo lớp | PUBLISHED | Admin mở lại, có lý do (BR-LCK-06) |

### 7.2 Chế độ nộp bài

| Chế độ | Số lần nộp | Nộp lại khi chưa có điểm | Lưu lịch sử | Bản được chấm |
|---|---|---|---|---|
| SINGLE | 1 | Không | — | Bản duy nhất |
| OVERWRITE | 1 bản, ghi đè | Có | Không | Bản hiện tại |
| MULTIPLE | Tối đa `max_attempts` | Có, tạo lần nộp mới | Có | Lần nộp mới nhất |
| OFFLINE | 0 (không nộp) | — | — | GV nhập điểm trực tiếp |

### 7.3 Nộp trễ

| Thời điểm nộp | REJECT | ACCEPT_MARK_LATE |
|---|---|---|
| Trước hoặc đúng hạn | Nhận, không trễ | Nhận, không trễ |
| Sau hạn, lớp chưa khóa sổ | Từ chối `SUBMISSION_PAST_DUE` | Nhận, gắn nhãn trễ |
| Lớp đã khóa sổ | Từ chối `SECTION_LOCKED` | Từ chối `SECTION_LOCKED` |

### 7.4 Hiển thị điểm cho sinh viên

| Tình huống | SV thấy điểm? | Thời điểm bắt đầu hiện (`visible_at`) |
|---|---|---|
| IMMEDIATE, đã chấm | Có, ngay khi lưu | Lúc chấm lần đầu |
| MANUAL, chưa công bố | Không | — |
| MANUAL, đã công bố | Có | Lúc công bố (hoặc lúc chấm, nếu chấm sau khi đã công bố) |
| Lớp LOCKED | Có, mọi điểm | Giữ nguyên nếu đã có; nếu chưa thì là lúc khóa sổ |

### 7.5 Trạng thái đăng ký học

`ENROLLED ⇄ DROPPED`. ENROLLED → DROPPED: SV hủy trong đợt hoặc Admin hủy. DROPPED → ENROLLED: đăng ký lại, phải qua đủ các bước kiểm tra như lần đầu.

## 8. Danh mục mã lỗi

| Mã lỗi | HTTP | Ý nghĩa |
|---|---|---|
| AUTH_REQUIRED | 401 | Chưa đăng nhập hoặc token không hợp lệ |
| AUTH_INVALID_CREDENTIALS | 401 | Sai email hoặc mật khẩu |
| ACCOUNT_DISABLED | 403 | Tài khoản bị khóa |
| PASSWORD_CHANGE_REQUIRED | 403 | Phải đổi mật khẩu trước |
| PASSWORD_POLICY_VIOLATION | 422 | Mật khẩu mới không đạt yêu cầu |
| FORBIDDEN | 403 | Không có quyền |
| NOT_SECTION_INSTRUCTOR | 403 | Không phải GV phụ trách lớp |
| NOT_ENROLLED | 403 | SV không thuộc lớp |
| NOT_FOUND | 404 | Không tìm thấy |
| VALIDATION_ERROR | 422 | Dữ liệu không hợp lệ (kèm danh sách trường lỗi) |
| EMAIL_ALREADY_EXISTS · STUDENT_CODE_EXISTS | 409 | Trùng email / mã SV |
| LAST_ADMIN_REQUIRED · ROLE_CHANGE_NOT_ALLOWED | 409 | Vi phạm rule tài khoản |
| IMPORT_INVALID_ROWS | 422 | File import có dòng lỗi |
| INVALID_STATE_TRANSITION | 409 | Chuyển trạng thái lớp không hợp lệ |
| PREREQUISITE_CYCLE · INVALID_TIME_RANGE | 422 | Dữ liệu học vụ không hợp lệ |
| SCHEDULE_ROOM_CONFLICT · SCHEDULE_INSTRUCTOR_CONFLICT · ROOM_CAPACITY_TOO_SMALL · ROOM_IN_USE | 409 | Xung đột khi xếp lịch/phòng |
| ENROLL_PERIOD_CLOSED · SECTION_NOT_OPEN | 409 | Ngoài đợt đăng ký / lớp chưa mở |
| SECTION_FULL · SCHEDULE_CONFLICT · PREREQUISITE_NOT_MET · CREDIT_LIMIT_EXCEEDED · SUBJECT_ALREADY_TAKEN · ALREADY_ENROLLED | 409 | Vi phạm ràng buộc đăng ký |
| ENROLLMENT_RULES_VIOLATED | 409 | Admin xếp lớp vi phạm ràng buộc mà chưa nhập lý do (kèm danh sách vi phạm) |
| ASSIGNMENT_WEIGHT_EXCEEDED · ASSIGNMENT_HAS_SUBMISSIONS | 409 | Vi phạm rule bài tập |
| SECTION_LOCKED | 409 | Lớp đã khóa sổ |
| SUBMISSION_NOT_ALLOWED · SUBMISSION_PAST_DUE · SUBMISSION_LIMIT_REACHED · SUBMISSION_ALREADY_GRADED | 409 | Vi phạm rule nộp bài |
| SUBMISSION_EMPTY · FILE_TYPE_NOT_ALLOWED · FILE_TOO_LARGE | 422 | Nội dung nộp không hợp lệ |
| GRADE_OUT_OF_RANGE | 422 | Điểm ngoài 0–10 hoặc sai định dạng |
| LOCK_PRECONDITION_FAILED | 409 | Chưa đủ điều kiện khóa sổ (kèm danh sách lý do) |
| UNLOCK_REASON_REQUIRED · REGRADE_REASON_REQUIRED | 422 | Thiếu lý do |
| REGRADE_WINDOW_CLOSED · REGRADE_EXISTS | 409 | Vi phạm rule phúc khảo |

## 9. Lịch sử thay đổi

| Phiên bản | Ngày | Thay đổi | Người duyệt |
|---|---|---|---|
| 0.1 | 2026-11-09 | Bản đầu, tổng hợp từ các quyết định ở 00 §4 | (chờ duyệt) |
