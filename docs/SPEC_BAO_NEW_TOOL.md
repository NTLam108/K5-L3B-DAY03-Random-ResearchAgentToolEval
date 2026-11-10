# SPEC — Tool mới + Unit test (phần việc của Trần Gia Bảo, CP3 / rubric C4)

> Dành cho AI/coding agent đọc và thực hiện. Mọi lệnh chạy từ thư mục `starter_v0/`.
> **Quy tắc tối thượng: KHÔNG đoán.** Chỗ nào spec ghi "CHƯA CÓ THÔNG TIN" thì phải hỏi người dùng, không tự bịa.

## 0. Mục tiêu

Thêm ít nhất 1 tool mới vào research agent và chứng minh code tool chạy đúng bằng unit test.

Điều kiện hoàn thành (tất cả phải đúng):
1. Có folder `tools/<tên_tool>/` gồm `tool.py` và `TOOL.md`.
2. Tool đăng ký trong `tools/__init__.py` (`TOOL_FUNCTIONS`) và khai báo trong `artifacts/tools.yaml`.
3. Có ≥ 3 unit test cho tool mới trong `tests/test_tools_todo.py`, không skip.
4. `pytest` báo **0 failed**; `pytest tests/test_tool_contract.py` xanh.
5. Điền bảng B5a trong `report/team/group_report.md` và file báo cáo cá nhân `report/team/2A202603914_TranGiaBao.md`.

## 0.5. QUYẾT ĐỊNH ĐÃ CHỐT: tool mới là `cite`

Người phụ trách nhóm đã ủy quyền chọn; các quyết định dưới đây thay cho câu hỏi #1–#3 ở mục 1. Đây là quyết định thiết kế, **không phải sự thật lấy từ đề bài**.

**Tool:** `cite` — tạo trích dẫn học thuật từ metadata của một bài báo. Ghép với output của tool `papers` (đã đọc `tools/papers/tool.py`: có `title`, `authors` là list, `published`, `url`, `arxiv_id`).

**Lý do chọn (để điểm cao + dễ):** chạy local, không cần API key, không cần mạng nên test offline gọn, không phụ thuộc quota; khác biệt rõ với `format` và các tool tìm kiếm; có luồng tự nhiên "papers -> cite".

**Chữ ký hàm (đề xuất):**

```python
def cite(title: str = "", authors: list[str] | None = None, published: str = "",
         url: str = "", style: str = "apa") -> dict[str, Any]
```

- `style` thuộc `["apa", "bibtex"]`, mặc định `apa`. Giá trị ngoài enum -> error dict (đây chính là test "input xấu").
- Thành công: `{"tool": "cite", "style": <style>, "citation": "<chuỗi>"}`.
- Lỗi: `err("cite", exc)` từ `tools/_shared.py`, không raise.

**Quy tắc đầu vào (chốt để test không mơ hồ):**
- `title` rỗng hoặc chỉ toàn khoảng trắng -> lỗi (`ValueError`, qua `err`).
- `authors` phải là list; sai kiểu (ví dụ chuỗi) -> lỗi; list rỗng -> lỗi.
- `published` lấy 4 ký tự đầu làm năm nếu là số; không có năm hợp lệ -> dùng `n.d.` (APA) / bỏ trường `year` (BibTeX). Đây là lựa chọn của nhóm, ghi vào `TOOL.md`.
- Tên tác giả từ arXiv dạng "Họ Tên" (ví dụ `Ashish Vaswani`): tool đảo thành "Họ, Chữ-cái-đầu." theo heuristic **từ cuối là họ**. Heuristic này sai với một số tên (tên nhiều từ, tên Việt Nam ghi họ trước). **Phải ghi giới hạn này vào `TOOL.md` và báo cáo**, không giấu.

