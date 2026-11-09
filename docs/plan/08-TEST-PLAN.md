# 08 — Kế hoạch kiểm thử và Definition of Done

> Phiên bản 0.1 · 2026-11-09 · Mỗi BR mức Must có ít nhất một test tự động (chỉ số thành công ở 02 §1)

## 1. Chiến lược

| Cấp | Phạm vi | Công cụ | Môi trường |
|---|---|---|---|
| Unit | Hàm thuần trong `api/src/domain` (tính điểm, quy đổi, GPA, trùng lịch, chính sách nộp) | pytest | Không cần DB |
| API / tích hợp | Từng BR qua HTTP: quyền, ràng buộc, mã lỗi | pytest + TestClient (cần `httpx`, hỏi trước khi cài, G4) | SQLite in-memory (ADR-15) |
| Smoke trên MySQL | Chạy seed, chạy kịch bản demo, kiểm tra tay đăng ký đồng thời | Thủ công | MySQL local (Docker) |
| Frontend | Kiểu dữ liệu, lint, build; checklist giao diện theo màn hình | `tsc`, ESLint, `next build` | Máy dev |
| Chấp nhận | Kịch bản demo §6 | Thủ công, cả nhóm | Máy demo |

Dữ liệu test tạo bằng hàm factory trong `tests/conftest.py` (tạo học kỳ, môn, lớp, SV…), không dùng dữ liệu seed demo.

## 2. Danh mục test case

Cột "Mức": M = phải có trước M-3; S = làm cùng tính năng Should.

