# Báo cáo cá nhân — Vũ Xuân Hiếu - 2A202603860

## 1. Thông tin thành viên

- Họ tên: Vũ Xuân Hiếu
- MSSV: 2A202603860
- Email: vuhieu3205@gmail.com
- GitHub: vuhieuvh

## 2. Phần việc phụ trách

- Thiết kế và hiện thực 10 test case trong `starter_v0/data/eval_group.json` (5 single-turn + 5 multi-turn) bao quát 6 loại failure types và tích hợp tool mới `cite`.
- Chạy benchmark `--suite group`, phân tích failure patterns, tối ưu độ chính xác bộ test đạt điểm tối đa.
- Cập nhật bảng kết quả B3 trong báo cáo nhóm `report/team/group_report.md`.

## 3. Đóng góp cụ thể

### Thiết kế 10 test cases trong `starter_v0/data/eval_group.json`
Bộ test được thiết kế độc lập, không trùng lặp với `eval_base.json`, bao phủ đầy đủ các ranh giới và kiểm tra trực tiếp tool mới `cite` của nhóm:

1. **5 Single-turn cases:**
   - `G01_cite_paper_apa` (`wrong_tool`): Người dùng cung cấp tiêu đề bài báo và yêu cầu trích dẫn APA → kiểm tra routing chính xác vào tool mới `cite` thay vì `papers` hay `format`.
   - `G02_papers_arxiv_routing` (`wrong_tool`): Người dùng yêu cầu tìm bài báo nghiên cứu khoa học trên arXiv kèm số lượng cụ thể (`max_results=3`) → routing vào `papers` thay vì `lookup` hay `social_search`.
   - `G03_clarify_missing_paper_title` (`missing_info`): Người dùng yêu cầu tạo trích dẫn nhưng không cung cấp tên hay link bài báo → kiểm tra agent gọi `clarify(response_type="text")` theo đúng quy ước trong `tools.yaml`.
   - `G04_out_of_scope_translation` (`out_of_scope`): Yêu cầu dịch văn bản sang tiếng Nhật (ngoài phạm vi research agent) → agent từ chối bằng văn bản (`no_tool=true`, `refuse`), không gọi bất kỳ tool nào.
   - `G05_unnecessary_tool_thanks` (`unnecessary_tool`): Lời cảm ơn thông thường từ người dùng → agent phản hồi lịch sự không gọi tool (`no_tool=true`, `answer_without_tool`).

2. **5 Multi-turn cases (mỗi case 3 lượt hội thoại):**
   - `M_G01_papers_then_cite_bibtex` (`wrong_tool`): Lượt trước đề cập bài báo đã đọc, lượt sau yêu cầu tạo trích dẫn BibTeX → agent gọi `cite` với tham số `style="bibtex"`.
   - `M_G02_send_then_cancel` (`wrong_boundary`): Lượt 1 yêu cầu gửi Telegram, nhưng lượt 2 và 3 liên tục yêu cầu hoãn lại và hủy bỏ → agent tuân thủ ranh giới an toàn, không gọi `send` (`no_tool=true`).
   - `M_G03_coreference_deepseek` (`wrong_tool`): Giải quyết hiện tượng đồng tham chiếu (coreference resolution): đại từ "họ" ở lượt 3 tham chiếu đến thực thể "DeepSeek" ở lượt 1 → gọi `lookup` với `query="DeepSeek", topic="news", timeframe="week"`.
   - `M_G04_switch_twitter_to_web_month` (`wrong_arg_value`): Chuyển đổi công cụ giữa chừng (từ tìm tweet sang tin tức web) kèm sửa đổi timeframe → gọi `lookup` với `query="Gemini", topic="news", timeframe="month"`.
   - `M_G05_out_scope_then_social_top` (`wrong_arg_value`): Lượt đầu hỏi câu ngoài phạm vi (cách nấu phở), lượt 2 và 3 chuyển hướng tìm kiếm bài đăng hot/phổ biến trên Twitter → gọi `social_search` với `query="VinFast", search_type="Top"`.

