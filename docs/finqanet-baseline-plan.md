# FinQANet-style retriever + program-generator baseline: M3 plan

**Status:** planned, not executed. No result in this document is observed unless it cites a notebook.

## Why this baseline

[Notebook 09](../notebooks/09_baseline_selection_inspection.ipynb) gives the train-split evidence for this choice:

| Observation (train) | Design consequence |
| --- | --- |
| 5,730/6,251 programs have ≤2 steps; the top 10 of 119 operation templates cover 86.8%. | Generate a short program over a fixed operation/constant vocabulary rather than free-form text. |
| 14,190/14,210 numeric literals occur in the record context (14,188 in gold evidence); 901 records use named constants. | Operands should be *copied* from retrieved evidence; constants come from a closed list. |
| Median context is 762 whitespace tokens; 5,398 records exceed 512. | A 512-token encoder needs a retriever stage first. |
| TF-IDF all-gold recall@3 is 53.8% overall and 28.5% for multi-fact records. | Train a retriever and judge it on all-gold recall, not any-gold recall. |
| Executing gold programs reproduces `exe_ans` for 6,251/6,251 train and 883/883 dev records. | `execute_program` can score generated programs under the official convention. |

This mirrors the two-stage design of the official FinQA code at the pinned commit. Its `code/retriever/config.py` uses `bert-base-uncased`, 3 random negatives per positive, top-5 retrieval, `max_seq_length=512`, batch size 16 and learning rate 2e-5. Its generator decodes over an operation list, a constant list and pointers to input-number positions, with `max_program_length=30`. FinEvidence reimplements the design and does not reuse the official code or derived files.

## Pipeline

1. **Segments.** Each raw table row and each `pre_text + post_text` sentence becomes a segment, keyed by the verified `table_n` / `text_n` convention. Table rows use FinEvidence's own header-paired serialization, never the publisher's `table_row_to_text` (which was repaired in 2022 after a label leak) and never the `table_retrieved`, `text_retrieved`, `model_input` or `tfidftopn` fields.
2. **Retriever.** A cross-encoder classifies `(question, segment)` pairs as gold or non-gold and ranks all segments in a record.
   - Training positives: train `gold_inds` keys. The flagged `text_-1` key is excluded and reported.
   - Training negatives: as in the official retriever, every non-gold segment joins one global pool, and each epoch draws `negatives_per_positive × positives` from it afresh (seeded). TF-IDF hard negatives are a separate, labelled ablation.
   - **Deliberate difference:** the official code uses the annotated `gold_inds` text for positives but renders negatives from the raw table. FinEvidence renders both from the raw context by key (`segment_retrieval_text`), so the classifier can't separate the classes by formatting.
   - Initial encoder: `bert-base-uncased` for comparability with the official setup. `roberta-base` is a later candidate.
3. **Generator.** The input is the question plus the top-k retrieved segments (k from config, starting at 3; varying it is an ablation). The output is a FinQA program string.
   - **Iteration 1, simplest working version:** fine-tune `t5-base` (or `flan-t5-base`) to emit the program string. The parser validates the output and the executor runs it.
   - **Iteration 2, only if needed:** if the operand-grounding check shows more than a small share of invented numbers, add a pointer/copy decoder over input numbers, as in FinQANet.
4. **Execution and scoring.** `finevidence.reasoning.execute_program` runs the program. `finevidence.evaluation.compare_execution` scores it against `exe_ans`.

## Training-data protocol and leakage

- The retriever is fit on train only. Dev is used for checkpoint and epoch selection and for choosing k. Test stays unloaded until the final M4 report.
- **Generator training context.** The official generator trains on `train_retrieve.json`, i.e. retriever outputs on train, which are in-sample. FinEvidence's starting point is gold facts plus sampled distractor segments, so that training doesn't depend on an overfit in-sample retriever. Training on retrieved train segments is a separate ablation, recorded with how its retrieval was produced.
- Prediction-time input stays within the documented allowlist (`id`, `question`, `table`, `pre_text`, `post_text`) through `build_structured_input`. Programs, `exe_ans`, answers and gold evidence are supervision only.

## Metrics (dev)

