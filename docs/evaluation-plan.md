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

## Primary answer metric: official execution accuracy

From M3 onward, the primary answer metric follows the official FinQA evaluator at the pinned commit (`code/evaluate/evaluate.py`, verified 2026-10-21). A predicted program or value is executed, a numeric result is rounded to five decimals, and it must equal `exe_ans` exactly. Every record stays in the denominator, and invalid or missing predictions count as incorrect.

- `finevidence.reasoning.execute_program` reimplements the official value rules on top of the non-executing parser, without `eval`. Program `%` literals are divided by 100, `const_m1` is −1, and table operations look up rows by their first cell. It reproduces `exe_ans` for 6,251/6,251 train and 883/883 dev gold programs ([Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb)).
- `finevidence.evaluation.compare_execution` applies the exact-equality rule.
- The display-answer comparator below is kept as a secondary metric. Notebook 09 shows it accepts the gold executed value for only 2,203 of 6,083 train records with numeric `exe_ans`, because display answers are rounded and percentages are scaled by 100. Display accuracy should not be read as an upper-bounded reasoning score.
- Program accuracy: `finevidence.evaluation.compare_programs` mirrors the official `equal_program`. Each distinct literal/constant token of the gold program, and each whole table step, becomes a symbol. A prediction that uses any other token is wrong. Otherwise both programs are expanded and compared after `sympy.simplify`. Expressions are built from sympy objects, never by `sympify`-ing program text. Tokens match verbatim, so `100` and `const_100` are different. On train it holds gold-vs-gold for 6,251/6,251 programs and agrees with the official function on 9,392/9,392 argument-swapped variants (2026-10-22).
- Retrieval is reported as any-gold and all-gold recall@k with `finevidence.evaluation.gold_recall_at_k`.

## Question-conditioned selection protocol

The Notebook 07 experiment ranks raw table rows and text passages with the question, then ranks candidates from the top three evidence segments using question-plus-local-context similarity. Gold evidence and reasoning annotations are unavailable at prediction time and are read only post prediction for diagnostics. The experiment uses the fixed display-answer comparator and dev-only protocol already defined for the lexical baseline.

## Conservative arithmetic protocol

Notebook 08 performs only add, subtract, multiply, and divide over two safely parsed candidates from train-fitted lexical retrieval. It abstains for ambiguous intent, insufficient operands, incompatible currency/percent/scale/period metadata, and zero denominators. Published FinQA programs are never executed. Coverage and answered-case accuracy must be reported with overall display-answer accuracy so abstention cannot mask performance.

## Display-answer comparator policy

The reusable comparator in `finevidence.evaluation` evaluates the raw FinQA `answer` field only; it never reads `exe_ans` to calibrate or replace a display-answer reference.

- An empty reference answer is `unavailable_reference`: retain the record and report it separately, but exclude it from the display-answer denominator.
- Isolated signed integers/decimals with an optional percent marker are numeric answers. Percentage status must match. Comparison tolerance is `max(1e-4 absolute, 1e-4 relative)`.
- Other non-empty strings are compared after case-folding and whitespace collapse. Currency/unit/date/mixed strings remain text; they are never silently coerced to numeric values.
- A missing or empty prediction is reported as unsupported, rather than counted as a match.

The policy was inspected on train annotations in `05_preprocessing_validation_and_answer_policy.ipynb`. It is fixed before dev baseline evaluation and must not be tuned on the official test split.

## Baseline protocol

`06_lexical_value_baseline.ipynb` fits TF–IDF vocabulary only on train questions and raw train context. It evaluates on dev only, selecting a raw table cell, numeric text span, or yes/no text span from the dev record's allowlisted context. It is an extractive lexical value-selection baseline, not a numerical-reasoning system. The official test file is reserved for final reporting.
