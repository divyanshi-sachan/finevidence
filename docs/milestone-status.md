# Milestone status

Each row is a required deliverable from [milestone-framework.md](milestone-framework.md), with the repository evidence for it. **Done** means the evidence exists and was executed or verified; **formal acceptance** of each milestone belongs to the project reviewer. Last audited 2026-10-22.

## M1 — Problem Definition & Business Case: done, awaiting acceptance

| Deliverable | Status | Evidence |
| --- | --- | --- |
| Problem brief | Done | [problem-statement.md](problem-statement.md) |
| Primary user and workflow | Done | Problem statement: target users and use cases |
| Business objective and bounded NLP task | Done | Problem statement: business objective and scope boundaries |
| Measurable success metrics (user-facing and technical) | Done | Ten metrics with numeric targets fixed before test use, e.g. ≥ 55% test execution accuracy, 100% of answers with evidence, ≤ 1 s per question |
| Feasibility (data, evidence, reasoning, compute, risks, scope) | Done | Problem statement: feasibility table, verified against M2 data and measured M3 compute (2.6 GPU-hours) |
| Exit condition | Met | Problem, user, objective, targets and feasibility are precise enough to have guided M2–M3 |

## M2 — Data Understanding & Preparation: done, awaiting acceptance

| Deliverable | Status | Evidence |
| --- | --- | --- |
| Data card: source, schema, splits, license, limitations, provenance | Done | [dataset-card.md](dataset-card.md); MIT and CDLA-Permissive terms verified; pinned commit and SHA-256 checksums |
| EDA with real examples, distributions, missingness, table/text characteristics, quality | Done | [Notebook 02](../notebooks/02_finQA_eda.ipynb), [m2-data-findings.md](m2-data-findings.md) |
| Reproducible cleaning, validation and preprocessing with before/after examples | Done | [Notebooks 03](../notebooks/03_finqa_preprocessing_analysis.ipynb)–[05](../notebooks/05_preprocessing_validation_and_answer_policy.ipynb), `finevidence.data`, [preprocessing-plan.md](preprocessing-plan.md) |
| Statistical analysis and split comparisons | Done | [Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb): KS tests on all splits (D ≤ 0.077), chi-square train vs dev (V ≤ 0.035) |
| Privacy and sensitive-information assessment, handling and retention | Done | Notebook 12 scan; decisions in the data card's privacy section |
| Exit condition: clean documented splits, leakage checks, privacy recorded, no test tuning | Met | Official splits unchanged; the inference-input allowlist is tested; test used for no decision |

## M3 — Baseline & Model Development: done, awaiting acceptance

| Deliverable | Status | Evidence |
| --- | --- | --- |
| Reproducible baseline with documented configuration and protocol | Done | Notebooks [06](../notebooks/06_lexical_value_baseline.ipynb)–[08](../notebooks/08_conservative_numerical_reasoning.ipynb) with versioned configs; [evaluation-plan.md](evaluation-plan.md) |
| At least one justified candidate improvement, after the baseline was understood | Done | [Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb) justified the design from train structure; retriever ([10](../notebooks/10_retriever_training.ipynb)) and generator ([11](../notebooks/11_program_generator.ipynb)) |
| Version-controlled code, tests and configs | Done | `src/finevidence/`, 53 passing tests, `configs/*.toml`, commits referenced in the log |
| Experiment log with commands, data revision, split, seed, metrics, artifacts, limitations | Done | [experiment-log.md](experiment-log.md), including the failed out-of-memory attempt |
| Exit condition: baseline and candidate run under comparable conditions, observed results | Met | Same dev split, inputs and metric; results below |

**M3 results (dev, 883 records, execution accuracy with bootstrap 95% CI; Notebook 12):**

| System | Execution accuracy | Program accuracy |
| --- | --- | --- |
| Lexical value selection (06) | 0.57% | — |
| Question-conditioned selection (07) | 0.68% | — |
| Conservative arithmetic (08) | 3.96% [2.72, 5.32] | — |
| **Retriever + T5 generator (10–11)** | **59.23% [56.06, 62.51]** | **55.61%** |
| Gold-facts oracle (diagnostic) | 65.46% [62.29, 68.52] | 61.83% |

The generator beats conservative arithmetic on 493 paired records and loses on 5 (McNemar p ≈ 6e-139). Retriever all-gold recall@5 is 86.98%, against 66.02% for TF-IDF.

## M4–M6

| Milestone | Status | Entry condition |
| --- | --- | --- |
| M4 Evaluation & Optimization | Not started | M3 reviewed. First task: categorized error analysis of the 360 dev errors. The single test evaluation comes after methods and targets are fixed (the retriever must be retrained at `7028afc` first). |
| M5 Deployment Prototype | Not started | M4 evaluation, error analysis and robustness evidence exist |
| M6 Final Delivery | Not started | M5 prototype demonstrated |

## Known limitations carried forward

- Dev-selected checkpoints, reported on dev; one seed, one GPU type.
- The retriever checkpoint was not kept; the generator checkpoint is stored locally (`models/`, SHA-256 in the log).
- Abstention, robustness and single-question latency are not yet measured.
- The privacy scan is pattern-based and is a screen, not a complete audit.
