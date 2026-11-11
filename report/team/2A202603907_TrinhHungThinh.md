# Báo cáo cá nhân — Trịnh Hưng Thịnh - 2A202603907

## 1. Thông tin thành viên

- Họ tên: Trịnh Hưng Thịnh
- MSSV: 2A202603907
- Email: 26ai.thinhth@vinuni.edu.vn (GitHub: TrnhThnh, commit: hungthinh05112002@gmail.com)

## 2. Phần việc phụ trách

- Xây dựng Giao diện người dùng Web tương tác (Web UI với Three.js) cho Checkpoint CP5.
- Thiết kế hệ thống frontend 3D trực quan hóa vòng lặp gọi công cụ của agent: agent core ở trung tâm, các tool là các đồ vật 3D bay quanh quỹ đạo, phát sáng khi được kích hoạt.
- Xây dựng web server backend bằng Python (`web_server.py`) tích hợp rate limiter và session management.
- Viết bộ unit test tự động cho web server (`test_web_server.py`).
- Thực hiện các phiên chat live thực tế với mô hình ngôn ngữ, xuất transcript đầy đủ và hoàn thiện Phần A, B4, B5a trong báo cáo nhóm `group_report.md`.

## 3. Đóng góp cụ thể

- **Web Server Backend (`starter_v0/web_server.py`):**
  - Xây dựng HTTP server thuần bằng Python `http.server` không phụ thuộc thư viện bên ngoài nặng nề.
  - Tích hợp rate limiting bảo vệ API (`--max-per-minute 20`), lắng nghe an toàn trên `127.0.0.1:8000`.
  - Che giấu an toàn các API key nhạy cảm nếu lọt vào thông báo lỗi.
  - Tự động ghi lại nhật ký phiên chat thành file JSON chuẩn định dạng `transcripts/*.transcript.json`.
- **Three.js Web UI (`starter_v0/web/`):**
  - Giao diện 3D sống động với Three.js tải từ CDN (jsdelivr v0.160.0). Khi mất kết nối CDN, giao diện tự động fallback sang chế độ chat văn bản thuần, không làm gián đoạn trải nghiệm người dùng.
  - Tích hợp mô hình 3D thật và ánh sáng môi trường HDRI đạt chuẩn giấy phép CC0 từ Poly Haven (tài liệu chi tiết tại `web/assets/CREDITS.md`).
  - Khung chat trực quan: hiển thị rõ ràng arguments truyền vào, kết quả trả về của tool và tô đỏ đánh dấu lỗi runtime.
- **Bộ Unit Test cho Web Server (`starter_v0/tests/test_web_server.py`):**
  - Viết 17 bài test tự động chạy offline, kiểm thử toàn diện các luồng: phục vụ static file, xử lý phiên chat hợp lệ, kiểm tra rate limit, che giấu key nhạy cảm, xử lý tool lỗi.
- **Thực nghiệm Chat Live & Báo cáo:**
  - Chạy live session với OpenRouter (`gpt-4o-mini`), ghi lại transcript tương tác nhiều lượt: `v3-cite_web_openrouter_20261111T005009308788.transcript.json` (thiếu thông tin rồi bổ sung), `v3-cite_web_openrouter_20261111T005020368434.transcript.json` (yêu cầu đăng Telegram rồi hủy) và phiên thử nghiệm tool mới `cite` qua UI `v3-cite_web_openrouter_20261111T005023452246.transcript.json`.
  - Hoàn thiện Phần A (Giới thiệu agent, hướng dẫn chạy UI, danh sách tool, câu hỏi mẫu) và các mục B4, B5a trong `report/team/group_report.md`.

## 4. Bằng chứng

- **File/Commit (tác giả Trịnh Hưng Thịnh <hungthinh05112002@gmail.com>):**
  - `f2b1e3e` Add Three.js web UI with Python backend and tests
  - `bd76ec0` Web UI: real 3D objects and studio lighting (Poly Haven CC0), blue core, stars, orbit layout
  - `b9748a8` CP5: live chat transcripts (web UI + chat.py) and group report Phan A/B4/B5a
- **File mã nguồn và tài sản:**
  - `starter_v0/web_server.py`, `starter_v0/web/app.js`, `starter_v0/web/index.html`, `starter_v0/web/style.css`, `starter_v0/web/assets/CREDITS.md`.
  - `starter_v0/tests/test_web_server.py` (17 unit tests offline, 100% pass).
- **Transcript thực tế:**
  - `starter_v0/transcripts/v3-cite_web_openrouter_20261111T005009308788.transcript.json`
  - `starter_v0/transcripts/v3-cite_web_openrouter_20261111T005020368434.transcript.json`
  - `starter_v0/transcripts/v3-cite_web_openrouter_20261111T005023452246.transcript.json`
- **Tài liệu báo cáo:** Phần A, B4, B5a trong `report/team/group_report.md`.

## 5. Tự đánh giá

- **Làm được:** Giao diện 3D trực quan, thẩm mỹ cao, thể hiện rõ bản chất hoạt động của agent; code sạch sẽ, không phụ thuộc nặng nề vào các framework ngoài; có cơ chế rate limiting và che key bảo mật; test tự động bao phủ trọn vẹn 17 ca kiểm thử.
- **Hạn chế đã biết:** Giao diện 3D phụ thuộc vào kết nối CDN để tải Three.js (mặc dù đã có fallback chat văn bản); các mô hình 3D từ Poly Haven có dung lượng khoảng 24MB cần thời gian tải ở lần đầu tiên; chưa cấu hình public domain chính thức qua Cloudflare Tunnel trên môi trường production.