| Metric | Definition | Status |
| --- | --- | --- |
| Execution accuracy, **primary** | `compare_execution` against `exe_ans`, all 883 dev records in the denominator. | Implemented and tested. |
| Program accuracy | `compare_programs`: symbolic equivalence with the gold program, as in the official evaluator. | Implemented and tested (`sympy` core dependency). |
| Retrieval any/all-gold recall@k | `gold_recall_at_k`, k ∈ {1, 3, 5, 10}, with multi-fact records reported separately. | Implemented and tested. |
| Invalid-program rate | Share of generated programs that fail to parse or execute. | Planned. |
| Operand grounding rate | Share of generated numeric literals present in the retrieved segments. | Planned. |
| Display-answer accuracy, secondary | The existing comparator, kept for continuity with Notebooks 06–08. | Implemented. |

**Reference rows on dev:** TF-IDF retrieval recall; the conservative-arithmetic run re-scored under execution accuracy (35/883); and an oracle that gives the generator gold facts, which bounds generator quality independently of retrieval.

## Implementation steps

| Step | Deliverable | Exit evidence |
| --- | --- | --- |
| 1 ✅ | `src/finevidence/retrieval/segments.py`: `build_evidence_segments` (optional `table_0` header row) and `segment_numeric_candidates`, with tests. | **Done 2026-10-22.** Matches Notebook 08's former inline functions on all 7,134 train+dev records; the Notebook 08 re-run reproduces 32/871 display and 35/883 execution with byte-identical predictions. Notebooks 06, 07 and 09 keep their own table renderings, which differ, and are unchanged. |
| 2 ✅ | `src/finevidence/evaluation/program.py`: symbolic program equivalence. | **Done 2026-10-22.** Gold-vs-gold holds for 6,251/6,251 train programs; agrees with the official `equal_program` on 9,392/9,392 argument-swapped train variants. |
| 3 ✅ | Model dependencies as a separate `model` extra (`torch`, `transformers`); [gpu-setup.md](gpu-setup.md); `python -m finevidence.data.acquisition`; `configs/retriever_bert_base.toml` with the validated `load_retriever_config`. | **Done 2026-10-22 (CPU side).** The config loads and validates in tests; the acquisition helper verified local train/dev checksums. Not yet run on a GPU runtime. |
| 4 ✅ | `finevidence.retrieval.pairs` (tested) and `notebooks/10_retriever_training.ipynb` with `configs/retriever_bert_base.toml`. | **Done 2026-10-22 (Kaggle T4, commit `7028afc`).** Dev all-gold recall@5 0.8698 vs TF-IDF 0.6602; all-gold@3 0.8075 vs 0.5345; multi-fact all-gold@5 0.7709 vs 0.4497. Epoch 3 of 5 selected on dev. See the experiment log for limitations. |
| 5 | `notebooks/11_program_generator.ipynb` and `configs/generator_t5_base.toml`. | Dev execution accuracy, program accuracy, invalid and grounding rates, and the gold-facts oracle. |
| 6 | Experiment-log entries for steps 4–5. | Commit hash, data checksums, seed, GPU type, wall-clock time, metrics, limitations. |

M3 exits after step 5: the baseline and at least one candidate have been run under comparable conditions. Iteration 2 (the pointer decoder), retriever variants and error analysis then move to M4.

## Reproducibility on Colab/Kaggle

- Follow [gpu-setup.md](gpu-setup.md): clone at a recorded commit, `pip install -e '.[model,research]'`, then `python -m finevidence.data.acquisition`, which downloads train/dev only and verifies their checksums.
- Fix seeds in Python, NumPy and torch, and log `torch.backends.cudnn` determinism settings. Record the GPU model, because results can vary across hardware.
- Keep checkpoints and predictions out of Git: use ignored `models/` and `data/processed/`, or a Drive path set by an environment variable. Log each artifact's path and size.
- Training time and cost are recorded once observed; this plan does not estimate them.

## Risks and open questions

- **Generator hallucination.** A text-to-text generator may invent numbers. The grounding rate measures this, and iteration 2 addresses it.
- **Multi-fact retrieval.** Low all-gold recall caps execution accuracy. The gold-facts oracle separates retrieval failures from generation failures.
- **Repeated question wording across splits** (16 train/dev pairs, different contexts) could inflate dev slightly. It's reported as a caveat, with no deduplication.
- **The license and permitted-use review** is still open in M2 and must be resolved before any model or demo is shared externally.
