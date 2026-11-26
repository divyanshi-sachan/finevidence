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

## 2026-10-22 — program generator, first Kaggle attempt (failed: out of memory)

- **Run:** Notebook 11 at commit `24db253` on a Kaggle Tesla T4 (torch 2.11.0+cu128, transformers 5.16.1): `t5-base`, fp32, batch 16, 10 epochs planned.
- **Observed before the failure:** training inputs reach 794 tokens (36 of 6,251 truncated to 512); dev retrieved inputs reach 704 tokens (14 of 883 truncated); targets are at most 50 tokens. 391 steps per epoch.
- **Failure:** `torch.OutOfMemoryError` during the first epoch's forward pass, with 13.77 GiB of 14.56 GiB allocated. The traceback shows the decoder key/value cache being filled during training.
- **Fix (commit after `24db253`):** each 16-example optimizer step is processed as two 8-example chunks, weighted by their target-token share, with `use_cache=False` during training. Beam-search decoding uses `eval_batch_size = 16`. `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` is set, and peak GPU memory is printed each epoch. On CPU with `t5-small`, the token-weighted 2×8 gradient matched the 16-example full-batch gradient (max absolute difference 1.4e-6, largest gradient 5.2), so the optimization target is unchanged.
- **Result:** none; no epoch completed. This entry records the attempt only.

## 2026-10-22 — T5 program generator over retrieved facts, dev (Notebook 11)

- **Question:** Given the Notebook 10 retriever's top 5 dev facts, how often does a fine-tuned `t5-base` generate a program whose execution equals `exe_ans`, and how much error comes from retrieval rather than generation?
- **Dataset and split protocol:** pinned public FinQA train (fitting) and dev (checkpoint selection and reporting), verified by SHA-256. The official test split was not loaded. Dev retrieved inputs come from the SHA-256-verified Notebook 10 ranking file and read no annotation field. The gold-facts oracle reads `gold_inds` keys by design and is a diagnostic only.
- **Configuration:** `configs/generator_t5_base.toml`: `t5-base`, fp32, effective batch 16 (2 × 8 token-weighted gradient accumulation), learning rate 3e-4, warmup ratio 0.05, 10 epochs, 5 facts per input (gold plus same-record distractors, resampled each epoch), beam size 4, seed 42. The checkpoint was selected by dev execution accuracy with retrieved inputs.
- **Command (Kaggle):** `papermill notebooks/11_program_generator.ipynb /kaggle/working/11_program_generator_executed.ipynb --log-output --cwd notebooks -k python3`
- **Code state and environment:** commit `5f10139`; Python 3.13.15, torch 2.11.0+cu128, transformers 5.16.1, Tesla T4 (Kaggle). Peak GPU memory 9.55 GB. About 580 s of training and 3 min of dev decoding per epoch; 7,651 s (2.1 h) for 10 epochs.
- **Input lengths:** 36/6,251 train and 14/883 dev retrieved sources exceed 512 tokens and are truncated; targets are at most 50 tokens (limit 64).
- **Training history (dev retrieved execution correct of 883):** 299, 373, 437, 455, 488, 494, 508, 501, **523 (epoch 9, selected)**, 515. Training loss fell from 1.342 to 0.132.
- **Observed dev results (selected checkpoint):**

  | Condition | Execution correct | Execution accuracy | Program accuracy | Invalid rate | Operand grounding |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Retrieved top 5 | 523 | 0.5923 | 0.5561 | 0.0079 | 0.9704 |
  | Gold-facts oracle | 578 | 0.6546 | 0.6183 | 0.0079 | 0.9755 |
  | Reference: Notebook 08 arithmetic | 35 | 0.0396 | — | — | — |

  The normal-approximation 95% interval for the retrieved condition is about 0.560–0.625. Per record: 494 are correct in both conditions, 29 only with retrieved inputs, and 84 only with gold facts. 32 retrieved-condition answers are execution-correct but not symbolically equivalent to the gold program.
