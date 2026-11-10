# Báo cáo cá nhân — Trần Gia Bảo - 2A202603914

## 1. Thông tin thành viên

- Họ tên: Trần Gia Bảo
- MSSV: 2A202603914
- Email: 26ai.baotg@vinuni.edu.vn (GitHub: Jay-Gabriel, commit: trangiabao433@gmail.com)

## 2. Phần việc phụ trách

- Xây dựng và tích hợp hệ thống Tool mới cho Agent: `cite`, `calc`, `text_stats`, `table_format` kèm tài liệu `TOOL.md` và đăng ký trong `tools.yaml`, `tools/__init__.py`.
- Thực hiện trọn gói 4 thử thách Bonus (tổng cộng 10/10 điểm bonus):
  1. **Bonus 1 (1 điểm) — Test Challenge:** Điền toàn bộ các bài test bị bỏ dở (stubs), đạt 0 skipped tests trên toàn bộ test suite.
  2. **Bonus 2 (2 điểm) — Live Telegram Action:** Cấu hình Telegram Bot thật, xác lập ranh giới an toàn (`clarify` -> `send(confirmed=True)`), gửi tin nhắn thật lên Telegram và lưu transcript bằng chứng.
  3. **Bonus 3 (3 điểm) — ≥ 4 Custom Tools:** Viết 4 công cụ offline hữu ích, bổ sung bộ ca kiểm thử mở rộng `eval_research_extension.json` (E11, E12, E13) và bộ unit test chặt chẽ.
  4. **Bonus 4 (4 điểm) — Small Local Model Challenge:** Triển khai hạ tầng mô hình nhỏ cục bộ (Ollama) không cần quyền root, benchmark 2 model 3B (`qwen2.5:3b` và `llama3.2:3b`), tối ưu prompt `system_prompt_local.md` (`v4-local`, `v5-local`), và hoàn thành phân tích mục B7 trong báo cáo nhóm.

## 3. Đóng góp cụ thể

