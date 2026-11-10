---
name: cite
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs: [title, authors, published, url, style]
outputs: [style, citation]
side_effect: false
---
# cite

Builds a citation string (`apa` or `bibtex`) from paper metadata already known, for
example an item returned by `papers` (`title`, `authors`, `published`, `url`).
Runs locally: no API key, no network.

## Rules implemented

- APA authors: `Surname, I.` separated by commas, with `&` before the last author
  (checked against several university APA guides). 1 to 20 authors; more than 20 returns an error.
- Year is the first 4 digits of `published`; otherwise `n.d.` (APA) or the `year` field is omitted (BibTeX).
- BibTeX: `@misc{<surname><year>, title, author joined by " and ", year, url}`.
- Invalid input (empty title, `authors` not a non-empty list, unknown `style`) returns an
  error dict (`{"tool": "cite", "error": ..., "message": ...}`) and never raises.

## Known limitations (simplified, not full APA/BibTeX)

- Name heuristic: the LAST word is treated as the surname. Wrong for surname-first names
  (e.g. many Vietnamese names) and multi-word surnames.
- Title capitalisation is kept as given; APA sentence case is NOT applied.
- For arXiv URLs the text `arXiv.` is added before the URL; this layout is a simplification
  and has not been verified against the official APA 7 rule for preprints.
- BibTeX layout follows common practice and was not checked against a formal specification.
