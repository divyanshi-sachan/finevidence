"""Program accuracy: symbolic equivalence under the official FinQA convention.

The official ``equal_program`` (``code/evaluate/evaluate.py`` at the pinned commit) maps
each distinct literal/constant token of the *gold* program, and each whole table step, to
a symbol. A prediction that uses any token outside that map is wrong. Otherwise both
programs are expanded into expressions and compared after ``sympy.simplify``. Here the
expressions are built from sympy objects directly; program text is never ``sympify``-ed.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy

from finevidence.data.annotations import ProgramStep, parse_finqa_program


@dataclass(frozen=True)
class ProgramComparison:
    """Whether a predicted program is symbolically equivalent to the gold program."""

    equivalent: bool
    reason: str


def _step_token(step: ProgramStep) -> str:
    return f"{step.operation}({', '.join(step.arguments)})"


def _symbol_map(gold_steps: tuple[ProgramStep, ...]) -> dict[str, sympy.Symbol]:
    tokens: list[str] = []
    for step in gold_steps:
        if step.operation.startswith("table_"):
            tokens.append(_step_token(step))
        else:
            tokens.extend(argument for argument in step.arguments if not argument.startswith("#"))
    symbols: dict[str, sympy.Symbol] = {}
    for token in tokens:
        symbols.setdefault(token, sympy.Symbol(f"a{len(symbols)}"))
    return symbols


def _expression(
    steps: tuple[ProgramStep, ...], symbols: dict[str, sympy.Symbol]
) -> sympy.Basic | str:
    """Expand the final step into an expression, or return a reason it cannot be built."""
    built: list[sympy.Basic] = []
    for index, step in enumerate(steps):
        if step.operation.startswith("table_"):
            token = _step_token(step)
            if token not in symbols:
                return f"table step not in gold program: {token!r}"
            built.append(symbols[token])
            continue
        operands = []
        for argument in step.arguments:
            if argument.startswith("#"):
                reference = int(argument[1:])
                if reference >= index:
                    return f"forward or self reference: {argument}"
                operands.append(built[reference])
            elif argument in symbols:
                operands.append(symbols[argument])
            else:
                return f"argument not in gold program: {argument!r}"
        left, right = operands
        try:
            if step.operation == "add":
                built.append(left + right)
            elif step.operation == "subtract":
                built.append(left - right)
            elif step.operation == "multiply":
                built.append(left * right)
            elif step.operation == "divide":
                built.append(left / right)
            elif step.operation == "exp":
                built.append(left**right)
            elif step.operation == "greater":
                built.append(sympy.StrictGreaterThan(left, right))
        except TypeError as error:
            return f"cannot build expression: {error}"
    return built[-1]


def compare_programs(predicted: str | None, gold: str) -> ProgramComparison:
    """Compare a predicted program string with the gold program string."""
    gold_parse = parse_finqa_program(gold)
    if not gold_parse.is_valid:
        raise ValueError(f"gold program does not parse: {gold_parse.error}")
    if predicted is None:
        return ProgramComparison(False, "prediction is unavailable")
    predicted_parse = parse_finqa_program(predicted)
    if not predicted_parse.is_valid:
        return ProgramComparison(False, f"prediction does not parse: {predicted_parse.error}")

    symbols = _symbol_map(gold_parse.steps)
    gold_expression = _expression(gold_parse.steps, symbols)
    if isinstance(gold_expression, str):
        raise ValueError(f"gold program cannot be expanded: {gold_expression}")
    predicted_expression = _expression(predicted_parse.steps, symbols)
    if isinstance(predicted_expression, str):
        return ProgramComparison(False, predicted_expression)

    if sympy.simplify(gold_expression) == sympy.simplify(predicted_expression):
        return ProgramComparison(True, "symbolically equivalent")
    return ProgramComparison(False, "symbolic expressions differ")
