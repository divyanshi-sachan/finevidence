# Evidence-based preprocessing plan

This plan follows the executed M2 audit. The reusable components are implemented and exercised in [Notebook 04](../notebooks/04_data_preprocessing.ipynb); they do not modify files under `data/raw/`.

## Principles

- Preserve the official split assignments and original records.
- Store derived outputs separately under ignored `data/processed/` or `data/interim/` paths with source revision and transformation metadata.
- Keep raw text, table cells, answer fields, programs, and evidence identifiers alongside any normalized representation.
- Fit learned vocabulary, statistics, indexes, or models on training data only. Use dev for decisions and reserve test annotations for final evaluation.
- For answer-prediction work, construct inputs only from the question and financial context. Keep `answer`, `exe_ans`, programs, and gold evidence outside model features.

## Field contract by experiment role

| Role | Required fields | Optional fields | Must not be used as answer-prediction input |
| --- | --- | --- | --- |
| Raw context loading | `id`, `filename`, `question`, `table`, `pre_text`, `post_text` | retrieved-context fields | All answer and annotation fields |
| Answer supervision | `answer` and/or `exe_ans`, selected by a documented task-specific policy | `explanation` | `program`, gold evidence, and annotation fields |
| Evidence evaluation | `gold_inds`, raw context, stable ID | row annotations | Answer labels, programs, and evidence annotations as retrieval features |
| Program analysis | `program`, `program_re`, `steps` | `explanation` | Program-derived information as answer-prediction features |

The raw record remains the source of truth. Derived fields must retain the record ID, split, source revision, raw value, transformation outcome, and any validation flag.

## Implemented M2 components

| Audit evidence | Preprocessing decision | Executed validation |
| --- | --- | --- |
| Common 11-field record and 12-field `qa` schema | Use explicit field checks in reusable input and annotation helpers. | Invalid structure raises an error; no record is dropped by the helpers. |
| Empty `answer` values while `exe_ans` exists | Keep both values; no canonical-answer policy has been chosen. | Diagnostics retain and count empty display answers. |
| 1.65–1.83% empty table cells and mixed numeric surface | Preserve raw cells and emit reversible candidate fields only for isolated recognizable strings. | Unit and notebook cases cover currency, leading decimals, parentheses, blanks, years, and unavailable markers. |
| `text_n` and `table_n` evidence references plus one `text_-1` anomaly | Range-check raw keys without rewrite. | The anomaly remains flagged in the aggregate diagnostics. |
| Non-empty program strings with observed operation patterns | Parse observed syntax without program execution; retain original program fields. | The pinned public splits achieve grammar coverage; coverage is explicitly separate from validity. |
| Exact questions repeat across splits | Keep official split labels and log overlap diagnostics. | No component merges, deduplicates, or reassigns records. |
| Predominantly empty `explanation` | Treat it as optional metadata rather than required model input or target. | Diagnostics retain and count empty explanations. |

## Acceptance criteria for M2 completion

| Criterion | Status and evidence |
| --- | --- |
| Actual examples, validation counts and tests for reusable logic | Met: Notebook 04, plus `tests/test_package.py` |
| Task-specific canonical-answer policy documented | Met: display-answer policy in Notebook 05; official execution accuracy adopted in Notebook 09 ([evaluation-plan.md](evaluation-plan.md)) |
| Split provenance retained | Met: pinned commit and SHA-256 checksums, verified at every load by `finevidence.data.acquisition` |
| Known anomalies recorded | Met: `text_-1` reference, empty display answers, derived-field provenance ([m2-data-findings.md](m2-data-findings.md)) |
| Preprocessing suitable for a simple baseline | Met: Notebooks 06–08 ran on it; Notebooks 10–11 use the same allowlisted inputs |
