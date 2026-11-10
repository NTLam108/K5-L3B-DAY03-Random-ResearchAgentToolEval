# Báo cáo cá nhân — Trần Gia Bảo - 2A202603914

## 1. Thông tin thành viên

- Họ tên: Trần Gia Bảo
- MSSV: 2A202603914
- Email: 26ai.baotg@vinuni.edu.vn

## 2. Phần việc phụ trách

Tool mới của nhóm là `cite`: tạo trích dẫn APA hoặc BibTeX từ metadata một bài báo (`title`, `authors`, `published`, `url`). Kèm theo là đăng ký tool vào agent, unit test cho tool, bonus test challenge (điền các test còn skip), và các mục liên quan trong báo cáo nhóm (A2, B5a, B5).

## 3. Đóng góp cụ thể

- **Tool `cite`:** `starter_v0/tools/cite/tool.py` và `TOOL.md`, đăng ký trong `starter_v0/tools/__init__.py`, khai báo trong `starter_v0/artifacts/tools.yaml`. Chạy local, không cần API key. Khi đầu vào sai (tiêu đề rỗng, `authors` không phải danh sách, `style` ngoài `apa`/`bibtex`) tool trả error dict, không raise.
- **Quy tắc đã cài đặt:** APA dùng `Họ, Chữ-cái-đầu.` và `&` trước tác giả cuối (2 đến 20 tác giả); từ 21 tác giả thì 19 tác giả đầu, `...`, tác giả cuối; không có tác giả thì tiêu đề lên vị trí tác giả; thiếu năm thì `n.d.`. BibTeX dùng `@misc`, tác giả dạng `Họ, Tên` nối bằng `and`, citation key là họ tác giả đầu cộng năm.
- **13 unit test cho `cite`** trong `starter_v0/tests/test_tools_todo.py` (1/2/3 tác giả, 21 tác giả, đúng 20 tác giả, không tác giả, thiếu năm, BibTeX, key chỉ giữ chữ và số, tiêu đề rỗng, `authors` sai kiểu, style lạ).
- **Chỉnh mô tả `cite` trong `tools.yaml`:** khi thử với model thật thấy model tự điền năm và link khi người dùng không đưa; nguyên nhân một phần là ví dụ ngày cụ thể trong mô tả. Đã bỏ ví dụ đó và dặn chỉ dùng thông tin người dùng đưa. Cải thiện được một phần: ca người dùng không nêu năm và link vẫn bị model điền từ trí nhớ (ghi ở mục 5).
- **Bonus test challenge:** điền 14 test cho `clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`; `pytest` từ 80 passed, 17 skipped lên **111 passed, 0 skipped**. Đã kiểm tra đột biến: cố ý làm hỏng guardrail `send`, việc tách dòng không tin cậy của `policy` và giới hạn 4000 ký tự của `fetch` thì đúng 3 test thất bại, sau đó hoàn lại code.
- **Báo cáo nhóm:** hàng `cite` ở A2, hàng "Tool mới" và "Unit test" ở B5a, hàng Test challenge ở B5.

## 4. Bằng chứng

- **File:** `starter_v0/tools/cite/tool.py`, `starter_v0/tools/cite/TOOL.md`, `starter_v0/tests/test_tools_todo.py`, `starter_v0/artifacts/tools.yaml`.
- **Commit** (tác giả `jay`, email `trangiabao433@gmail.com`), trên `main`:
  - `a39b590` Add cite tool (APA/BibTeX) with unit tests
  - `2e5410b` cite: APA 21+ authors, no-author, BibTeX Last-First names; document sources
  - `d7ac21f` cite: record source of APA preprint claim
  - `597f673` cite: tighten tools.yaml description to stop invented date/url and keep bibtex style
  - `7ffea6b` Test challenge: fill 14 tool unit tests, pytest 111 passed / 0 skipped
- **Kết quả `pytest`** (chạy ngày 11/11/2026): 111 passed, 0 skipped, 0 failed.
- **Chat thật với model** (OpenRouter, `openai/gpt-4o-mini`): `starter_v0/transcripts/v3_openrouter_20261110T190906181009.transcript.json` (4 lượt, gõ tay bằng `chat.py`, lượt đầu gọi `cite` đúng) và `starter_v0/transcripts/v3-cite_web_openrouter_20261111T005023452246.transcript.json` (`cite` qua UI web). Base eval có `cite` trong danh sách tool cho cùng điểm với v3 (0.95), nhưng lần chạy đó ghi ở thư mục tạm nên không có file run trong repo.
- **AI/công cụ đã dùng và cách tự kiểm tra:**
  - Code và test của `cite` được viết với sự hỗ trợ của trợ lý AI (Kiro); các test tool có sẵn cũng vậy. Điểm APA về `arXiv:ID` và nhãn `[Preprint]` lấy từ ChatGPT.
  - Cách kiểm tra: chạy `pytest`; gọi trực tiếp `cite` với ví dụ Attention Is All You Need và đối chiếu chuỗi kết quả; kiểm tra đột biến cho các test mới; chat thật với model và đọc tham số model truyền vào; dò transcript không chứa key.
  - **Chưa làm được:** đối chiếu trang APA Style chính thức (trang không truy cập được khi thử). Vì vậy chuỗi APA cho preprint arXiv là bản đơn giản hóa, đã ghi trong `TOOL.md`.

## 5. Tự đánh giá

- **Làm được:** tool chạy ổn định, trả error dict thay vì raise, test có assert chuỗi đầy đủ, ghi nguồn tham khảo và giới hạn trong `TOOL.md`, đưa `pytest` về 0 skipped.
- **Hạn chế đã biết:**
  - Đoán họ là từ cuối của tên nên sai với tên ghi họ trước (nhiều tên Việt Nam).
  - Xuất văn bản thuần nên không in nghiêng được tiêu đề; không áp dụng sentence case của APA.
  - Model vẫn có thể tự điền năm và link từ trí nhớ khi người dùng không đưa (quan sát được khi hỏi về bài ResNet không kèm năm và link).
  - `cite` được thêm sau v3 nên không nằm trong run v0 đến v3 (đã ghi ở B1).
- **Quan sát về tool có sẵn (chưa sửa):** `timeline` và `social_search` với `limit=-1` trả 4 trong 5 mục (cắt mục cuối), `limit=0` rơi về 5; trong khi `policy` chặn giá trị âm về tối thiểu 1. Cách chặn không nhất quán. Chưa làm nhánh regression test của bonus vì chưa quyết hành vi mong đợi.
- **Quan sát rút ra từ dự án:** một ví dụ cụ thể trong mô tả tham số có thể bị model chép nguyên (ví dụ ngày xuất bản); mô tả tool ảnh hưởng mạnh tới việc model có tự điền dữ liệu hay không.
