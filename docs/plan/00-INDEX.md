# CampusHub v3 — Bộ tài liệu kế hoạch

> Phiên bản 0.1 (bản nháp đầu) · Ngày 2026-11-09 · Hạn chung cho tài liệu, sơ đồ và demo: khoảng **2026-11-23**
>
> Trạng thái: **chờ nhóm duyệt.** Mục nào ghi **ĐỀ XUẤT** là do người soạn đề xuất, cần được duyệt trước khi code.

## 1. Mục đích

Đây là bản thiết kế cho đợt tối ưu CampusHub v3 (FastAPI + MySQL + Next.js), phục vụ bảo vệ đồ án môn **System Design**. Sơ đồ, code và test đều dẫn chiếu tới các mã định danh (FR, BR, AC…) trong bộ tài liệu này. Nhờ vậy, khi hội đồng hỏi một chi tiết, nhóm luôn chỉ ra được rule nằm ở đâu, sơ đồ nào thể hiện nó, code nào thực thi nó và test nào kiểm chứng nó.

## 2. Danh sách tài liệu (theo thứ tự đọc)

| # | File | Nội dung | Phụ trách | Trạng thái |
|---|---|---|---|---|
| 00 | `00-INDEX.md` | Mục lục, quyết định đã chốt, quy ước mã, thuật ngữ | Lead | Nháp |
| 01 | `01-AS-IS.md` | Hiện trạng hệ thống và các lỗi đã tìm (đầu vào cho sơ đồ as-is) | Lead | Nháp |
| 02 | `02-PRD.md` | Mục tiêu, persona, phạm vi MoSCoW, FR, NFR, AC | Lead | Nháp |
| 03 | `03-BUSINESS-RULES.md` | Danh mục rule nghiệp vụ BR, bảng trạng thái, ví dụ tính điểm | Lead | Nháp |
| 04 | `04-UX-SPEC.md` | Màn hình, trạng thái giao diện, design token, i18n | Lead + TV | Nháp |
| 05 | `05-DATA-MODEL.md` | ERD to-be, lược đồ quan hệ, ràng buộc, ma trận phân quyền, seed | Lead | Nháp |
| 06 | `06-ARCHITECTURE.md` | Cấu trúc module, luồng request, hợp đồng API, quyết định kiến trúc | Lead | Nháp |
| 07 | `07-DIAGRAMS.md` | Danh sách sơ đồ as-is/to-be, quy ước vẽ, phân công, checklist | TV1, TV2 | Nháp |
| 08 | `08-TEST-PLAN.md` | Test theo BR/AC, Definition of Done, ma trận truy vết, kịch bản demo | Lead | Nháp |
| 09 | `09-ROADMAP.md` | Giai đoạn, mốc, tiến độ (PROGRESS), nợ kỹ thuật, rủi ro | Lead | Nháp |
| 10 | `10-TASKS.md` | Đặc tả việc giao cho từng thành viên | Lead | Nháp |
| — | `/AGENTS.md` (+ `/CLAUDE.md`) | Luật làm việc chung cho người và AI | Lead | Nháp |

Nếu thiếu thời gian, ưu tiên hoàn thiện theo thứ tự **03 → 02 → 05 → 06 → 07**. Các file 08–10 cập nhật dần trong quá trình làm.

## 3. Quy ước mã định danh

| Tiền tố | Ý nghĩa | Ví dụ | Định nghĩa ở |
|---|---|---|---|
| `DEC-xx` | Quyết định đã chốt với chủ dự án | DEC-E2 | 00 §4 |
| `OQ-xx` | Câu hỏi mở | OQ-01 | 00 §5 |
| `ISS-xx` | Lỗi của hệ thống hiện tại | ISS-03 | 01 |
| `FR-<nhóm>-xx` | Yêu cầu chức năng | FR-ENR-02 | 02 |
| `NFR-<nhóm>-xx` | Yêu cầu phi chức năng | NFR-SEC-01 | 02 |
| `AC-<nhóm>-xx.y` | Tiêu chí chấp nhận của một FR | AC-ENR-02.3 | 02 |
| `BR-<nhóm>-xx` | Rule nghiệp vụ | BR-LCK-02 | 03 |
| `SCR-xx` | Màn hình | SCR-S02 | 04 |
| `ADR-xx` | Quyết định kiến trúc | ADR-02 | 06 |
| `UC-xx` | Use case | UC-10 | 07 |
| `TC-<nhóm>-xx` | Test case | TC-ENR-04 | 08 |
| `M-x` | Mốc tiến độ | M-1 | 09 |
| `T-xx` | Việc được giao | T-20 | 10 |

Mã nhóm dùng chung: **ACC** tài khoản · **ACD** học vụ (học kỳ, môn, phòng, lớp, lịch) · **ENR** đăng ký học · **ASG** bài tập/cột điểm · **SUB** nộp bài · **GRD** chấm và công bố điểm · **LCK** khóa sổ và tổng kết · **TRN** bảng điểm/GPA · **REG** phúc khảo · **ANN** thông báo lớp · **NOT** thông báo hệ thống · **AUD** nhật ký thao tác · **STA** thống kê · **DSH** dashboard · **I18N** đa ngôn ngữ · **GEN** quy tắc chung.

