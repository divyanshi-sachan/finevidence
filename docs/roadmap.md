# FinEvidence roadmap

FinEvidence follows the six-stage Industry Track. The detailed objectives, deliverables, entry conditions, and exit conditions are defined in [milestone-framework.md](milestone-framework.md). This document tracks the intended sequence; it is not proof that a stage is complete.

| Milestone | Stage | Primary repository evidence |
| --- | --- | --- |
| M1 | Problem Definition & Business Case | Problem brief, user definition, business objective, measurable success criteria, feasibility analysis. |
| M2 | Data Understanding & Preparation | Verified data card, EDA, data cleaning/validation record, statistical analysis, privacy assessment. |
| M3 | Baseline & Model Development | Reproducible baseline, candidate approach, version-controlled implementation, experiment log. |
| M4 | Evaluation & Optimization | Evaluation report, inference record, categorized errors, improvement iterations, robustness tests. |
| M5 | Deployment Prototype | Working application or API, deployment record, monitoring strategy, failure handling. |
| M6 | Final Delivery | Technical report, repository handover, live demonstration, business presentation, viva preparation. |

## Current stage

**M3 — Baseline & Model Development** is active. M1 and M2 repository evidence exists, but formal milestone acceptance is still pending; the M2 license/permitted-use review and privacy assessment remain open. Three dev-only lexical/arithmetic runs are logged. [Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb) adopted official execution accuracy as the primary metric and selected a FinQANet-style baseline.

## Immediate next task

Implement the [FinQANet-style baseline plan](finqanet-baseline-plan.md): move segment construction into `src/`, add program-equivalence scoring, then train and evaluate the retriever (Notebook 10) and the program generator (Notebook 11) on dev. Keep the official test split reserved for final reporting.
