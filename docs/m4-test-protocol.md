# M4 single test evaluation: frozen protocol

Written on 2026-11-25, before any test prediction exists. Nothing below may change after Notebook 18
is run; any deviation must be recorded as such in the experiment log.

## Pipeline (fixed on dev)

1. **Retriever:** the Notebook 10 cross-encoder (`bert-base-uncased`, `configs/retriever_bert_base.toml`),
   retrained unchanged on Kaggle because the original checkpoint was not kept (kernel
   `divyanshi92/finevidence-m4-retriever-rerun`). The rerun is accepted only if its dev all-gold
   recall@5 is within 1.5 points of the original 0.8698; this check reads dev labels only.
2. **Inputs:** question plus the top 10 retrieved segments (`build_retrieved_examples`,
   `facts_per_input = 10`), source truncated at 1,024 tokens.
3. **Generator:** the Notebook 17 adapter `models/generator-qwen2.5-1.5b-lora-top10-v1/best`
   (`adapter_model.safetensors` SHA-256 `1646a66b99ae80c1b738420d94b6d589af0b1796b03c9d8cd915ea433a58b4f5`)
   on `Qwen/Qwen2.5-1.5B-Instruct`, fp16, `configs/generator_qwen_lora_top10.toml`.
4. **Answer:** the top of 4 beams.
5. **Confidence:** the share of 16 sampled programs (temperature 0.7, top-p 0.95, seed 42) whose
   executed value equals the answer's (0 if the answer does not execute).

## Reported metrics (test, all 1,147 records in the denominator)

- **Primary:** execution accuracy (official rounding to 5 decimals against `exe_ans`) with a 95%
  Clopper–Pearson interval.
- Program accuracy, invalid-program rate, operand grounding, retrieval all-gold recall@5 and @10.
- **Selective answering:** the system answers when confidence ≥ **1.0** (all 16 samples agree;
  primary threshold) and, as the one secondary operating point, ≥ **0.75**. Both report coverage
  and accuracy on answered records with 95% intervals, plus the full accuracy–coverage curve as a
  description only.
- **M1 targets judged:** execution accuracy ≥ 55% at full coverage; ≥ 80% accuracy at ≥ 50%
  coverage at the primary threshold.

## Dev expectations (dev-selected, therefore optimistic)

Execution accuracy 0.7078; threshold 1.0: 55.6% coverage, 89.41% accuracy; threshold 0.75: 74.4%
coverage, 84.17% accuracy. These dev numbers used the original retriever's rankings.

## Rules

- Test labels, programs and `gold_inds` are read only by the scoring cells, after all predictions
  are written. The notebook runs once; a crash before scoring may be rerun unchanged, and any rerun
  is logged.
- No method, threshold or setting is changed in response to test results.
