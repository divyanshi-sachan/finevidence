# M2 data findings — executed FinQA audit

**Scope.** This is the measured record behind every M2 deliverable. Evidence comes from five executed notebooks:

| Notebook | M2 deliverable it supports |
| --- | --- |
| [02](../notebooks/02_finQA_eda.ipynb) | Acquisition, schema, EDA, data quality, split integrity |
| [03](../notebooks/03_finqa_preprocessing_analysis.ipynb) | Value formats, program grammar, evidence alignment, leakage-safe serialization |
| [04](../notebooks/04_data_preprocessing.ipynb) | Tested, reusable preprocessing components |
| [05](../notebooks/05_preprocessing_validation_and_answer_policy.ipynb) | Train-only validation and the canonical-answer policy |
| [12](../notebooks/12_milestone_audit_statistics_privacy.ipynb) | Statistical split comparison and privacy scan |

The data card ([dataset-card.md](dataset-card.md)) holds provenance, license and privacy decisions; [preprocessing-plan.md](preprocessing-plan.md) holds the field contract.

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

## Follow-up anomaly investigation

The follow-up audit was executed after the original EDA. Its full record-level output is saved in Notebook 02; the results below are measured from that output.

### Empty and optional fields

All 74 records with an empty display `answer` have a non-empty `exe_ans` and a non-empty `program`: 48 train, 12 dev, and 14 test. Examples include `ABMD/2012/page_75.pdf-1` (`answer=""`, `exe_ans="yes"`) and `PNC/2012/page_110.pdf-3` (`answer=""`, `exe_ans=22929.0`). They are therefore not structurally unusable examples. `answer` is an optional display field in this release for at least these records; preserve it while selecting any canonical answer representation explicitly.

`explanation` is empty in 5,276 train, 742 dev, and 970 test records, including otherwise complete records with answers, programs, and gold evidence. It is optional metadata in this release and must not be a required training target or preprocessing input.

`table_retrieved` and `text_retrieved` are also optional auxiliary retrieval fields, not a structural-context requirement: all corresponding records retain non-empty `table`, `pre_text`, and `post_text`. For example, `GIS/2008/page_83.pdf-1` has an empty `table_retrieved` but a complete table and program; `GIS/2019/page_45.pdf-1` has empty `text_retrieved` but complete raw text context. Do not exclude records on these fields alone.

### Evidence-index convention and anomaly

Verified examples show that `table_n` maps to the zero-based row index `n` in raw `table`; `text_n` maps to zero-based index `n` in `pre_text + post_text`. This is a field-level validation rule, not a rewrite rule. The suspicious train record is `RE/2010/page_120.pdf-2` (`RE/2010/page_120.pdf`), whose `gold_inds` includes `text_-1` with value `"this guidance had no impact on how the company records its derivatives. ."`. That sentence is the final `post_text` item, but `-1` is not a valid zero-based published index. Preserve the raw key and flag it as an annotation anomaly; do not silently convert it to `text_23`.

### Cross-split question wording

The overlap audit compared 21 train/dev record pairs from 16 question strings, 7 train/test pairs from 7 strings, and 2 dev/test pairs from 2 strings. Across all 30 pairs, filenames and complete raw context signatures (table plus pre/post text) were different. Eight train/dev, one train/test, and zero dev/test pairs happened to share the same executable answer. The overlap is therefore repeated question wording over different report contexts, not an exact duplicate example under the checked signature. Official splits remain unchanged; overlap statistics must remain an evaluation caveat rather than a deduplication instruction.

### Conservative program-parser experiment

`parse_finqa_program` was implemented as a non-executing validator: it uses balanced-parenthesis scanning and token checks, never `eval`. It accepts flat arithmetic/comparison calls whose arguments are literals, percentages, `const_n`, or intermediate `#n` references. Under that deliberately narrow grammar it validates 6,029/6,251 train, 840/883 dev, and 1,107/1,147 test programs. The remaining 222/43/40 programs are unsupported by the current grammar, not evidence of corrupt raw data.

Representative unsupported forms are table operations with textual labels, such as `table_average(2016, none)` in `ALLE/2016/page_29.pdf-1`; leading-decimal numerals, such as `divide(285.7, .76)` in `RSG/2008/page_114.pdf-1`; and signed constants, such as `multiply(3176, const_m1)` in `AWK/2014/page_122.pdf-3`. Notebook 03 should extend syntax support only after adding representative tests, while preserving the original `program` and `program_re` fields.