- **Post-hoc breakdown (execution accuracy, retrieved / oracle):** 1-step programs (523) 0.6558 / 0.7208; 2-step (287) 0.5540 / 0.6341; 3+-step (73) 0.2877 / 0.2603. Single gold fact (416) 0.6274 / 0.6947; 2+ gold facts (467) 0.5610 / 0.6188. All gold facts in the top 5 (768) 0.6393 / 0.6979; not all (115) 0.2783 / 0.3652.
- **Verification:** the executed notebook's cell sources are identical to `5f10139` and contain no error outputs. Re-scoring both downloaded prediction files locally, with `execute_program`, `compare_execution`, `compare_programs` and `operand_grounding` on rebuilt inputs, reproduced every metric and breakdown above. The downloaded checkpoint regenerated the first 16 retrieved dev predictions exactly on CPU.
- **Artifacts (ignored by Git):** `models/generator-t5-base-dev-v1/best/` (`model.safetensors` SHA-256 `c9c5c8cc9ac46a72627d47bd974307240fbcb30cb3ef80bb0f48cde9496ca945`), `models/generator-t5-base-dev-v1/history.json`, and `data/processed/generator-t5-base-dev-v1_dev_{retrieved,gold_facts_oracle}_predictions.jsonl`. The executed notebook is committed.
- **Limitations:** the checkpoint was selected on dev and is also reported on dev; epochs 7–10 span about 2.5 points, so the result is somewhat optimistic. This is one seed, one GPU type, and untuned FinEvidence hyperparameters. Oracle inputs average about 2 facts while training used 5, so the oracle differs in input distribution, not only in evidence quality. The breakdowns are correlations, not causal error categories. The Notebook 10 retriever checkpoint was not kept, so test-time retrieval in M4 requires re-running Notebook 10 at `7028afc`.
- **Decision:** accept the retriever + generator pipeline as the M3 candidate. The M3 exit condition (baseline and candidate run under comparable conditions with observed results) is met on dev. M4 should start with categorized error analysis of the 360 retrieved-condition errors.

## 2026-10-22 — M1–M3 audit: split statistics, privacy scan, result uncertainty (Notebook 12)

- **Question:** Do the splits differ statistically, does the report text contain personal data, and how certain are the M3 dev comparisons?
- **Data:** pinned public train, dev and test files (SHA-256 verified). Input-side statistics and the privacy scan cover all splits. Label-side statistics are train vs dev only; no new test-label statistic was computed. M3 uncertainty uses the saved dev prediction artifacts of Notebooks 08 and 11.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 notebooks/12_milestone_audit_statistics_privacy.ipynb`; seed 42 for all resampling.
- **Observed results:**
  - KS D ≤ 0.077 for all input features. The largest detectable shifts are train vs dev in sentences per report (D = 0.075, p = 0.0003) and train vs test in table rows (D = 0.077, p < 0.0001).
  - Train vs dev label distributions: smallest chi-square p = 0.074; Cramér's V ≤ 0.035. 77.0% of train questions mention a year.
  - Privacy: 0 SSN-like strings; 1 email (test, corporate); 35 phone-pattern matches (21 space-separated table figures, 14 formatted, corporate in the examples inspected); 158 URLs; 2 report pages naming individuals.
  - Bootstrap 95% CIs for dev execution accuracy: conservative arithmetic 0.0396 [0.0272, 0.0532]; generator, retrieved 0.5923 [0.5606, 0.6251]; oracle 0.6546 [0.6229, 0.6852].
  - McNemar tests: generator vs arithmetic 493 vs 5 discordant records (p ≈ 6e-139); oracle vs retrieved 84 vs 29 (p ≈ 2e-7).
- **Re-executions in the same audit:** Notebook 07 re-ran cleanly; it reproduced 3/871 with a byte-identical prediction file, which resolves an earlier stale cell. Notebooks 01 and 02 were re-executed after replacing an absolute local path in their outputs with a repository-relative one. Notebook 02's parser-coverage cell now shows 6,251/883/1,147, because it uses the parser extended in Notebook 04; the original narrower-grammar counts stay recorded in `m2-data-findings.md`. No other Notebook 02 output changed.
- **External verification:** FinQA repository `LICENSE` (MIT) at the pinned commit; FinQA paper provenance, splits, human performance and published dev/test results ([research-notes.md](research-notes.md)).
- **Limitations:** the intervals do not cover checkpoint selection, seed or hardware variance; the privacy scan is pattern-based.
- **Decision:** M2's statistical-analysis and privacy deliverables are complete; the M1 success criteria now carry numeric targets fixed before any test use.

## 2026-11-01 — Categorized dev error analysis of the M3 pipeline (Notebook 13)

- **Question:** Where do the 360 retrieved-condition dev errors of the Notebook 11 generator come from, and which error type should the first M4 improvement target?
- **Data and protocol:** pinned dev split (SHA-256 verified) and the saved Notebook 11 prediction files (retrieved and gold-facts oracle). The test split was not loaded. Dev labels are read for diagnosis only.
- **Method:** `finevidence.evaluation.categorize_error` assigns one primary category per error in a fixed priority order: invalid program, retrieval miss, scale, sign, near miss (within 1%), operation sequence, operands, other. Covered by `tests/test_error_categories.py`.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 notebooks/13_error_analysis.ipynb` (code state: branch `m4/error-analysis` from `5c991cf`, uncommitted at run time).
- **Observed results (360 errors):** operation error 123 (34.2%), operand error 108 (30.0%), retrieval miss 81 (22.5%), scale 14, sign 14, near miss 13, invalid 7, other 0.
  - 272 errors (75.6%) occur with every gold fact among the 5 inputs.
  - The gold-facts oracle fixes 17 of 81 retrieval misses, 42 operand errors and 16 operation errors; 65 of its 84 gains are on records with complete retrieval.
  - Operation errors: 72 of 123 have 2+ step gold programs; 13 stop early (prefix of gold), 13 add extra steps, 97 use a different sequence.
  - Operand errors: 16 use a value from the same table row as a gold value; 19 reuse the gold literals in another order or with another constant; 73 use other values.
  - 9 of 14 sign errors are questions naming two or more years.
