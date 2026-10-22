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

**M1–M3 deliverables are complete and ready for review; formal acceptance is pending.** The 2026-10-22 audit closed the remaining M2 items: license terms verified, a privacy assessment and statistical split comparison added in Notebook 12, and M1 success criteria given numeric targets. M4 has not started.

## M3 handoff (2026-10-22)

- **Completed deliverables.** Baselines: lexical value selection, question-conditioned selection and conservative arithmetic (Notebooks 06–08). Evaluation convention: official execution and program accuracy, safe executor, retrieval recall (Notebook 09). Candidate: a cross-encoder retriever (Notebook 10) and a T5 program generator (Notebook 11), all with versioned configs, tested `src/` code and experiment-log entries.
- **Observed dev results (execution accuracy, 883 records).** Conservative arithmetic 0.0396; retriever + generator **0.5923** (program accuracy 0.5561); gold-facts oracle 0.6546. Retriever all-gold recall@5 is 0.8698, against 0.6602 for TF-IDF.
- **Validation.** `ruff check`, `ruff format --check` and `pytest` pass. The executor and program-equivalence checks were validated against the official evaluator on train/dev gold programs. Both GPU runs were re-scored locally from their saved artifacts and matched exactly.
- **Known limitations and risks.** Checkpoints were selected on dev and reported on dev. Each result is a single seed on one GPU type. The retriever checkpoint was not kept, so it must be retrained at `7028afc` before test-time retrieval.
- **M4 entry condition.** M3 results reviewed; test split still untouched. First M4 task: categorized error analysis of the 360 dev errors (retrieval, operand selection, period/unit, multi-step composition, ambiguity), then robustness checks. The single test evaluation happens only after these decisions are fixed.

## Immediate next task

Start M4 with a categorized error analysis of the Notebook 11 retrieved-condition dev errors, using the saved predictions in `data/processed/`. Keep the official test split reserved for the final M4 run.
