# M4 evaluation report

Summary of the M4 evidence for review, written 2026-11-26. Every number below was observed in an
executed run recorded in [the experiment log](experiment-log.md); nothing is projected.

## Adopted pipeline

1. **Retriever:** `bert-base-uncased` cross-encoder (Notebook 10), retrained unchanged for the test
   run (dev all-gold recall@5 0.8822, within the frozen 1.5-point band of the original 0.8698).
2. **Inputs:** question plus the top 10 retrieved table rows and sentences.
3. **Generator:** Qwen2.5-1.5B-Instruct with a LoRA adapter (Notebook 17; `adapter_model.safetensors`
   SHA-256 `1646a66b…`), emitting a FinQA program run by the safe executor.
4. **Answer and confidence:** the top of 4 beams; confidence is the share of 16 sampled programs that
   execute to the same value. The system answers when all 16 agree (primary) or ≥ 12 agree (secondary).

## Improvement iterations (dev, 883 records)

| Iteration | Decision tested | Dev execution accuracy | Decision |
|---|---|---|---|
| M3 candidate (Notebook 11) | T5-base program generator, top 5 facts | 59.23% | baseline |
| 1 (Notebook 14) | Grounded beam selection; fewer facts | 61.95% (24 fixed, 0 broken) | adopted; fewer facts rejected |
| 2 (Notebook 15) | Hard-distractor retraining | 539 vs 547 correct (p = 0.53) | not adopted |
| 3 (Notebook 16) | Qwen2.5-1.5B LoRA generator | 69.08% (p = 4.5e-7) | adopted |
| 4 (Notebook 17) | 10 facts; sample-agreement confidence | 70.78% (p = 0.12); 89.41% at 55.6% coverage | adopted |

Dev numbers were used for selection and are therefore optimistic.

## Held-out test evaluation (Notebook 18, run once)

Run under the [frozen protocol](m4-test-protocol.md), written before any test prediction existed.

| Metric (test, n = 1,147) | Result | 95% CI |
|---|---|---|
| Execution accuracy | 69.05% (792) | 66.3–71.7% |
| Program accuracy | 65.56% (752) | 62.7–68.3% |
| Invalid programs | 0.35% | |
| Retrieval all-gold recall@5 / @10 | 86.84% / 92.68% | |
| Answer when all 16 agree | 87.79% accuracy at 52.14% coverage | 84.9–90.3% / 49.2–55.1% |
| Answer when ≥ 12 of 16 agree | 83.91% accuracy at 70.44% coverage | 81.2–86.4% / 67.7–73.1% |

**M1 targets:** ≥ 55% test execution accuracy — met. ≥ 80% accuracy at ≥ 50% coverage — met, narrowly
(the coverage interval's lower bound is 49.2%). ≤ 1 s per question — **not met**.

## Inference record

Tesla T4, fp16, commit `4dea6a5`, transformers 5.20.2, peft 0.21.2. Mean seconds per question:
retrieval 0.046, 4-beam decoding 1.48, 16-sample confidence 4.31, total 5.84. The per-record test
predictions and confidences (`m4-test_predictions.jsonl`) and the report are kept as Kaggle kernel
output (`divyanshi92/finevidence-m4-test`), not in the public repository; they derive from the test
split's content.

## Error analysis (Notebook 13, and Notebook 16 categories)

Errors of the iteration 3 pipeline on dev (273): operation 91, operand 85, retrieval miss 72, scale 13,
sign 9, near miss 2, invalid 1. Accuracy falls with program length (75.1% / 64.1% / 45.2% for 1 / 2 /
3+ steps) and is lower when evidence is in text (56.1%) or both table and text (53.9%) than in the
table only (77.9%). A manual review of 40 earlier errors found 35% (CI 22–50%) were ambiguous
questions, debatable gold labels or convention mismatches.

## Robustness (Notebook 19, dev, label-preserving)

| Perturbation | Accuracy | Change | Significant |
|---|---|---|---|
| None | 70.78% | — | — |
| Reworded question | 69.88% | −0.9 | no (p = 0.32) |
| Reversed fact order | 68.18% | −2.6 | yes (p = 0.018) |
| Irrelevant fact inserted | 68.86% | −1.9 | yes (p = 0.005) |
| Thousands separators in numbers | 42.92% | −27.9 | yes (p < 0.001) |

The separator failure comes from programs copying `136,104` as two arguments. FinQA itself has no
separators, so the test score is unaffected, but real documents do.

**Justified exception.** The contract asks for robustness to reporting periods and units. Changing a
period or unit changes the correct answer, so it needs new gold labels that M4 did not create. The
error analysis measures only the observed form of this risk (13 scale errors among 273), and M5 must treat unit and period handling as an unverified risk.

## Known limitations

- One seed and one GPU type for every result; no variance estimate.
- Accuracy falls sharply on 3+ step programs and text-heavy evidence.
- 5.84 s per question, dominated by the 16 samples used for confidence.
- Separator-formatted numbers break programs unless normalized first.
- Unit and period robustness is unmeasured.
- About half of test questions are answered at the primary threshold; the rest must be shown as
  unanswered, not guessed.

## Is a prototype justified?

Yes, with conditions. The pipeline meets both accuracy targets on a single held-out run and has a
calibrated way to decline. M5 must: normalize number formatting before generation; show the evidence
and executed program with every answer; withhold answers below the agreement threshold; and either
bring latency down (fewer samples, or confidence only when asked) or state the latency honestly.
