#!/usr/bin/env python3
"""bilingual_doc.py - the one rule for splitting a player-facing EN+FR document.

Why this exists
---------------
House rule is that player-facing text ships in English AND French. For a
downloadable markdown artifact that means one file with both halves in it, and
the moment there are two halves every gate that reads that file has to know
where one ends and the other begins:

  * tools/check_flash_instructions.py parses each half's esptool commands
    separately. Parsed as one document, the FR half's commands look like a
    second `--chip esp32` block and the gate errors out on its own document;
    worse, an FR-only offset typo would hide behind a correct EN one.
  * tools/check_fr_accents.py must scan the FR half ONLY. Run over the whole
    file it trips over English words that happen to be accent-stripped French
    ("cable", "controle", "interet"), which is a false red, and a gate that
    cries wolf gets switched off.

So the rule lives here once, and both gates plus the generator import it. It is
deliberately a rule about the TEXT, not a marker written by one tool and read by
another: any author can satisfy it by hand, and a document that does not satisfy
it fails loudly instead of being silently treated as English-only.

THE RULE
--------
The French half starts at the first markdown heading line whose text contains
the word "francais" spelled correctly, i.e. with its cedilla: "(francais)" with
a c-cedilla. Everything above that line is the English half, that line and
everything below it is the French half.

Exactly one such heading must exist. Zero means the document is monolingual (or
the FR heading lost its cedilla, which is the accent-stripping failure this
repo has shipped three times, and which therefore must be loud). Two or more
means the split is ambiguous and no gate should guess.
"""
from __future__ import annotations

import re

# A heading line carrying the word with its cedilla. Case-insensitive on the
# first letter only in practice, but the cedilla is NOT optional: that is the
# point. `Francais` with a plain c does not match and the document is then
# reported as having no FR half at all.
FR_HEADING = re.compile(r"^#{1,6}[ \t].*français.*$", re.M | re.I)


class BilingualError(ValueError):
    """The document does not satisfy THE RULE above."""


def find_fr_heading(text: str) -> list[str]:
    """Every heading line that opens a French half. Usually exactly one."""
    return FR_HEADING.findall(text)


def split_bilingual(text: str) -> tuple[str, str]:
    """(english_half, french_half). Raises BilingualError if the rule fails.

    The returned French half INCLUDES its own heading line, so a caller
    scanning it for accents sees the heading too.
    """
    matches = list(FR_HEADING.finditer(text))
    if not matches:
        raise BilingualError(
            "no French half: expected a markdown heading containing "
            "'français' (with its cedilla). A document with an EN half "
            "only is not shippable, and a heading spelled 'francais' is the "
            "accent strip this check exists to catch"
        )
    if len(matches) > 1:
        lines = ", ".join(repr(m.group(0).strip()) for m in matches)
        raise BilingualError(
            f"{len(matches)} headings open a French half ({lines}); the split "
            f"is ambiguous, keep exactly one"
        )
    cut = matches[0].start()
    en = text[:cut]
    fr = text[cut:]
    if not en.strip():
        raise BilingualError(
            "the French heading is the first thing in the document, so there "
            "is no English half above it"
        )
    if not fr.strip():
        raise BilingualError("the French half is empty")
    return en, fr