| Mã | Kịch bản | Kết quả mong đợi | Liên quan | Mức |
|---|---|---|---|---|
| TC-ACC-01 | Admin tạo tài khoản SV | 201, có mật khẩu tạm, `must_change_password = true`; đọc lại user không thấy mật khẩu | BR-ACC-01, 03, 04 · AC-USR-01.1 | M |
| TC-ACC-02 | Gọi `POST /api/auth/register` | 404 | BR-ACC-01 · ISS-01 · AC-USR-01.3 | M |
| TC-ACC-03 | Đăng nhập bằng email viết hoa; sai mật khẩu; email không tồn tại | Lần đầu thành công; hai lần sau cùng trả `AUTH_INVALID_CREDENTIALS` | BR-ACC-02 · AC-AUTH-01.1, 01.2 | M |
| TC-ACC-04 | Tài khoản phải đổi mật khẩu gọi `GET /me/sections` | `PASSWORD_CHANGE_REQUIRED`; đổi xong thì gọi được | BR-ACC-04 · AC-AUTH-02.1 | M |
| TC-ACC-05 | Mật khẩu mới 7 ký tự / 73 byte / trùng mật khẩu cũ | 422 `PASSWORD_POLICY_VIOLATION`, không phải 500 | BR-ACC-05 · ISS-07 · AC-AUTH-02.2 | M |
| TC-ACC-06 | Khóa tài khoản rồi dùng token cũ | `ACCOUNT_DISABLED` | BR-ACC-06 · AC-USR-04.1 | M |
| TC-ACC-07 | Admin tự khóa mình; hạ quyền Admin cuối cùng | `LAST_ADMIN_REQUIRED` | BR-ACC-07 · AC-USR-04.2 | M |
| TC-ACC-08 | Import CSV có một dòng lỗi | Không tạo tài khoản nào; trả lỗi theo số dòng | BR-ACC-10 | S |
| TC-ACD-01 | Thêm buổi học trùng phòng | `SCHEDULE_ROOM_CONFLICT` kèm lớp bị trùng | BR-ACD-05 · AC-ACD-05.1 | M |
| TC-ACD-02 | Thêm buổi học trùng giờ của GV | `SCHEDULE_INSTRUCTOR_CONFLICT` | BR-ACD-05 · AC-ACD-05.2 | M |
| TC-ACD-03 | Phòng nhỏ hơn sĩ số; hai buổi 08:00–10:00 và 10:00–12:00 | Lần đầu `ROOM_CAPACITY_TOO_SMALL`; lần sau không bị coi là trùng | BR-ACD-05 · AC-ACD-05.3, 05.4 | M |
| TC-ACD-04 | Đặt tiên quyết vòng lặp A ↔ B | `PREREQUISITE_CYCLE` | BR-ACD-02 | M |
| TC-ACD-05 | SV xem lớp DRAFT; Admin công bố rồi xem lại | Trước: không thấy; sau: thấy | BR-ACD-04 · AC-ACD-04.1 | M |
| TC-ENR-01 | Đăng ký ngoài đợt | `ENROLL_PERIOD_CLOSED` | BR-ENR-01 · AC-ENR-02.1 | M |
| TC-ENR-02 | Đăng ký lớp đã đủ sĩ số | `SECTION_FULL` | BR-ENR-03 · AC-ENR-02.2 | M |
| TC-ENR-03 | Đăng ký lớp trùng lịch | `SCHEDULE_CONFLICT` | BR-ENR-04 · AC-ENR-02.3 | M |
| TC-ENR-04 | Thiếu môn tiên quyết; đang học môn tiên quyết cùng kỳ | Cả hai trả `PREREQUISITE_NOT_MET` | BR-ENR-05 · AC-ENR-02.4 | M |
| TC-ENR-05 | Vượt tín chỉ tối đa; dưới mức tối thiểu | Lần đầu `CREDIT_LIMIT_EXCEEDED`; lần sau thành công kèm cảnh báo | BR-ENR-06 · AC-ENR-02.5 | M |
| TC-ENR-06 | Lớp khác cùng môn trong kỳ; môn đã có kết quả | `SUBJECT_ALREADY_TAKEN` | BR-ENR-07 · AC-ENR-02.6 | M |
| TC-ENR-07 | Hủy trong đợt; hủy ngoài đợt | Thành công; `ENROLL_PERIOD_CLOSED` | BR-ENR-02 · AC-ENR-03.1 | M |
| TC-ENR-08 | Admin xếp SV vi phạm hai ràng buộc, không lý do / có lý do | Lần đầu `ENROLLMENT_RULES_VIOLATED` liệt kê đủ cả hai; lần sau thành công, có nhật ký | BR-ENR-08 · AC-ENR-04.1 | M |
| TC-ENR-09 | Hủy rồi đăng ký lại | Vẫn là một bản ghi, trạng thái ENROLLED | BR-ENR-09 | M |
| TC-ENR-10 | (Thủ công, MySQL) Hai request đăng ký chỗ cuối cùng cùng lúc | Chỉ một thành công | BR-ENR-03 · AC-ENR-02.2 · ADR-15 | M |
| TC-ASG-01 | GV không phụ trách tạo bài | 403 `NOT_SECTION_INSTRUCTOR` | BR-ASG-03 · ISS-02 · AC-ASG-01.1 | M |
| TC-ASG-02 | Tổng trọng số vượt 100% | `ASSIGNMENT_WEIGHT_EXCEEDED` | BR-ASG-02 · AC-ASG-01.2 | M |
| TC-ASG-03 | Bài OFFLINE có hạn nộp; MULTIPLE thiếu số lần tối đa | 422 `VALIDATION_ERROR` | BR-ASG-04, 05 · AC-ASG-01.3 | M |
| TC-ASG-04 | Bài đã có bài nộp: đổi chế độ, xóa bài; đổi hạn nộp | Hai thao tác đầu `ASSIGNMENT_HAS_SUBMISSIONS`; đổi hạn thì nhãn trễ được tính lại | BR-ASG-06, 07 · AC-ASG-01.4 | M |
| TC-SUB-01 | SINGLE nộp lần hai | `SUBMISSION_LIMIT_REACHED` | BR-SUB-04 · AC-SUB-01.1 | M |
| TC-SUB-02 | OVERWRITE nộp lại khi chưa có điểm | Còn đúng một bản, nội dung mới | BR-SUB-05 · ISS-03 · AC-SUB-01.2 | M |
| TC-SUB-03 | MULTIPLE (tối đa 3) nộp 4 lần | Ba lần đầu được lưu, lần thứ tư lỗi; GV thấy lần mới nhất | BR-SUB-06 · AC-SUB-01.3 | M |
| TC-SUB-04 | Nộp bài OFFLINE | `SUBMISSION_NOT_ALLOWED` | BR-SUB-01 · AC-SUB-01.4 | M |
| TC-SUB-05 | Nộp khi đã có điểm (mọi chế độ) | `SUBMISSION_ALREADY_GRADED` | BR-SUB-07 · AC-SUB-01.5 | M |
| TC-SUB-06 | REJECT, nộp sau hạn | `SUBMISSION_PAST_DUE` | BR-SUB-03 · ISS-06 · AC-SUB-01.6 | M |
| TC-SUB-07 | ACCEPT_MARK_LATE, nộp sau hạn | Nhận, `is_late = true` | BR-SUB-03 · AC-SUB-01.6 | M |
| TC-SUB-08 | SV không thuộc lớp nộp bài | `NOT_ENROLLED` | BR-SUB-01 · AC-SUB-01.7 | M |
| TC-SUB-09 | Trạng thái hiển thị theo từng trường hợp | Đúng một trong: Chưa nộp / Đã nộp / Nộp trễ / Đã chấm / Không cần nộp | ISS-04 · AC-SUB-03.1 | M |
| TC-GRD-01 | GV khác lớp chấm điểm | 403 `NOT_SECTION_INSTRUCTOR` | BR-GRD-03 · ISS-02 · AC-GRD-01.2 | M |
| TC-GRD-02 | Chấm 10.5 / −1 / 8.123 | `GRADE_OUT_OF_RANGE` | BR-GRD-01 · AC-GRD-01.1 | M |
| TC-GRD-03 | Chấm SV không nộp; chấm bài OFFLINE | Thành công | BR-GRD-02 · AC-GRD-01.3 | M |
| TC-GRD-04 | Bài MANUAL: SV xem trước và sau khi công bố | Trước: không thấy; sau: thấy, có `visible_at` | BR-GRD-04 · AC-GRD-02.1 | M |
| TC-GRD-05 | Điểm tạm tính theo Ex6 | 8.30, "đã có điểm 50% trọng số", không có điểm chữ | BR-GRD-05 · ISS-05 · AC-GRD-04.1 | M |
| TC-GRD-06 | Sửa một điểm đã có | Có bản ghi nhật ký điểm cũ → mới | BR-GRD-03, BR-AUD-01 | S |
| TC-LCK-01 | Khóa sổ khi tổng trọng số 90% | `LOCK_PRECONDITION_FAILED` kèm lý do | BR-LCK-01 · AC-LCK-01.1 | M |
| TC-LCK-02 | Còn bài nộp chưa chấm; còn phúc khảo đang chờ | Cả hai bị chặn kèm lý do | BR-LCK-01, BR-REG-04 | M |
| TC-LCK-03 | Khóa sổ với dữ liệu Ex1 và Ex2 | 8.61 → A (3.7); thiếu điểm giữa kỳ → 6.06 → C (2.0) | BR-LCK-02, 03 · AC-LCK-01.2 | M |
| TC-LCK-04 | Sau khóa: tạo bài, nộp, chấm, xếp SV; đăng thông báo | Bốn thao tác đầu `SECTION_LOCKED`; đăng thông báo vẫn được | BR-LCK-06 · AC-LCK-01.3 | M |
| TC-LCK-05 | GV mở lại sổ; Admin mở lại không lý do / có lý do | 403; `UNLOCK_REASON_REQUIRED`; thành công: lớp PUBLISHED, `course_results` bị xóa, có nhật ký | BR-LCK-06 · AC-LCK-02.1 | M |
| TC-LCK-06 | Đổi bảng quy đổi sau khi khóa sổ | Kết quả đã chốt không đổi | BR-LCK-04 | M |
| TC-TRN-01 | Quy đổi ở biên (Ex3) | 8.4999 → B+; 4.9999 → F; 5.0 → D+; 10.0 → A+ | BR-LCK-03 | M |
| TC-TRN-02 | GPA học kỳ (Ex4) | GPA 2.31; TBC 7.00; tín chỉ tích lũy 7 | BR-TRN-02, 03, 05 · AC-TRN-01.2 | M |
| TC-TRN-03 | GPA tích lũy (Ex5) | 2.85 (không phải 3.03) | BR-TRN-04 · AC-TRN-01.2 | M |
| TC-TRN-04 | Môn Non-Graded | Không vào GPA và tín chỉ; Đạt khi điểm ≥ 5.0 | BR-TRN-05, BR-LCK-05 | M |
| TC-TRN-05 | Làm tròn half-up bằng Decimal | 2.345 → 2.35; 7.005 → 7.01 | BR-TRN-06 | M |
| TC-TRN-06 | Lớp chưa khóa sổ trong bảng điểm | Không vào GPA, hiện "Đang học" | BR-TRN-01 · ISS-05 · AC-TRN-01.1 | M |
| TC-REG-01 | Phúc khảo quá 7 ngày; phúc khảo điểm đang ẩn | `REGRADE_WINDOW_CLOSED`; không gửi được | BR-REG-01 | S |
| TC-REG-02 | Gửi phúc khảo lần hai cho cùng một điểm | `REGRADE_EXISTS` | BR-REG-02 | S |
| TC-REG-03 | Chấp nhận phúc khảo; từ chối không lý do | Điểm đổi, lưu điểm cũ/mới, có nhật ký và thông báo; `REGRADE_REASON_REQUIRED` | BR-REG-03 | S |
| TC-ANN-01 | GV khác lớp đăng thông báo | 403 | BR-ANN-01 · AC-ANN-01.1 | M |
| TC-ANN-02 | SV ngoài lớp và SV trong lớp xem thông báo | 403; xem được | BR-ANN-01 | M |
| TC-NOT-01 | Chấm bài IMMEDIATE; chấm bài MANUAL rồi công bố | Lần đầu SV nhận một thông báo ngay; lần sau chỉ nhận khi công bố | BR-NOT-01, BR-GRD-06 | S |
| TC-GEN-01 | Các trường thời gian trong response | Đều kết thúc bằng `Z` | BR-GEN-01 · ISS-08 | M |
| TC-GEN-02 | Gọi API không có token | 401 `AUTH_REQUIRED` với mọi endpoint trừ login | BR-GEN-03 | M |
| TC-GEN-03 | Ma trận phân quyền 05 §5 | Test tham số hóa duyệt từng ô | BR-GEN-02 · NFR-SEC-03 | M |

