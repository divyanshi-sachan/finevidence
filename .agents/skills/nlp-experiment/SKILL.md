---
name: nlp-experiment
description: "Plan or implement a reproducible FinEvidence NLP experiment with explicit splits, configuration, baselines, and observed results."
---

# NLP experiment

Use for a concrete preprocessing, retrieval, reasoning, or model experiment after the relevant data is available.

1. State the question, hypothesis, dataset revision, splits, metric, baseline, and stopping criterion before implementing.
2. Store non-secret settings in `configs/`; use a fixed seed when randomness is involved. Keep train, validation, and test roles separate.
3. Begin with the smallest transparent baseline that can answer the question. Put reusable logic in `src/finevidence/` and cover stable behavior with tests.
4. Log only commands and metrics that were actually executed. Include failures, data exclusions, runtime context, and limitations when they affect interpretation.
5. Update the relevant numbered notebook with concise rationale, real intermediate inspection, and an evidence-based conclusion.

Do not choose a costly model or report comparative performance without a completed, reproducible baseline run.
