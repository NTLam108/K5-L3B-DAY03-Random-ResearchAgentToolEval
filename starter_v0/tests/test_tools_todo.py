"""Tool unit tests (CP3 / test challenge): starter tools plus the team tool `cite`.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations


from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](question="Chọn một:", response_type="choice", options=["A", "B"])

    assert result["options"] == ["A", "B"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

ITEMS_AB = [
    {"title": "x", "section": "A", "url": "https://a.com/1"},
    {"title": "y", "section": "B", "url": "https://b.com/2"},
    {"title": "z", "section": "A", "url": "https://a.com/3"},
]


def test_format_sections_groups_items_by_section() -> None:
    result = TOOL_FUNCTIONS["format"](items=ITEMS_AB, template="sections")

    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    section_a = result["markdown"].split("## B")[0]
    assert "x - [a.com](https://a.com/1)" in section_a and "z - [a.com](https://a.com/3)" in section_a


def test_format_thread_numbers_items() -> None:
    result = TOOL_FUNCTIONS["format"](items=ITEMS_AB[:2], template="thread")

    assert result["markdown"] == "1/ x - [a.com](https://a.com/1)\n\n2/ y - [b.com](https://b.com/2)"


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty, template="sections")
        assert result["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin hôm nay", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == "https://api.telegram.org/bottest-token/sendMessage"
    assert calls[0]["json"]["chat_id"] == "-100123"
    assert calls[0]["json"]["text"] == "Bản tin hôm nay"
    assert result == {"tool": "send_telegram", "status": "sent"}


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert calls == []
    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="OpenAI", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Hello",
        "metadata": {"title": "T", "sourceURL": "https://example.com/final"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/a")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"] == {"url": "https://www.example.com/a", "formats": ["markdown"]}
    assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
    assert result["items"][0] == {
        "title": "T", "url": "https://example.com/final", "source": "example.com", "summary": "# Hello",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    result = TOOL_FUNCTIONS["fetch"](url="https://example.com")

    assert len(result["items"][0]["summary"]) == 4000
    assert result["items"][0]["title"] == "https://example.com"  # no metadata title -> falls back to the URL


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    raw = [{"text": "no id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(100 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["url"] == "https://twitter-api45.p.rapidapi.com/timeline.php"
    assert calls[0]["params"] == {"screenname": "sama"}
    assert calls[0]["headers"]["x-rapidapi-key"] == "test-key"
    assert [item["url"] for item in result["items"]] == [f"https://x.com/sama/status/{100 + i}" for i in range(3)]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Top")
    TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Latest")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert calls[1]["params"] == {"query": "OpenAI", "search_type": "Latest"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    policy = TOOL_FUNCTIONS["policy"]

    assert policy(query="")["results"] == []
    assert policy(query="the of")["results"] == []  # only stopwords -> nothing to match


def test_policy_area_filter_only_returns_that_area() -> None:
    result = TOOL_FUNCTIONS["policy"](query="data", policy_area="data_privacy")

    assert result["results"], "expected at least one data_privacy hit"
    assert {hit["policy_area"] for hit in result["results"]} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = TOOL_FUNCTIONS["policy"](query="injection probe citation", policy_area="source_citation")
    probe = next(hit for hit in result["results"] if hit["section"] == "Injection probe")

    assert any("ignore the citation policy" in line for line in probe["untrusted_text"])
    assert all("ignore the citation policy" not in hit["facts"] for hit in result["results"])


# ---------------- cite (team tool) ----------------

cite_tool = TOOL_FUNCTIONS["cite"]
ARXIV_URL = "https://arxiv.org/abs/1706.03762"


def test_cite_apa_three_authors_formats_names_and_ampersand() -> None:
    result = cite_tool(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        published="2017-06-12T17:57:34Z",
        url=ARXIV_URL,
    )
    assert result["tool"] == "cite"
    assert result["style"] == "apa"
    assert result["citation"] == (
        "Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention Is All You Need. arXiv. " + ARXIV_URL
    )


def test_cite_apa_single_author_has_no_ampersand() -> None:
    result = cite_tool(title="Notes", authors=["Ada Lovelace"], published="1843")
    assert result["citation"] == "Lovelace, A. (1843). Notes."
    assert "&" not in result["citation"]


def test_cite_apa_two_authors_use_comma_and_ampersand() -> None:
    result = cite_tool(title="Engines", authors=["Ada Lovelace", "Charles Babbage"], published="1843")
    assert result["citation"].startswith("Lovelace, A., & Babbage, C. (1843).")


def test_cite_apa_missing_year_uses_nd() -> None:
    result = cite_tool(title="Undated", authors=["Ada Lovelace"], published="not a date")
    assert "(n.d.)" in result["citation"]


def test_cite_bibtex_builds_key_and_joins_authors_with_and() -> None:
    result = cite_tool(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer"],
        published="2017-06-12",
        url=ARXIV_URL,
        style="bibtex",
    )
    assert result["style"] == "bibtex"
    assert result["citation"] == (
        "@misc{vaswani2017,\n"
        "  title = {Attention Is All You Need},\n"
        "  author = {Vaswani, Ashish and Shazeer, Noam},\n"
        "  year = {2017},\n"
        "  url = {" + ARXIV_URL + "}\n"
        "}"
    )


def test_cite_empty_title_returns_error_dict() -> None:
    result = cite_tool(title="   ", authors=["Ada Lovelace"])
    assert result["tool"] == "cite"
    assert result["error"] == "ValueError"
    assert "title" in result["message"]


def test_cite_authors_wrong_type_returns_error_dict_not_raise() -> None:
    result = cite_tool(title="Notes", authors="Ada Lovelace")
    assert result["error"] == "TypeError"
    assert "authors" in result["message"]


def test_cite_apa_without_authors_moves_title_to_author_position() -> None:
    for no_authors in ([], None):
        result = cite_tool(title="Notes on engines", authors=no_authors, published="1843")
        assert result["citation"] == "Notes on engines. (1843)."


def test_cite_bibtex_without_authors_omits_author_field() -> None:
    result = cite_tool(title="Notes", authors=[], published="1843", style="bibtex")
    assert result["citation"].startswith("@misc{anon1843,")
    assert "author" not in result["citation"]


def test_cite_unknown_style_returns_error_dict() -> None:
    result = cite_tool(title="Notes", authors=["Ada Lovelace"], style="chicago")
    assert result["error"] == "ValueError"
    assert "apa" in result["message"]


def test_cite_apa_21_or_more_authors_lists_first_19_ellipsis_and_last() -> None:
    authors = [f"Given{i} Surname{i}" for i in range(25)]
    citation = cite_tool(title="Big paper", authors=authors)["citation"]
    assert citation.startswith("Surname0, G., Surname1, G.")
    assert "Surname18, G., ... Surname24, G. (n.d.)." in citation
    assert "Surname19" not in citation
    assert "&" not in citation


def test_cite_apa_exactly_20_authors_lists_all_with_ampersand() -> None:
    authors = [f"Given{i} Surname{i}" for i in range(20)]
    citation = cite_tool(title="Big paper", authors=authors)["citation"]
    assert ", & Surname19, G." in citation
    assert "..." not in citation


def test_cite_bibtex_key_keeps_only_letters_and_digits() -> None:
    result = cite_tool(title="Notes", authors=["Jean O'Neil-Smith"], published="2020", style="bibtex")
    assert result["citation"].startswith("@misc{oneilsmith2020,")


# ---------------- calc ----------------

calc_tool = TOOL_FUNCTIONS.get("calc")


def test_calc_evaluates_basic_arithmetic_and_precedence() -> None:
    result = calc_tool(expression="(120 - 80) / 80 * 100")
    assert result["tool"] == "calc"
    assert result["result"] == 50.0
    assert result["formatted"] == "50.0"


def test_calc_handles_math_functions_and_precision() -> None:
    result = calc_tool(expression="round(150 / 300, 4)", precision=3)
    assert result["tool"] == "calc"
    assert result["result"] == 0.5

    result_min = calc_tool(expression="min(12, 5, 20)")
    assert result_min["result"] == 5


def test_calc_empty_or_whitespace_expression_returns_error_dict() -> None:
    for empty in ("", "   ", None):
        result = calc_tool(expression=empty)
        assert result["tool"] == "calc"
        assert "error" in result
        assert "message" in result


def test_calc_division_by_zero_returns_error_dict() -> None:
    result = calc_tool(expression="100 / 0")
    assert result["tool"] == "calc"
    assert result["error"] == "ZeroDivisionError"


def test_calc_rejects_unsafe_code_execution() -> None:
    result = calc_tool(expression="__import__('os').system('ls')")
    assert result["tool"] == "calc"
    assert "error" in result


# ---------------- text_stats ----------------

text_stats_tool = TOOL_FUNCTIONS.get("text_stats")


def test_text_stats_calculates_words_sentences_reading_time() -> None:
    sample = "Artificial intelligence is advancing rapidly. It changes research methodology completely."
    result = text_stats_tool(text=sample)
    assert result["tool"] == "text_stats"
    assert result["words"] == 10
    assert result["sentences"] == 2
    assert result["reading_time_minutes"] > 0
    assert "characters" in result


def test_text_stats_flesch_reading_ease_and_level() -> None:
    sample = "The quick brown fox jumps over the lazy dog. Cats like fish."
    result = text_stats_tool(text=sample)
    assert 0 <= result["flesch_reading_ease"] <= 100
    assert isinstance(result["reading_level"], str)


def test_text_stats_empty_string_returns_error_dict() -> None:
    for empty in ("", "    ", None):
        result = text_stats_tool(text=empty)
        assert result["tool"] == "text_stats"
        assert "error" in result


def test_text_stats_non_string_type_returns_error_dict() -> None:
    result = text_stats_tool(text=12345)
    assert result["tool"] == "text_stats"
    assert "error" in result


# ---------------- table_format ----------------

table_format_tool = TOOL_FUNCTIONS.get("table_format")


def test_table_format_generates_markdown_table_with_alignment() -> None:
    headers = ["Model", "Score"]
    rows = [["GPT-4o", 95], ["Claude-3.5", 94]]
    result = table_format_tool(headers=headers, rows=rows, alignment="center")
    assert result["tool"] == "table_format"
    assert result["rows_count"] == 2
    assert result["cols_count"] == 2
    assert "| Model | Score |" in result["markdown_table"]
    assert "| :---: | :---: |" in result["markdown_table"]
    assert "| GPT-4o | 95 |" in result["markdown_table"]


def test_table_format_pads_short_rows_and_truncates_long_rows() -> None:
    headers = ["A", "B", "C"]
    rows = [["1"], ["1", "2", "3", "4"]]
    result = table_format_tool(headers=headers, rows=rows, alignment="left")
    assert result["tool"] == "table_format"
    assert result["rows_count"] == 2
    assert "| :--- | :--- | :--- |" in result["markdown_table"]
    # Row 1 padded with empty strings
    assert "| 1 |  |  |" in result["markdown_table"]
    # Row 2 truncated to 3 columns
    assert "| 1 | 2 | 3 |" in result["markdown_table"]


def test_table_format_empty_headers_returns_error_dict() -> None:
    for empty in ([], None, ""):
        result = table_format_tool(headers=empty, rows=[["1", "2"]])
        assert result["tool"] == "table_format"
        assert "error" in result


def test_table_format_invalid_alignment_returns_error_dict() -> None:
    result = table_format_tool(headers=["Col1"], rows=[["Val1"]], alignment="diagonal")
    assert result["tool"] == "table_format"
    assert "error" in result

