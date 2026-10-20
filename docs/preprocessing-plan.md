# Evidence-based preprocessing plan

This plan follows the executed M2 audit. It specifies transformations to implement and validate in Notebook 03; it does not modify files under `data/raw/`.

## Principles

- Preserve the official split assignments and original records.
- Store derived outputs separately under ignored `data/processed/` or `data/interim/` paths with source revision and transformation metadata.
- Keep raw text, table cells, answer fields, programs, and evidence identifiers alongside any normalized representation.
- Fit learned vocabulary, statistics, indexes, or models on training data only. Use dev for decisions and reserve test annotations for final evaluation.

## Planned work

| Audit evidence | Preprocessing decision | Validation in Notebook 03 |
| --- | --- | --- |
| Common 11-field record and 12-field `qa` schema | Add explicit per-record field/type validation with clear error reporting. | Compare valid/invalid counts before and after loading; never discard invalid records silently. |
| Empty `answer` values while `exe_ans` exists | Keep both values; create a typed canonical-answer view only after documenting observed answer cases. | Show before/after examples, count canonicalization outcomes, and retain a record-level reason. |
| 1.65–1.83% empty table cells and mixed numeric surface | Preserve raw cells; add reversible numeric candidates with token, sign, currency, percent, and unit/period context. | Test representative currency, percentage, negative, blank, and year-like cells without claiming semantic resolution. |
| `text_n` and `table_n` evidence references plus one `text_-1` anomaly | Normalize references to explicit source type and index, but retain original key/value. | Range-check every reference, flag invalid records, and prove that no annotation is silently changed or dropped. |
| Non-empty program strings with observed operation patterns | Tokenize conservatively from the observed grammar; retain raw `program` and `program_re`. | Report tokenization coverage and all unrecognized forms before any program execution. |
| Exact questions repeat across splits | Keep official split labels and log overlap diagnostics. | Assert no transformation merges or deduplicates across splits. |
| Predominantly empty `explanation` | Treat it as optional metadata rather than required model input or target. | Report availability by split. |

## Acceptance criteria for M2 completion

Notebook 03 should show actual before/after examples, validation counts, and tests for reusable logic. M2 is ready for M3 only when transformations are reproducible, raw data is unchanged, split provenance is retained, known anomalies are recorded, and the preprocessing outcome is suitable for a simple baseline.
