# Research notebook workflow

Notebooks are core research deliverables. They document executed inspection and experiments, while stable reusable logic lives under `src/finevidence/` with tests.

## Sequence

| Notebook | Milestone | Purpose | Status |
| --- | --- | --- | --- |
| `01_problem_and_dataset.ipynb` | M1 → M2 | Questions, source record, examples, and schema inspection. | Initial executable scaffold. |
| `02_finQA_eda.ipynb` | M2 | EDA for questions, answers, tables/text, missing values, and visualizations. | Create when data is inspected. |
| `03_finqa_preprocessing_analysis.ipynb` | M2 | Executed analysis of value formats, program grammar, evidence alignment, and inference-safe serialization. | Executed 2026-10-20. |
| `04_data_preprocessing.ipynb` | M2 | Executed reusable value, parser, diagnostics, and input-construction implementation. | Executed 2026-10-20. |
| `05_preprocessing_validation_and_answer_policy.ipynb` | M2 → M3 | Train-only preprocessing validation and display-answer evaluation policy. | Executed 2026-10-20. |
| `06_lexical_value_baseline.ipynb` | M3 | Executed train-fitted lexical value-selection baseline, evaluated on dev only. | Executed 2026-10-20. |
| `07_question_conditioned_evidence_value_selection.ipynb` | M3 | Retrieve-then-select lexical run, evaluated on dev only. | Executed 2026-10-20. |
| `08_conservative_numerical_reasoning.ipynb` | M3 | One-operation arithmetic over retrieved values, evaluated on dev only. | Executed 2026-10-20. |
| `09_baseline_selection_inspection.ipynb` | M3 | Train-structure inspection, official execution-accuracy convention, re-scoring of 06–08. | Executed 2026-10-21. |
| `10_retriever_training.ipynb` | M3 | Cross-encoder evidence retriever (GPU), dev recall@k against TF-IDF. | Executed on Kaggle T4 2026-10-22 (commit `7028afc`); the executed copy with interpretation is committed. |
| `11_program_generator.ipynb` | M3 | T5 program generator over retrieved facts; dev execution/program accuracy, retrieved vs gold-facts oracle. | Executed on Kaggle T4 2026-10-22 (commit `5f10139`); the executed copy with interpretation is committed. |
| `12_model_evaluation.ipynb` | M4 | Consistent comparison of approaches. | Create after comparable runs exist. |
| `13_error_analysis.ipynb` | M4 | Incorrect predictions, failure categories, limitations, improvements. | Create after evaluation. |

## Standards

- Start each notebook with a concise research question and why it matters.
- Use paths relative to the repository root, explicit seeds where relevant, and documented dependencies.
- Combine readable Markdown with focused, sequential code cells. Inspect actual examples and show only outputs produced by execution.
- Interpret observed evidence, not generic expectations. Record a limitation or decision that motivates the next experiment.
- Never add artificial outputs, invented metrics, synthetic observations, or claims of execution.
- Keep raw data, outputs, and large artifacts ignored. Move complex/reused code to `src/finevidence/` and test it outside the notebook.

The future notebooks are listed here rather than created as speculative, unexecuted code. Create each at its corresponding milestone.
