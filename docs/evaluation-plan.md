# Evaluation plan

Choose metric implementations only after checking the official benchmark conventions for the downloaded FinQA release. The evaluation should report:

- numerical answer accuracy or exact match under the benchmark's accepted normalization;
- reasoning-program correctness when programs are available and evaluated;
- evidence retrieval quality, such as precision/recall or ranking measures against validated annotations;
- evidence support and answer faithfulness, including whether a cited value and calculation support the answer;
- categorized errors: retrieval, value parsing, unit/period interpretation, calculation, and ambiguity;
- robustness checks for ambiguous periods, units, and wording;
- seeds, data versions, runtime, hardware context where relevant, and inference cost.

Use one consistent split protocol across comparisons. Report coverage and uncertainty where appropriate, and separate observed results from planned measurements.
