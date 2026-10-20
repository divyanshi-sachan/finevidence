---
name: evaluation-review
description: "Review FinEvidence evaluation design, metrics, error cases, and reproducibility before interpreting or reporting model results."
---

# Evaluation review

Use when creating, reviewing, or interpreting an evaluation run.

1. Confirm that the benchmark version, split protocol, answer normalization, and metric implementation follow documented source conventions.
2. Check that model selection did not use test labels, programs, or evidence. Verify configurations, seeds, and code revisions are recoverable.
3. Compare approaches under the same protocol and report coverage, failures, and inference cost alongside headline metrics.
4. Inspect wrong predictions and classify retrieval, parsing, unit/period, calculation, and ambiguity failures before proposing improvements.
5. Distinguish observed findings from untested explanations. Update `docs/experiment-log.md` and the evaluation/error-analysis notebooks only with executed evidence.

Do not convert a planned metric or a single example into a general performance claim.