**Quy tắc APA áp dụng (đã đối chiếu với các hướng dẫn thư viện đại học tìm được, ví dụ Purdue OWL, JCU, TU Dublin):**
- Tác giả: họ trước, theo sau là chữ cái đầu của tên; ngăn cách bằng dấu phẩy; có `&` trước tác giả cuối khi có 2 đến 20 tác giả; liệt kê theo thứ tự nguồn.
- Chỉ viết hoa chữ đầu tiên của tiêu đề (và danh từ riêng); tool có thể chuẩn hóa chữ đầu, nhưng không bắt buộc xử lý danh từ riêng, ghi giới hạn vào `TOOL.md`.
- Chưa xác minh được từ nguồn nào: định dạng chính xác của phần "arXiv" và URL cho preprint trong APA 7, quy tắc khi có hơn 20 tác giả. **Bảo cần tra tài liệu chính thức (APA Style) cho hai điểm này trước khi chốt chuỗi mong đợi trong test**, hoặc nhóm tự quyết và ghi rõ trong `TOOL.md` rằng đó là định dạng đơn giản hóa. Để đơn giản và không đoán, nhóm quy ước: > 20 tác giả -> trả lỗi `ValueError` ("too many authors"), không xử lý.
- Mẫu chuỗi APA (đơn giản hóa, nhóm chấp nhận): `Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention is all you need. arXiv. https://arxiv.org/abs/1706.03762` — đây là mẫu định dạng, chưa kiểm chứng bằng nguồn APA chính thức cho phần "arXiv. URL".

**BibTeX:** dùng entry `@misc{key, title = {...}, author = {A and B and C}, year = {...}, url = {...}}`, tác giả nối bằng ` and `, key sinh từ họ tác giả đầu + năm (chữ thường, bỏ ký tự không phải chữ/số). Đây là quy ước phổ biến mình biết nhưng **chưa tra lại tài liệu**; Bảo nên đối chiếu một nguồn BibTeX trước khi chốt.

**`track` trong `TOOL.md`:** tạm đặt `bonus` (README: core đủ để qua bài cơ bản, bonus là phần thêm). **Chưa xác nhận với coach** — nếu coach nói khác thì đổi.

**Thời điểm merge:** làm trên branch riêng `feat/cite-tool`; chỉ merge phần sửa `artifacts/tools.yaml` vào `main` **sau khi Lâm chạy xong và push run v0**, để không làm lệch baseline.

**Bộ test chốt (≥ 3 bắt buộc, khuyến nghị 7 để chắc điểm, tất cả offline, không cần `fake_http`):**
1. `test_cite_apa_three_authors_formats_names_and_ampersand` — happy path, assert chuỗi đầy đủ.
2. `test_cite_apa_single_author_has_no_ampersand`
3. `test_cite_bibtex_builds_key_and_joins_authors_with_and`
4. `test_cite_empty_title_returns_error_dict`
5. `test_cite_authors_wrong_type_returns_error_dict_not_raise`
6. `test_cite_unknown_style_returns_error_dict`
7. `test_cite_missing_year_uses_nd_in_apa`

**Eval case route tới `cite` (gợi ý cho Hiếu):** câu hỏi người dùng kèm metadata của paper và yêu cầu citation APA. Lưu ý: model phải truyền `title`, `authors`, `published` vào args; nếu case khó thì vẫn hợp lệ, miễn kết quả được phân tích trung thực.

**Mô tả `tools.yaml` đề xuất (nói khi nào dùng/không dùng):** "Tạo trích dẫn APA hoặc BibTeX từ metadata một bài báo đã biết (title, authors, published, url). Dùng khi người dùng xin citation/tham khảo của một paper cụ thể. KHÔNG dùng để tìm paper (dùng papers) và không dùng để trình bày bản tin (dùng format)."

## 1. Các câu hỏi còn lại (câu #1–#3 đã được chốt ở mục 0.5)

| # | Câu hỏi | Vì sao cần |
|---|---|---|
| 1 | Tên tool mới là gì? (snake_case, ngắn) | Dùng ở `tools.yaml`, `TOOL_FUNCTIONS`, `TOOL.md`, và Hiếu viết eval case route tới nó |
| 2 | Tool làm gì, nhận arg nào, trả field nào? | Quyết định toàn bộ code, test, description |
| 3 | Tool gọi API ngoài (cần key / provider nào) hay chạy local? | Quyết định có cần mock HTTP và `requires_env` |
| 4 | `track` trong `TOOL.md` là `core` hay `bonus`? | Repo chỉ liệt kê 2 giá trị, không nói tool học viên thêm dùng giá trị nào |
| 5 | Máy đã cài dependency chưa, `pytest` chạy được chưa? | Chưa kiểm tra |

