"""Validation for FinQA evidence keys and non-executing reasoning programs."""

from __future__ import annotations

import re
from dataclasses import dataclass

_CALL_PATTERN = re.compile(r"^(?P<operation>[a-z_]+)\((?P<arguments>.*)\)$")
_NUMERIC_TOKEN_PATTERN = re.compile(r"-?(?:\d+(?:\.\d+)?|\.\d+)%?$")
_CONSTANT_PATTERN = re.compile(r"const_(?:m)?\d+$")
_REFERENCE_PATTERN = re.compile(r"#\d+$")
_EVIDENCE_PATTERN = re.compile(r"^(?P<source>text|table)_(?P<index>-?\d+)$")
_ARITHMETIC_OPERATIONS = frozenset({"add", "subtract", "multiply", "divide", "exp", "greater"})
_TABLE_OPERATIONS = frozenset({"table_average", "table_max", "table_min", "table_sum"})
SUPPORTED_OPERATIONS = _ARITHMETIC_OPERATIONS | _TABLE_OPERATIONS


@dataclass(frozen=True)
class EvidenceReference:
    """A parsed raw FinQA evidence key and its validity against local context."""

    raw_key: str
    source: str | None
    index: int | None
    is_valid: bool
    reason: str | None = None


@dataclass(frozen=True)
class ProgramStep:
    """One parsed program call; this object intentionally has no execution behavior."""

    operation: str
    arguments: tuple[str, ...]
    argument_kinds: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProgramParseResult:
    """A conservative parse result for a FinQA program string."""

    steps: tuple[ProgramStep, ...]
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


def validate_evidence_key(raw_key: str, *, text_count: int, table_count: int) -> EvidenceReference:
    """Validate a `text_n` or `table_n` key without changing its raw form."""
    match = _EVIDENCE_PATTERN.fullmatch(raw_key)
    if match is None:
        return EvidenceReference(raw_key, None, None, False, "unsupported key format")

    source = match["source"]
    index = int(match["index"])
    upper_bound = text_count if source == "text" else table_count
    if not 0 <= index < upper_bound:
        return EvidenceReference(raw_key, source, index, False, "index outside source bounds")
    return EvidenceReference(raw_key, source, index, True)


def _split_top_level_calls(program: str) -> tuple[list[str], str | None]:
    """Split comma-separated calls while respecting parentheses; never execute text."""
    parts: list[str] = []
    depth = 0
    start = 0
    for position, character in enumerate(program):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                return [], "unbalanced closing parenthesis"
        elif character == "," and depth == 0:
            parts.append(program[start:position].strip())
            start = position + 1
    if depth != 0:
        return [], "unbalanced parentheses"
    parts.append(program[start:].strip())
    return parts, None


def parse_finqa_program(program: str) -> ProgramParseResult:
    """Parse observed FinQA calls without eval, exec, or program execution.

    The supported grammar is deliberately limited to operations observed in the
    pinned public FinQA release. Table operations have two arguments: usually
    an uninterpreted row/column label and ``none``, with observed numeric-pair
    table sums also accepted. Arithmetic operations have two numeric literals,
    named constants, or intermediate references.
    """
    if not isinstance(program, str) or not program.strip():
        return ProgramParseResult((), "program must be a non-empty string")

    call_texts, split_error = _split_top_level_calls(program)
    if split_error is not None:
        return ProgramParseResult((), split_error)

    steps: list[ProgramStep] = []
    for call_text in call_texts:
        match = _CALL_PATTERN.fullmatch(call_text)
        if match is None:
            return ProgramParseResult((), f"invalid call syntax: {call_text!r}")
        operation = match["operation"]
        if operation not in SUPPORTED_OPERATIONS:
            return ProgramParseResult((), f"unsupported operation: {operation!r}")

        arguments = tuple(argument.strip() for argument in match["arguments"].split(","))
        if len(arguments) != 2 or any(not argument for argument in arguments):
            return ProgramParseResult((), f"expected two non-empty arguments in: {call_text!r}")

        if operation in _TABLE_OPERATIONS:
            label, none_argument = arguments
            if none_argument == "none":
                steps.append(ProgramStep(operation, arguments, ("table_label", "none")))
                continue
            argument_kinds = tuple(_argument_kind(argument) for argument in arguments)
            if any(kind == "unsupported" for kind in argument_kinds):
                return ProgramParseResult((), f"unsupported table arguments in: {call_text!r}")
            steps.append(ProgramStep(operation, arguments, argument_kinds))
            continue

        argument_kinds = tuple(_argument_kind(argument) for argument in arguments)
        if any(kind == "unsupported" for kind in argument_kinds):
            return ProgramParseResult((), f"unsupported arithmetic argument in: {call_text!r}")
        steps.append(ProgramStep(operation, arguments, argument_kinds))
    return ProgramParseResult(tuple(steps))


def _argument_kind(argument: str) -> str:
    """Classify a parsed token without converting it to a value."""
    if _NUMERIC_TOKEN_PATTERN.fullmatch(argument):
        return "numeric_literal"
    if _CONSTANT_PATTERN.fullmatch(argument):
        return "named_constant"
    if _REFERENCE_PATTERN.fullmatch(argument):
        return "intermediate_reference"
    return "unsupported"