## 3. Kiểm tra frontend

- `npx tsc --noEmit` không lỗi · `npm run lint` **0 lỗi** · `npm run build` thành công.
- Checklist cho từng màn hình ở 04 §3: đủ bốn trạng thái (đang tải, rỗng, lỗi, 403); không có `alert()`; đổi Vi/En không còn chuỗi gán cứng; hiển thị được ở chiều rộng 375 px; giờ hiển thị theo giờ Việt Nam.

## 4. Definition of Done

**Một PR được merge khi:**
- [ ] Mô tả PR ghi mã task (T-xx) và các FR/BR liên quan.
- [ ] Có test cho các BR/AC mà PR động tới; `pytest` pass.
- [ ] `npm run lint` 0 lỗi, `npx tsc --noEmit` và `npm run build` pass (nếu PR có sửa `web/`).
- [ ] Không có chuỗi giao diện gán cứng; có khóa dịch tiếng Việt.
- [ ] Nếu đổi hành vi: đã cập nhật 03/05/06 và ghi vào 09 §3 sơ đồ nào cần sửa.
- [ ] Không commit `.env`, `venv/`, `node_modules/`, `storage/`.
- [ ] Lead đã review và đồng ý.

**Một tính năng là "xong" khi:** đủ AC ở 02 §6 · test M trong §2 pass · chạy được trong kịch bản demo §6 · sơ đồ liên quan đã khớp.

