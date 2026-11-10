# Báo cáo cá nhân — Trần Gia Bảo - 2A202603914

## 1. Thông tin thành viên

- Họ tên: Trần Gia Bảo
- MSSV: 2A202603914
- Email: 26ai.baotg@vinuni.edu.vn (GitHub: Jay-Gabriel, commit: trangiabao433@gmail.com)

## 2. Phần việc phụ trách

- Xây dựng và tích hợp 4 tool mới cho Agent: `cite`, `calc`, `text_stats`, `table_format` kèm tài liệu `TOOL.md`, đăng ký trong `starter_v0/tools/__init__.py` và `starter_v0/artifacts/tools.yaml`.
- Đảm nhận triển khai 4 thử thách Bonus:
  1. **Bonus 1 (1 điểm) — Test Challenge:** Điền 14 test stubs cho các tool có sẵn, đưa test suite về 0 skipped tests.
  2. **Bonus 2 (2 điểm) — Live Telegram Action:** Cấu hình bot Telegram, kiểm tra ranh giới an toàn (`clarify(yes_no)` trước khi `send(confirmed=true)`), thực hiện gửi tin nhắn và lưu transcript.
  3. **Bonus 3 (3 điểm) — ≥ 4 Custom Tools:** Viết 4 công cụ offline hữu ích, bổ sung bộ ca kiểm thử mở rộng `eval_research_extension.json` (E11, E12, E13) và bộ unit test chặt chẽ.
  4. **Bonus 4 (4 điểm) — Small Local Model Challenge:** Triển khai hạ tầng mô hình nhỏ cục bộ (Ollama), benchmark 2 model 3B (`qwen2.5:3b` và `llama3.2:3b`), tối ưu prompt `system_prompt_local.md` (`v4-local`, `v5-local`), và đóng góp số liệu phân tích mục B7 trong báo cáo nhóm.
- Duy trì và nâng cấp toàn bộ test suite đạt **143 passed, 0 skipped, 0 failed**.

## 3. Đóng góp cụ thể

