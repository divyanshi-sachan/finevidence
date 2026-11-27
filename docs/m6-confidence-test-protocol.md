# Second test use: beam log-probability confidence — frozen protocol

Written on 2026-11-27, before any test beam score is read. Nothing below may change after the check is run; any deviation must be recorded in the experiment log.

## Why a second test use

The M4 test run (Notebook 18, [protocol](m4-test-protocol.md)) is spent. On dev, the top beam's length-normalized log-probability matched the 16-sample confidence without the sampling step ([experiment log, step 6a](experiment-log.md)). This check evaluates that one change once on test. The answers are unchanged: the test predictions and beam scores already saved by Notebook 18 (kernel `divyanshi92/finevidence-m4-test`, commit `4dea6a5`) are re-scored; nothing is decoded again.

## Fixed method

- **Answer:** the top of 4 beams, as in M4 (test execution accuracy stays 792/1147).
- **Confidence:** `beam_scores[0]`, the top beam's length-normalized log-probability.
- **Primary threshold:** answer when confidence ≥ **−0.0150** (dev: 55.6% coverage, 89.82% accuracy).
- **Secondary threshold:** ≥ **−0.0377** (dev: 74.4% coverage, 83.71% accuracy).
- Thresholds were taken from dev at the coverages of the M4 primary and secondary operating points.

## Reported

Coverage and accuracy on answered records at both thresholds with 95% Clopper–Pearson intervals, against the M4 16-sample results on the same test records (primary 52.14% / 87.79%; secondary 70.44% / 83.91%), described, not tested for significance. M1 target judged: ≥ 80% accuracy at ≥ 50% coverage at the primary threshold.

## Rules

- Run once by a script that reads only `beam_scores` and the saved `execution_correct` of each test record.
- No threshold or method is changed in response to the result. Whatever the result, it is reported.
- Latency is not measured by this check; the about 1.5 s per question figure remains an estimate until the M5 prototype measures it.
