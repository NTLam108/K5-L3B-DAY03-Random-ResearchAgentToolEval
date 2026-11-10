# SPEC — Hoàn thiện toàn bộ dự án để đạt điểm tối đa

> Dành cho người và AI cùng đọc. Mọi lệnh chạy từ `starter_v0/` trừ khi ghi khác.
> **Quy tắc tối thượng: không đoán, không bịa.** Chỗ ghi "CHƯA CÓ THÔNG TIN" thì phải hỏi người phụ trách. Không bịa run, metric, transcript, commit (RULES.md cấm).
> Spec phần tool mới chi tiết hơn nằm ở `docs/SPEC_BAO_NEW_TOOL.md`.

## 0. Thang điểm (RUBRIC.md) và ai phụ trách

| Tiêu chí | Điểm | Người phụ trách (theo kết quả random) |
|---|---:|---|
| C1 Baseline v0 + phân tích lỗi | 10 | Lâm |
| C2 Prompt + tool declaration | 15 | Lâm (v1), Hiếu (v2, v3) |
| C3 Vòng lặp v1→v3 có bằng chứng | 20 | Lâm, Hiếu |
| C4 Tool mới + unit test | 15 | Bảo |
| C5 10 case eval nhóm | 10 | Hiếu |
| C6 UI + live chat | 10 | Thịnh |
| C7 Báo cáo nhóm | 10 | Thịnh gom, mọi người điền |
| C8 Đóng góp cá nhân | 10 | Cả 4 |
| Bonus (ghi riêng, tối đa 10) | 10 | Tùy chọn, làm sau |

**Run hợp lệ:** chỉ dùng run có `summary.provider_error_cases == 0` và `summary.measured_cases == summary.total_cases`. Run không hợp lệ thì không tính điểm (C1: 0 điểm).

## 1. CHƯA CÓ THÔNG TIN — phải hỏi trước

| # | Câu hỏi | Ai quyết |
|---|---|---|
| 1 | Provider/model nào chạy eval? (repo khuyến nghị OpenRouter, mặc định trong code `openai/gpt-4o-mini`; chưa có thông tin giá/quota) | Lâm |
| 2 | Ai giữ `.env` và có đủ key `OPENROUTER_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`? | Lâm |
| 3 | Tool mới của nhóm là gì (tên, chức năng, arg)? | Cả nhóm, Bảo ghi lại |
| 4 | `track` của tool mới là `core` hay `bonus`? | Hỏi coach |
| 5 | UI dùng Streamlit hay Vercel? Chưa thấy file UI trong cấu trúc README mô tả (chưa kiểm tra thư mục); repo không cung cấp mã UI mẫu | Thịnh |
| 6 | Email, GitHub, họ tên đầy đủ của Hiếu (MSSV 2A202603860) | Từng người |
| 7 | Deadline thực tế (mặc định 23h59 ngày lab GMT+7, coach có thể gia hạn tối đa 48h) | Coach |
| 8 | Nhóm có làm bonus nào không? Máy có RAM bao nhiêu (cho Ollama)? | Cả nhóm |

## 2. Thứ tự và phụ thuộc (quan trọng)

```text
Lâm: setup -> chạy v0 (tools.yaml/prompt CHƯA sửa) -> push run v0
        |
        +--> Lâm: v1  -->  Hiếu: v2, v3 (làm trên nền v1)
        |
Bảo: viết tool (làm offline được ngay) -> merge SAU khi v0 chạy xong
        |
        +--> Hiếu: eval case route tới tool mới (cần tên tool + arg)
        |
Thịnh: UI + chat live (cần prompt/tools gần ổn định, sau v3) -> gom báo cáo
```

Lý do: CHECKPOINTS yêu cầu v0 chạy khi `system_prompt.md` và `tools.yaml` chưa sửa. Thêm tool vào `tools.yaml` có thể đổi `tools_hash` (suy luận từ README, chưa đọc `versioning.py`). Vì vậy Bảo làm trên branch riêng hoặc merge sau v0.

Quy ước git: mỗi người commit phần mình, `git pull` trước khi push, không force-push, không sửa lịch sử (RULES.md).

## 3. Bước 1 — Lâm: Setup + Baseline v0 (C1, 10 điểm)

