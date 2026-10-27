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

## FinQA paper and license review — 2026-10-22

Sources: FinQA paper full text, [arXiv HTML v3](https://arxiv.org/html/2109.00122v3) (accessed 2026-10-22); repository `LICENSE` at pinned commit `0f16e28`.

- **Verified source fact (§4.1).** The reports are "publicly available earnings reports of S&P 500 companies from 1999 to 2019, collected in the FinTabNet dataset."
- **Verified source fact (§4.2).** The questions were written by eleven US-based finance experts (CPAs, MBAs, etc.), recruited on UpWork.
- **Verified source fact (§4.4).** 8,281 examples split 6,251 / 883 / 1,147; "The three sets do not have overlapping input reports."
- **Verified source fact (§4.3).** Human expert execution / program accuracy is 91.16% / 87.49%; a general crowd reaches 50.68% / 48.17%.
- **Verified source fact (Table 5, labelled "Results on validation set").** FinQANet dev execution / program accuracy is 49.91 / 47.15 (BERT-base), 56.27 / 53.49 (RoBERTa-base) and 61.22 / 58.05 (RoBERTa-large).
- **Verified source fact (Table 2, main results).** FinQANet RoBERTa-large reaches 61.24 / 58.86 and RoBERTa-base 56.10 / 54.38; TF-IDF + single operation reaches 1.01 / 0.90. The text does not explicitly label Table 2 as the test set; reading it as test is an inference from its role as the main table.
- **Open question.** The introduction quotes 65.05% execution accuracy, which matches neither table; no explanation was found. FinEvidence does not use that figure.
- **Verified source fact (§8).** FinTabNet is available under CDLA-Permissive, which permits publishing additional annotations. The repository `LICENSE` is MIT.
- **Project comparison.** FinEvidence's dev result (59.2% / 55.6%, BERT-base retriever + T5-base generator) sits between FinQANet RoBERTa-base and RoBERTa-large on dev. This is context, not a controlled comparison: the implementations, the checkpoint-selection details and the encoders all differ.
