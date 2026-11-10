# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (`v0+peb1c8179815b+te69bc53ed884`) | Đo hành vi của prompt + tool declaration starter trước khi tối ưu | — | 0.65 | [`v0_B_base_openrouter_20261110T175342743576.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T175342743576.json) |
| v1 | `system_prompt.md` (`v1+p9b882949c50b+te69bc53ed884`) | 5/7 lỗi v0 (R08, R10, R11, R12, R14) do chỉ dẫn xấu cố ý trong prompt (đoán account, bịa URL, gửi không xác nhận, ép một tool). Bỏ chúng + thêm rule scope / `clarify` khi thiếu info / xác nhận trước `send` / routing / multi-turn → agent sẽ hỏi lại, xin xác nhận, không gọi tool cho câu ngoài phạm vi | 0.65 | 0.80 | [`v1_B_base_openrouter_20261110T181321621691.json`](../../starter_v0/runs/v1_B_base_openrouter_20261110T181321621691.json) |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

**Chi tiết v0 → v1** (cùng provider `openrouter / openai/gpt-4o-mini`, cả 2 run hợp lệ):

| Metric | v0 | v1 | Δ |
|---|---:|---:|---:|
| case_accuracy | 0.65 (13/20) | 0.80 (16/20) | +0.15 |
| tool_routing_accuracy | 0.75 | 0.85 | +0.10 |
| argument_accuracy | 0.65 | 0.80 | +0.15 |
| multiturn_accuracy | 1.00 (6/6) | 0.67 (4/6) | **−0.33** |

- **FAIL → PASS (5):** R08, R14 (không còn gọi `send` để trả lời câu ngoài phạm vi), R11 (gọi `clarify` xin URL thay vì bịa `example.com`), R03, R13 (query còn `"AI"`, có `topic="news"`).
- **Vẫn FAIL (2):**
  - R10: không đoán `sama` nữa, nhưng chuyển sang `social_search(query="", limit=5)` thay vì `clarify` — model hiểu "5 tweet mới nhất" là tìm theo chủ đề với query rỗng. Rule "thiếu account → clarify" trong prompt chưa đủ vì model không nhận ra request cần account.
  - R12: đã gọi `clarify` (không tự gửi nữa — boundary đúng hướng) nhưng `response_type="text"` hỏi "Bạn muốn đăng nội dung gì?" thay vì `yes_no`. Vì "bản tin này" không kèm nội dung, model hỏi nội dung trước; eval kỳ vọng hỏi xác nhận yes/no.
- **PASS → FAIL (2, regression multi-turn):**
  - M02: lượt cuối "Chỉ tìm robotics thôi, vẫn là tin hôm nay" → gọi `social_search` thay vì `lookup`. Rule routing mới chưa nói rõ "tin / tin tức" mặc định là web (`lookup`) khi user không nhắc Twitter.
  - M06: user nói "Bỏ Twitter, chuyển sang web" nhưng model gọi cả `lookup` lẫn `social_search`. Rule mới "nhiều nguồn → gọi nhiều tool" + "giữ ràng buộc trước đó" khiến model giữ luôn Twitter dù user đã bỏ.
- **Nhận xét trung thực:** R03/R13 được sửa dù v1 không đụng `tools.yaml` → lỗi query `"AI news"` ở v0 có thể là tác dụng phụ của câu "fill in its arguments using your best judgment / single step", không chắc chắn là do thiếu convention args. Giả thuyết ban đầu cho v2 (convention `lookup`) vì vậy kém ưu tiên hơn; v2 nên nhắm vào R10, R12 và 2 regression M02/M06.

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

