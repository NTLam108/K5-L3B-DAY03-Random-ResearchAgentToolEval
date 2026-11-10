# Source code

Toàn bộ source code của lab nằm trong folder này. Chạy mọi lệnh từ `starter_v0/`.

- File bắt đầu chạy: `run_eval.py` (chạy eval), `chat.py` (chat live), `scripts/preflight_provider.py` (kiểm tra provider).
- Cách chạy: `python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json`; `python chat.py --provider openrouter --version v3`; `pytest`.
- Input: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, bộ case `data/*.json`, API key trong `.env` (mẫu ở `.env.example`).
- Output: `runs/*.json` (kết quả eval), `transcripts/*.transcript.json` (chat live), `analysis/*.csv` (nếu chạy `scripts/parse_runs.py`).
- File học viên được sửa: `artifacts/system_prompt.md`, `artifacts/tools.yaml`, `artifacts/version_log.csv`, `data/eval_group.json`, `tools/` (thêm tool mới và đăng ký trong `tools/__init__.py`), `tests/test_tools_todo.py`, code UI và `requirements.txt`. Không sửa nội dung case trong `data/eval_base.json`.

Chi tiết từng bước xem [README.md](../README.md) ở root; cấu hình API key xem [docs/TOOL-SETUP.md](../docs/TOOL-SETUP.md).

## Web UI (Three.js)

Giao diện web có cảnh 3D: lõi agent ở giữa, mỗi tool là một nút quay quanh, tool nào được gọi thì sáng lên. Panel chat hiện đầy đủ args và kết quả của từng lần gọi tool (kể cả khi tool lỗi). Không cần cài thêm thư viện Python.

```bash
cd starter_v0
python web_server.py --provider openrouter --version v3     # mở http://127.0.0.1:8000
```

- Mỗi cuộc trò chuyện được lưu thành `transcripts/*.transcript.json` (cùng định dạng với `chat.py`, có thêm `"client": "web"`).
- Server chỉ lắng nghe `127.0.0.1` theo mặc định và giới hạn 20 request chat mỗi phút (`--max-per-minute`) để người ngoài không đốt hết quota API khi mở link công khai.
- Chia sẻ link cho team khác: `cloudflared tunnel --url http://localhost:8000`.
- Three.js được tải từ CDN (jsdelivr, bản 0.160.0). Không có mạng thì cảnh 3D tắt nhưng chat vẫn dùng được.
- Model 3D và ánh sáng HDRI (khoảng 24 MB) nằm trong `web/assets/`, lấy từ Poly Haven (CC0), danh sách ở `web/assets/CREDITS.md`. Mỗi tool là một đồ vật thật; tool mới chưa có trong bảng `TOOL_MODELS` của `web/app.js` sẽ hiện thành một quả cầu kim loại đơn giản.
- Test: `pytest tests/test_web_server.py`.