## 4. Quyết định đã chốt với chủ dự án (2026-11-09)

**A. Mục tiêu và cách làm**
- **DEC-A1** Dùng để bảo vệ đồ án System Design. Tài liệu, sơ đồ và demo có cùng hạn, khoảng 2026-11-23. Không chia việc theo ngày, chỉ cần mọi việc xong trước hạn.
- **DEC-A2** Giữ stack FastAPI + MySQL + Next.js, cho phép refactor mạnh.
- **DEC-A3** Đạt đủ các rule nghiệp vụ của v2, rồi làm vượt v2.
- **DEC-A4** Nhóm 3 người: Lead code phần lớn; TV1, TV2 học dự án và làm các tính năng được giao.
- **DEC-A5** Tài liệu và sơ đồ mô tả cả as-is lẫn to-be. Rubric của môn sẽ được bổ sung vào `docs/references/`.
- **DEC-A6** Chia việc song song: chốt PRD, BR và ERD trước; sau đó Lead code, TV1/TV2 vẽ sơ đồ, Lead duyệt.
- **DEC-A7** Phạm vi chia theo mức ưu tiên MoSCoW để kịp hạn.

**B. Sơ đồ**
- **DEC-B1** Bốn sơ đồ UML trọng tâm: Use Case, Activity, Sequence, Class.
- **DEC-B2** Thêm BPMN 2.0, ERD và lược đồ quan hệ.
- **DEC-B3** Vẽ bằng draw.io. Với BPMN, chuẩn bị cả file `.bpmn` (BPMN 2.0 XML chuẩn) lẫn `.drawio` cho tới khi giảng viên xác nhận (OQ-02).

**C. Tài khoản và đăng ký học**
- **DEC-C1** Không có đăng ký công khai; Admin tạo mọi tài khoản (từng người hoặc import CSV/Excel). Đăng nhập bằng email. Mật khẩu ban đầu do hệ thống sinh ngẫu nhiên, Admin tải về một lần để gửi. Bắt buộc đổi mật khẩu ở lần đăng nhập đầu.
- **DEC-C2** Admin tạo học kỳ, môn học, lớp học phần, phòng học; xếp lịch; phân công giảng viên.
- **DEC-C3** Sinh viên vào lớp theo hai cách: Admin xếp, hoặc tự đăng ký/hủy trong đợt mở.
- **DEC-C4** Khi vào lớp, hệ thống kiểm tra sĩ số tối đa, trùng lịch, môn tiên quyết và giới hạn tín chỉ mỗi kỳ.

**D. Bài tập và nộp bài** (giảng viên đặt cho từng bài)
- **DEC-D1** Chọn 1 trong 4 chế độ nộp: nộp 1 lần (SINGLE), nộp lại ghi đè (OVERWRITE), nhiều lần có lịch sử (MULTIPLE), không cần nộp (OFFLINE).
- **DEC-D2** Chọn 1 trong 2 chính sách nộp trễ: không nhận (REJECT), hoặc nhận và gắn nhãn trễ (ACCEPT_MARK_LATE).
- **DEC-D3** Sinh viên nộp bằng link hoặc upload file.

**E. Điểm**
- **DEC-E1** Mỗi cột điểm là đúng 1 bài; trọng số do giảng viên đặt, tổng bằng 100%; điểm môn = Σ(điểm bài × trọng số).
- **DEC-E2** Bảng quy đổi, lưu thành cấu hình trong DB: A+ ≥ 9.0 (4.0) · A ≥ 8.5 (3.7) · B+ ≥ 8.0 (3.5) · B ≥ 7.0 (3.0) · C+ ≥ 6.5 (2.5) · C ≥ 5.5 (2.0) · D+ ≥ 5.0 (1.5) · F < 5.0 (0.0).
- **DEC-E3** Không làm tròn điểm hệ 10 trước khi quy đổi; tính từ điểm gốc, chỉ làm tròn kết quả cuối. Môn đã có điểm chữ chốt thì dùng trực tiếp điểm chữ đó.
- **DEC-E4** GPA và TBC hệ 10 học kỳ tính theo trọng số tín chỉ. GPA tích lũy tính lại trên toàn bộ tín chỉ, không lấy trung bình các kỳ.
- **DEC-E5** Môn F tính 0 vào GPA; tín chỉ tích lũy chỉ cộng môn đạt (từ D+). Môn Non-Graded không tính vào tín chỉ và GPA.
- **DEC-E6** Mặc định điểm hiện ngay khi chấm; giảng viên có thể chọn ẩn rồi công bố từng bài.
- **DEC-E7** Khóa sổ cuối kỳ: bài không nộp tính 0; không khóa được khi còn bài đã nộp mà chưa chấm, hoặc tổng trọng số khác 100%; sau khi khóa chỉ Admin mở lại được.
- **DEC-E8** Có chức năng phúc khảo.