## Updated M2 findings and experiment contract

| Finding | Current conclusion | Action |
| --- | --- | --- |
| Empty `answer` fields | Some records have usable alternative labels in `exe_ans` and non-empty programs. | Validate and select targets per experiment; retain raw answer fields. |
| Empty explanations | Common in all three splits. | Treat as optional unless a specific task requires explanation supervision. |
| Repeated questions | Checked pairs have no matching filenames or full raw contexts. | Preserve official splits and retain overlap diagnostics. |
| Unsupported programs | The current conservative parser has intentional grammar limitations. | Expand syntax only from observed examples, with parser tests before use. |
| `text_-1` reference | Anomaly under the verified zero-based context-index convention. | Preserve and flag it; do not rewrite it without source-backed justification. |
| Numerical reasoning | Programs use literals, constants, intermediate references, and unit-sensitive values. | Build parsing and calculation tests before any numerical-reasoning experiment. |

### Experiment-input boundary

For answer-prediction experiments, the permissible model input is the question plus financial context (`table`, `pre_text`, and `post_text`, or a documented derived representation). Do **not** include `program`, `program_re`, `exe_ans`, `answer`, `gold_inds`, `steps`, `ann_table_rows`, `ann_text_rows`, or other answer/evidence annotations as input features. They are supervision, analysis, or evaluation data depending on the experiment. This rule applies to baselines, retrieval, and numerical-reasoning experiments unless a future experiment explicitly changes the prediction task and documents that change.

## Decision recorded after the EDA (2026-10-20)

Proceed to split-preserving, reversible preprocessing (done in Notebooks 03–04) before any model training. The detailed plan is in [preprocessing-plan.md](preprocessing-plan.md); its entry requirements, the evidence-key validator and the non-executing program parser, are covered by tests.

## Preprocessing-focused investigation

**Execution evidence:** [notebooks/03_finqa_preprocessing_analysis.ipynb](../notebooks/03_finqa_preprocessing_analysis.ipynb) was executed on 2026-10-20 against the same pinned public files. It intentionally does not repeat generic question or missing-value EDA.

### Financial value surface forms

The notebook searches table cells and source text separately, preserving the original strings. It found accounting-parentheses matches in 14,348 train, 1,848 dev, and 2,641 test source strings; currency in 55,576 / 8,105 / 9,945; percentages in 13,479 / 1,815 / 2,295; decimals in 43,976 / 6,658 / 8,556; scale words in 31,310 / 4,478 / 5,183; years in 84,577 / 12,316 / 15,639; month-name dates in 35,397 / 5,157 / 6,881; and exact unavailable markers in 3,701 / 399 / 699. The comma-number pattern found zero matches: this pinned surface form is often space-tokenized (for example, `$ 6427`) rather than comma-grouped. These are string-match counts, not counts of independently meaningful financial values.

Policy: keep raw values untouched and produce only reversible numeric candidates with their source location, sign style, currency symbol, percent marker, and nearby table/text context. A date, scale word, dash, or parenthesized token alone is insufficient to infer a scalar or unit.

### Program grammar and evidence alignment

The non-executing parser accepted 6,029/6,251 train programs, 840/883 dev programs, and 1,107/1,147 test programs. Its 305 out-of-current-grammar cases comprise 270 textual table arguments, 21 signed named constants, and 14 leading-decimal literals. The most frequent observed operation strings are `divide` (5,901), `subtract` (3,676), `add` (1,952), and `multiply` (759). These counts describe the pinned files; parser failures are not treated as invalid labels.

Evidence alignment reproduced the zero-based convention: all 7,512 train, 1,071 dev, and 1,318 test table references map to raw table rows; all 4,206 in-range text references map exactly to a line in `pre_text + post_text`. There were no ambiguous in-range text mappings under literal equality. The only invalid reference remains `RE/2010/page_120.pdf-2`, `text_-1`; it is retained and flagged without repair.

### Serialization and artifact boundary

The notebook's structured payload and independent deterministic row serialization both passed full-data preservation checks for all splits. A one-row table was found during this check, so the serialization deliberately emits its raw first row as `header` rather than assuming it has an associated data row. This preserves the source even when a table's header/data interpretation is uncertain.