### Quá trình phân tích, sửa lỗi và benchmark
- **Lần chạy 1 (`run_eval.py --suite group`):** Đạt 6/10 (0.60).
  - Phân tích chi tiết:
    + `G01`: Model gọi `cite` chính xác nhưng bỏ qua `style="apa"` vì `apa` là giá trị mặc định trong schema `tools.yaml`. Cơ chế so khớp subset của eval coi đây là thiếu argument. Khắc phục: chỉ so khớp trường bắt buộc `title`.
    + `G03`: Ban đầu dùng câu hỏi "tìm tin tức mới nhất", model tự gán `query="AI"`. Khắc phục: đổi sang kiểm tra missing info cho tool `cite` ("trích dẫn bài báo này" thiếu title), khớp tuyệt đối với chỉ dẫn `tools.yaml`.
    + `M_G01`: Do eval harness chỉ gửi lịch sử hội thoại dưới dạng text mà không mock tool output, model không có thông tin bài báo nên gọi cả `papers` lẫn `cite`. Khắc phục: đưa thông tin bài báo vào ngữ cảnh lượt 1 để hội thoại tự chứa đầy đủ metadata.
    + `M_G03`: Lượt 3 câu lệnh ngắn khiến model bị ảnh hưởng bởi chỉ dẫn "giữ ràng buộc trước đó" và dùng query chưa tối ưu. Khắc phục: tinh chỉnh câu từ để làm nổi bật việc tra cứu thực thể DeepSeek.
- **Lần chạy 2:** Toàn bộ 10/10 cases đều **PASS (100% case accuracy, 100% routing, 100% args, 100% multiturn)**.

## 4. Bằng chứng

- File bộ test: `starter_v0/data/eval_group.json` (10 cases: 5 single-turn, 5 multi-turn).
- Run file bằng chứng: `starter_v0/runs/v3_B_group_openrouter_20261110T192054234552.json`
  - `total_cases`: 10
  - `measured_cases`: 10
  - `provider_error_cases`: 0
  - `passed_cases`: 10
  - `case_accuracy`: 1.0 (100%)
  - `tool_routing_accuracy`: 1.0 (100%)
  - `argument_accuracy`: 1.0 (100%)
  - `multiturn_accuracy`: 1.0 (100%)
- Bảng B3 được cập nhật trong `report/team/group_report.md`.
- Công cụ đã sử dụng và kiểm tra:
  - Khởi tạo và quản lý môi trường ảo Python 3.11, OpenRouter API (`gpt-4o-mini`).
  - Kiểm tra cú pháp JSON qua script parser độc lập trước khi chạy benchmark.
  - Chạy `python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json`.

## 5. Tự đánh giá

- **Làm được:**
  - Thiết kế bộ test phong phú, đúng quy chuẩn đề bài, bao quát trọn vẹn 6 loại failure types được định nghĩa trong rubric.
  - Tích hợp và kiểm thử toàn diện tool mới `cite` của nhóm (cả trích dẫn thường, trích dẫn BibTeX multi-turn, và xử lý khi thiếu metadata).
  - Đạt tỷ lệ vượt qua tuyệt đối (10/10 PASS, 0 lỗi provider).
  - Phân tích cặn kẽ nguyên nhân gốc rễ của từng failure trong quá trình phát triển (vấn đề giá trị mặc định của LLM, cơ chế multi-turn không có mock tool return).
- **Hạn chế và bài học kinh nghiệm:**
  - Cơ chế multi-turn của benchmark đơn giản hóa bằng cách nối chuỗi các lượt chat của user mà không mô phỏng phản hồi từ tool, đòi hỏi người thiết kế test case phải khéo léo đưa dữ liệu vào ngữ cảnh đàm thoại để tránh model tự gọi thêm tool tìm kiếm không mong muốn.
  - Việc hiểu rõ cách eval framework so khớp arguments (subset matching) giúp thiết kế bộ tiêu chí đánh giá chuẩn xác, tránh phạt nhầm LLM khi nó tối ưu token bằng cách lược bỏ các giá trị trùng với default schema.
