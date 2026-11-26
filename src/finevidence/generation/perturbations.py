"""Label-preserving input perturbations for robustness checks (dev only).

Each perturbation rewrites a generator input so that the gold program and answer stay correct:

- ``reword``: fixed surface rewrites of the question (tense, synonyms, punctuation) that do not
  change what is asked.
- ``reverse_facts``: the retrieved facts in reverse order (position sensitivity).
- ``thousands_separators``: thousands separators added to fact numbers (``2457.5`` ->
  ``2,457.5``), so the values are unchanged but tokenize differently. FinQA writes numbers without
  separators; integers from 1900 to 2099 are left alone because they are usually years.
- ``foreign_fact``: one fact from a different record inserted first. It cannot be gold for this
  record, so the answer is unchanged; it tests distraction by plausible but irrelevant evidence.

Perturbations that change the answer (rescaling units, shifting periods) are excluded because they
would need new gold labels.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from dataclasses import replace

from finevidence.generation.inputs import GeneratorExample, format_generator_source

# Each group swaps in either direction; only the first matching rule of a group applies.
_REWRITE_GROUPS: tuple[tuple[tuple[re.Pattern[str], str], ...], ...] = (
    (
        (re.compile(r"^what was\b", re.IGNORECASE), "what is"),
        (re.compile(r"^what is\b", re.IGNORECASE), "what was"),
    ),
    (
        (re.compile(r"\bpercentage change\b", re.IGNORECASE), "percent change"),
        (re.compile(r"\bpercent change\b", re.IGNORECASE), "percentage change"),
    ),
    ((re.compile(r"\bthe total\b", re.IGNORECASE), "the overall"),),
    ((re.compile(r"\bin millions\b", re.IGNORECASE), "in millions of dollars"),),
)
_LONG_INTEGER = re.compile(r"(?<![\d.,])\d{4,}(?![\d,])")

PERTURBATIONS = ("reword", "reverse_facts", "thousands_separators", "foreign_fact")


def reword_question(question: str) -> str:
    """Apply the first matching rule of each rewrite group; toggle a trailing '?'."""
    text = question.strip()
    for group in _REWRITE_GROUPS:
        for pattern, replacement in group:
            if pattern.search(text):
                text = pattern.sub(replacement, text, count=1)
                break
    return text[:-1].rstrip() if text.endswith("?") else f"{text} ?"


def _separate(match: re.Match[str]) -> str:
    digits = match.group()
    if 1900 <= int(digits) <= 2099:
        return digits
    return f"{int(digits):,}"


def thousands_separators(text: str) -> str:
    """Write integer parts of 1,000 and above with separators; year-like integers are kept."""
    return _LONG_INTEGER.sub(_separate, text)


def _rebuild(example: GeneratorExample, question: str, facts: Sequence[str]) -> GeneratorExample:
    return replace(
        example, source=format_generator_source(question, facts), fact_texts=tuple(facts)
    )


def perturb_example(
    example: GeneratorExample, question: str, name: str, foreign_fact: str | None = None
) -> GeneratorExample:
    """Return ``example`` with perturbation ``name`` applied; ``question`` is its question text."""
    facts = list(example.fact_texts)
    rules: dict[str, Callable[[], GeneratorExample]] = {
        "reword": lambda: _rebuild(example, reword_question(question), facts),
        "reverse_facts": lambda: _rebuild(example, question, facts[::-1]),
        "thousands_separators": lambda: _rebuild(
            example, question, [thousands_separators(f) for f in facts]
        ),
        "foreign_fact": lambda: _rebuild(example, question, [foreign_fact or "", *facts]),
    }
    if name not in rules:
        raise ValueError(f"unknown perturbation {name!r}")
    if name == "foreign_fact" and not foreign_fact:
        raise ValueError("foreign_fact needs a fact from another record")
    return rules[name]()
