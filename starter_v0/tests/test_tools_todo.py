"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

def test_my_new_tool_happy_path() -> None:
    pytest.skip(TODO)


def test_my_new_tool_bad_input_from_model() -> None:
    pytest.skip(TODO)


def test_my_new_tool_failure_returns_error_dict() -> None:
    pytest.skip(TODO)


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
