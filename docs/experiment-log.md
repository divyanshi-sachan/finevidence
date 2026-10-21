# Experiment log

## 2026-10-20 — lexical value-selection baseline, dev

- **Question:** Can a train-fitted lexical ranker select a display-answer candidate from raw report context?
- **Dataset:** pinned public FinQA files recorded in `docs/dataset-card.md`; train used for fitting, dev used once for evaluation, official test not loaded.
- **Configuration:** `configs/lexical_value_baseline.toml`; seed `42` is recorded although this deterministic TF–IDF run has no randomized training step.
- **Command:** `.venv/bin/jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=300 notebooks/06_lexical_value_baseline.ipynb`
- **Code state:** local working tree; no commit revision exists yet.
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
- **Code state:** local working tree; no commit revision exists yet.
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
- **Code state:** local working tree; no commit revision exists yet.
- **Observed results (train):** 5,730/6,251 programs have ≤2 steps, and the top 10 of 119 templates cover 86.8%. 14,190/14,210 numeric literals occur in the context. 5,398 records exceed 512 whitespace tokens. TF-IDF within-record recall@3 is 82.9% any-gold and 53.8% all-gold (28.5% all-gold for multi-fact records). The display comparator accepts the gold executed value for 2,203/6,083 numeric-`exe_ans` records, and for 0/3,480 percentage answers when given the raw ratio.
- **Executor validation:** `execute_program` on gold programs equals `exe_ans` for 6,251/6,251 train and 883/883 dev records.
- **Re-scored dev execution accuracy (denominator 883):** lexical value selection 5 (0.566%), question-conditioned selection 6 (0.680%), conservative arithmetic 35 (3.964%). The display-answer results in the entries above are unchanged.
- **Limitations:** literal-provenance matching ignores sign and uses six-decimal rounding. Context lengths are whitespace tokens, a lower bound on sub-word length. TF-IDF recall was measured in-sample on train, so it is a diagnostic only. Program accuracy is not implemented.
- **Decision:** adopt execution accuracy as the primary metric and build the FinQANet-style retriever + program-generator baseline described in `docs/finqanet-baseline-plan.md`.
