# Architecture

FinEvidence is a pipeline of tested modules, not a set of autonomous agents. Each stage reads only what it needs, and every model input is built from the allowlisted raw fields (`id`, `question`, `table`, `pre_text`, `post_text`).

## Pipeline (implemented in M3)

```
question + report (table, pre_text, post_text)
        │
        ▼
1. Load and verify ── finevidence.data          pinned splits, SHA-256 check, schema validation
        │
        ▼
2. Segment ───────── finevidence.retrieval      one segment per table row and sentence, keyed like gold_inds
        │                                       (table_n, text_n), rendered with column headers
        ▼
3. Retrieve ──────── Notebook 10                bert-base-uncased cross-encoder scores every
        │            (finevidence.retrieval)     (question, segment) pair; keep the top 5
        ▼
4. Generate ──────── Notebook 11                t5-base writes a FinQA program, e.g.
        │            (finevidence.generation)    subtract(5829, 5735), divide(#0, 5735)
        ▼
5. Execute ───────── finevidence.reasoning      safe executor (no eval), official FinQA value rules
        │
        ▼
answer + cited facts + program + executed value
        │
        ▼
6. Evaluate ──────── finevidence.evaluation     execution and program accuracy, retrieval recall,
                     finevidence.generation      invalid rate, operand grounding
```

## Modules

| Package | Responsibility | Key public functions |
| --- | --- | --- |
| `finevidence.data` | Load, validate and preprocess raw records; parse programs without executing them; check evidence keys; download pinned data | `load_finqa_split`, `build_structured_input`, `parse_finqa_program`, `validate_evidence_key`, `normalize_financial_value`, `acquisition.download_finqa_splits` |
| `finevidence.retrieval` | Evidence segments, retriever training and ranking pairs, retriever config | `build_evidence_segments`, `build_training_pairs`, `build_ranking_pairs`, `sample_epoch_pairs`, `load_retriever_config` |
| `finevidence.generation` | Generator inputs (training, retrieved, gold-facts oracle), config, per-record scoring | `build_training_examples`, `build_retrieved_examples`, `build_oracle_examples`, `score_program_prediction`, `load_generator_config` |
| `finevidence.reasoning` | Safe program executor; the conservative arithmetic baseline | `execute_program`, `reason_over_candidates` |
| `finevidence.evaluation` | Metrics | `compare_execution`, `compare_programs`, `gold_recall_at_k`, `operand_grounding`, `compare_display_answers` |

Training loops live in Notebooks 10–11, because they need a GPU and `torch`. Everything they call that runs without a GPU is in `src/` and unit-tested (`pytest`, 53 tests).

## Baselines kept for comparison

Notebooks 06–08 use TF-IDF retrieval with extractive value selection or one-operation conservative arithmetic. They are transparent lower bounds: 0.6–4.0% dev execution accuracy, against 59.2% for the pipeline above.

## Design decisions

- **Program generation, not answer generation.** The model writes an executable program, so every answer carries an auditable calculation and the arithmetic is exact.
- **Shared rendering for training and inference.** Positives and negatives (retriever), and gold and distractor facts (generator), are all rendered from the raw context by key, never from annotated `gold_inds` text, so no class can be told apart by its formatting.
- **No publisher-derived inputs.** `table_retrieved`, `text_retrieved`, `model_input` and `tfidftopn` are excluded, because the official repository documents an earlier label leak in its table-to-text conversion.
- **Planned for M4–M5:** an abstention signal, so low-confidence questions are flagged rather than answered, and a serving interface that presents answer, evidence and calculation together.
