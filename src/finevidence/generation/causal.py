"""Prompt and label construction for a decoder-only (causal LM) program generator.

The model sees the same ``question: ... facts: ...`` source as the T5 generator, followed by a
fixed instruction and the marker ``program:``. Only the program tokens and the end-of-sequence
token are trained; prompt tokens get the ignore label. These helpers work on token-id lists, so
they need no tokenizer or deep-learning library and are tested on their own.
"""

from __future__ import annotations

from collections.abc import Sequence

IGNORE_INDEX = -100
PROGRAM_MARKER = "\nprogram:"
INSTRUCTION = (
    "Write the FinQA program that answers the question from the facts. "
    "Use only numbers from the facts.\n"
)


def causal_prompt(source: str) -> str:
    """The full prompt text for one generator source; the program follows ``program:``."""
    return f"{INSTRUCTION}{source}{PROGRAM_MARKER}"


def build_causal_example(
    source_ids: Sequence[int],
    marker_ids: Sequence[int],
    target_ids: Sequence[int],
    eos_id: int,
    *,
    max_source_tokens: int,
) -> tuple[list[int], list[int]]:
    """Return ``(input_ids, labels)`` with the source cut from the end and the prompt masked.

    ``source_ids`` covers the instruction and source; it is truncated from the end, which drops
    the lowest-ranked facts first, as T5 truncation does. The program marker and target are kept.
    """
    if max_source_tokens < 1:
        raise ValueError("max_source_tokens must be positive")
    prompt = [*source_ids[:max_source_tokens], *marker_ids]
    answer = [*target_ids, eos_id]
    return [*prompt, *answer], [IGNORE_INDEX] * len(prompt) + answer


def extract_program(generated_text: str) -> str:
    """The program from decoded generated tokens: text up to the first line break, stripped."""
    return generated_text.strip().split("\n", 1)[0].strip()
