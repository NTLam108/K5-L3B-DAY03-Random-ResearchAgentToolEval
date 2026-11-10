from __future__ import annotations

import re
from typing import Any

from tools._shared import err


def _count_syllables(word: str) -> int:
    """Heuristic syllable counter for English and romanized text."""
    w = word.lower().strip(".:;?!,'\"-()[]{}")
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    # Count vowel groups
    vowels = "aeiouy"
    count = len(re.findall(r"[aeiouy]+", w))
    # Discount silent trailing 'e'
    if w.endswith("e") and not w.endswith("le") and len(w) > 2 and w[-2] not in vowels:
        count = max(1, count - 1)
    return max(1, count)


def analyze_text_stats(text: str = "") -> dict[str, Any]:
    """Analyzes text content and returns length, readability, and reading time metrics."""
    if not isinstance(text, str) or not text.strip():
        return {
            "tool": "text_stats",
            "error": "ValueError",
            "message": "text must be a non-empty string",
        }
    try:
        raw = text.strip()
        words = re.findall(r"\b\w+\b", raw)
        word_count = len(words)
        if word_count == 0:
            return {
                "tool": "text_stats",
                "error": "ValueError",
                "message": "text must contain at least one word",
            }

        char_count = len(raw)
        char_no_spaces = len(raw.replace(" ", "").replace("\n", "").replace("\t", ""))

        # Sentences split by sentence terminal punctuations
        sentences = [s for s in re.split(r"[.!?]+", raw) if s.strip()]
        sentence_count = max(1, len(sentences))

        # Reading time estimate (200 words per minute standard reading speed)
        reading_time_mins = round(max(0.1, word_count / 200.0), 2)

        # Flesch Reading Ease score
        syllables = sum(_count_syllables(w) for w in words)
        flesch_score = 206.835 - (1.015 * (word_count / sentence_count)) - (84.6 * (syllables / word_count))
        flesch_clamped = round(max(0.0, min(100.0, flesch_score)), 1)

        if flesch_clamped >= 90:
            level = "Very Easy (5th grade)"
        elif flesch_clamped >= 80:
            level = "Easy (6th grade)"
        elif flesch_clamped >= 70:
            level = "Fairly Easy (7th grade)"
        elif flesch_clamped >= 60:
            level = "Standard (8th-9th grade)"
        elif flesch_clamped >= 50:
            level = "Fairly Difficult (10th-12th grade)"
        elif flesch_clamped >= 30:
            level = "Difficult (College)"
        else:
            level = "Very Difficult (Graduate)"

        return {
            "tool": "text_stats",
            "words": word_count,
            "characters": char_count,
            "characters_no_spaces": char_no_spaces,
            "sentences": sentence_count,
            "reading_time_minutes": reading_time_mins,
            "flesch_reading_ease": flesch_clamped,
            "reading_level": level,
        }
    except Exception as exc:
        return err("text_stats", exc)
