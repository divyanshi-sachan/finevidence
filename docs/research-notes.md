# Research notes

Use this file for concise, sourced observations that materially influence the project. Distinguish verified facts, hypotheses, and open questions. Include a URL or citation for external claims and an access date for mutable sources.

## FinQA source review — 2026-10-20

- **Verified source fact.** The [FinQA paper](https://aclanthology.org/2021.emnlp-main.300/) presents financial question answering over tables and text with annotated numerical reasoning programs. This supports keeping table and narrative source segments distinct during M2 preprocessing.
- **Verified source fact.** The official [FinQA repository update](https://github.com/czyssrs/FinQA#updates) dated 2022-05-04 says an incorrect `table_row_to_text` function leaked label information and produced retriever results higher than actual. The repository also describes a later positive/negative formatting repair (2022-04-29). FinEvidence therefore uses an independent raw-table serialization and excludes publisher-derived retrieval and model-input artifacts until their provenance is tested.
- **Project decision.** The non-executing parser is an inspection tool, not an evaluator or calculator. Its grammar will expand only from observed forms with unit tests; it will never execute program strings with `eval`.
- **Open question.** The exact provenance of `table_retrieved`, `text_retrieved`, `model_input`, and `tfidftopn` in the pinned release remains unverified. Their observed overlap with gold evidence is sufficient reason to exclude them from inference inputs, but not enough to infer how every artifact was produced.

## Official FinQA evaluator and model settings — 2026-10-21

- **Verified source fact.** The pinned official evaluator ([`code/evaluate/evaluate.py`](https://github.com/czyssrs/FinQA/blob/0f16e2867befa6840783e58be38c9efb9229d742/code/evaluate/evaluate.py)) reports execution accuracy and program accuracy over all records. Execution accuracy rounds a numeric executed result to five decimals and requires exact equality with `exe_ans`. Program accuracy uses `sympy`-based symbolic equivalence.
- **Verified source fact.** The pinned [`code/retriever/config.py`](https://github.com/czyssrs/FinQA/blob/0f16e2867befa6840783e58be38c9efb9229d742/code/retriever/config.py) uses `bert-base-uncased`, `neg_rate = 3` random negatives, `topn = 5`, `max_seq_length = 512`, batch size 16 and learning rate 2e-5. The generator config trains from `*_retrieve.json` retriever outputs with `max_program_length = 30`. These are configuration files, not reproduced results.
- **Project decision.** FinEvidence reimplements the execution rules (`execute_program`) instead of running the official script, and adopts execution accuracy as its primary answer metric.
