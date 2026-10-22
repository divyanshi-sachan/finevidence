# Experiment log

## 2026-10-20 — lexical value-selection baseline, dev

- **Question:** Can a train-fitted lexical ranker select a display-answer candidate from raw report context?
- **Dataset:** pinned public FinQA files recorded in `docs/dataset-card.md`; train used for fitting, dev used once for evaluation, official test not loaded.
- **Configuration:** `configs/lexical_value_baseline.toml`; seed `42` is recorded although this deterministic TF–IDF run has no randomized training step.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/06_lexical_value_baseline.ipynb`
- **Code state:** run from an uncommitted working tree; that code state was first committed as `a6d6ac2`.
- **Metric:** display-answer accuracy under the documented comparator; denominator is 871 dev records with non-empty `answer`. The 12 dev records with empty display answers are retained and reported separately.
- **Observed result:** 3/871 correct (0.003444, 0.344%). By reference type: numeric 3/356 (0.008427, 0.843%); numeric percent 0/492; text 0/23.
- **Diagnostics:** among 868 incorrect eligible predictions, 567 candidate source keys matched a dev gold-evidence key and 301 did not. This is an evidence-alignment diagnostic only, not a causal error classification.
- **Artifact:** ignored `data/processed/lexical_value_baseline_dev_predictions.jsonl`.
- **Limitations:** candidate selection is lexical and extractive; it cannot calculate, normalize units, resolve periods, or prove evidence sufficiency. It is not a numerical-reasoning system. No test metrics were computed.
- **Decision:** retain this run as a transparent lower bound. Next, evaluate retrieval ranking separately before testing a constrained arithmetic candidate.

## 2026-10-20 — question-conditioned evidence/value selection, dev

- **Question:** Does retrieving rows/passages before ranking their raw value candidates improve the lexical baseline?
- **Dataset and split protocol:** pinned public FinQA train and dev files; vocabulary fitted on train raw questions and raw context only; evaluated once on dev. The official test split was not loaded.
- **Configuration:** configs/question_conditioned_value_selection.toml; fixed TF–IDF settings with top three evidence segments.
- **Command:** .venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/07_question_conditioned_evidence_value_selection.ipynb
- **Code state:** run from an uncommitted working tree; that code state was first committed as `a6d6ac2`.
- **Prediction boundary:** only ID, question, table, pre_text, and post_text enter candidate construction/ranking. Gold answers, executable answers, programs, gold evidence, and derived retrieval artifacts are accessed only after predictions for metrics/diagnostics.
- **Metric:** fixed display-answer comparator. Denominator 871 dev records with non-empty display answers; 12 empty display answers retained and reported separately.
- **Observed result:** 3/871 correct (0.003444, 0.344%), exactly equal to the lexical value-selection reference. By reference type: numeric 3/356 (0.843%); numeric percent 0/492; text 0/23. This run does not demonstrate improvement.
- **Post-prediction diagnostics:** at least one gold evidence key was among the three retrieved segments for 715/883 records. Among 880 incorrect or unavailable predictions, it was retrieved for 712. Gold annotations identify 467 records with multiple evidence sources, 360 with multi-step programs, and 35 with table operations. Question wording contains temporal cues in 517 records and unit/conversion cues in 398. These are scope diagnostics, not causal error labels.
- **Artifact:** ignored data/processed/question_conditioned_value_selection_dev_predictions.jsonl.
- **Limitations:** the pipeline is lexical and extractive. It cannot choose or execute arithmetic, reconcile multiple evidence sources, resolve reporting periods, or safely convert units. Gold evidence retrieval overlap does not show that the selected candidate was sufficient or that retrieval caused an error.
- **Decision:** do not spend the next experiment solely on lexical retrieval: gold evidence was frequently retrieved yet answers remained incorrect. Prioritize an explicitly tested numerical-reasoning component that operates on retrieved raw values, while retaining retrieval diagnostics separately.

## 2026-10-20 — conservative arithmetic reasoning, dev

- **Hypothesis:** explicit arithmetic over safely parsed, question-retrieved raw values can improve the extractive lexical reference.
- **Protocol:** train-only TF–IDF vocabulary fit over questions and raw context; one dev-only evaluation; official test split not loaded. Prediction uses only ID, question, table, pre_text, and post_text. Gold answers/programs/evidence are unavailable during prediction and are read after outputs only for evaluation and diagnostics.
- **Configuration:** configs/conservative_arithmetic.toml; top three retrieved evidence segments; fixed seed 42.
- **Metric:** fixed display-answer comparator. The denominator is 871 non-empty dev display answers; 12 empty references remain in the dataset and are counted separately.
- **Observed result:** 32/871 correct (0.036739, 3.674%), compared with 3/871 (0.344%) for the lexical reference. Numeric: 32/356 (8.989%); numeric percent: 0/492; text: 0/23.
- **Coverage:** 293/883 records produced an arithmetic result (33.18%); answered-case accuracy was 0.110345 (11.03%). Abstentions: 525 unsupported/ambiguous intents, 38 mismatched unit or period metadata, and 27 insufficient safely parsed operands.
- **Intent counts:** 130 additive, 121 subtractive, 106 divisive, 1 multiplicative, 5 comparison, and 520 ambiguous.
- **Post-hoc scope diagnostics:** 360 dev records have multi-step gold programs, 467 have multiple gold evidence sources, 517 have temporal cues, and 398 have unit/conversion cues. These are not prediction features or causal failure labels.
- **Artifact:** ignored data/processed/conservative_arithmetic_dev_predictions.jsonl.
- **Limitations:** only one operation over the first two metadata-compatible retrieved operands is attempted. The component does not execute published programs, convert percent/decimal/currency/scale values, resolve differing periods, or compose multiple operations. It therefore remains unsuitable for most percentage and text answers.
- **Decision:** the observed overall improvement supports continuing explicit numerical reasoning. The next experiment should improve grounded operand selection and period/unit alignment before adding multi-step arithmetic; pure lexical retrieval is not the primary bottleneck.

## 2026-10-21 — baseline-selection inspection and execution-accuracy re-scoring

- **Question:** Which FinQA structure should the M3 baseline exploit, and does the display-answer comparator measure what the official benchmark measures?
- **Dataset and split protocol:** pinned public FinQA train and dev files. Train annotations were inspected for design decisions. Dev was used only to validate the executor on gold programs and to re-score the fixed Notebook 06–08 dev prediction artifacts. The official test split was not loaded.
- **Configuration:** `configs/baseline_selection_inspection.toml`; seed 42; TF-IDF settings match the earlier runs, with `sublinear_tf=True`.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/09_baseline_selection_inspection.ipynb`
- **Code state:** run from an uncommitted working tree; that code state was first committed as `a6d6ac2`.
- **Observed results (train):** 5,730/6,251 programs have ≤2 steps, and the top 10 of 119 templates cover 86.8%. 14,190/14,210 numeric literals occur in the context. 5,398 records exceed 512 whitespace tokens. TF-IDF within-record recall@3 is 82.9% any-gold and 53.8% all-gold (28.5% all-gold for multi-fact records). The display comparator accepts the gold executed value for 2,203/6,083 numeric-`exe_ans` records, and for 0/3,480 percentage answers when given the raw ratio.
- **Executor validation:** `execute_program` on gold programs equals `exe_ans` for 6,251/6,251 train and 883/883 dev records.
- **Re-scored dev execution accuracy (denominator 883):** lexical value selection 5 (0.566%), question-conditioned selection 6 (0.680%), conservative arithmetic 35 (3.964%). The display-answer results in the entries above are unchanged.
- **Limitations:** literal-provenance matching ignores sign and uses six-decimal rounding. Context lengths are whitespace tokens, a lower bound on sub-word length. TF-IDF recall was measured in-sample on train, so it is a diagnostic only. Program accuracy is not implemented.
- **Decision:** adopt execution accuracy as the primary metric and build the FinQANet-style retriever + program-generator baseline described in `docs/finqanet-baseline-plan.md`.