1. Tạo môi trường:
   ```bash
   cd starter_v0
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
2. Điền `.env` (key tên trong `.env.example`). Không commit `.env`.
3. Kiểm tra: `python scripts/preflight_provider.py --provider openrouter` phải pass; `pytest` (contract + example xanh, TODO test đang skipped).
4. Chạy baseline, **không sửa** `system_prompt.md` / `tools.yaml`:
   ```bash
   python run_eval.py --provider openrouter --version v0 --suite base --eval-cases data/eval_base.json
   ```
5. Kiểm tra run hợp lệ: `provider_error_cases == 0` và `measured_cases == total_cases`. Nếu không hợp lệ, sửa nguyên nhân (key, mạng, quota) và chạy lại; ghi lỗi vào mục 5 của group report.
6. Ghi dòng v0 vào `artifacts/version_log.csv` với header đúng:
   `version,author,changed_artifact,artifact_version,prompt_hash,tools_hash,reason,hypothesis,metric_before,metric_after,run_file`. Hash và đường dẫn run lấy từ output của eval. Mẫu format: `samples/version_log.example.csv`.
7. Điền bảng B2 (Failure Analysis) trong `group_report.md`: mỗi case FAIL một dòng gồm Case ID, Failure Type, Actual Tool Calls, What Failed, Fix. Lấy từ `results[*].result.failures`, `observed_mismatch`, `actual_tool_calls`. Failure type hợp lệ: `wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`.
8. Push `runs/<v0>.json` và `version_log.csv`.

Tùy chọn: `python scripts/parse_runs.py runs/ --output analysis/base_runs.csv`.

## 4. Bước 2 — Prompt + tool declaration, v1→v3 (C2 15đ + C3 20đ)

Chỉ sửa `artifacts/system_prompt.md`, `artifacts/tools.yaml`. **Không sửa nội dung case** trong `data/eval_base.json`.

### 4.1 Hiện trạng đã đọc

- `system_prompt.md` hiện cố ý xấu theo 3 hướng: (a) không hỏi lại, tự đoán (ví dụ "pick a well-known account like Sam Altman"); (b) gửi/đăng ngay không xác nhận; (c) ép làm "single step", chỉ một tool.
- `tools.yaml` hiện: description mỗi tool chỉ một câu sơ sài, không nói khi nào dùng/không dùng, không nói convention args.

### 4.2 Việc cần có để đạt C2 (rubric)

- Bỏ cả 3 chỉ dẫn xấu ở trên.
- Có rule routing: khi nào `timeline` (tin CỦA một tài khoản) / `social_search` (theo chủ đề) / `lookup` (web, `topic=news` cho tin tức) / `fetch` (đã có URL) / `clarify` (thiếu thông tin).
- Mỗi `description` trong `tools.yaml` nói: làm gì, **khi nào dùng, khi nào không dùng**.
- Convention args (đã thấy ở case eval cơ sở): handle không có `@` và map tên người sang handle (ví dụ `sama`, `elonmusk`, `karpathy`); `topic=news` cho tin tức; `timeframe` (hôm nay = `day`, tuần này = `week`); `search_type=Top` cho "phổ biến/top", mặc định `Latest`; `limit` lấy từ số trong câu hỏi.
- `send`: mô tả rõ chỉ gửi khi người dùng đã xác nhận (`confirmed=true`); chưa xác nhận thì hỏi lại bằng `clarify` với `response_type=yes_no` (case R12).
- Hỏi lại đúng lúc (R10, R11); từ chối câu ngoài phạm vi (R08, R14); không gọi tool cho câu meta (R09); gọi song song nhiều tool khi cần (R13).
- Tên và tham số khớp registry; `pytest tests/test_tool_contract.py` xanh.

### 4.3 Việc cần có để đạt C3 (20 điểm — trọng số cao nhất)

Mỗi version (v1, v2, v3):
1. Đọc run JSON của version trước, chọn **một** giả thuyết (ví dụ "prompt đang khuyến khích đoán nên R10/R11 sai").
2. Sửa **một** thứ để kiểm chứng giả thuyết đó.
3. Chạy:
   ```bash
   python run_eval.py --provider openrouter --version v1 --suite base --eval-cases data/eval_base.json
   ```
   (tương tự `v2`, `v3`).
4. Thêm một dòng vào `version_log.csv`: hash, `reason`, `hypothesis`, `metric_before`, `metric_after`, `run_file`. Metric lấy từ `summary` trong run JSON (ví dụ `case_accuracy`).
5. Mỗi version phải có `prompt_hash`/`tools_hash` khác version trước (nếu chỉ đổi nhãn thì không tính).

Quy tắc điểm: version không tăng điểm vẫn được tính nếu phân tích trung thực. Thiếu run hoặc run không hợp lệ thì không tính. **Dùng cùng một model cho v0–v3.**

Điền bảng B1 trong `group_report.md` từ `version_log.csv`.

## 5. Bước 3 — Bảo: Tool mới + unit test (C4, 15 điểm)

Làm theo `docs/SPEC_BAO_NEW_TOOL.md`. Tóm tắt điều kiện đạt:
- `tools/<tên>/tool.py` + `TOOL.md` (frontmatter đúng contract trong `tools/README.md`).
- Đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`) và khai báo trong `artifacts/tools.yaml`.
- ≥ 3 test trong `tests/test_tools_todo.py`: happy path, input xấu, nhánh lỗi (trả error dict, không raise). Offline, mock bằng `fake_http`, có assert thật.
- `pytest` 0 failed.
- Điền B5a trong group report. Bảng đó có yêu cầu một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được — chỉ ghi nếu thật sự gặp.

