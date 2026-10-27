# FinQA dataset card

## Source and access

**Provenance (verified, FinQA paper §4.1–4.4):** FinQA questions were written by eleven US-based finance experts (CPAs, MBAs and similar) over pages from publicly available earnings reports of S&P 500 companies, 1999–2019, as collected in the FinTabNet dataset. The paper reports 8,281 examples over 2,789 report pages, split 6,251 / 883 / 1,147 (75% / 10% / 15%), and states that the three splits share no input reports.

The public splits were downloaded on 2026-10-20 from the official [FinQA repository](https://github.com/czyssrs/FinQA), pinned to commit `0f16e2867befa6840783e58be38c9efb9229d742`. The acquisition workflow lives in [Notebook 02](../notebooks/02_finQA_eda.ipynb): it uses commit-pinned raw GitHub URLs, refuses to overwrite existing files, parses JSON before the final move, and reports SHA-256 checksums. For non-notebook runtimes such as Colab or Kaggle, `python -m finevidence.data.acquisition` applies the same rules, verifies the SHA-256 values below, and fetches only train and dev unless `--include-test` is passed.

| Split | Source file | Records | Bytes | SHA-256 |
| --- | --- | ---: | ---: | --- |
| Train | `dataset/train.json` | 6,251 | 78,216,616 | `49f237eb9779b569473b26b08048867d04635a7cc39ad6a7a5664c55bb428db6` |
| Dev | `dataset/dev.json` | 883 | 10,954,658 | `a847fb7e0d61a3125a1e2909852df6b89f1ee64d2c5ff1bf689e332214deee51` |
| Test | `dataset/test.json` | 1,147 | 14,395,143 | `831dbfb2e785dbc227f895ce3f24046433467aec67b09db2bd6ac7692a8a30dc` |

Raw data remains ignored by Git and unchanged after download. `private_test.json` was not downloaded.

## Observed schema

All three public files parse as JSON lists of object records. Each split has the same 11 top-level fields:

`filename`, `id`, `pre_text`, `post_text`, `table`, `table_ori`, `table_retrieved`, `table_retrieved_all`, `text_retrieved`, `text_retrieved_all`, and `qa`.

Every `qa` object has the same 12 observed fields:

`ann_table_rows`, `ann_text_rows`, `answer`, `exe_ans`, `explanation`, `gold_inds`, `model_input`, `program`, `program_re`, `question`, `steps`, and `tfidftopn`.

`id` and `filename` are strings; `pre_text`, `post_text`, and table-related fields are lists; `qa` is a dictionary. Within `qa`, `answer`, `explanation`, `program`, `program_re`, and `question` are strings; `exe_ans` is observed as either a float or string; `gold_inds` and `tfidftopn` are dictionaries; the remaining observed annotation fields are lists. No top-level or `qa` fields were absent from any record in the public splits.

## Evidence and reasoning annotations

All 8,281 records contain a non-empty string `program` and dictionary `gold_inds`. Program strings use observed operation forms including `divide`, `subtract`, `add`, `multiply`, `greater`, `table_average`, `table_max`, `table_sum`, `table_min`, and `exp`; this is an observation of the release, not a complete grammar specification.

Gold evidence keys use `table_n` and `text_n` forms. Every observed `table_n` reference was in range for its table. Of 4,207 observed `text_n` references, 4,206 were in range for the concatenated `pre_text + post_text` context. The remaining train annotation is `RE/2010/page_120.pdf-2` with key `text_-1`; it must be retained and flagged rather than silently changed or dropped.

## Data quality and split integrity

The executed audit found no empty IDs, duplicate IDs within a split, empty questions, empty pre/post text lists, empty tables, or irregular table row widths. Exact question-string overlap was observed across split pairs: 16 train/dev, 7 train/test, and 2 dev/test; ID overlap was zero for all pairs. This is a diagnostic finding, not proof of leakage and not a reason to alter official splits.

Some fields are incompletely populated: `answer` is empty for 48 train, 12 dev, and 14 test records, while `exe_ans` remains present; `explanation` is empty for 5,276 train, 742 dev, and 970 test records. These fields need explicit handling rules in preprocessing rather than record deletion. See [m2-data-findings.md](m2-data-findings.md) for the full measured report.

## Licensing and permitted use

- **Verified source facts (2026-10-22):** at the pinned commit, the FinQA repository's `LICENSE` file is the MIT License (copyright 2021 Zhiyu Chen). The FinQA paper (§8) states that the underlying FinTabNet data is available under the CDLA-Permissive license, which permits creating and publishing additional annotations.
- **Project decision:** using the public splits for this non-commercial research project is within these terms. FinEvidence still does not redistribute the data: raw files and derived artifacts stay in ignored directories, and the repository contains only code, configuration and aggregate results. If the repository, a model or the demo is shared beyond the project, keep the MIT notice and the CDLA attribution with any data-derived artifact.
- **Limitation:** this is a record of the published terms, not legal advice. Commercial or production use would need its own review.

## Privacy assessment

**Measured in [Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb)**, which scans report text in all splits and reads no answers or programs:

| Pattern | Train | Dev | Test | Interpretation |
| --- | ---: | ---: | ---: | --- |
| SSN-like strings | 0 | 0 | 0 | None found. |
| Email addresses | 0 | 0 | 1 | A corporate shareholder-services address. |
| Phone-number pattern | 31 | 0 | 4 | 21 of 35 are space-separated table figures (false positives); the rest, in the examples inspected, are corporate shareholder-service numbers. |
| URLs | 114 | 32 | 12 | Web addresses printed in the reports. |
| Honorific + name | 14 | 0 | 0 | Two report pages name individuals (executives and related persons) in public compensation or related-party disclosures. |

**Assessment:** the corpus is public corporate disclosure. It contains limited personal data, namely named executives in public filings, and no records about private individuals were found. Regular expressions miss names without honorifics, so this is a screen, not a complete audit.

**Handling and retention:**
- Raw data and derived artifacts stay in Git-ignored `data/` and `models/` directories and are never committed.
- The data is not used to profile or analyse individuals.
- The prototype shows report text only as evidence for the question being answered.
- Local copies are kept for the duration of the project and can be deleted and re-downloaded from the pinned commit (`python -m finevidence.data.acquisition`).

## Use restrictions

The prototype must not provide financial advice or investment recommendations. The paper's own guidance is that such systems augment human decision-making in financial analysis and do not replace human experts (§8).

## Leakage prevention

Preserve official train/dev/test assignments. Use train data to fit transformations, dev data for model/preprocessing decisions, and test data only for final reporting. Do not use test answers, programs, or gold evidence for training or selection. Keep split-overlap diagnostics in the experiment record and do not silently deduplicate benchmark records.

The executed preprocessing analysis defined two safe representations: a structured payload containing only `id`, `question`, `table`, `pre_text`, and `post_text`, and a deterministic table-row rendering built from the raw table. Across all 8,281 public records, the structured payload preserved the raw table exactly and the rendering contained every non-empty raw table cell and header. This is a structural preservation check, not proof that a rendering retains every financial meaning.

The official repository records a 2022 repair to its earlier `table_row_to_text` function: the original function leaked label information and overstated retriever results. FinEvidence must not reuse derived fields (`table_retrieved`, `text_retrieved`, `model_input`, or `tfidftopn`) as model inputs until their provenance is independently documented. The local analysis observed `model_input` key overlap with `gold_inds`; it is therefore explicitly excluded from answer-prediction inputs, rather than treated as neutral context.

## Split comparability

[Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb) tests input-side distributions for all splits and label-side distributions for train vs dev only (test labels are not analysed). Every KS statistic is at most 0.077 and every Cramér's V at most 0.035; no train–dev label difference is significant at 0.05. The splits are comparable, and the small input shifts fit the paper's report-level split.

## Limitations and unresolved questions

- **Resolved since M2 began:** source provenance, license terms, and the official evaluation convention (execution accuracy against `exe_ans`, verified against the pinned `evaluate.py`; see [evaluation-plan.md](evaluation-plan.md)).
- **Still open:** the exact provenance of the derived fields `table_retrieved`, `text_retrieved`, `model_input` and `tfidftopn`. They stay excluded from inputs.
- **Generalization:** financial language, units, reporting-period ambiguity and table extraction format may limit transfer beyond this benchmark's report pages.
