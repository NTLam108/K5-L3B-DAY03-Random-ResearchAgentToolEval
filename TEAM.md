# Team

## Thông tin nhóm

- Tên nhóm: Random
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Random-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/NTLam108/K5-L3B-DAY03-Random-ResearchAgentToolEval
- Nhánh nộp: `main`
- Commit chốt: `5a4449c` (kỹ thuật) / `dc3d1d3` (tài liệu báo cáo)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Trọng Lâm (nhóm trưởng) | 2A202603817 | 26ai.lamnt2@vinuni.edu.vn | NTLam108 | Quản lý repo, setup, baseline v0 + phân tích lỗi, 3 vòng tối ưu v1/v2/v3 |
|   2 | Trần Gia Bảo | 2A202603914 | 26ai.baotg@vinuni.edu.vn | Jay-Gabriel | Tool mới (`cite`, `calc`, `text_stats`, `table_format`), 4 Bonus challenges, test suite |
|   3 | Vũ Xuân Hiếu | 2A202603860 | 26ai.hieuvx2@vinuni.edu.vn | vuhieuvh | 10 case eval nhóm, benchmark `--suite group`, phân tích lỗi |
|   4 | Trịnh Hưng Thịnh | 2A202603907 | 26ai.thinhth@vinuni.edu.vn | TrnhThnh | Web UI 3D (Three.js), web server backend, chat live + transcripts, báo cáo Phần A |

## Báo cáo cá nhân

Mỗi thành viên nộp một báo cáo cá nhân trong `report/team/`:
- `report/team/2A202603817_NguyenTrongLam.md`
- `report/team/2A202603914_TranGiaBao.md`
- `report/team/2A202603860_VuXuanHieu.md`
- `report/team/2A202603907_TrinhHungThinh.md`

---

## Nguyễn Trọng Lâm - 2A202603817

### Phần việc phụ trách

- Quản lý repo nhóm, phân công nhiệm vụ và rà soát tiến độ checkpoints.
- Setup môi trường, cấu hình `.env`, chạy `scripts/preflight_provider.py`.
- Thực hiện chạy baseline `v0` và phân tích các dạng lỗi (Mục B2 trong `group_report.md`).
- Lên giả thuyết và thực hiện 3 vòng tối ưu cốt lõi: `v1` (tối ưu system prompt), `v2` (tinh chỉnh tool description), và `v3` (bổ sung cơ chế an toàn xác nhận trước khi gửi `send`).
- Ghi nhận nhật ký phiên bản vào `starter_v0/artifacts/version_log.csv`.

### Đóng góp cụ thể

- Setup môi trường ảo, cấu hình API key OpenRouter (`openai/gpt-4o-mini`) và kiểm tra preflight thành công.
- Chạy baseline `v0` trên `eval_base.json` đạt 13/20 (65% accuracy). Phân loại 7 lỗi gốc rễ từ prompt starter.
- Thực hiện 3 vòng tối ưu:
  + Vòng 1 (`v1`): Rút gọn và bổ sung ranh giới an toàn cho `system_prompt.md`, tăng lên 16/20 (80%).
  + Vòng 2 (`v2`): Tinh chỉnh mô tả phân luồng tool trong `tools.yaml`, tăng lên 19/20 (95%).
  + Vòng 3 (`v3`): Thiết lập ranh giới `clarify` (yes_no) và `send` (confirmed=true), giữ vững 19/20 (95%), đạt 100% routing và multiturn.

### Bằng chứng

- File: `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`, `starter_v0/artifacts/version_log.csv`.
- Runs: `runs/v0_B_base_openrouter_20261110T175735749717.json`, `runs/v1_B_base_openrouter_20261110T181958269786.json`, `runs/v2_B_base_openrouter_20261110T183359733221.json`, `runs/v3_B_base_openrouter_20261110T183608163642.json`.
- Commit (NTLam108 <lam.nt108204@gmail.com>): `d4de72b`, `f7128f7`, `7e9089b`, `70b5c7a`.

---

## Trần Gia Bảo - 2A202603914

### Phần việc phụ trách

- Xây dựng 4 custom tools mới: `cite`, `calc`, `text_stats`, `table_format` kèm `TOOL.md` và đăng ký agent.
- Đảm nhận toàn bộ 4 thử thách Bonus (10/10 điểm):
  + Bonus 1 (1 pt): Test Challenge (0 skipped).
  + Bonus 2 (2 pts): Gửi Telegram thật sau xác nhận kèm transcript.
  + Bonus 3 (3 pts): ≥ 4 Custom Tools offline kèm unit tests và extension evals.
  + Bonus 4 (4 pts): Small Local Model Challenge (Ollama local, 2 models 3B, 2 vòng tối ưu prompt, phân tích B7).
- Duy trì và nâng cấp toàn bộ test suite đạt **143 passed, 0 skipped, 0 failed**.

### Đóng góp cụ thể

