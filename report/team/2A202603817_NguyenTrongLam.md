# Báo cáo cá nhân — Nguyễn Trọng Lâm - 2A202603817

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trọng Lâm (nhóm trưởng)
- MSSV: 2A202603817
- Email: 26ai.lamnt2@vinuni.edu.vn (GitHub: NTLam108, commit: lam.nt108204@gmail.com)

## 2. Phần việc phụ trách

- Quản lý repo nhóm, phân công nhiệm vụ và rà soát tiến độ checkpoints.
- Setup môi trường, cấu hình `.env`, chạy `scripts/preflight_provider.py`.
- Thực hiện chạy baseline `v0` và phân tích các dạng lỗi (Mục B2 trong `group_report.md`).
- Lên giả thuyết và thực hiện 3 vòng tối ưu cốt lõi: `v1` (tối ưu system prompt), `v2` (tinh chỉnh tool description), và `v3` (bổ sung cơ chế an toàn xác nhận trước khi gửi `send`).
- Ghi nhận nhật ký phiên bản vào `starter_v0/artifacts/version_log.csv`.

## 3. Đóng góp cụ thể

- **Khởi tạo và kiểm tra provider:** Chạy preflight provider với OpenRouter (`openai/gpt-4o-mini`), xác nhận kết nối và định dạng phản hồi chuẩn xác.
- **Chạy Baseline `v0`:** Chạy bộ đánh giá `eval_base.json` cho phiên bản starter `v0`, thu được 13/20 passed (65% accuracy). Phân tích chi tiết 7 ca lỗi (R08, R10, R11, R12, R13, R14, M03) do các chỉ dẫn xấu trong prompt starter gây ra.
- **Vòng tối ưu `v1` (`system_prompt.md`):** Loại bỏ các quy tắc sai lệch (như ép dùng lookup cho mọi câu hỏi, tự ý bịa account/link); thêm quy tắc gọi `clarify` khi thiếu thông tin, từ chối câu ngoài phạm vi và ranh giới xác nhận trước khi gửi. Kết quả v1 tăng vọt lên 16/20 passed (80% accuracy).
- **Vòng tối ưu `v2` (`tools.yaml`):** Nhận diện lỗi phân vân giữa các tool mạng xã hội (`timeline`, `social_search`, `lookup`) trong các ca multi-turn (M02, M06). Tinh chỉnh lại description của 4 tool trong `tools.yaml`, định rõ khi nào dùng account timeline và khi nào tìm kiếm theo chủ đề. Kết quả v2 đạt 19/20 passed (95% accuracy).
- **Vòng tối ưu `v3` (`clarify` / `send` boundary):** Tinh chỉnh mô tả của `clarify` và `send` để phân định rõ ràng giữa câu hỏi lấy thêm thông tin (`response_type="text"`) và câu hỏi xin xác nhận hành động (`response_type="yes_no"`). Giữ vững độ chính xác 19/20 (95% accuracy), toàn bộ tool routing và multi-turn đạt 100%.

## 4. Bằng chứng

- **File/Commit:**
  - `d4de72b` CP1: baseline v0 run, version log and failure analysis
  - `f7128f7` CP2 v1: remove bad prompt instructions, add clarify/confirm/scope rules
  - `7e9089b` CP2 v2: clarify routing boundaries in tools.yaml
  - `70b5c7a` CP2 v3: add send confirmation boundary to clarify/send
- **File run kết quả:**
  - `starter_v0/runs/v0_B_base_openrouter_20261110T175342743576.json` (13/20 - 65%)
  - `starter_v0/runs/v1_B_base_openrouter_20261110T181321621691.json` (16/20 - 80%)
  - `starter_v0/runs/v2_B_base_openrouter_20261110T183311636102.json` (19/20 - 95%)
  - `starter_v0/runs/v3_B_base_openrouter_20261110T183608163642.json` (19/20 - 95%)
- **Tài liệu báo cáo:**
  - Mục B1, B2, B6 trong `report/team/group_report.md`.
  - `starter_v0/artifacts/version_log.csv`.

## 5. Tự đánh giá

- **Làm được:** Hoàn thành xuất sắc toàn bộ chuỗi tối ưu theo vòng lặp evidence-driven đúng chuẩn yêu cầu lab: đo baseline -> đọc log lỗi -> đặt giả thuyết -> sửa 1 thành phần -> đo lại. Đưa độ chính xác của agent từ 65% lên 95%, giải quyết triệt để các vấn đề về routing và bảo vệ an toàn dữ liệu.
- **Hạn chế đã biết:** Ca lỗi duy nhất còn lại ở v3 là R12 (yêu cầu 'đăng bản tin này lên Telegram' nhưng chưa có nội dung). Model gọi `clarify` dạng `text` để xin nội dung thay vì gọi `yes_no` để xin xác nhận gửi. Đây là phản ứng hợp lý về mặt trải nghiệm người dùng thực tế, nhưng bị tính là FAIL trong cơ chế eval so khớp cứng.