### 1. Xây dựng 4 Tool mới và bộ Unit Test
- **Tool `cite` (`starter_v0/tools/cite/`):** Tự động sinh trích dẫn chuẩn APA 7 hoặc BibTeX từ metadata bài báo (`title`, `authors`, `published`, `url`). Tự động xử lý các ca phức tạp (2 đến 20 tác giả, ≥ 21 tác giả, khuyết tác giả, khuyết năm). Kèm 13 unit tests.
- **Tool `calc` (`starter_v0/tools/calc/`):** Công cụ tính toán biểu thức số học và thống kê (mean, median, stdev, min, max, sum) an toàn bằng cây cú pháp trừu tượng (Python AST). Chặn toàn bộ truy cập thuộc tính nguy hiểm. Sau khi rà soát lỗi bảo mật DoS, đã bổ sung cơ chế chặn lũy thừa quá lớn (ước tính quá 10.000 bit), chặn nhân danh sách khổng lồ và giới hạn biểu thức tối đa 500 ký tự; kèm 9 unit tests (5 test gốc + 4 test hồi quy).
- **Tool `text_stats` (`starter_v0/tools/text_stats/`):** Phân tích thống kê văn bản: đếm từ, ký tự, số câu, ước tính thời gian đọc và tính chỉ số độ dễ đọc Flesch Reading Ease; kèm 4 unit tests.
- **Tool `table_format` (`starter_v0/tools/table_format/`):** Chuyển đổi dữ liệu có cấu trúc thành Markdown Table chuẩn, hỗ trợ căn lề từng cột (`left`, `center`, `right`), tự động cân bằng số cột; kèm 4 unit tests.
- **Test Challenge:** Điền 14 stub test còn thiếu cho các tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`), đưa test suite lên **143 passed, 0 skipped, 0 failed**.

### 2. Thử nghiệm gửi Telegram sau xác nhận (Bonus 2)
- Khởi tạo Telegram Bot và lấy chat ID cá nhân (`5701163375`).
- Kiểm tra ranh giới an toàn: lượt 1 người dùng yêu cầu đăng tin -> Agent gọi `clarify(response_type="yes_no")` để xin xác nhận; lượt 2 sau khi người dùng đồng ý tường minh -> Agent mới gọi `send(confirmed=True)` và gửi tin nhắn thật lên Telegram qua Bot API.
- Xuất file transcript bằng chứng: `starter_v0/transcripts/v3_telegram_real_openrouter_20261111T013500.transcript.json`.

### 3. Small Local Model Challenge (Bonus 4)
- Cài đặt Ollama nhị phân vào `~/.local/bin/ollama` (không cần sudo), cấu hình chạy ngầm `ollama serve` (port 11434).
- Tải 2 model 3B: `qwen2.5:3b` và `llama3.2:3b`.
- Đo đạc baseline trên `eval_base.json` (chạy trên bộ 14 tools): `qwen2.5:3b` đạt 55% (11/20), `llama3.2:3b` đạt 30% (6/20).
- Thiết kế file prompt rút gọn `system_prompt_local.md` gồm 18 dòng rule-based đanh thép, thiết lập rào chắn phủ định chặn gọi tool ngoài phạm vi.
- Chạy 2 vòng tối ưu (`v4-local`, `v5-local`), đưa độ chính xác của `qwen2.5:3b` lên 75% (15/20) và multi-turn đạt 100% (6/6). Nhóm đã kiểm chứng thực nghiệm: bản `v5-local` cho kết quả giống hệt `v4-local` (giả thuyết v5 không tạo thêm khác biệt); khi đem prompt `v5-local` chạy ngược trên model cloud (`gpt-4o-mini`) thì độ chính xác tụt xuống 0.90 và multi-turn tụt xuống 0.67 (hỏng ca M01 và M06).
- Đóng góp số liệu phân tích mục B5, B5a và B7 trong báo cáo nhóm `report/team/group_report.md`.

## 4. Bằng chứng

- **File mã nguồn và cấu hình:**
  - `starter_v0/tools/cite/`, `starter_v0/tools/calc/`, `starter_v0/tools/text_stats/`, `starter_v0/tools/table_format/` (kèm `TOOL.md` tương ứng).
  - `starter_v0/tests/test_tools_todo.py`, `starter_v0/data/eval_research_extension.json`.
  - `starter_v0/artifacts/system_prompt_local.md`, `starter_v0/artifacts/version_log.csv`.
- **File run và transcript bằng chứng:**
  - `starter_v0/transcripts/v3_telegram_real_openrouter_20261111T013500.transcript.json` (phiên tương tác gửi Telegram sau xác nhận).
  - Các file run local và cloud trên bộ 14 tools:
    + `starter_v0/runs/v3-qwen3b_B_base_ollama_20261111T014257117342.json`
    + `starter_v0/runs/v3-llama3b_B_base_ollama_20261111T014442478093.json`
    + `starter_v0/runs/v4-local_B_base_ollama_20261111T014656952766.json`
    + `starter_v0/runs/v5-local_B_base_ollama_20261111T014908279941.json`
    + `starter_v0/runs/v3-14tools_B_base_openrouter_20261111T021154387572.json` (cloud 14 tool: 0.95)
    + `starter_v0/runs/v3-14tools_B_extension_openrouter_20261111T021300460391.json` (extension: E11-E13 pass)
    + `starter_v0/runs/v5-local-cloud_B_base_openrouter_20261111T021438902981.json` (kiểm tra ngược trên cloud: 0.90)
- **Lịch sử commit kỹ thuật (tác giả `jay <trangiabao433@gmail.com>` trên `main`):**
  - `a39b590` Add cite tool (APA/BibTeX) with unit tests
  - `7ffea6b` Test challenge: fill 14 tool unit tests, pytest 111 passed / 0 skipped
  - `3726a90` feat(bonus): implement 3 new tools (calc, text_stats, table_format) with full unit tests and eval cases
  - `abe8c37` feat(bonus): live telegram delivery transcript with user confirmation boundary
  - `cb41f08` feat(bonus): complete Small Local Model Challenge (B7) with qwen2.5:3b and llama3.2:3b
  - `5a4449c` Bonus hardening: cap calc pow/list/length, cloud evals on 14 tools, v5-local on cloud, rewrite B7 with measured data
- **Kết quả kiểm thử tự động:** `pytest` đạt **143 passed, 0 skipped, 0 failed** trong 1.67s.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - *Công cụ AI:* Sử dụng trợ lý AI (Kiro, Claude, ChatGPT) để hỗ trợ sinh khung phân tích cú pháp AST cho tool `calc`, công thức âm tiết và Flesch Reading Ease cho `text_stats`, và gợi ý các test stubs.
  - *Cách tự kiểm tra:*
    + Chạy `pytest` toàn bộ 143 test cases offline.
    + Tự kiểm tra đột biến (mutation testing): cố tình làm sai guardrail của `send`, logic chia dòng của `policy`, giới hạn ký tự của `fetch`, và xác nhận các unit test tương ứng báo đỏ trước khi khôi phục code.
    + Thử nghiệm stress test cho `calc` với các biểu thức DoS (`10**10**10`, `[0]*10**9`) để xác nhận cơ chế bảo vệ từ chối tính toán trong ~0.2s mà không làm sập server.
    + Kiểm tra transcript và run files để đảm bảo API key, Telegram bot token không bị rò rỉ vào mã nguồn hay log git.

## 5. Tự đánh giá

- **Làm được:**
  - Viết 4 tool mới hoàn toàn (`cite`, `calc`, `text_stats`, `table_format`) chạy offline, tuân thủ đúng tool contract (trả error dict khi input sai, không raise exception).
  - Khắc phục lỗ hổng bảo mật DoS trong `calc` bằng các rào chắn độ dài và kích thước số mũ, bổ sung 4 test hồi quy bảo vệ.
  - Hoàn thành bộ test challenge, đưa toàn bộ test suite từ 17 skipped về 0 skipped (143 passed).
  - Triển khai thành công 2 model 3B qua Ollama, đo đạc dữ liệu thực tế và thực hiện phân tích đối sánh đa chiều giữa local và cloud.
- **Hạn chế đã biết:**
  - *Bằng chứng Telegram:* Do tin nhắn được gửi vào tài khoản bot và chat ID cá nhân của người viết (Bảo), các thành viên khác hoặc người chấm không thể tự truy cập trực tiếp kênh để xem tin nhắn nếu không có chat ID/token này. File transcript là bằng chứng ghi lại từ session tương tác.
  - *Bộ test extension:* Việc thêm các case E11-E13 vào `starter_v0/data/eval_research_extension.json` dù không sửa nội dung các case có sẵn (E01-E10) nhưng vẫn thuộc diện chỉnh sửa file extension, cần hỏi ý kiến coach để xác nhận tính hợp lệ theo quy định `RULES.md`.
  - *Prompt local trên cloud:* Bản prompt rút gọn cho model nhỏ khi chạy ngược trên cloud làm tụt điểm (từ 0.95 xuống 0.90, multi-turn tụt còn 0.67) do các luật ngắn làm mất khả năng giữ ngữ cảnh đa lượt của GPT-4o-mini.
  - *Chưa có link deploy public:* Giao diện Web UI hiện chỉ chạy nội bộ trên máy (`127.0.0.1:8000`).