- **Artifact (ignored by Git):** `data/processed/generator-t5-base-dev-v1_dev_error_categories.csv` (360 rows).
- **Limitations:** categories are rule-based proxies with one label per error, not causes. Ambiguous questions and debatable gold labels are not detected by rules; a manual review of a fixed sample is still needed. Dev only, dev-selected checkpoint, one seed.
- **Decision:** the first M4 improvement iteration should target distractor robustness of the generator (upper bound from oracle gains on fully retrieved records: 65 records), ahead of retrieval improvements (measured ceiling about 17 records on these errors). Before that, run the manual ambiguity review so the error taxonomy covers the M4-required ambiguity category.

## 2026-11-01 — Manual ambiguity and label-quality review of a dev error sample (Notebook 13, section 5)

- **Question:** How many dev errors are ambiguous questions, debatable gold labels or convention differences rather than model errors?
- **Sample and protocol:** 40 of the 360 retrieved-condition errors, drawn with `errors.sample(n=40, random_state=42)`; dev only. Each error was labelled by one reviewer (Claude, the coding assistant, at the user's request) as `clear_model_error`, `ambiguous_question`, `debatable_gold` or `convention_mismatch`, with a note. Labels: [m4-ambiguity-review.csv](m4-ambiguity-review.csv). The notebook re-draws the sample and checks it matches the labelled ids.
- **Observed results:** clear model error 26, debatable gold 7, ambiguous question 4, convention mismatch 3. Not a clear model error: 14/40 = 0.35 (Wilson 95% CI 0.22–0.50). In 2 debatable-gold cases the prediction follows the question and the gold does not. 5 of the 26 clear errors copy a number with a wrong digit or use a year as a value.
- **Limitations:** a single reviewer and a small sample; labels are judgements, not measurements. The interval is too wide to scale to an exact count over all 360 errors.
- **Decision:** keep the official metric and gold labels unchanged and report the share as an evaluation caveat. Improvement priority unchanged: distractor robustness, then constraining program literals to numbers in the input facts.

## 2026-11-02 — Improvement iteration 1: fewer facts and grounded beam selection, dev (Notebook 14)

- **Question:** Without retraining, does passing fewer retrieved facts (H1, distractors) or choosing the first grounded, executable beam candidate (H2, copy errors) improve dev execution accuracy?
- **Data and protocol:** pinned dev split and SHA-256-verified Notebook 10 dev rankings; the saved Notebook 11 checkpoint. Test not loaded. The selector reads only input facts and the raw table.
- **Settings:** top 3, 4 or 5 facts × top beam or grounded selection over the 4 beam candidates (`select_grounded_candidate`, covered by `tests/test_candidate_selection.py`). Beam size 4, other generation settings from `configs/generator_t5_base.toml`.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=7200 notebooks/14_inference_iteration.ipynb`; Apple M5 (MPS), Python 3.13.16, torch 2.15.0, transformers 5.22.1, code at `469e59a` plus the uncommitted selector.
- **Reproduction check:** top-5 candidate 0 equals the saved Notebook 11 prediction for 883/883 records.
- **Observed results (execution correct of 883):**

  | Setting | Correct | Execution acc. | Program acc. | Invalid | Grounding | Fixed / broken vs baseline |
  | --- | ---: | ---: | ---: | ---: | ---: | ---: |
  | Top 5, top beam (M3 baseline) | 523 | 0.5923 | 0.5561 | 0.0079 | 0.9704 | — |
  | **Top 5, grounded** | **547** | **0.6195** | **0.5855** | **0.0011** | **0.9923** | **24 / 0** (p ≈ 1.2e-7) |
  | Top 4, top beam | 516 | 0.5844 | 0.5504 | 0.0079 | 0.9699 | 8 / 15 |
  | Top 4, grounded | 542 | 0.6138 | 0.5821 | 0.0023 | 0.9922 | 29 / 10 |
  | Top 3, top beam | 509 | 0.5764 | 0.5402 | 0.0091 | 0.9698 | 13 / 27 (p = 0.039) |
  | Top 3, grounded | 537 | 0.6082 | 0.5742 | 0.0045 | 0.9948 | 35 / 21 |

- **Artifact (ignored by Git):** `data/processed/generator-t5-base-dev-v1_dev_iteration1_candidates.jsonl` (4 candidates per record and setting).
- **Limitations:** dev only, one checkpoint and seed; the chosen setting was picked among 6 on dev. Decode wall-clock times are invalid as latency (the machine was suspended mid-run).
- **Decision:** H1 rejected (fewer facts lose more recall than they save in distractors). H2 supported: adopt top 5 facts + grounded beam selection as the current pipeline (dev 0.6195, up from 0.5923). Next: retrain with retrieved-style hard distractors on a GPU.

## 2026-11-02 — Improvement iteration 2: generator retrained with hard distractors, dev (Notebook 15)

- **Question:** Does training the generator with hard distractors (non-gold facts sharing the most words with the question) make it more robust to the distractors it sees at prediction time?
- **Data and protocol:** pinned train (fitting) and dev (epoch selection and reporting), SHA-256 verified; Notebook 10 dev rankings. Test not loaded.
- **Configuration:** `configs/generator_t5_base_hard.toml`: identical to Notebook 11 except `hard_distractor_share = 0.5` (a single untuned choice). Epoch selected by dev execution accuracy, top beam.
- **Command:** `kaggle/iteration2/launch.sh` (private Kaggle kernel `divyanshi92/finevidence-m4-iteration2`, version 1, running `kaggle/iteration2/run.py`, which executes the notebook with papermill). The first two pushes were refused by Kaggle's two-GPU-session limit while other kernels were running; the third ran.
- **Code state and environment:** commit `a03599d`; Python 3.13.15, torch 2.11.0+cu128, transformers 5.16.1, Tesla T4. Peak GPU memory 9.55 GB; about 650 s of training and 3 min of dev decoding per epoch; 8,486 s (2.4 h) in total. 114/6,251 train sources exceed 512 tokens (36 with random distractors).
- **Training history (dev retrieved execution correct, top beam):** 294, 401, 443, 455, 472, 495, 494, 512, 517, **520 (epoch 10, selected)**.
- **Observed dev results (selected checkpoint, 883 records):**

  | Condition | Correct | Execution acc. | Program acc. | Invalid | Grounding |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Retrieved, top beam | 520 | 0.5889 | 0.5504 | 0.0034 | 0.9710 |
  | Retrieved, grounded | 539 | 0.6104 | 0.5742 | 0.0023 | 0.9939 |
  | Gold-facts oracle, top beam | 564 | 0.6387 | 0.6036 | 0.0045 | 0.9744 |
  | Gold-facts oracle, grounded | 586 | 0.6636 | 0.6308 | 0.0023 | 0.9959 |

  Paired with the Notebook 11 checkpoint (top beam, 523): 68 fixed, 71 broken (p = 0.87). Paired with the current pipeline (Notebook 11 + grounded selection, 547), computed locally from the downloaded predictions and the Notebook 14 candidates: 57 fixed, 65 broken (p = 0.53); 604 records are correct for at least one of the two.
- **Verification:** the executed notebook's cell sources are identical to `a03599d`; it has no error outputs.
- **Artifacts (ignored by Git):** `models/generator-t5-base-hard-v1/best/` (`model.safetensors` SHA-256 `e42200d8ba97e30d56741f1580d17a94418aca2bcd35e84bd0fc1199d60ced0c`), `models/generator-t5-base-hard-v1/history.json`, `data/processed/generator-t5-base-hard-v1_dev_{retrieved,gold_facts_oracle}_{top_beam,grounded}_predictions.jsonl`. The executed notebook is committed.
- **Limitations:** one seed, one untuned share; dev accuracy was still rising at epoch 10; more train inputs are truncated than with random distractors.
- **Decision:** do not adopt. The pipeline stays the Notebook 11 checkpoint with grounded selection (dev 0.6195).

## 2026-11-25 — Improvement iteration 3: Qwen2.5-1.5B-Instruct LoRA program generator, dev (Notebook 16)

- **Question:** Does a larger decoder-only generator (Qwen2.5-1.5B-Instruct with LoRA) beat the T5-base pipeline with the same inputs (question plus top-5 retrieved facts)?
- **Data and protocol:** pinned train (fitting) and dev (epoch selection and reporting), SHA-256 verified; Notebook 10 dev rankings. Test not loaded.
- **Configuration:** `configs/generator_qwen_lora.toml`: LoRA rank 16, alpha 32, dropout 0.05 on all linear layers (18.5M trainable of 1.56B parameters, 1.18%); 3 epochs, micro batch 4 × accumulation 4, lr 2e-4, warmup 3%, fp16 autocast, gradient checkpointing; 4 beams. Epoch selected by dev greedy execution accuracy.
- **Command:** `kaggle/launch.sh notebooks/16_llm_lora_generator.ipynb finevidence-m4-iteration3 generator-qwen2.5-1.5b-lora-v1` (private Kaggle kernel `divyanshi92/finevidence-m4-iteration3`, version 2; version 1 failed on a torchao import, fixed in `45b1542`).
- **Code state and environment:** commit `45b1542`; Python 3.13.16, torch 2.11.0+cu130, transformers 5.20.2, peft 0.21.2, Tesla T4. Peak GPU memory 9.2 GB; about 37.5 min of training plus 7 min of greedy dev decoding per epoch; training 2 h 14 min, final 4-beam dev decode 14 min 42 s. 126/6,251 train sources truncated at 512 tokens.
- **Training history (dev greedy execution correct):** 530, 570, **596 (epoch 3, selected)**. Train loss 0.229, 0.091, 0.060.
- **Observed dev results (selected adapter, 883 records):**

  | Condition | Correct | Execution acc. | Program acc. | Invalid | Grounding |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Retrieved, top beam | 610 | 0.6908 | 0.6523 | 0.0011 | 0.9990 |
  | Retrieved, grounded | 610 | 0.6908 | 0.6523 | 0.0011 | 0.9990 |

  Grounded selection changes nothing here because the top beam is almost always grounded. Paired with the current pipeline (Notebook 11 + grounded selection, 547), computed locally from the downloaded predictions and the Notebook 14 candidates: 109 fixed, 46 broken, exact McNemar p = 4.5e-7.
- **Further dev metrics (retrieved, grounded; computed locally from the downloaded predictions):** execution accuracy 610/883 (95% Clopper–Pearson CI 65.9–72.1%); program accuracy 576/883 = 65.23% (CI 62.0–68.4%); 34 answers correct with a non-equivalent program; 1 invalid program; 1,948/1,950 literals grounded (99.90%). Retrieval is unchanged (Notebook 10 BERT, all-gold recall@3 80.75%, @5 86.98%).
  - By gold program steps: 1 step 393/523 (75.1%), 2 steps 184/287 (64.1%), 3+ steps 33/73 (45.2%).
  - By gold evidence source: table only 422/542 (77.9%), text only 111/198 (56.1%), table and text 77/143 (53.9%).
  - By first gold operation: divide 246/323 (76.2%), subtract 254/360 (70.6%), add 49/100 (49.0%), multiply 24/56 (42.9%); table_average 15/19, table_max 7/7, table_min 5/5, greater 8/9, table_sum 2/4 (too few to interpret).
  - Error categories (`categorize_error`, 273 errors; current-pipeline counts from Notebook 13 in brackets): operation 91 (123), operand 85 (108), retrieval miss 72 (81), scale 13 (14), sign 9 (14), near miss 2 (13), invalid 1 (7).
  - Beam-agreement abstention (`candidate_agreement`, answer if ≥ threshold): 1.00 → 10 answered (1.1%), 100%; 0.75 → 65 (7.4%), 84.62%; 0.50 → 234 (26.5%), 73.93%; 0.25 → 882 (99.9%), 69.16%. Too coarse to reach ≥ 80% at ≥ 50% coverage; a finer signal needs beam log-probabilities, which this run did not save.
- **Verification:** the executed notebook's cell sources are identical to `45b1542`; it has no error outputs.
- **Artifacts (ignored by Git):** `models/generator-qwen2.5-1.5b-lora-v1/best/` (`adapter_model.safetensors` SHA-256 `9cc4f93c09ed9f122ceee005b37461918d4cf48dcd60a4620b5e861b4bd7b03d`), `models/generator-qwen2.5-1.5b-lora-v1/history.json`, `data/processed/generator-qwen2.5-1.5b-lora-v1_dev_{candidates,retrieved_top_beam_predictions,retrieved_grounded_predictions}.jsonl`. The executed notebook is committed.
- **Limitations:** one seed and configuration; dev accuracy was still rising at epoch 3, and the epoch was selected on the same dev split it is reported on. Gold-facts oracle not run for this generator.
- **Decision:** adopt. The current pipeline becomes the BERT retriever (top 5 facts) plus the Qwen2.5-1.5B LoRA generator (dev 0.6908, up from 0.6195). Next: abstention on its candidates toward ≥ 80% selective accuracy at ≥ 50% coverage.

## 2026-11-25 — Improvement iteration 4 (planned): 10 facts and self-consistency, dev (Notebook 17)

- **Hypotheses (not results):** H1: giving the Notebook 16 generator 10 retrieved facts instead of 5 recovers part of the 72 retrieval-miss errors (dev all-gold recall@10 93.54% vs @5 86.98%; 41 of the 72 have all gold facts in the top 10), if the extra distractors cost less. H2: majority voting over 16 sampled programs (temperature 0.7, top-p 0.95) fixes some operation and operand errors, and its vote share is a finer abstention confidence than 4-beam agreement.
- **Configuration:** `configs/generator_qwen_lora_top10.toml`: Notebook 16 settings except `facts_per_input = 10`, `max_source_tokens = 1024`, `eval_batch_size = 4`, plus `[sampling]`. Untuned single choices.
- **Comparison planned:** against the Notebook 16 pipeline (610/883) with an exact paired McNemar test; vote share against the M1 target (>= 80% accuracy at >= 50% coverage). Test is not loaded.
- **Verification so far:** CPU smoke run with a tiny model completed and wrote all prediction and candidate files.
- **Run 1 (Kaggle kernel version 1, `c9679f3`):** failed after about 10 minutes with CUDA out of memory in the first training steps (10-fact sequences at micro batch 4). Changed to micro batch 2 × accumulation 8 (same 16 examples per optimizer step) and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` in `kaggle/run_notebook.py`.
- **Run 2 (Kaggle kernel version 2, `8014175`):** training completed: 3 epochs of about 60 min each (peak GPU memory 8.76 GB); dev greedy execution correct 556, 590, **604 (epoch 3, selected)**, against 530, 570, 596 with 5 facts in Notebook 16. The 4-beam dev decode finished in 23 min 38 s, then the sampling decode (4 records × 16 sequences per batch, with the training model still in memory) ran out of CUDA memory before any prediction file was written. The best adapter was kept (`adapter_model.safetensors` SHA-256 `1646a66b99ae80c1b738420d94b6d589af0b1796b03c9d8cd915ea433a58b4f5`). Fix: the notebook frees the training model before decoding, samples one record per batch (`sample_batch_size = 1`), and gains a decode-only mode (`FINEVIDENCE_REUSE_ADAPTER=1`, `kaggle/launch.sh ... reuse`) that loads this adapter instead of retraining.
- **Run 3 (Kaggle kernel version 3, `6cc650e`, decode only with the run-2 adapter):** 4-beam decode 23 min 23 s; 16 samples per record 1 h 10 min 23 s. The executed notebook's cell sources are identical to `6cc650e`; no error outputs.
- **Observed dev results (883 records):**

  | Selection | Correct | Execution acc. | Program acc. | Invalid | vs Notebook 16 (610): fixed / broken, exact McNemar p |
  | --- | ---: | ---: | ---: | ---: | --- |
  | Top beam | 625 | 0.7078 | 0.6636 | 0.0 | 49 / 34, p = 0.12 |
  | Grounded | 625 | 0.7078 | 0.6636 | 0.0 | same as top beam |
  | Vote (16 samples) | 617 | 0.6988 | 0.6523 | 0.0 | 53 / 46, p = 0.55 |

- **Abstention (dev, answer only when confidence ≥ threshold):**

  | Threshold | Vote answer, vote share: answered (coverage), accuracy | Top-beam answer, share of samples agreeing: answered (coverage), accuracy |
  | --- | --- | --- |
  | 1.0 | 494 (55.9%), 89.07% (95% CI 86.0–91.7%) | 491 (55.6%), 89.41% |
  | 0.9375 | 533 (60.4%), 87.99% | 530 (60.0%), 88.30% |
  | 0.875 | 575 (65.1%), 86.61% | 572 (64.8%), 86.89% |
  | 0.75 | 671 (76.0%), 82.86% | 657 (74.4%), 84.17% |
  | 0.625 | 727 (82.3%), 79.50% | 703 (79.6%), 81.65% |

- **Limitations:** one seed; the epoch, the selection rule and the thresholds were all chosen on dev, so these selective accuracies are optimistic until the single test run. H1 (10 facts) is a non-significant +15 records; H2's voting did not raise full-coverage accuracy.
- **Decision:** adopt the 10-fact adapter with the top-beam answer and the share of 16 samples agreeing with it as confidence. It meets the M1 abstention target on dev at every threshold from 1.0 to 0.75 (for example 84.17% at 74.4% coverage), against 4-beam agreement's 73.93% at 26.5%. Freeze one threshold before the test run.

### M4 retriever rerun for the test evaluation (2026-11-25)

Kernel `divyanshi92/finevidence-m4-retriever-rerun` v1 reran Notebook 10 unchanged (code identical to `7028afc`). Dev all-gold recall@5 per epoch: 0.8573, 0.8732, **0.8822** (best, kept), 0.8641, 0.8573. The best checkpoint is 1.24 points from the original 0.8698, within the protocol's 1.5-point band, so the rerun is **accepted**. Only dev labels were read.

### M4 single test evaluation, Notebook 18 (2026-11-26)

Kernel `divyanshi92/finevidence-m4-test` v1 at commit `4dea6a5`, Tesla T4, run once per [the frozen protocol](m4-test-protocol.md); adapter SHA-256 `1646a66b…` verified, `smoke_test: false`, retriever from the accepted rerun. No setting was changed after the run.

| Metric (test, n = 1,147) | Result | 95% CI |
|---|---|---|
| Execution accuracy | 792/1147 = 69.05% | 66.3–71.7% |
| Program accuracy | 752/1147 = 65.56% | 62.7–68.3% |
| Invalid-program rate / operand grounding | 0.35% / 99.54% | |
| Retrieval all-gold recall@5 / @10 | 0.8684 / 0.9268 | |
| Selective, threshold 1.0 (primary) | coverage 598/1147 = 52.14% (49.2–55.1%); accuracy 525/598 = 87.79% (84.9–90.3%) | |
| Selective, threshold 0.75 | coverage 808/1147 = 70.44% (67.7–73.1%); accuracy 678/808 = 83.91% (81.2–86.4%) | |

Inference record: 0.046 s retrieval, 1.48 s beams, 4.31 s sampling, 5.84 s per record in total on a T4.

**M1 targets:** ≥ 55% test execution accuracy — met (69.05%). ≥ 80% accuracy at ≥ 50% coverage — met at the primary threshold (87.79% at 52.14%), though the coverage interval's lower bound (49.2%) falls just below 50%. The latency target of ≤ 1 s per question is **not met** (5.84 s, dominated by 16-sample confidence). Test is now spent; it must not be used for further tuning.

### M4 robustness checks, Notebook 19 (planned, 2026-11-26)

Dev only, the frozen adapter and Notebook 10 dev rankings, top of 4 beams. Four label-preserving perturbations (`finevidence.generation.perturbations`): `reword` (surface rewrites of the question; 588 of 883 questions get a word-level change, all get the trailing "?" toggled), `reverse_facts`, `thousands_separators` (2457 -> 2,457, years 1900–2099 kept; changes 624 records — FinQA writes numbers without separators, so removing them would change nothing), and `foreign_fact` (the next record's top fact inserted first). Each condition is compared with the unperturbed run: accuracy, flips, exact McNemar test, and the share of answers kept. Answer-changing perturbations (unit rescaling, period shifts) are out of scope because they need new labels. Limitation: operand grounding is computed on the perturbed fact text, so separator-formatted numbers may lower that side metric without affecting execution accuracy.

### M4 robustness checks, Notebook 19 (results, 2026-11-26)

Kernel `divyanshi92/finevidence-m4-robustness` v1 at commit `d6c02c9`, Tesla T4; adapter SHA `1646a66b…` verified, `smoke_test: false`. The unperturbed run reproduces Notebook 17 exactly (625/883). Dev only; no setting was tuned.

| Condition | Inputs changed | Correct | Accuracy | Fixed / broken vs original | McNemar p | Answer kept |
|---|---:|---:|---:|---|---:|---:|
| original | 0 | 625 | 70.78% | — | — | 100% |
| reword | 883 | 617 | 69.88% | 21 / 29 | 0.32 | 88.6% |
| reverse_facts | 883 | 602 | 68.18% | 32 / 55 | 0.018 | 79.7% |
| thousands_separators | 624 | 379 | 42.92% | 3 / 249 | < 0.001 | 59.2% |
| foreign_fact | 883 | 608 | 68.86% | 8 / 25 | 0.005 | 90.3% |

**Reading.** Question rewording causes no significant drop, though 11.4% of answers change. Fact order and an irrelevant extra fact each cost about 2 points (significant). Thousands separators are a severe failure: of 366 changed programs, 223 copy a separator-formatted literal (e.g. `divide(136,104, const_1000)`), which FinQA program syntax reads as extra arguments. **Mitigation for M5:** normalize separators out of evidence text before generation (FinQA's own convention), and treat any user-supplied document format as a robustness risk. Each result is one seed; label-changing perturbations (units, periods) remain untested.

### Improvement step 1: number canonicalization (2026-11-26, after M4 handoff)

Plan agreed after the improvement research ([report](../reports/Improving%20FinQA%20model%20accuracy.md), not committed): canonicalization, number-format robustness, executor-verified self-training, retrieval from measured errors, then evaluation. The test split is spent; every step is selected on dev and any further test use needs a new written protocol.

**Audit.** Evidence text reached the retriever and generator unchanged; the executor splits program arguments on commas, so a copied `136,104` becomes two arguments. The grounding check and table operations already strip separators.

**Change.** `finevidence.data.numbers.canonicalize_numbers` removes thousands separators in well-formed groups and maps Unicode minus and non-breaking spaces to ASCII. It is applied in `segment_retrieval_text` and to the question in retriever pairs and generator inputs, so retrieval, generation and any future app share it. Parenthesised negatives and scale words are kept as FinQA writes them. **Verified identity on FinQA:** it changes 0 of 191,354 train and 0 of 26,834 dev segments and 0 questions, so existing rankings, adapters and results are unaffected. Applied after the `thousands_separators` perturbation it restores the original text for all but 54 dev segments, where the perturbation itself drops leading zeros in identifiers (e.g. `055000000`).

**Planned check.** Notebook 19 gains a `thousands_separators_canonical` condition; it runs with `FINEVIDENCE_CONDITIONS=thousands_separators,thousands_separators_canonical` (plus `original`).

**Result** (kernel `divyanshi92/finevidence-m4-robustness-canonical` v1, commit `43514fd`, T4, adapter `1646a66b…`, `smoke_test: false`, dev):

| Condition | Inputs changed | Correct | Accuracy | Fixed / broken | Answer kept |
|---|---:|---:|---:|---|---:|
| original | 0 | 625 | 70.78% | — | 100% |
| thousands_separators | 624 | 379 | 42.92% | 3 / 249 | 59.2% |
| thousands_separators_canonical | 15 | 625 | 70.78% | 0 / 0 | 100% |

Canonicalization fully removes the separator failure on dev: every answer matches the unperturbed run. The 15 records whose input still differs (leading zeros dropped by the perturbation) gave the same answers. Adopted; it is a no-op on FinQA, so no earlier result changes.

### Improvement step 4a: self-training samples, Notebook 20 (planned, 2026-11-26)

Rejection-sampling fine-tuning, part 1. On **train only**, the frozen Notebook 17 adapter samples 8 programs per record (temperature 0.8, top-p 0.95) from one training-style input (gold plus random distractors, 10 facts, input seed 1042). `finevidence.generation.self_training.select_verified_programs` keeps up to 4 distinct programs, other than the gold one, that execute to the gold answer with every literal found in the shown facts. Expected runtime about 4 hours on a T4. Part 2 (Notebook 21) retrains on gold plus verified programs and is selected on dev against 625/883; it is accepted only with an exact McNemar p < 0.05 on dev. Hypothesis, not a result: the math-benchmark gains (5–13 points) may not transfer to FinQA.
