# FinQA dataset card

## Source and access

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

## Licensing, privacy, and use

The release source and files are verified, but a legal interpretation of the repository's license or permitted-use terms is not yet recorded. Verify those terms before external redistribution, deployment, or any use beyond the approved research scope. The data contains financial-report content; raw files, derived artifacts, and potentially sensitive material remain outside Git. The prototype must not provide financial advice or investment recommendations.

## Leakage prevention

Preserve official train/dev/test assignments. Use train data to fit transformations, dev data for model/preprocessing decisions, and test data only for final reporting. Do not use test answers, programs, or gold evidence for training or selection. Keep split-overlap diagnostics in the experiment record and do not silently deduplicate benchmark records.

The executed preprocessing analysis defined two safe representations: a structured payload containing only `id`, `question`, `table`, `pre_text`, and `post_text`, and a deterministic table-row rendering built from the raw table. Across all 8,281 public records, the structured payload preserved the raw table exactly and the rendering contained every non-empty raw table cell and header. This is a structural preservation check, not proof that a rendering retains every financial meaning.

The official repository records a 2022 repair to its earlier `table_row_to_text` function: the original function leaked label information and overstated retriever results. FinEvidence must not reuse derived fields (`table_retrieved`, `text_retrieved`, `model_input`, or `tfidftopn`) as model inputs until their provenance is independently documented. The local analysis observed `model_input` key overlap with `gold_inds`; it is therefore explicitly excluded from answer-prediction inputs, rather than treated as neutral context.

## Limitations and unresolved questions

Field semantics, annotation completeness, source-document provenance, official benchmark normalization, and permitted-use conditions still need deeper verification. Financial language, units, reporting-period ambiguity, and table extraction format can limit generalization beyond this benchmark.