### 1. Xây dựng 4 Tool mới và bộ Unit Test
- **Tool `cite` (`starter_v0/tools/cite/`):** Tự động sinh trích dẫn chuẩn APA 7 hoặc BibTeX từ metadata bài báo (`title`, `authors`, `published`, `url`). Tự động xử lý các ca phức tạp (2 đến 20 tác giả, ≥ 21 tác giả, khuyết tác giả, khuyết năm). Kèm 13 unit tests.
- **Tool `calc` (`starter_v0/tools/calc/`):** Công cụ tính toán biểu thức số học và thống kê (mean, median, stdev, min, max, sum) an toàn bằng cây cú pháp trừu tượng (Python AST). Chặn toàn bộ truy cập thuộc tính nguy hiểm, chống mã độc; kèm 5 unit tests.
- **Tool `text_stats` (`starter_v0/tools/text_stats/`):** Phân tích thống kê văn bản: đếm từ, ký tự, số câu, ước tính thời gian đọc và tính chỉ số độ dễ đọc Flesch Reading Ease; kèm 4 unit tests.
- **Tool `table_format` (`starter_v0/tools/table_format/`):** Chuyển đổi dữ liệu có cấu trúc thành Markdown Table chuẩn, hỗ trợ căn lề từng cột (`left`, `center`, `right`), tự động cân bằng số cột; kèm 4 unit tests.
- **Test Challenge:** Điền 14 stub test còn thiếu cho các tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`), đưa test suite lên **139 passed, 0 skipped, 0 failed**.

### 2. Tích hợp gửi tin nhắn thật lên Telegram sau xác nhận (Bonus 2)
- Khởi tạo Telegram Bot và lấy chat ID cá nhân (`5701163375`).
- Kiểm tra ranh giới an toàn: lượt 1 người dùng yêu cầu đăng tin -> Agent gọi `clarify(response_type="yes_no")` để xin xác nhận; lượt 2 sau khi người dùng đồng ý tường minh -> Agent mới gọi `send(confirmed=True)` và gửi tin nhắn thật lên Telegram.
- Xuất file transcript bằng chứng hoàn chỉnh: `starter_v0/transcripts/v3_telegram_real_openrouter_20261111T013500.transcript.json`.

### 3. Small Local Model Challenge (Bonus 4)
- Cài đặt Ollama nhị phân vào `~/.local/bin/ollama` (không cần sudo), cấu hình chạy ngầm `ollama serve` (port 11434).
- Tải 2 model 3B: `qwen2.5:3b` và `llama3.2:3b`.
- Đo đạc baseline trên `eval_base.json`: `qwen2.5:3b` đạt 55% (11/20), `llama3.2:3b` đạt 30% (6/20).
- Thiết kế file prompt rút gọn [system_prompt_local.md](file:///home/jay/K5-L3B-DAY03-Random-ResearchAgentToolEval/starter_v0/artifacts/system_prompt_local.md) gồm 18 dòng rule-based đanh thép, thiết lập rào chắn phủ định chặn gọi tool ngoài phạm vi.
- Chạy 2 vòng tối ưu (`v4-local`, `v5-local`), đưa độ chính xác của `qwen2.5:3b` lên **75% (15/20)** và multi-turn đạt mức tuyệt đối **100% (6/6)**.
- Điền đầy đủ dữ liệu bảng so sánh, đếm mẫu lỗi (Failure Patterns) và viết phần trả lời câu hỏi phản biện chuyên sâu tại mục B7 của `group_report.md`.

## 4. Bằng chứng

- **File mã nguồn và cấu hình:**
  - `starter_v0/tools/cite/`, `starter_v0/tools/calc/`, `starter_v0/tools/text_stats/`, `starter_v0/tools/table_format/` (kèm `TOOL.md` tương ứng).
  - `starter_v0/tests/test_tools_todo.py`, `starter_v0/data/eval_research_extension.json`.
  - `starter_v0/artifacts/system_prompt_local.md`, `starter_v0/artifacts/version_log.csv`.
- **File run và transcript bằng chứng:**
  - `starter_v0/transcripts/v3_telegram_real_openrouter_20261111T013500.transcript.json` (Telegram live gửi thật).
  - `starter_v0/runs/v3-qwen3b_B_base_ollama_20261111T014257117342.json`
  - `starter_v0/runs/v3-llama3b_B_base_ollama_20261111T014442478093.json`
  - `starter_v0/runs/v4-local_B_base_ollama_20261111T014656952766.json`
  - `starter_v0/runs/v5-local_B_base_ollama_20261111T014908279941.json`
- **Lịch sử commit kỹ thuật (tác giả `jay <trangiabao433@gmail.com>` trên `main`):**
  - `a39b590` Add cite tool (APA/BibTeX) with unit tests
  - `7ffea6b` Test challenge: fill 14 tool unit tests, pytest 111 passed / 0 skipped
  - `3726a90` feat(bonus): implement 3 new tools (calc, text_stats, table_format) with full unit tests and eval cases
  - `abe8c37` feat(bonus): live telegram delivery transcript with user confirmation boundary
  - `cb41f08` feat(bonus): complete Small Local Model Challenge (B7) with qwen2.5:3b and llama3.2:3b
- **Kết quả kiểm thử tự động:** `pytest` đạt **139 passed, 0 skipped, 0 failed** trong 1.69s.

## 5. Tự đánh giá

- **Làm được:** Hoàn thành xuất sắc 100% các yêu cầu từ bài tập chính khóa đến trọn vẹn 4 hạng mục bonus. Xây dựng bộ công cụ hữu ích, chạy offline an toàn; rào chắn guardrail Telegram chuẩn xác không phát sinh rủi ro gửi nhầm; tối ưu hóa thành công mô hình cục bộ giúp tiết kiệm chi phí và tăng tính riêng tư.
- **Hạn chế đã biết:**
  - Model 3B cục bộ vẫn có xu hướng tự đoán username hoặc nhầm lẫn giữa các tool phân tích văn bản trong một số ít ca đơn lẻ khi danh sách công cụ tăng lên.
  - Bộ công cụ tính toán và bảng biểu hiện chỉ hỗ trợ các phép toán thống kê cơ bản và bảng Markdown, chưa mở rộng ra các định dạng biểu đồ trực quan (charting).