Nếu người dùng không trả lời được câu nào, ghi lại là "không có thông tin" và dừng ở phần phụ thuộc câu đó.

Không được tự chọn ý tưởng tool. Không được dùng tên của tool có sẵn (`clarify`, `timeline`, `social_search`, `lookup`, `fetch`, `format`, `send`, `policy`, `papers`, `paper_text`); đổi tên tool có sẵn không tính là tool mới.

## 2. Bối cảnh repo (đã xác minh bằng cách đọc file)

- Registry: `tools/__init__.py`, dict `TOOL_FUNCTIONS` map tên (model nhìn thấy) -> hàm Python. Có comment `TODO CP3 (student)` đánh dấu chỗ thêm.
- Khai báo cho model: `artifacts/tools.yaml`, key `tools:` là list; mỗi item có `name`, `description`, `parameters` (JSON schema kiểu object, có `properties`, `required`).
- Helper dùng chung: `tools/_shared.py` có `err(tool, exc)` -> `{"tool", "error", "message"}`, `domain(url)`, `terms()`, `fold_text()`, `TIMEOUT = 30`.
- Mẫu tool gọi API: `tools/lookup/tool.py`. Mẫu tool local: `tools/format/tool.py`, `tools/clarify/tool.py`.
- Fixture test (`tests/conftest.py`):
  - `FakeResponse(payload, status_code, text, content)`.
  - `fake_http(response_or_exception)` patch `requests.get` và `requests.post`, trả list `calls` ghi lại `method`, `url`, và kwargs (`json`, `headers`, ...).
  - Autouse: xóa env `TAVILY_API_KEY, FIRECRAWL_API_KEY, RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID` trước mỗi test; chặn `requests.Session.request` (request thật làm test fail).
- Mẫu viết test: `tests/test_tools_examples.py`.
- `pytest.ini`: `testpaths = tests`, `addopts = -ra`.

## 3. Các bước thực hiện

### Bước 1 — Tạo `tools/<tên_tool>/tool.py`

Quy tắc:
- Hàm có default cho mọi tham số (ví dụ `query: str = ""`), theo style các tool có sẵn.
- Toàn bộ logic nằm trong `try/except Exception as exc: return err("<tên>", exc)`. **Không được raise ra ngoài** (rubric trừ điểm).
- Kết quả thành công là dict có field `"tool"`.
- Nếu cần key: `os.getenv(...)`, thiếu thì `raise RuntimeError("Missing <ENV> env var")` bên trong `try` (giống `lookup`).
- Gọi HTTP bằng `requests.get` / `requests.post` (không dùng `requests.Session`), để `fake_http` mock được.
- Import helper bằng `from tools._shared import ...`.

### Bước 2 — Tạo `tools/<tên_tool>/TOOL.md`

Frontmatter nằm **ở đầu file**, đúng các trường:

```yaml
---
name: <tên_tool>
track: <core|bonus — xem câu hỏi #4>
kind: live_api | local_formatter | local_knowledge | action | control
provider: <tên provider nếu có>
requires_env: [<ENV nếu có>]
inputs: [<arg>]
outputs: [<field>]
side_effect: false | true | local_file_write
---
```

Sau frontmatter là vài dòng mô tả. `name` phải trùng `name` trong `tools.yaml` (test contract kiểm tra, đọc frontmatter bằng `split("---")[1]`).

### Bước 3 — Đăng ký trong `tools/__init__.py`

1. Thêm import: `from .<tên_tool>.tool import <hàm>` cạnh các import hiện có.
2. Thêm `"<tên_tool>": <hàm>,` vào `TOOL_FUNCTIONS` ở chỗ comment `TODO CP3`.

### Bước 4 — Khai báo trong `artifacts/tools.yaml`

Thêm vào cuối list `tools:`:

```yaml
  - name: <tên_tool>
    description: "<làm gì>. Dùng khi <...>. KHÔNG dùng khi <...>."
    parameters:
      type: object
      properties:
        <arg>: {type: string, default: "", description: "<convention cụ thể>"}
      required: [<arg bắt buộc>]
```