Bị trừ điểm: test gọi mạng thật, không assert, tool raise thay vì trả error dict, tên/tham số lệch registry.

## 6. Bước 4 — Hiếu: 10 case eval nhóm (C5, 10 điểm)

Ghi vào `data/eval_group.json` (hiện `"cases": []`). Đúng **10 case: 5 single turn (`query`) + 5 multi turn (`turns`)**.

Mỗi case cần: `id`, `phase: "B"`, `query` hoặc `turns`, `failure_type` (thuộc `allowed_failure_types` trong file), `expect` (`tool_calls` hoặc `no_tool`), `metadata.what_it_tests`. Format mẫu lấy từ `data/eval_base.json` (single: `query`; multi: `turns` là list `{"role":"user","content":...}`; `expect.tool_calls[].args` chỉ cần chứa các arg cần kiểm tra).

Yêu cầu:
- Ít nhất 1 case route tới **tool mới của Bảo** (cần biết tên tool và arg — xem câu hỏi #3).
- Không chép case có sẵn (chép thì không tính).
- Nên nhắm vào lỗi mà v0 mắc phải (xem B2 của Lâm) để case có ý nghĩa.
- Test contract tự kiểm tra: eval chỉ được expect tool đã khai báo trong `tools.yaml`.

Chạy:
```bash
python run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```
Điền bảng B3 (10 dòng).

## 7. Bước 5 — Thịnh: UI + live chat + báo cáo (C6 10đ + C7 10đ)

### 7.1 UI (bắt buộc)

- Phải có UI chạy được bằng Streamlit hoặc Vercel (README). Repo không có mã UI mẫu; xem câu hỏi #5.
- Thêm dependency UI vào `requirements.txt`.
- Ghi lệnh chạy UI và link dùng thử vào mục A1 của `group_report.md`. Deploy nhanh bằng Cloudflare Tunnel (README mục "Deploy nhanh"): `cloudflared tunnel --url http://localhost:8501`; link tạm thời, sống theo phiên `cloudflared`.
- Bị trừ điểm nếu UI che lỗi tool hoặc chỉ có ảnh chụp.

### 7.2 Live chat

```bash
python chat.py --provider openrouter --version v3
```
Transcript lưu ở `transcripts/*.transcript.json`. Cần ≥ 3 lượt gồm đủ:
1. Yêu cầu research bình thường.
2. Yêu cầu thiếu thông tin (không nói rõ tài khoản/URL), rồi lượt sau bổ sung.
3. Yêu cầu gửi/đăng bản tin lên Telegram — quan sát agent hỏi lại trước hay gửi ngay, tự quyết hành vi đúng và sửa prompt cho khớp.

Điền bảng B4. Kiểm tra `transcripts/` và `runs/` không có key/token trước khi commit.

### 7.3 Báo cáo nhóm (`report/team/group_report.md`)

- **Phần A** (mục 2: A1 agent làm gì + lệnh UI + link, A2 danh sách tool kể cả tool mới, A3 3–5 câu hỏi mẫu) phải xong **trước showdown 16:30** (giờ buổi lab; CHƯA CÓ THÔNG TIN về ngày lab thực tế của nhóm).
- **Phần B**: B1 (version), B2 (failure), B3 (10 case), B4 (live chat), B5a (tool mới + test + UI), mục 5 (khó khăn), mục 6, mục 7 (reflection), mục 1 (provider/model dùng cho v0–v3).
- Mỗi bảng phải trỏ tới file/run/transcript/commit thật; nhận xét không bằng chứng thì không tính điểm.

## 8. Bước 6 — Cả nhóm: Đóng góp cá nhân + nộp bài (C8, 10 điểm)

- `TEAM.md`: điền email, GitHub, URL repo, nhánh nộp, commit chốt (đã điền tên/MSSV/vai trò).
- Mỗi người điền file `report/team/<MSSV>_<HoTen>.md`: đóng góp cụ thể, bằng chứng (file/commit/PR), công cụ AI đã dùng và cách tự kiểm tra, tự đánh giá. Hiếu: đổi tên file `2A202603860_Hieu.md` thành tên đầy đủ khi có.
- Xóa file mẫu `report/team/MSSV_HoTen.md` trước khi nộp (đang còn trong repo; rubric yêu cầu file đúng tên từng người).
- Mỗi người có ≥ 1 commit kỹ thuật trong lịch sử branch nộp.
- Mỗi người phải tự giải thích được phần của mình (người chấm có thể hỏi trực tiếp).
- Đổi tên repo đúng quy ước `K5-L3B-DAY03-TenNhom-ResearchAgentToolEval` (hiện repo `K5-L3B-DAY03-Random-...`; tên nhóm "Random" mình suy ra từ tên repo, cần xác nhận).
- Mỗi thành viên tự nộp cùng link repo trên LMS, trước deadline.

## 9. Checklist nghiệm thu cuối (trước khi nộp)

- [ ] `cd starter_v0 && pytest` báo 0 failed; `pytest tests/test_tool_contract.py` xanh.
- [ ] `runs/` có v0, v1, v2, v3 và run `--suite group`, đều hợp lệ (provider_error_cases == 0, measured == total).
- [ ] `version_log.csv` có v0–v3 với hash, giả thuyết, metric trước/sau, run_file.
- [ ] `data/eval_group.json` đúng 10 case (5 single + 5 multi), ≥ 1 case route tới tool mới.
- [ ] `eval_base.json` không bị sửa nội dung case.
- [ ] `transcripts/` có ≥ 3 lượt đủ 3 loại.
- [ ] UI chạy được, link/lệnh ghi ở A1.
- [ ] `group_report.md` đủ Phần A và B, mọi bảng trỏ tới bằng chứng thật.
- [ ] `TEAM.md` điền đủ; 4 file báo cáo cá nhân đúng tên; file mẫu `MSSV_HoTen.md` đã xóa.
- [ ] Mỗi người có commit kỹ thuật.
- [ ] Không có `.env`, API key, token, `.venv`, `arxiv_papers/` trong git.
- [ ] Đã push; repo mở được cho người chấm; mọi người đã nộp link trên LMS.

## 10. Bonus (ghi riêng, tối đa 10 điểm; chỉ làm khi phần bắt buộc xong)

| Bonus | Điểm | Điều kiện |
|---|---:|---|
| Small Local Model (README Step 7) | 4 | ≥ 2 model local (≤ 8B, tool-calling) chạy base eval, ≥ 2 vòng tối ưu `v4-local`, `v5-local` có log, bảng cloud vs local ở B7 |
| ≥ 4 tool mới tự viết | 3 | Mỗi tool có `TOOL.md`, đăng ký, ≥ 3 test, và eval case route tới |
| `send` gửi Telegram thật sau xác nhận | 2 | Transcript: hỏi lại -> user xác nhận -> `send(confirmed=true)` -> `status: sent` trên private channel của nhóm. Cần tự tạo bot (BotFather) và channel; xem `docs/TOOL-SETUP.md` mục 6 |
| Test challenge | 1 | `pytest` 0 skipped toàn suite, hoặc regression test cho bug tìm được trong tool có sẵn (ghi ở B5) |

Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus; đổi tên tool có sẵn không tính là tool mới.

## 11. Rủi ro cần canh

- **Hết quota API**: Tavily/Firecrawl/RapidAPI mỗi cái 1,000/tháng theo `TOOL-SETUP.md` (ghi là kiểm tra 2026-06-02, có thể đã đổi). Chạy thử vài case trước, chỉ một người chạy eval chính.
- **Đổi model giữa các version** làm bảng so sánh vô nghĩa.
- **Thêm tool vào `tools.yaml` trước khi chạy v0** làm lệch baseline.
- **Lộ key** trong `runs/` hoặc `transcripts/`.
- **Đổi tên tool** phải đồng bộ `tools.yaml`, `tools/__init__.py`, và các file eval (README mục "Nếu nhóm đổi tên tool").
