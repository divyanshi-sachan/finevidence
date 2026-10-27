# Evaluation plan

This document defines how FinEvidence measures results. Observed numbers live in [experiment-log.md](experiment-log.md); the targets they are judged against are in [problem-statement.md](problem-statement.md).

## Split protocol

- **Train** fits everything that is learned: TF-IDF vocabularies, retriever and generator weights, and answer-policy inspection.
- **Dev** is used for model and checkpoint selection and for all M3 reporting. Dev numbers are labelled as dev, and they are optimistic whenever a checkpoint was selected on dev.
- **Test** is used **once**, in the final M4 evaluation, after every method and target is fixed. No test label, program or gold evidence has been used for any decision. The only test-label statistics are descriptive M2 audit counts (Notebooks 02–04: schema, empty fields, evidence-key validity and parser grammar coverage). The parser grammar was extended from observed train programs, not test ones.
- Every comparison uses the same pinned data files (SHA-256-verified at load), the same 883-record dev denominator, and the same metric code.

## Metrics

| Metric | Definition | Implementation | Validation |
| --- | --- | --- | --- |
| **Execution accuracy (primary)** | The predicted program is executed; a numeric result is rounded to 5 decimals and must equal `exe_ans` exactly. Every record is in the denominator; invalid or missing predictions count as wrong. This follows the official FinQA `code/evaluate/evaluate.py` at the pinned commit (verified 2026-10-21). | `finevidence.reasoning.execute_program` and `finevidence.evaluation.compare_execution` | Reproduces `exe_ans` for 6,251/6,251 train and 883/883 dev gold programs ([Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb)) |
| **Program accuracy** | Symbolic equivalence with the gold program, as in the official `equal_program`. Each gold literal, constant or table-step token becomes a symbol, and any other token fails. Both expressions are compared after `sympy.simplify`. Tokens match verbatim, so `100` ≠ `const_100`. | `finevidence.evaluation.compare_programs`, which builds expressions from sympy objects and never `sympify`s program text | Gold-vs-gold 6,251/6,251; agrees with the official function on 9,392/9,392 argument-swapped train variants |
| **Retrieval recall@k** | Within a record, whether any gold fact (any-gold) and whether all gold facts (all-gold) are among the top-k segments. Multi-fact records are also reported separately. | `finevidence.evaluation.gold_recall_at_k` | Unit tests; re-scored from saved rankings |
| **Invalid-program rate** | Share of predictions that fail to parse or execute. | `finevidence.generation.summarize_scores` | Unit tests |
| **Operand grounding** | Share of a program's numeric literals (by absolute value, rounded to 6 decimals) that occur in the facts given to the generator. Constants and references are excluded. | `finevidence.evaluation.operand_grounding` | Unit tests; reported per run in Notebook 11 |
| **Display-answer accuracy (secondary)** | Comparison against the raw `answer` field under the policy below. | `finevidence.evaluation.compare_display_answers` | Kept for continuity with Notebooks 06–08; see the caveat below |
| **Uncertainty** | Percentile bootstrap 95% intervals (10,000 resamples, seed 42) and exact McNemar tests for paired comparisons on the same records. | [Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb) | — |

**Display-answer caveat.** The display comparator accepts the gold executed value for only 2,203 of 6,083 train records with numeric `exe_ans`, because display answers are rounded and percentages are shown multiplied by 100 (Notebook 09). Display accuracy is therefore not an upper-bounded reasoning score, and it is never the primary metric.

### Display-answer comparator policy

Fixed on train in [Notebook 05](../notebooks/05_preprocessing_validation_and_answer_policy.ipynb) before any dev evaluation. It reads only the raw `answer` field, never `exe_ans`.

- An empty reference answer is `unavailable_reference`: the record is kept and reported separately, but excluded from the display denominator (871 of 883 dev records remain).
- Isolated signed integers or decimals, with an optional percent marker, are numeric. The percent status must match, and the tolerance is `max(1e-4 absolute, 1e-4 relative)`.
- Other non-empty strings are compared after case-folding and whitespace collapse. Currency, unit, date and mixed strings stay text and are never coerced to numbers.
- A missing or empty prediction is reported as unsupported, not counted as a match.

## Experiment protocols (dev)

| Notebook | System | Fitted on | Prediction inputs | Notes |
| --- | --- | --- | --- | --- |
| [06](../notebooks/06_lexical_value_baseline.ipynb) | Lexical value selection | TF-IDF on train questions + context | Allowlisted dev context | Extractive: picks one raw cell or span. |
| [07](../notebooks/07_question_conditioned_evidence_value_selection.ipynb) | Question-conditioned selection | Same | Top 3 TF-IDF segments | Gold evidence is read only after predictions, for diagnostics. |
| [08](../notebooks/08_conservative_numerical_reasoning.ipynb) | Conservative arithmetic | Same | Top 3 segments | One operation over two compatible operands; abstains when unsure; coverage and answered-case accuracy are reported. |
| [10](../notebooks/10_retriever_training.ipynb) | Cross-encoder retriever | Train `gold_inds` pairs (3 random negatives per positive, resampled each epoch) | All segments of the dev record | Checkpoint chosen by dev all-gold recall@5. |
| [11](../notebooks/11_program_generator.ipynb) | T5 program generator | Train programs with gold + distractor facts | Top 5 retriever facts (prediction) or gold facts only (oracle diagnostic) | Checkpoint chosen by dev execution accuracy with retrieved inputs. |

All predictions use only `id`, `question`, `table`, `pre_text` and `post_text` (`build_structured_input`). Answers, programs and gold evidence are supervision or evaluation data and are never model inputs; the gold-facts oracle is a labelled diagnostic that reads `gold_inds` keys by design.

## Planned for M4

- The single test evaluation of the selected pipeline. This requires re-running Notebook 10 at commit `7028afc`, because the retriever checkpoint was not kept.
- Categorized error analysis: retrieval, operand selection, period/unit interpretation, multi-step composition, ambiguity and other observed categories.
- Robustness checks for question rewording, reporting-period and unit perturbations.
- Abstention: a confidence signal, calibrated on dev, reported as accuracy against coverage.
- Inference record: per-question latency and cost under a documented setup.