Ràng buộc do `tests/test_tool_contract.py` kiểm tra:
- Mọi key trong `properties` phải có trong signature của hàm.
- Mọi phần tử `required` phải nằm trong `properties`.
- `description` không rỗng; tên không trùng tool khác.
- Có `tools/*/TOOL.md` với `name` trùng.

Description phải nói rõ khi nào dùng và khi nào không dùng để model không chọn nhầm với tool có sẵn.

**Không sửa** description / nội dung các tool có sẵn trong file này (đó là việc của vòng v1–v3 do người khác phụ trách).

### Bước 5 — Viết ≥ 3 unit test trong `tests/test_tools_todo.py`

- Thêm section mới cho tool mới; **không xóa** các stub `pytest.skip(TODO)` của tool có sẵn.
- Lấy hàm: `TOOL_FUNCTIONS["<tên_tool>"]`.
- Ba test tối thiểu, mỗi test một hành vi, tên test mô tả hành vi:
  1. **Happy path**: input hợp lệ, assert kết quả. Với API tool: assert cả request gửi đi (`calls[0]["url"]`, `["json"]`, `["headers"]`) và cách map response (mẫu: `test_lookup_sends_expected_request_and_maps_results`).
  2. **Input xấu từ model**: chuỗi rỗng, sai kiểu, hoặc ngoài enum. Assert hành vi cụ thể (error dict hoặc xử lý an toàn).
  3. **Nhánh lỗi**: thiếu key (`result["error"] == "RuntimeError"`) hoặc HTTP lỗi (`fake_http(FakeResponse(status_code=429))` -> `result["error"] == "HTTPError"`). Trả error dict, không raise.
- Mọi test phải có assert thật. Không gọi mạng thật. Key giả set bằng `monkeypatch.setenv`.

### Bước 6 — Chạy kiểm tra

```bash
pytest tests/test_tool_contract.py
pytest -v
```

Đạt khi: 0 failed; 3 test tool mới không skipped. Stub của tool có sẵn được phép còn skip.

Nếu một lệnh fail: đọc lỗi, sửa gốc rễ. Nếu cùng một cách sửa fail hai lần, dừng lại và báo người dùng, không vá mò.

### Bước 7 — Báo cáo và commit

- `report/team/group_report.md`, bảng B5a: điền hàng "Tool mới" (folder, What worked, Risk/Guardrail) và hàng "Unit test tool mới" (dán output `pytest`, số test). Dòng "ví dụ lỗi mà unit test bắt được nhưng eval không bắt được" chỉ điền nếu thật sự xảy ra; không bịa. Thêm tool vào bảng A2 (danh sách tool) của Phần A.
- `report/team/2A202603914_TranGiaBao.md`: điền "Đóng góp cụ thể", "Bằng chứng" (file/commit), "AI/công cụ đã dùng và cách tự kiểm tra kết quả".
- Commit riêng cho phần tool (mỗi thành viên cần ít nhất 1 commit kỹ thuật). Không commit `.env`, API key.
- Báo cho Hiếu (người viết `data/eval_group.json`) tên tool và danh sách tham số.

## 4. Lưu ý phối hợp (suy luận, chưa xác minh)

CHECKPOINTS yêu cầu baseline v0 chạy khi `tools.yaml` chưa sửa. Thêm tool vào `tools.yaml` rất có thể làm đổi `tools_hash` của run (README nói run JSON lưu `tools_hash`; chưa đọc `versioning.py` để xác nhận). Nên merge tool sau khi Lâm chạy xong v0, hoặc làm trên branch riêng. Hỏi người dùng nếu chưa rõ v0 đã chạy chưa.

## 5. Tiêu chí bị trừ điểm (RUBRIC C4)

- Test gọi mạng thật, hoặc không assert gì.
- Tool raise thay vì trả error dict.
- Tên / tham số lệch giữa `tools.yaml` và code.
- Dưới 3 test cho tool mới, hoặc `pytest` còn failed.

## 6. Ngoài phạm vi (không làm)

- Không sửa `data/eval_base.json`.
- Không sửa `artifacts/system_prompt.md` và description các tool có sẵn.
- Không viết eval case (việc của Hiếu), UI hay báo cáo nhóm ngoài bảng B5a và Phần A2.
- Bonus (≥ 4 tool mới, `pytest` 0 skipped, v.v.) chỉ làm khi người dùng yêu cầu.