**Ngưỡng coverage** (chỉ áp dụng nếu được duyệt cài `pytest-cov`): `src/domain` ≥ 90%; các module `enrollments`, `submissions`, `grading` ≥ 80%; toàn backend ≥ 60%.

## 5. Ma trận truy vết (FR mức Must)

| FR | BR | Use case | Sơ đồ | Test |
|---|---|---|---|---|
| FR-AUTH-01, 02, 03 | BR-ACC-02, 04, 05, 06 | UC-01, UC-02 | ACT-01, SEQ-01 | TC-ACC-03…06 |
| FR-USR-01, 03, 04, 05 | BR-ACC-01…03, 06…09 | UC-03 | ACT-01 | TC-ACC-01, 02, 07 |
| FR-ACD-01…04 | BR-ACD-01…04, 06 | UC-04…07 | BPMN-01, CLS-01, ERD-01 | TC-ACD-04, 05 |
| FR-ACD-05 | BR-ACD-05 | UC-08 | BPMN-01 | TC-ACD-01…03 |
| FR-ENR-01…04, 06 | BR-ENR-01…09 | UC-09…11, UC-26 | ACT-02, BPMN-01, SEQ-02, CLS-02 | TC-ENR-01…10 |
| FR-ASG-01, 02 | BR-ASG-01…08 | UC-12 | BPMN-02 | TC-ASG-01…04 |
| FR-SUB-01, 03, 04 | BR-SUB-01, 03…08 | UC-13 | ACT-03, BPMN-02, SEQ-03 | TC-SUB-01…09 |
| FR-GRD-01…04 | BR-GRD-01…05 | UC-14, UC-15 | ACT-04, BPMN-02, SEQ-04 | TC-GRD-01…05 |
| FR-LCK-01, 02 | BR-LCK-01…07 | UC-18, UC-19 | ACT-06, BPMN-03, SEQ-05 | TC-LCK-01…06 |
| FR-TRN-01 | BR-TRN-01…07 | UC-20 | BPMN-03, SEQ-06 | TC-TRN-01…06 |
| FR-TRN-02 | BR-ACD-05, BR-GEN-01 | UC-21 | — | TC-GEN-01, kiểm tra tay |
| FR-ANN-01 | BR-ANN-01 | UC-22 | — | TC-ANN-01, 02 |
| FR-DSH-01, 02 | — | — | — | Kịch bản demo §6 |