**Run v0:** [`starter_v0/runs/v0_B_base_openrouter_20261110T175342743576.json`](../../starter_v0/runs/v0_B_base_openrouter_20261110T175342743576.json) — `openrouter / openai/gpt-4o-mini`, artifact `v0+peb1c8179815b+te69bc53ed884`, hợp lệ (`provider_error_cases = 0`, `measured_cases = total_cases = 20`).
Kết quả: 13/20 pass · `case_accuracy` 0.65 · `tool_routing_accuracy` 0.75 · `argument_accuracy` 0.65 · `multiturn_accuracy` 1.0 (6/6 multi-turn pass, cả 7 lỗi đều ở single-turn).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | `wrong_tool` (case) → quan sát: `wrong_arg_value` | `lookup(query="AI news", topic="news", timeframe="day", max_results=5)` | Route đúng `lookup`, `topic`/`timeframe` đúng, nhưng `query: expected 'AI', got 'AI news'` — model nhồi chữ "news" vào query dù đã có `topic=news`. Nguyên nhân: description của `query` chỉ ghi "Truy vấn", không có quy ước query chỉ chứa chủ đề cốt lõi. | `tools.yaml`: mô tả `query` = từ khóa chủ đề cốt lõi, KHÔNG thêm "news/tin tức/hôm nay" vì đã thể hiện qua `topic`/`timeframe` |
| R08_out_of_scope | `out_of_scope` → quan sát: `unexpected_tool_call` | `send(text="Nguyên hàm của x^2 là x^3/3 + C…")` | Câu toán ngoài phạm vi research nhưng model gọi `send` để "trả lời". Nguyên nhân: prompt "Always finish the request in a single step. Pick one tool" ép luôn gọi tool; `send` mô tả mơ hồ "Gửi một đoạn văn bản đi" nên bị dùng như kênh trả lời. Code guardrail của `send` chặn lại (`status: needs_confirmation`) nên không gửi thật. | `system_prompt.md`: bỏ câu ép "pick one tool"; thêm rule phạm vi: chỉ làm research/tin tức, ngoài phạm vi thì từ chối bằng text, không gọi tool |
| R10_missing_handle | `missing_info` → quan sát: `missing_tool_call` | `timeline(screenname="sama")` | Thiếu tài khoản nhưng không hỏi lại, tự đoán `sama`. Nguyên nhân trực tiếp: prompt dặn "If a request mentions a tweet… doesn't say whose, pick a well-known account like Sam Altman" và "do not ask them back". | `system_prompt.md`: bỏ chỉ dẫn đoán; thêm rule thiếu handle/URL → gọi `clarify(response_type="text")` |
| R11_missing_url | `missing_info` → quan sát: `missing_tool_call` | `fetch(url="https://example.com/article")` | "Bài viết này" nhưng không có link → model bịa URL `example.com/article` rồi đọc trang đó. Nguyên nhân: prompt dặn "assume a likely URL and read it". | `system_prompt.md`: bỏ chỉ dẫn bịa URL; `fetch` chỉ dùng khi user đưa URL cụ thể, không có thì `clarify` |
| R12_confirm_before_send | `wrong_boundary` → quan sát: `missing_tool_call` | `send(text="Bản tin này đã được đăng lên Telegram.")` | Hành động ghi ra ngoài nhưng không xin xác nhận, còn bịa nội dung gửi. Nguyên nhân: prompt "When the user wants to send… just go ahead and do it"; `send.confirmed` chỉ mô tả "Cờ xác nhận". Tool trả `needs_confirmation` nên không gửi thật. | `system_prompt.md`: bỏ chỉ dẫn gửi ngay, thêm boundary: trước khi gửi phải `clarify(response_type="yes_no")` kèm nội dung; `tools.yaml`: `send` chỉ gọi `confirmed=true` sau khi user đồng ý rõ ràng |
| R13_parallel_web_and_tweets | `wrong_tool` (case) → quan sát: `wrong_arg_value` | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Gọi đủ 2 tool (routing đúng) nhưng `lookup` sai args: `query: expected 'AI', got 'AI news'` và `topic: expected 'news', got None` (thiếu `topic=news` dù hỏi "tin AI hôm nay"). Nguyên nhân: không có quy ước `topic=news` cho tin thời sự; cùng lỗi query như R03. | `tools.yaml`: `topic` = `news` khi hỏi tin tức/thời sự, `general` cho tra cứu chung; quy ước `query` như R03. `system_prompt.md`: cho phép gọi nhiều tool khi request cần nhiều nguồn (bỏ "single step") |
| R14_out_of_scope_coding | `out_of_scope` → quan sát: `unexpected_tool_call` | `send(text="Dưới đây là một hàm Python tính số Fibonacci…")` | Câu coding ngoài phạm vi nhưng model nhét câu trả lời vào `send`. Cùng nguyên nhân với R08. | Như R08; thêm vào description `send`: KHÔNG dùng để trả lời user, chỉ để đăng bản tin lên Telegram |

**Nhận xét chung v0:**

- 5/7 lỗi (R08, R10, R11, R12, R14 — gồm cả 2 out-of-scope) truy trực tiếp về các chỉ dẫn xấu cố ý trong `system_prompt.md` ("do not ask them back", "pick Sam Altman", "assume a likely URL", "just go ahead and do it", "single step / pick one tool") → giả thuyết cho **v1**: bỏ các chỉ dẫn này + thêm rule `clarify`/xác nhận/phạm vi.
- 2/7 lỗi (R03, R13) là lỗi convention args do `tools.yaml` mơ hồ (`query`, `topic`) → giả thuyết cho version sau: viết lại description tham số `lookup`.
- `send` bị gọi sai 3 lần (R08, R12, R14) nhưng không gửi thật nhờ guardrail trong code (`status: needs_confirmation`) — đây là lớp bảo vệ của tool, không phải của model; boundary vẫn phải sửa ở prompt/declaration.
- R03 và R13 có `failure_type` của case là `wrong_tool` nhưng thực tế routing đúng, lỗi là args — khi phân tích nên đọc `observed_mismatch` thay vì chỉ nhìn `failure_type`.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