## 2026-10-22 — Notebook 08 refactor reproduction check

- **Question:** Does moving segment construction and candidate parsing into `finevidence.retrieval` preserve the conservative-arithmetic results?
- **Change:** Notebook 08 now imports `build_evidence_segments` and `segment_numeric_candidates` instead of defining them inline. Its prediction logic, configuration (`configs/conservative_arithmetic.toml`) and split protocol are unchanged. The official test split was not loaded.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=600 notebooks/08_conservative_numerical_reasoning.ipynb`
- **Equivalence check:** the package functions and the former inline functions produce identical segment keys, texts and parsed candidates for 7,134/7,134 train+dev records.
- **Observed result:** 32/871 display-answer correct (0.036739) and 35/883 execution correct (0.039638). Answered 293/883. The prediction artifact `data/processed/conservative_arithmetic_dev_predictions.jsonl` is byte-identical to the previous run.
- **Decision:** the refactor is behavior-preserving. Use `finevidence.retrieval` segments for the retriever work in Notebook 10, with `include_header_row=True` there, because some gold evidence references `table_0`.

## 2026-10-22 — program-accuracy implementation check

- **Question:** Does `compare_programs` reproduce the official FinQA program-accuracy convention?
- **Data:** pinned public train split only; dev and test were not used.
- **Method:** (1) compare every train gold program with itself; (2) for each non-table step of each train program, swap that step's two arguments and compare the variant with the gold program, using both `compare_programs` and the official `equal_program`. The official function was extracted by AST from `code/evaluate/evaluate.py` at the pinned commit and run in a scratch script outside the repository.
- **Code state:** this check ran on the working tree that became the program-accuracy commit (`git log -- src/finevidence/evaluation/program.py`).
- **Observed result:** gold-vs-gold equivalent for 6,251/6,251 programs (about 14 s on CPU). On 9,392 swapped variants, the two implementations agreed 9,392/9,392 times. Equivalent: add 1,512, multiply 567, divide 19, subtract 23. Not equivalent: divide 4,426, subtract 2,716, greater 124, exp 5. The few equivalent divide/subtract swaps are cases where swapping leaves the expression unchanged, such as identical arguments.
- **Limitations:** swapped arguments test only one kind of perturbation. Agreement on generated programs is untested until a generator exists. Matching tokens verbatim (`100` ≠ `const_100`) follows the official script, even where the values are equal.
- **Decision:** use `compare_programs` as the program-accuracy metric for Notebooks 10–11.

## 2026-10-22 — cross-encoder evidence retriever, dev (Notebook 10)

- **Question:** Does a cross-encoder trained on train `gold_inds` retrieve all gold facts more often than train-fitted TF-IDF on the same segment rendering?
- **Dataset and split protocol:** pinned public FinQA train (fitting) and dev (checkpoint selection and reporting), both verified by SHA-256 through `finevidence.data.acquisition`. The official test split was not loaded. Prediction inputs used only `id`, `question`, `table`, `pre_text` and `post_text`. Dev `gold_inds` were read only after scoring, for recall.
- **Configuration:** `configs/retriever_bert_base.toml`: `bert-base-uncased`, 3 random negatives per positive resampled every epoch, 5 epochs, batch size 16, learning rate 2e-5, warmup ratio 0.1, `max_seq_length` 512, header row included, seed 42. The checkpoint was selected by dev all-gold recall@5.
- **Command (Kaggle):** `papermill notebooks/10_retriever_training.ipynb /kaggle/working/10_retriever_training_executed.ipynb --log-output --cwd notebooks -k python3`
- **Code state and environment:** commit `7028afc`; Python 3.13.15, torch 2.11.0+cu128, transformers 5.16.1, Tesla T4 (Kaggle).
- **Data sizes:** 6,251 train records → 10,691 positives, a 180,663-segment negative pool, and 42,764 pairs (2,673 steps) per epoch. The only unmatched train gold key is the flagged `text_-1`. Dev: 883 records, 26,834 segments (467 records have more than one gold fact).
- **Training history (dev all-gold@5 / any-gold@5):** epoch 1 0.8539 / 0.9841; epoch 2 0.8686 / 0.9853; **epoch 3 0.8698 / 0.9887 (selected)**; epoch 4 0.8630 / 0.9819; epoch 5 0.8437 / 0.9751. Mean training loss fell from 0.2733 to 0.0667. About 300 s of training plus 40 s of dev ranking per epoch; 28 min 25 s in total.
- **Observed dev recall (selected checkpoint vs TF-IDF):**

  | k | TF-IDF any | TF-IDF all | TF-IDF all, multi-fact | Cross-encoder any | Cross-encoder all | Cross-encoder all, multi-fact |
  | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
  | 1 | 0.5878 | 0.2922 | 0.0000 | 0.8947 | 0.4134 | 0.0000 |
  | 3 | 0.8256 | 0.5345 | 0.2719 | 0.9728 | 0.8075 | 0.6724 |
  | 5 | 0.9015 | 0.6602 | 0.4497 | 0.9887 | 0.8698 | 0.7709 |
  | 10 | 0.9604 | 0.8414 | 0.7452 | 0.9943 | 0.9354 | 0.8865 |

  At k = 5, records still missing at least one gold fact fall from about 300 to about 115 of 883. All-gold@1 for multi-fact records is 0 by construction.
- **Artifacts:** the executed notebook is committed as `notebooks/10_retriever_training.ipynb`; its cell sources are identical to `7028afc`. Ignored local copies: `data/processed/retriever_bert_base_dev_rankings.jsonl` (883 rows, all stamped `7028afc`) and `models/retriever-bert-base-dev-v1/history.json`. The checkpoint `best/` remains on Kaggle only. Re-scoring the local rankings against dev `gold_inds` reproduced every recall value in the table to four decimals.
- **Limitations:** the checkpoint was selected on dev and is also reported on dev, so these dev numbers are slightly optimistic. Epochs 2–4 are within 0.007 of each other, so the selection effect is small but nonzero. Unbiased retrieval numbers need the final held-out evaluation in M4. Dev all-gold recall fell after epoch 3 while training loss kept falling, which suggests overfitting with longer training. This is one seed and one GPU type. Recall measures evidence availability only, not answer correctness.
- **Decision:** accept this retriever as the M3 stage 1. Feed the generator the top 5 segments (`top_n_for_generator = 5`). About 13% of dev records still lack a gold fact in the top 5, which caps end-to-end execution accuracy; the gold-facts oracle in Notebook 11 will separate that cap from generator errors.