## 6. Kịch bản demo (khoảng 12 phút, dùng dữ liệu seed ở 05 §6)

1. **Admin** đăng nhập → Người dùng → tạo một SV → hộp hiện mật khẩu tạm một lần (BR-ACC-03).
2. **Admin** → Lớp học phần kỳ 2027-1 → thêm buổi học vào Lab301 Thứ Tư 13:30 → hệ thống báo trùng phòng (BR-ACD-05).
3. Đăng nhập **sv.moi** → bị chuyển tới trang đổi mật khẩu (BR-ACC-04) → đổi xong vào dashboard.
4. **SV** → Đăng ký học phần → thử EN101-01 (đủ chỗ), CS302-01 cùng MA101-02 (trùng lịch), CS401-01 (thiếu tiên quyết) → mỗi lần hiện đúng lý do → đăng ký một lớp hợp lệ → xem thời khóa biểu.
5. **GV** → lớp CS201-01 (2026-2) → tab Bài tập: tổng trọng số; tạo một bài ở chế độ hiện điểm MANUAL.
6. **SV (2026-2)** → nộp bài OVERWRITE rồi nộp lại; nộp bài REJECT đã quá hạn thì bị chặn; bài ACCEPT_MARK_LATE được gắn nhãn trễ.
7. **GV** → chấm bài; với bài MANUAL, SV chưa thấy điểm → GV công bố → SV thấy (và nhận thông báo, nếu đã làm S).
8. (S) **SV** gửi phúc khảo → **GV** chấp nhận và đổi điểm.
9. **GV** → lớp CS301-01 → tab Khóa sổ: checklist báo còn bài chưa chấm → chấm nốt → khóa sổ.
10. **SV** → Bảng điểm: có kết quả mới, GPA học kỳ và GPA tích lũy; giải thích cách tính theo Ex4, Ex5.
11. **GV** thử sửa điểm sau khi khóa → `SECTION_LOCKED`. **Admin** mở lại sổ kèm lý do → (C) xem trong nhật ký.
12. (S) Đổi giao diện sang English.

## 7. Lệnh chạy

```bash
cd api && source venv/bin/activate && pytest -q
cd web && npm run lint && npx tsc --noEmit && npm run build
```