**F. Tính năng khác, giao diện, vận hành**
- **DEC-F1** Có thông báo trong hệ thống, nhật ký thao tác, thống kê cho Admin, quản lý phòng học, import CSV/Excel.
- **DEC-F2** UI đổi được Vi/En. Trước mắt refactor cấu trúc UI; thiết kế lại theo hướng tối giản là lựa chọn để sau, khi đó không đổi logic nghiệp vụ.
- **DEC-F3** Demo chạy ổn định trên máy local; deploy để sau nếu cần.
- **DEC-F4** Dùng một repo chung (`github.com/kitalikedev/CampusHub`), mỗi thành viên một nhánh, merge qua PR. Đẩy tài liệu kế hoạch trước; code chỉ đẩy sau khi có bản demo sơ bộ. Commit đầu tiên là `Initial Commit`.

**G. Giả định** (sai thì báo Lead)
- **G1** MySQL hiện chỉ chứa dữ liệu seed, nên khi đổi schema có thể xóa đi rồi seed lại.
- **G2** Tài liệu viết tiếng Việt, giữ thuật ngữ tiếng Anh.
- **G3** Repo GitHub chưa có code v2 (kiểm tra khi push).
- **G4** Thư viện mới chỉ cài vào `api/venv` và `web/node_modules`, và hỏi Lead trước mỗi lần cài.
- **G5** Tài khoản demo trong seed dùng mật khẩu cố định ghi trong tài liệu, chỉ dùng trên máy local.

## 5. Câu hỏi mở

| Mã | Câu hỏi | Cách xử lý tạm thời | Ai trả lời |
|---|---|---|---|
| OQ-01 | Học lại/học cải thiện thì GPA tích lũy lấy lần cao nhất hay lần gần nhất? | Chặn đăng ký lại môn đã có kết quả (BR-ENR-07); dữ liệu vẫn thiết kế để thêm sau | Chủ dự án |
| OQ-02 | Môn yêu cầu BPMN 2.0 XML chuẩn (`.bpmn`) hay XML của draw.io? | Làm cả hai dạng | Giảng viên |
| OQ-03 | Rubric chấm điểm của môn | Bổ sung vào `docs/references/`, rà lại 07-DIAGRAMS | Chủ dự án |
| OQ-04 | Văn bản chính thức về ngưỡng điểm và cách làm tròn | Dùng DEC-E2/E3; bảng quy đổi là cấu hình, đổi được | Chủ dự án |
| OQ-05 | Hiển thị điểm môn và GPA bao nhiêu chữ số thập phân? | ĐỀ XUẤT 2 chữ số | Chủ dự án |
| OQ-06 | Môn Non-Graded xét Đạt theo ngưỡng nào? | ĐỀ XUẤT điểm môn ≥ 5.0 | Chủ dự án |
| OQ-07 | Giới hạn tín chỉ khi đăng ký có tính môn Non-Graded không? | ĐỀ XUẤT có tính (vì vẫn là khối lượng học) | Chủ dự án |

## 6. Thuật ngữ

| Tiếng Việt | Tiếng Anh (dùng trong code) | Giải thích |
|---|---|---|
| Học kỳ | Semester | Có ngày bắt đầu/kết thúc, đợt đăng ký, giới hạn tín chỉ |
| Môn học | Subject | Mã môn, tên, số tín chỉ, cờ Non-Graded, môn tiên quyết |
| Lớp học phần | Course Section | Một lần mở môn trong một học kỳ, có giảng viên và sĩ số |
| Buổi học | Schedule Slot | Thứ, giờ bắt đầu, giờ kết thúc, phòng |
| Đăng ký học | Enrollment | Quan hệ sinh viên – lớp học phần |
| Bài tập / Cột điểm | Assignment | Một cột của sổ điểm, có trọng số; có thể là bài thi offline |
| Bài nộp / Lần nộp | Submission / Attempt | Nội dung sinh viên nộp; chế độ MULTIPLE có nhiều lần nộp |
| Điểm bài | Grade | Điểm 0–10 của một sinh viên cho một bài |
| Sổ điểm | Gradebook | Bảng sinh viên × bài của một lớp |
| Khóa sổ | Lock | Chốt điểm cuối kỳ của lớp, sau đó chỉ đọc |
| Kết quả môn | Course Result | Điểm hệ 10, điểm chữ, hệ 4, đạt/không đạt được chốt khi khóa sổ |
| Phúc khảo | Regrade Request | Yêu cầu chấm lại một điểm bài |
| Thông báo lớp | Announcement | Giảng viên đăng cho lớp |
| Thông báo hệ thống | Notification | Chuông thông báo theo sự kiện |
| Nhật ký thao tác | Audit Log | Ghi lại ai làm gì với dữ liệu nhạy cảm |

## 7. Cách thay đổi một quyết định

- Đổi rule thì sửa `03-BUSINESS-RULES.md` (ghi vào lịch sử thay đổi), đồng thời cập nhật FR/AC, sơ đồ và test liên quan trong **cùng một PR**.
- Không code một rule chưa có trong 03. Thấy thiếu thì thêm một dòng OQ và hỏi Lead, không tự đoán.
