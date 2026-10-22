# FinEvidence — M1 Problem Definition & Business Case

**Status:** M1 brief, revised 2026-10-22. The problem, users, scope and research questions are unchanged from the original M1 draft. The dataset and feasibility facts below are now verified in M2, and the success criteria have explicit numeric targets informed by M2 data analysis and M3 dev results. Every number is labelled as **verified** (from a source or the pinned data), **measured** (observed in this repository's executed runs) or **target** (a goal for later milestones, not a result).

## Project overview

| Item | Definition |
| --- | --- |
| Project | FinEvidence — Evidence-Grounded Financial Question Answering with Numerical Reasoning |
| Domain | Financial services / FinTech |
| Technical track | Natural language processing and machine learning |
| Dataset | FinQA, pinned to commit `0f16e28` of the official repository ([dataset-card.md](dataset-card.md)) |
| Intended deliverable | A reproducible research prototype that shows answers with evidence and calculations; not financial advice or a production advisory system |

FinEvidence answers questions about financial reports from their narrative text and tables. Each answer comes with the supporting evidence and an executable calculation trail.

## Problem statement

Financial analysts need to retrieve figures from reports, compare them across reporting periods, and calculate metrics such as growth rates, changes and ratios. That takes more than finding similar text: a system must select the right figures, keep their table or narrative context, distinguish periods and units, and do the right arithmetic.

General-purpose question-answering systems can select irrelevant evidence, confuse periods or units, calculate incorrectly, or give confident answers that are hard to verify. The FinEvidence problem is therefore:

> How can an NLP-based system identify relevant report evidence, perform transparent numerical reasoning, and present a verifiable financial answer while signalling when the available evidence is insufficient or ambiguous?

**Why the task is hard (measured on the FinQA train split, M2):**
- 55.6% of answers are percentages and 39.4% are other numbers ([Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb)).
- 40.5% of reasoning programs need two or more operations (Notebook 12).
- 54.4% of questions need two or more evidence facts (Notebook 12), and 13.9% combine table and text evidence ([Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb)).
- 77.0% of questions mention a year, so the period has to be resolved (Notebook 12).
- The median context (question, table rows and text) is 762 whitespace tokens, and 86.4% of contexts exceed 512, so the evidence has to be found before reasoning (Notebook 09).

**Reference points (verified, FinQA paper, Chen et al., EMNLP 2021):**
- Finance experts reach 91.16% execution accuracy, but a general crowd only 50.68% (§4.3). The task needs domain skill.
- A TF-IDF baseline with a single operation scores 1.01% (Table 2). Simple lexical matching does not work.

## Target users and use cases

**Primary users:** financial analysts and financial-research professionals who need to inspect the source behind a numerical answer.

**Secondary users:** corporate-finance teams, business analysts, and students learning financial-statement analysis. These groups are not the primary evaluation audience for the initial prototype.

| Use case | User need | FinEvidence responsibility |
| --- | --- | --- |
| Financial performance comparison | Compare revenue, expense, or profit values across periods. | Find candidate evidence, retain period and unit context, and expose the comparison calculation. |
| Numerical QA | Answer a question requiring arithmetic over report information. | Extract values, apply a deterministic calculation where supported, and show inputs. |
| Evidence retrieval | Locate the text passages and table entries that support a claim. | Return the selected evidence with a clear relationship to the answer. |
| Calculation verification | Audit how an answer was derived. | Present the program, its operands and the executed value. |
| Uncertainty handling | Avoid a misleading answer when evidence is missing or ambiguous. | Flag unsupported or low-confidence cases for review rather than imply certainty. |

## Business objective

Show that combining evidence retrieval with an executable reasoning program makes financial question answering **more accurate and more verifiable** than transparent simpler baselines, at a compute cost a small team can afford.

The value to the user is verifiability. Every answer arrives with the facts it used and the calculation that produced it, so an analyst checks a short trail instead of searching the report. The M5 prototype assists that inspection. It must not provide investment recommendations, financial advice, or a guarantee of correctness on arbitrary documents.

## Research questions

1. How effectively can the system identify relevant financial evidence from tables and narrative text?
2. How accurately can it answer questions requiring multi-step numerical calculations?
3. Does explicit evidence retrieval and deterministic calculation improve answer reliability compared with a simpler baseline?
4. Which failures occur most often around values, units, reporting periods, evidence selection, and arithmetic?
5. Can the system recognize questions that cannot be answered reliably from the available evidence?

## Success criteria

Targets apply to the **single held-out test evaluation in M4** unless stated otherwise; test has not been used yet. The "Measured so far" column is dev-only evidence from M3 ([experiment-log.md](experiment-log.md); intervals from [Notebook 12](../notebooks/12_milestone_audit_statistics_privacy.ipynb)).

| Area | Metric (definition in [evaluation-plan.md](evaluation-plan.md)) | Target | Measured so far (dev) | Basis for the target |
| --- | --- | --- | --- | --- |
| Answer quality | Execution accuracy (official FinQA convention, all records) | **≥ 55%** on test | 59.2% (bootstrap 95% CI 56.1–62.5%) | Above the general crowd (50.68%) and at least FinQANet RoBERTa-base (56.10% in Table 2), while allowing for the optimism of a dev-selected checkpoint. |
| Reasoning | Program accuracy (symbolic equivalence) | **≥ 52%** on test | 55.6% | Same margin below dev as execution accuracy. |
| Retrieval | All-gold recall@5 | **≥ 85%** on test | 87.0% (TF-IDF: 66.0%) | Complete evidence is a precondition for a correct answer. |
| Verifiability | Share of answers shown with cited facts, program and executed value | **100%** in the M5 prototype | Built into the pipeline output | Core business value; a design requirement, not a model score. |
| Program validity | Invalid-program rate | **≤ 2%** | 0.8% | An unexecutable program cannot be audited. |
| Grounding | Numeric literals found in the cited facts | **≥ 95%** | 97.0% | Invented numbers defeat evidence-based checking. |
| Robustness | Execution-accuracy drop under question rewording and period perturbations | **≤ 5 points** | Not yet measured (M4) | The answer should not depend on surface wording. |
| Abstention | Accuracy on the questions the system chooses to answer, at stated coverage | **≥ 80% accuracy at ≥ 50% coverage** | Not yet measured (M4) | When it answers, an assistant should be right most of the time. This target is provisional until the M4 dev calibration. |
| Efficiency | GPU time per question (batched, T4) | **≤ 1 s** | 0.05 s retrieval + 0.19 s generation | Interactive use. Single-question latency is measured in M5. |
| Cost | Total training compute | **≤ 4 GPU-hours** on a free-tier T4 | 2.6 GPU-hours (retriever 0.5 h, generator 2.1 h) | Reproducible on free hosted GPUs. |

**Upper reference:** finance experts reach 91.16% execution accuracy (FinQA paper §4.3). No target assumes expert-level performance.

## Feasibility, assumptions, and risks

| Area | Assessment (as of M3) | Risk or dependency | Control |
| --- | --- | --- | --- |
| Dataset | **Verified:** 8,281 public examples (6,251 / 883 / 1,147), from earnings reports of S&P 500 companies, 1999–2019, written by 11 finance experts. Every example has a reasoning program and gold evidence; the repository is MIT-licensed and the source reports are CDLA-Permissive. | Benchmark reports may not represent other document types. | Keep claims to FinQA-like reports; document limitations. |
| Technical approach | **Measured:** retriever + program generator reaches 59.2% dev execution accuracy, against 4.0% for the best rule-based baseline. | Multi-step programs remain weak (28.8% dev accuracy at 3+ steps). | M4 error analysis targets multi-step composition and distractor confusion. |
| Evaluation | **Verified:** the executor and program-equivalence checks agree with the official FinQA evaluator on all train/dev gold programs. | Selecting checkpoints on dev inflates dev numbers. | Test is used once in M4; dev numbers are labelled as dev. |
| Resources | **Measured:** 2.6 GPU-hours on a free Kaggle T4 for both models; peak memory 9.55 GB. | Free-tier GPU quotas and session limits. | Live progress, per-epoch checkpoints, and a setup guide ([gpu-setup.md](gpu-setup.md)). |
| Safety and privacy | **Measured:** public corporate disclosures; no SSN-like strings; 2 report pages name individuals (executives) in public filings. | Over-trust in financial answers. | Data stays out of Git; answers always show evidence; no advice. |
| Unsupported questions | Not yet measured. | The system may answer despite weak evidence. | Abstention target and calibration in M4. |

## Scope boundaries

### In scope

- Financial-question understanding.
- Retrieval of supporting text and table evidence.
- Interpretation of relevant financial values, units, and reporting periods.
- Deterministic numerical reasoning and calculation verification.
- Evidence-grounded answer construction, evaluation, robustness testing, and error analysis.

### Out of scope for the initial milestones

- Production financial advice, investment recommendations, or automated decisions.
- Guaranteed correctness for arbitrary financial documents.
- Large-scale enterprise integrations.
- Deployment before the core NLP approach has been evaluated.
- Expanding to additional datasets without a documented FinQA limitation.

## M1 decision and gate

M1's content is complete: problem, users, business objective, measurable success criteria and feasibility are recorded, and M2 and M3 have since executed against them. Formal M1 acceptance belongs to the project reviewer. The targets above are fixed before the M4 test evaluation and must not be adjusted after test results are seen.
