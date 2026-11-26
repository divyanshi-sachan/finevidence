"""Canonical number formatting for evidence text.

FinQA writes numbers without thousands separators (``$ 2457``), and generated programs copy numbers
from the evidence. A separator-formatted number (``2,457``) is copied as two program arguments, so
evidence from other sources must be brought to the FinQA convention before retrieval and generation.

Only formatting is changed, never a value: thousands separators in well-formed groups are removed,
and Unicode minus signs and non-breaking spaces become their ASCII forms. Parenthesised negatives
and scale words are left as FinQA writes them, because the models were trained on that convention.
"""

from __future__ import annotations

import re

_GROUPED = re.compile(r"(?<![\d,.])\d{1,3}(?:,\d{3})+(?![\d,])")
_CHARACTERS = str.maketrans({"−": "-", "–": "-", " ": " ", " ": " "})


def canonicalize_numbers(text: str) -> str:
    """Return ``text`` with numbers in the FinQA convention (``1,234.5`` -> ``1234.5``)."""
    text = text.translate(_CHARACTERS)
    return _GROUPED.sub(lambda match: match.group().replace(",", ""), text)
