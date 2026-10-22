# Intended architecture

The system will be organized as cooperating modules, not autonomous agents:

1. Ingest a financial question and report context.
2. Validate the FinQA example and schema.
3. Preprocess the question, including financial terms and period cues.
4. Select relevant table cells and narrative evidence.
5. Extract and normalize values, units, and periods.
6. Execute deterministic numerical operations when required.
7. Construct an answer tied to selected evidence.
8. Evaluate answers, reasoning, evidence support, and failures.

Implemented module boundaries: `finevidence.data` (loading, validation, preprocessing, annotation parsing), `finevidence.retrieval` (gold-key-compatible evidence segments and their numeric candidates), `finevidence.reasoning` (conservative arithmetic and the safe program executor), and `finevidence.evaluation` (display-answer, execution-accuracy and retrieval-recall metrics).

Initial baselines should be simple and reproducible: question-only or majority-style references where meaningful, lexical retrieval, constrained arithmetic, and transparent metrics. Model selection is deferred until data inspection and baselines establish a justified need.
