# M2 data findings — executed FinQA audit

**Execution evidence:** [notebooks/02_finQA_eda.ipynb](../notebooks/02_finQA_eda.ipynb) was executed on 2026-10-20 against the commit-pinned public splits recorded in [dataset-card.md](dataset-card.md). Findings below are measured from that run.

## Dataset structure and size

| Split | Records | Question words: median / mean | Table rows: median / mean | Table columns: median / mean |
| --- | ---: | ---: | ---: | ---: |
| Train | 6,251 | 15 / 16.65 | 6 / 6.34 | 4 / 3.84 |
| Dev | 883 | 15 / 16.41 | 6 / 6.27 | 4 / 3.94 |
| Test | 1,147 | 16 / 16.72 | 6 / 6.55 | 4 / 3.92 |

Question lengths are broadly similar across splits. Train questions range from 5 to 62 words; dev from 5 to 43; test from 5 to 44. After an explicit small stop-word filter, frequent train tokens include `total`, `percentage`, `change`, `net`, `percent`, `millions`, `december`, and `average`. This is a descriptive lexical count, not a financial-concept classifier.

## Context, tables, and numeric-looking values

Every record has non-empty pre-text, post-text, and table lists. The audit found no irregular row widths. Empty cells occur in 2,697 of 147,061 train cells (1.83%), 345 of 20,895 dev cells (1.65%), and 479 of 28,085 test cells (1.71%).

The notebook's heuristic identified numeric-looking text in 74.78% of train cells, 75.82% of dev cells, and 75.69% of test cells. It also exposes percentage, currency, negative-marker, and year-like cell counts. This is deliberately not semantic value extraction: value meaning, units, and reporting periods remain contextual.

## Quality issues and interpretation

| Observation | Measured evidence | Impact | Proposed handling |
| --- | --- | --- |
| Missing structural fields | Zero missing top-level or `qa` fields across all public records. | A common loader contract is viable. | Validate field presence and type before downstream transformations. |
| Blank display answers | 48 train, 12 dev, 14 test `answer` values are empty; `exe_ans` is present. | Answer normalization cannot assume `answer` is populated. | Retain both fields and define an explicit canonical-answer policy from observed types. |
| Blank explanations | 84.40% train, 84.03% dev, 84.57% test `explanation` values are empty. | Explanations cannot be treated as universally available supervision. | Do not use `explanation` as a required preprocessing feature. |
| Auxiliary retrieval fields empty | `table_retrieved` is empty for 7.04%, 5.32%, 7.85%; `text_retrieved` for 9.92%, 11.44%, 9.68% of train/dev/test. | These auxiliary fields need missing-value treatment if used. | Do not rely on them as mandatory context; evaluate their role separately. |
| Evidence anomaly | One train `gold_inds` key is `text_-1`; all table keys and all other text keys are in range. | Direct positional mapping needs validation. | Preserve raw annotation; flag invalid indices instead of repairing or deleting them. |
| Exact question duplicates across splits | 16 train/dev, 7 train/test, 2 dev/test; zero shared IDs. | Potentially relevant to generalization interpretation. | Keep official splits; report overlap diagnostics and do not claim leakage from string overlap alone. |

## Programs and evidence

All programs are non-empty strings. Regex inspection found at least one operation in every program. The observed number of operations per program has median 1 and mean 1.54 for all three splits; maximum is 6 in train and 5 in dev/test. Arithmetic operations (`divide`, `subtract`, `add`, `multiply`) are most frequent, with a smaller observed set of comparisons and table aggregations.

Gold evidence includes both `table_n` and `text_n` references: 7,512 table and 3,180 text keys in train; 1,071 and 442 in dev; 1,318 and 585 in test. The position audit validates 9,901 of 9,901 table references and 4,206 of 4,207 text references. Any future evidence metric must preserve the raw identifier and treat the single invalid text reference as a documented annotation exception.

## Decision for the next milestone task

Proceed to `03_data_preprocessing.ipynb` with split-preserving, reversible preprocessing. Do not train a model yet. The detailed plan is in [preprocessing-plan.md](preprocessing-plan.md).
