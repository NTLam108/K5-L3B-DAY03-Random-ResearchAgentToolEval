---
name: text_stats
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [text]
outputs: [tool, words, characters, characters_no_spaces, sentences, reading_time_minutes, flesch_reading_ease, reading_level]
side_effect: false
---
# text_stats

Analyzes article content, paper abstracts, or scraped web text and calculates length and readability statistics. Runs 100% locally with zero external network or API keys.

## Features & Capabilities

- Calculates total word count, raw characters, and characters excluding whitespace.
- Detects sentence count and estimates reading time in minutes (based on 200 words per minute).
- Computes standard Flesch Reading Ease score (0 to 100) and maps to academic reading level (e.g. Standard, Difficult, Graduate).
- Handles bad or empty inputs gracefully by returning a structured error dictionary (`{"tool": "text_stats", "error": ..., "message": ...}`) without raising exceptions.

## Usage Guidelines

- **When to use**: When evaluating the length, complexity, reading time, or readability metrics of a paper, article, or draft.
- **When NOT to use**: Do not use for sentiment analysis, language translation, or factual verification.