The historical repository update documents a table-to-text label-leakage bug; use its corrected results only as background, not as a validation of a new implementation. The notebook records the sizes and gold-key overlaps of `table_retrieved`, `text_retrieved`, `model_input`, and `tfidftopn`, but does not use them as inference input. Structural forbidden-field and sentinel tests demonstrate that the new serializers do not access annotation fields. Their limitation is important: they cannot prove that a naturally occurring answer string is absent from financial-report context, or establish provenance for existing derived artifacts.

## Reusable preprocessing implementation

**Execution evidence:** [notebooks/04_data_preprocessing.ipynb](../notebooks/04_data_preprocessing.ipynb) was executed on 2026-10-20 after the implementations below were covered by automated tests. It writes only the ignored aggregate summary `data/processed/m2_preprocessing_diagnostics.json`; it does not modify or copy raw records.

| Component | Implemented behavior | Measured result |
| --- | --- | --- |
| Financial-value candidates | `normalize_financial_value` retains the exact raw input and emits a status plus optional token/sign/currency/percent/scale fields. It does not convert values or infer units. | Across raw table cells: train 69,191 recognized, 14,016 date/year ambiguous, 152 scale-only ambiguous, 3,701 unavailable, and 60,001 unsupported; dev 10,059 / 1,977 / 21 / 399 / 8,439; test 13,634 / 2,590 / 16 / 699 / 11,146. Unsupported is a conservative unresolved state, not a rejected record. |
| Program parser | `parse_finqa_program` is non-executing and supports the observed arithmetic operations, table operations, leading decimals, `const_m1`, intermediate references, text labels with `none`, and observed numeric table-sum arguments. | 6,251/6,251 train, 883/883 dev, and 1,147/1,147 test program strings parse. This measures grammar coverage only; it does not validate annotation correctness or execute programs. |
| Input construction | `build_structured_input` uses an explicit raw-context allowlist. `serialize_table_for_retrieval` emits a header line and explicit row/header-cell associations from the raw table. | Unit tests verify forbidden annotation/artifact fields are absent structurally and a sentinel answer cannot enter the structured payload. These checks do not establish semantic leakage freedom in the underlying reports or unverified external artifacts. |
| Annotation diagnostics | `audit_record_annotations` range-checks evidence, reports parser status, and records empty display fields without deleting examples. | The official `text_-1` annotation remains the only invalid reference: train 1, dev 0, test 0. Empty answer/explanation counts remain diagnostics, not exclusion rules. |

The test suite contains 17 passing tests after this implementation. The final parser extension was motivated by two observed train programs, `HOLX/2005/page_27.pdf-1` and `HOLX/2005/page_27.pdf-2`, which use `table_sum(17695228, 963202)`; this is documented as observed syntax, not an arithmetic interpretation.

## Canonical-answer policy (Notebook 05)

Notebook 05 fixed the display-answer comparison rules on train before any dev evaluation: empty display answers are reported separately, numeric answers must match their percent marker within a 1e-4 tolerance, and text is compared after normalization. Notebook 09 later showed that this comparator rejects most correct values, because display answers are rounded and percentages are scaled by 100. The official execution accuracy therefore became the primary metric; the display comparator remains secondary. Both are specified in [evaluation-plan.md](evaluation-plan.md).

## Statistical split comparison and privacy scan (Notebook 12)

- **Input side, all splits.** KS statistics are at most 0.077 for question length, table size, text length, numeric-cell share and year mentions, and the medians are identical or within one unit. The small detectable shifts (train vs dev in sentences per report, D = 0.075; train vs test in table rows, D = 0.077) are consistent with report-level splits.
- **Label side, train vs dev only.** Answer type, program length, operation family and gold-fact count show no significant difference (smallest p = 0.074; Cramér's V ≤ 0.035). No new test-label statistic was computed.
- **Privacy.** No SSN-like strings. One corporate email address, a few corporate phone numbers, and two report pages naming executives in public disclosures. Handling decisions are in the data card.

## M2 completion

All M2 deliverables now have executed evidence. They are:
- a verified data card with source, schema, splits, license, provenance and privacy;
- EDA with real examples, distributions, missingness and quality issues;
- reproducible, tested preprocessing with before/after examples;
- a statistical split comparison;
- a privacy assessment with handling and retention decisions.

The M2 exit condition (clean, documented splits; leakage checks and privacy recorded; no test labels used for tuning) is met. [milestone-status.md](milestone-status.md) maps each deliverable to its evidence.
