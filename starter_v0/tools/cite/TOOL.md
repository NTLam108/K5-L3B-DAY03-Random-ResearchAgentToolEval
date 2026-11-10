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

- APA authors: `Surname, I.` separated by commas, `&` before the last author for 2 to 20 authors.
- 21 or more authors: first 19, `...`, then the last author, no `&`.
- No author (`authors=[]` or omitted): the title moves to the author position.
- No usable year in `published`: `n.d.` (APA) or the `year` field is omitted (BibTeX).
- BibTeX `@misc`: authors as `Last, First` joined by ` and `; key = first surname (lowercase letters/digits) + year (or `nd`); no required fields.
- Invalid input (empty title, `authors` not a list, unknown `style`) returns an error dict
  (`{"tool": "cite", "error": ..., "message": ...}`) and never raises.

## Sources checked (university library guides; official apastyle.apa.org pages could NOT be opened)

- Authors, `&`, up to 20: https://owl.purdue.edu/owl/research_and_citation/apa_style/apa_formatting_and_style_guide/reference_list_author_authors.html
- 21+ authors (19 + ellipsis + last): https://libguides.wintec.ac.nz/APA7/multiauthors
- No author -> title in author position: https://library.carleton.ca/help/apa-citation-style/reference-list/reference-components
- Preprint layout (Author. (Year). *Title*. Repository. DOI/URL): https://library.rgu.ac.uk/apa-referencing/pre-print-post-print
- BibTeX `@misc`, names joined by `and`, citation key characters: https://www.bibtex.org/Format/ (community reference)

## Status of two points (NOT independently verified)

- Team member reported that the official APA 7 preprint examples do not require `arXiv:ID`
  or a `[Preprint]` label. The tool does not output either. Not confirmed by us because
  apastyle.apa.org was not reachable; other (non-official) sources disagree about `[Preprint]`.

## Known limitations (simplified, not full APA/BibTeX)

- Name heuristic: the LAST word is the surname. Wrong for surname-first names
  (e.g. many Vietnamese names) and multi-word surnames.
- Plain text only: APA italics for the title cannot be shown.
- Title capitalisation is kept as given; APA sentence case is NOT applied (proper nouns and
  acronyms cannot be detected reliably).
- For arXiv URLs the text `arXiv.` is added before the URL; other repositories get only the URL.
- BibTeX layout was checked against bibtex.org only, not a formal specification.
