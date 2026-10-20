# FinEvidence — M1 Problem Definition & Business Case

**Status:** Draft for M1 review. This document defines intended outcomes and measurement plans; it does not report dataset findings or model performance.

## Project overview

| Item | Definition |
| --- | --- |
| Project | FinEvidence — Evidence-Grounded Financial Question Answering with Numerical Reasoning |
| Domain | Financial services / FinTech |
| Technical track | Natural language processing and machine learning |
| Primary dataset candidate | FinQA, pending M2 verification of its downloaded release |
| Intended deliverable | A reproducible research prototype, not financial advice or a production advisory system |

FinEvidence will investigate financial question answering over report narrative text and tables. Its intended answer format includes the numerical answer, supporting evidence, and an interpretable calculation trail when a calculation is required.

## Problem statement

Financial analysts frequently need to retrieve information from reports, compare performance across reporting periods, and calculate metrics such as revenue growth, expense changes, and profitability ratios. These tasks require more than finding similar text: a system must select the right figures, preserve their table or narrative context, distinguish periods and units, and perform the appropriate arithmetic.

General-purpose question-answering systems can select irrelevant evidence, confuse periods or units, calculate incorrectly, or produce confident answers that are difficult to verify. The FinEvidence problem is therefore:

> How can an NLP-based system identify relevant report evidence, perform transparent numerical reasoning, and present a verifiable financial answer while signalling when the available evidence is insufficient or ambiguous?

## Target users and use cases

**Primary users:** financial analysts and financial-research professionals who need to inspect the source behind a numerical answer.

**Secondary users:** corporate-finance teams, business analysts, and students learning financial-statement analysis. These groups are not the primary evaluation audience for the initial prototype.

| Use case | User need | FinEvidence responsibility |
| --- | --- | --- |
| Financial performance comparison | Compare revenue, expense, or profit values across periods. | Find candidate evidence, retain period and unit context, and expose the comparison calculation. |
| Numerical QA | Answer a question requiring arithmetic over report information. | Extract values, apply a deterministic calculation where supported, and show inputs. |
| Evidence retrieval | Locate the text passages and table entries that support a claim. | Return the selected evidence with a clear relationship to the answer. |
| Calculation verification | Audit how an answer was derived. | Present intermediate values, operation sequence, and assumptions where available. |
| Uncertainty handling | Avoid a misleading answer when evidence is missing or ambiguous. | Identify unsupported or ambiguous cases for review rather than imply certainty. |

## Business objective

The business objective is to investigate whether combining evidence retrieval, financial-value extraction, and deterministic numerical calculations can improve the reliability and verifiability of financial question answering compared with a transparent simpler baseline.

The intended M5 outcome is a narrow research prototype that assists evidence inspection. It must not provide investment recommendations, financial advice, or a guarantee of correctness on arbitrary documents.

## Research questions

1. How effectively can the system identify relevant financial evidence from tables and narrative text?
2. How accurately can it answer questions requiring multi-step numerical calculations?
3. Does explicit evidence retrieval and deterministic calculation improve answer reliability compared with a simpler baseline?
4. Which failures occur most often around values, units, reporting periods, evidence selection, and arithmetic?
5. Can the system recognize questions that cannot be answered reliably from the available evidence?

## Success criteria and measurement plan

These are measurement areas, not promised scores. Exact definitions, benchmark conventions, and any target thresholds will be finalized after M2 dataset inspection and M3 baseline results.

| Area | Planned measure | Decision it supports | Planned stage |
| --- | --- | --- | --- |
| Answer quality | Numerical answer accuracy, exact match, or benchmark-approved numerical equivalence. | Whether the system answers the task correctly. | M3–M4 |
| Reasoning | Correctness of calculation steps or reasoning program, where dataset annotations support it. | Whether arithmetic is valid and reproducible. | M3–M4 |
| Retrieval | Precision, recall, or ranking quality for supporting evidence. | Whether the answer is grounded in relevant report content. | M3–M4 |
| Evidence support | Review or metric indicating whether cited evidence supports the final answer. | Whether the answer is verifiable rather than merely plausible. | M4 |
| Robustness | Performance on meaningful wording, period, unit, and ambiguity variations. | Whether behavior is dependable beyond easy cases. | M4 |
| Abstention | Quality of identifying unsupported or insufficiently grounded questions. | Whether uncertainty is handled safely. | M4 |
| Efficiency | Inference latency and computational cost under a documented setup. | Whether the prototype is feasible to demonstrate and operate. | M3–M5 |

## Feasibility, assumptions, and risks

| Area | Current assessment | Risk or dependency | Planned control |
| --- | --- | --- | --- |
| Dataset | FinQA is the initial candidate because it is intended for financial QA with numerical reasoning. Its actual schema, evidence fields, splits, and license remain unverified. | The release may not support every planned measure or use case. | Inspect the official downloaded version in M2 before committing to field-level design. |
| Technical approach | Python, notebooks, standard data tools, transparent baselines, retrieval, and deterministic arithmetic support incremental development. | Table-text alignment, numeric normalization, and multi-step reasoning are technically challenging. | Start with simple, auditable baselines; isolate reusable components and test calculations. |
| Evaluation | The project can compare a baseline and candidate approach under one split protocol. | Leakage or inconsistent normalization would invalidate comparison. | Preserve publisher splits; tune only on training/validation data; document normalization and seeds. |
| Resources | The project is scoped to lightweight local experiments before considering larger models. | Compute or time may constrain advanced models. | Prefer small, reproducible methods and justify any heavier dependency with baseline evidence. |
| Safety and privacy | The prototype will use an approved public research dataset only. | Source reports may contain sensitive or licensed material; financial answers can be over-trusted. | Verify permitted use, keep data out of Git, show evidence, state limitations, and exclude advice. |
| Unsupported questions | The planned abstention behavior is a research objective, not a solved capability. | The system may answer despite weak evidence. | Define and test unsupported/ambiguous-case handling in M4. |

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

## M1 decision and next gate

This proposal defines the starting scope for review. M1 is ready for approval only after the problem, users, research questions, measurement plan, and feasibility assumptions are accepted by the project stakeholders.

Once approved, M2 begins by acquiring an approved FinQA release, recording provenance and permitted-use information, and executing the schema-inspection portion of `notebooks/01_problem_and_dataset.ipynb`.
