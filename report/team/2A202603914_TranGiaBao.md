# Báo cáo cá nhân — Trần Gia Bảo - 2A202603914

> BẢN NHÁP ĐỂ BẢO SỬA. Các ô **[Bảo điền]** chỉ Bảo biết. Xóa dòng này và mọi ghi chú trong ngoặc vuông trước khi nộp.
> Chỉ giữ những câu Bảo thật sự đã làm hoặc đã tự kiểm tra; viết lại bằng lời của mình.

## 1. Thông tin thành viên

- Họ tên: Trần Gia Bảo
- MSSV: 2A202603914
- Email: **[Bảo điền]**

## 2. Phần việc phụ trách

Mình phụ trách tool mới của nhóm là `cite`: tạo trích dẫn APA hoặc BibTeX từ metadata của một bài báo (title, authors, published, url). Mình cũng đăng ký tool vào agent, viết unit test và điền các bảng A2, B5a trong báo cáo nhóm.

## 3. Đóng góp cụ thể

- Tool `cite` nằm ở `starter_v0/tools/cite/` (`tool.py`, `TOOL.md`), được đăng ký trong `starter_v0/tools/__init__.py` và khai báo trong `starter_v0/artifacts/tools.yaml`.
- Tool chạy hoàn toàn local, không cần API key. Khi đầu vào sai (tiêu đề rỗng, `authors` không phải list, `style` không hợp lệ) tool trả về error dict, không raise.
- Viết 13 unit test trong `starter_v0/tests/test_tools_todo.py`, gồm: APA với 1, 2, 3 tác giả; APA với hơn 20 tác giả (19 tác giả đầu, dấu `...`, tác giả cuối); APA không có tác giả và thiếu năm (`n.d.`); BibTeX (key, nối tác giả bằng `and`); các trường hợp lỗi.
- Quy tắc trích dẫn lấy từ hướng dẫn thư viện đại học và bibtex.org; danh sách nguồn ghi trong `TOOL.md`.
- Thử với model thật qua OpenRouter (`gpt-4o-mini`): model chọn đúng `cite` khi hỏi citation, nhưng có lúc tự điền năm và link khi mình không đưa. Mình sửa mô tả trong `tools.yaml` (bỏ ví dụ ngày cụ thể, dặn không tự điền) và thử lại: giảm được một phần, nhưng ca không có năm và link vẫn bị điền.
- **[Bảo điền]** Những việc mình tự làm thêm: ví dụ đọc và hiểu từng hàm, sửa/bổ sung test nào, tra nguồn nào, đối chiếu với trang APA Style nào.

## 4. Bằng chứng

- File/commit/PR:
  - Branch `feat/cite-tool`; commit của mình: **[Bảo điền hash và mô tả, lấy bằng `git log --oneline`]**
  - Kết quả `pytest` ngày **[Bảo điền ngày giờ]**: 80 passed, 17 skipped, 0 failed (17 skip là stub của tool có sẵn).
  - Bảng A2 và B5a trong `report/team/group_report.md`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Mình dùng trợ lý AI (Kiro) để hỗ trợ viết code và test ban đầu cho `cite`. Điểm APA về `arXiv:ID` và nhãn `[Preprint]` lấy từ ChatGPT. **[Bảo điền]** mình đã tự đọc và sửa những gì, và đã tự đối chiếu trang APA Style chính thức chưa (kết quả: ...).
  - Cách tự kiểm tra: chạy `pytest`; gọi trực tiếp `cite` với ví dụ Attention Is All You Need và so chuỗi kết quả; thử với model thật và xem tham số model truyền vào.

## 5. Tự đánh giá

- Làm được: tool chạy ổn định, test có assert chuỗi đầy đủ, ghi nguồn và giới hạn trong `TOOL.md`.
- Hạn chế: tool đoán họ là từ cuối của tên nên sai với tên ghi họ trước (nhiều tên Việt Nam); không in nghiêng được vì xuất text thuần; không đổi tiêu đề sang sentence case; model vẫn có thể tự điền năm và link khi người dùng không đưa.
- **[Bảo điền]** Mình học được gì, khó khăn gặp phải, nếu làm lại mình sẽ đổi điều gì.