- Viết 4 công cụ offline an toàn: `cite` (trích dẫn APA/BibTeX), `calc` (tính toán an toàn qua AST), `text_stats` (phân tích từ và chỉ số Flesch), `table_format` (tạo bảng Markdown). Khắc phục lỗi bảo mật DoS trong `calc` qua rào chắn lũy thừa và kích thước danh sách, bổ sung 4 test hồi quy.
- Viết 30 unit tests cho 4 tool mới và 14 unit tests lấp đầy các stubs cho các tool có sẵn trong `tests/test_tools_todo.py`.
- Tích hợp gửi thật lên Telegram Bot vào Private Channel của nhóm (`Random`, Chat ID: `-1004489921806`), ghi transcript bảo vệ xác nhận người dùng và ảnh chụp minh chứng.
- Triển khai Ollama offline, benchmark `qwen2.5:3b` và `llama3.2:3b`, viết prompt rút gọn `system_prompt_local.md` nâng độ chính xác của Qwen 3B từ 55% lên 75% (multiturn đạt 100%).
- Hoàn thiện toàn bộ số liệu và phân tích mục B5, B5a, B7 trong `report/team/group_report.md`.

### Bằng chứng

- File: `starter_v0/tools/cite/`, `starter_v0/tools/calc/`, `starter_v0/tools/text_stats/`, `starter_v0/tools/table_format/`, `starter_v0/tests/test_tools_todo.py`.
- Runs, transcripts & ảnh: `starter_v0/transcripts/v3_telegram_real_openrouter_20261111T013500.transcript.json`, ảnh `report/team/telegram_evidence.jpg`, 4 runs Ollama local (`v3-qwen3b`, `v3-llama3b`, `v4-local`, `v5-local`), 3 runs hardening trên bộ 14 tools (`v3-14tools` base + extension, `v5-local-cloud`).
- Test suite: `pytest` đạt 143 passed, 0 skipped, 0 failed.
- Commit (jay <trangiabao433@gmail.com>): `a39b590`, `7ffea6b`, `3726a90`, `abe8c37`, `cb41f08`, `5a4449c`.

---

## Vũ Xuân Hiếu - 2A202603860

### Phần việc phụ trách

- 10 case trong `data/eval_group.json` (5 single + 5 multi turn); vòng v2, v3; chạy `--suite group`.

### Đóng góp cụ thể

- Thiết kế và cài đặt đủ 10 case trong `starter_v0/data/eval_group.json` gồm 5 single-turn và 5 multi-turn, bao quát 6 loại failure types (`wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`).
- Tích hợp kiểm thử tool mới `cite` ở cả single-turn (`G01_cite_paper_apa`), multi-turn (`M_G01_papers_then_cite_bibtex`), và kiểm thử thiếu metadata (`G03_clarify_missing_paper_title`).
- Chạy benchmark `--suite group` qua OpenRouter (`gpt-4o-mini`), phân tích chi tiết lỗi lần chạy đầu (6/10) về cơ chế default argument và multi-turn context, sau đó tinh chỉnh đạt **10/10 PASS (100%)**.
- Cập nhật mục B3 trong `report/team/group_report.md` và hoàn thiện báo cáo cá nhân `report/team/2A202603860_VuXuanHieu.md`.

### Bằng chứng

- File bộ test: `starter_v0/data/eval_group.json` (10 test cases hợp lệ theo schema).
- Run file bằng chứng: `starter_v0/runs/v3_B_group_openrouter_20261110T192054234552.json` (10/10 PASS, `provider_error_cases: 0`, độ chính xác 1.0).
- Bảng B3 trong `report/team/group_report.md` và báo cáo cá nhân `report/team/2A202603860_VuXuanHieu.md`.
- Commit (vuhieuvh <26ai.hieuvx2@vinuni.edu.vn>): `cce14ac`, `16ea408`, `a5eff75`.

---

## Trịnh Hưng Thịnh - 2A202603907

### Phần việc phụ trách

- Xây dựng Giao diện người dùng Web tương tác (Web UI với Three.js) cho Checkpoint CP5.
- Thiết kế web server backend (`web_server.py`) tích hợp rate limit và bảo mật API key.
- Viết 17 bài unit test tự động cho web server (`test_web_server.py`).
- Thực hiện chat live thực tế và xuất các bản transcript tương tác nhiều lượt.
- Viết tài liệu Phần A (Giới thiệu, Hướng dẫn chạy UI, Danh sách tool, Câu hỏi mẫu) và mục B4 trong `group_report.md`.

### Đóng góp cụ thể

- Xây dựng ứng dụng web 3D Three.js trực quan hóa trực tiếp quỹ đạo và trạng thái hoạt động của các tool xung quanh lõi agent.
- Tích hợp mô hình 3D và HDRI chuẩn CC0 từ Poly Haven (có fallback text mode khi mất kết nối CDN).
- Viết web server Python thuần hỗ trợ rate limit (20 req/phút), che giấu key bảo mật và tự động kết xuất transcript.
- Viết 17 unit tests offline kiểm thử toàn diện web server (`pytest tests/test_web_server.py`).
- Ghi lại các phiên chat live thực tế với GPT-4o-mini qua Web UI và chat CLI.

### Bằng chứng

- File: `starter_v0/web_server.py`, `starter_v0/web/`, `starter_v0/tests/test_web_server.py` (17 tests passed).
- Transcripts: `starter_v0/transcripts/v3_web_openrouter_20261111T003816480838.transcript.json`, `starter_v0/transcripts/v3-cite_web_openrouter_20261111T005023452246.transcript.json`.
- Báo cáo: Phần A và mục B4, B5a trong `report/team/group_report.md`.
- Commit (TrnhThnh <hungthinh05112002@gmail.com>): `f2b1e3e`, `bd76ec0`, `b9748a8`.
