# Báo cáo cá nhân — Trịnh Hưng Thịnh - 2A202603907

## 1. Thông tin thành viên

- Họ tên: Trịnh Hưng Thịnh
- MSSV: 2A202603907
- Email:

## 2. Phần việc phụ trách

UI (Streamlit/Vercel) + link dùng thử; chat live ≥ 3 lượt và transcript; `group_report.md`.

## 3. Đóng góp cụ thể

- Tạo `starter_v0/app.py`: UI Streamlit chat live dùng provider và tool loop hiện có; có cấu hình provider/version/model, hội thoại nhiều lượt, lưu transcript, liệt kê tool/schema và hiển thị rõ args/kết quả/lỗi từng lần gọi tool.
- Thêm Streamlit vào `starter_v0/requirements.txt` và cập nhật lệnh chạy UI, tool list, câu hỏi mẫu trong `report/team/group_report.md`.
- Transcript live ≥ 3 lượt và URL deploy public chưa có trong workspace; cần chạy UI với provider/API key của nhóm và ghi transcript thật trước khi nộp.

## 4. Bằng chứng

- File/commit/PR: `starter_v0/app.py`, `starter_v0/requirements.txt`, `report/team/group_report.md` (chưa có commit được ghi nhận).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: Codex; đã kiểm tra cú pháp bằng `python -m py_compile starter_v0/app.py` và định dạng diff bằng `git diff --check`.

## 5. Tự đánh giá

UI và phần nối với tool loop đã được triển khai; chưa xác nhận phiên gọi model thật hoặc deploy public trong môi trường này.
