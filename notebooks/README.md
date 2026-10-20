# Research notebook workflow

Notebooks are core research deliverables. They document executed inspection and experiments, while stable reusable logic lives under `src/finevidence/` with tests.

## Sequence

| Notebook | Milestone | Purpose | Status |
| --- | --- | --- | --- |
| `01_problem_and_dataset.ipynb` | M1 → M2 | Questions, source record, examples, and schema inspection. | Initial executable scaffold. |
| `02_finQA_eda.ipynb` | M2 | EDA for questions, answers, tables/text, missing values, and visualizations. | Create when data is inspected. |
| `03_data_preprocessing.ipynb` | M2 | Preprocessing decisions, validation, and before/after examples. | Create after EDA decisions. |
| `04_baseline_models.ipynb` | M3 | Simple baselines and reproducible evaluation. | Create after preprocessing. |
| `05_financial_retrieval.ipynb` | M3 | Retrieval experiments and evidence selection. | Create when retrieval work begins. |
| `06_numerical_reasoning.ipynb` | M3 | Value normalization, calculations, and reasoning evaluation. | Create when reasoning work begins. |
| `07_model_evaluation.ipynb` | M4 | Consistent comparison of approaches. | Create after comparable runs exist. |
| `08_error_analysis.ipynb` | M4 | Incorrect predictions, failure categories, limitations, improvements. | Create after evaluation. |

## Standards

- Start each notebook with a concise research question and why it matters.
- Use paths relative to the repository root, explicit seeds where relevant, and documented dependencies.
- Combine readable Markdown with focused, sequential code cells. Inspect actual examples and show only outputs produced by execution.
- Interpret observed evidence, not generic expectations. Record a limitation or decision that motivates the next experiment.
- Never add artificial outputs, invented metrics, synthetic observations, or claims of execution.
- Keep raw data, outputs, and large artifacts ignored. Move complex/reused code to `src/finevidence/` and test it outside the notebook.

The future notebooks are listed here rather than created as speculative, unexecuted code. Create each at its corresponding milestone.
