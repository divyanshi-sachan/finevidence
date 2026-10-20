# Industry Track milestone framework

This is the working delivery contract for FinEvidence. It turns the Industry Track milestones into repository evidence and decision gates. A milestone is complete only when its required deliverables are reviewable, based on observed evidence where applicable, and its exit condition is met.

## M1 — Problem Definition & Business Case

**Objective:** Frame a real business problem as a well-scoped NLP task and define success before implementation begins.

**Required deliverables:**

- Problem brief in `docs/problem-statement.md`.
- Identification of the primary user and the decision or workflow they need to support.
- Business objective and the bounded FinEvidence NLP task.
- Measurable success metrics, including an operational or user-facing measure and technical evaluation measures.
- Feasibility analysis covering data availability, evidence requirements, numerical reasoning needs, cost/compute, risks, and scope boundaries.

**Exit condition:** The problem, user, business objective, success criteria, and feasibility assumptions have been recorded and are precise enough to guide data acquisition and evaluation design. Metrics may be targets at this stage; they are not results.

## M2 — Data Understanding & Preparation

**Objective:** Understand, clean, and prepare data responsibly for modelling.

**Required deliverables:**

- Data card with verified source, schema, splits, license/permitted-use status, limitations, and provenance.
- Exploratory analysis with real examples, distributions, missingness, table/text characteristics, and data-quality observations.
- Reproducible cleaning, validation, and preprocessing decisions with before/after examples.
- Statistical analysis appropriate to observed variables and split comparisons.
- Privacy and sensitive-information assessment, including handling and retention decisions.

**Exit condition:** Clean, documented splits are ready for baseline modelling; leakage checks and privacy considerations are recorded. Do not use test labels, evidence, or reasoning programs to tune the system.

## M3 — Baseline & Model Development

**Objective:** Establish a fair baseline and iterate toward a stronger approach.

**Required deliverables:**

- A working, reproducible baseline with a documented configuration and evaluation protocol.
- At least one justified candidate improvement, implemented only after the baseline is understood.
- Version-controlled code, tests for reusable behavior, and configurations required to reproduce runs.
- An experiment log containing commands, data revision, split, seed, observed metrics, artifacts, and limitations.

**Exit condition:** A baseline and at least one candidate approach have been run under comparable conditions. Results must be observed, not estimated or copied from external work.

## M4 — Evaluation & Optimization

**Objective:** Evaluate models rigorously, understand errors, and improve responsibly.

**Required deliverables:**

- Documented evaluation using the agreed benchmark conventions and held-out protocol.
- Model inference record, including inputs/outputs or a safe reproducible sample and performance/cost context.
- Improvement iterations with the decision each iteration was intended to test.
- Categorized error analysis covering retrieval, parsing, period/unit interpretation, calculation, ambiguity, and other observed categories.
- Robustness testing for question wording, reporting periods, units, and other meaningful risks.

**Exit condition:** Comparative evaluation, error categories, improvement decisions, and robustness evidence are documented. The team can state known limitations and choose whether a prototype is justified.

## M5 — Deployment Prototype

**Objective:** Turn the selected approach into a functioning, monitored system that could plausibly run in production.

**Required deliverables:**

- Working application or API that presents answers with evidence and calculation context.
- Deployment or reproducible local-serving instructions, including environment/configuration requirements.
- Monitoring strategy for availability, latency, errors, input quality, answer/evidence failures, and cost where relevant.
- Failure-handling policy for invalid inputs, missing evidence, numerical errors, unsupported questions, and degraded dependencies.

**Exit condition:** A demonstrable prototype functions on representative inputs, has measured performance, and documents monitoring and failure handling. It must not hide uncertainty or present unsupported financial answers as certain.

## M6 — Final Delivery

**Objective:** Deliver a professional, business-ready handover.

**Required deliverables:**

- Technical report covering the problem, data, methods, evaluation, limitations, and reproducibility.
- Clean GitHub-ready repository with setup, run, test, and demonstration instructions.
- Live demonstration using a prepared, reproducible scenario.
- Business presentation that connects user value, evidence, performance, risk, and next steps.
- Viva preparation material that explains trade-offs, results, limitations, and ownership of the implementation.

**Exit condition:** The complete package can be independently reviewed and demonstrated, with claims traceable to code, data documentation, and executed results.

## Cross-milestone operating rules

1. Preserve a single source of truth: durable decisions belong in `docs/`, executed experiments in `docs/experiment-log.md`, and data/model analysis in the numbered notebooks.
2. Keep raw data, model artifacts, credentials, and sensitive material out of Git by default.
3. Make all metrics, comparisons, and conclusions reproducible from versioned code, configuration, data provenance, and documented commands.
4. Record risks, limitations, and unresolved questions as they are discovered; do not postpone them until final reporting.
5. Review the previous milestone's exit condition before starting implementation work for the next milestone.
