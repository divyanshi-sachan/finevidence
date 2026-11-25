# FinEvidence roadmap

FinEvidence follows the six-stage Industry Track. The detailed objectives, deliverables, entry conditions, and exit conditions are defined in [milestone-framework.md](milestone-framework.md). This document tracks the sequence and the current stage; [milestone-status.md](milestone-status.md) maps every deliverable to its evidence.

| Milestone | Stage | Primary repository evidence |
| --- | --- | --- |
| M1 | Problem Definition & Business Case | Problem brief, user definition, business objective, measurable success criteria, feasibility analysis. |
| M2 | Data Understanding & Preparation | Verified data card, EDA, data cleaning/validation record, statistical analysis, privacy assessment. |
| M3 | Baseline & Model Development | Reproducible baseline, candidate approach, version-controlled implementation, experiment log. |
| M4 | Evaluation & Optimization | Evaluation report, inference record, categorized errors, improvement iterations, robustness tests. |
| M5 | Deployment Prototype | Working application or API, deployment record, monitoring strategy, failure handling. |
| M6 | Final Delivery | Technical report, repository handover, live demonstration, business presentation, viva preparation. |

## Current stage

**M1–M3 deliverables are complete and ready for review; formal acceptance is pending.** The 2026-10-22 audit closed the remaining M2 items: license terms verified, a privacy assessment and statistical split comparison added in Notebook 12, and M1 success criteria given numeric targets. M4 is in progress: the categorized error analysis is done.

## M3 handoff (2026-10-22)

- **Completed deliverables.** Baselines: lexical value selection, question-conditioned selection and conservative arithmetic (Notebooks 06–08). Evaluation convention: official execution and program accuracy, safe executor, retrieval recall (Notebook 09). Candidate: a cross-encoder retriever (Notebook 10) and a T5 program generator (Notebook 11), all with versioned configs, tested `src/` code and experiment-log entries.
- **Observed dev results (execution accuracy, 883 records).** Conservative arithmetic 0.0396; retriever + generator **0.5923** (program accuracy 0.5561); gold-facts oracle 0.6546. Retriever all-gold recall@5 is 0.8698, against 0.6602 for TF-IDF.
- **Validation.** `ruff check`, `ruff format --check` and `pytest` pass. The executor and program-equivalence checks were validated against the official evaluator on train/dev gold programs. Both GPU runs were re-scored locally from their saved artifacts and matched exactly.
- **Known limitations and risks.** Checkpoints were selected on dev and reported on dev. Each result is a single seed on one GPU type. The retriever checkpoint was not kept, so it must be retrained at `7028afc` before test-time retrieval.
- **M4 entry condition.** M3 results reviewed; test split still untouched. First M4 task: categorized error analysis of the 360 dev errors (retrieval, operand selection, period/unit, multi-step composition, ambiguity), then robustness checks. The single test evaluation happens only after these decisions are fixed.

## Immediate next task

M4 has started. The categorized dev error analysis is executed ([Notebook 13](../notebooks/13_error_analysis.ipynb)): 272 of 360 errors occur with all gold facts retrieved, and the gold-facts oracle mostly helps by removing distractors. A manual review of 40 sampled errors found 14 (35%, CI 22–50%) that are ambiguous questions, debatable gold labels or convention mismatches. Improvement iteration 1 ([Notebook 14](../notebooks/14_inference_iteration.ipynb)) adopted grounded beam selection: dev execution accuracy 61.95% (from 59.23%; 24 fixed, 0 broken). Passing fewer facts was rejected. Iteration 2 ([Notebook 15](../notebooks/15_hard_distractor_generator.ipynb)) retrained the generator with hard distractors on a Kaggle T4: 539 vs 547 with grounded selection (57 fixed, 65 broken, p = 0.53), so it was not adopted. Iteration 3 ([Notebook 16](../notebooks/16_llm_lora_generator.ipynb)) fine-tuned Qwen2.5-1.5B-Instruct with LoRA on a Kaggle T4: dev 610/883 (0.6908) vs 547 (109 fixed, 46 broken, p = 4.5e-7), adopted as the current generator. Iteration 4 ([Notebook 17](../notebooks/17_llm_top10_self_consistency.ipynb)) gave it 10 facts and 16 sampled programs: dev 625/883 (0.7078, +15, p = 0.12), and the share of samples agreeing with the answer reaches 89.41% accuracy at 55.6% coverage and 84.17% at 74.4% (dev-selected, to be confirmed on test). Next: robustness checks, abstention and the inference record on dev, then retrain the retriever at `7028afc` and run the single test evaluation. The official test split stays reserved for the final M4 run.
