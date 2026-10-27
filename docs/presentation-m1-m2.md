# FinEvidence — Presentation content (M1 + M2)

Every number below is taken from the repo records (`problem-statement.md`, `dataset-card.md`, `m2-data-findings.md`, `milestone-status.md`). Sources are listed per slide.

---

## PART A — M1: Problem Definition & Business Case (present this first)

### Slide 1 — Problem brief
- Analysts must find figures, compare periods and compute growth/ratios. Generic QA picks wrong evidence, mixes up units/periods, miscalculates, and is hard to verify.
- **Problem statement:** How can an NLP system identify relevant report evidence, perform transparent numerical reasoning, and present a verifiable answer while signalling when evidence is insufficient?
- Reference points (paper): finance experts **91.16%**, general crowd **50.68%**, TF-IDF single-op baseline **1.01%**. → needs domain skill; lexical matching fails.

### Slide 2 — User identification
- **Primary:** financial analysts / research professionals who must inspect the source behind a number.
- **Secondary:** corporate-finance teams, business analysts, finance students.
- Use cases: period comparison, numerical QA, evidence retrieval, calculation verification, uncertainty handling.

### Slide 3 — Business objective
- Show that **retrieval + an executable program** is more **accurate and verifiable** than simpler baselines, at a cost a small team can afford.
- Value = **verifiability**: every answer ships with cited facts + calculation, so the analyst checks a short trail instead of searching the report.
- Not financial advice; not a production advisory system.

### Slide 4 — Success metrics: what the research reports, what we aim for, what each metric means

**Images to use** (folder `screenshot/`): `execution_accuracy_comparison.png`
Targets apply to the **single held-out test run in M4**, fixed before test is touched. They are goals, not results.

**What the researchers reported (FinQA paper, Chen et al., EMNLP 2021; Table 2 unless noted):**
| System | Execution acc. | Program acc. |
|---|---:|---:|
| Finance experts (§4.3) | 91.16% | 87.49% |
| General crowd (§4.3) | 50.68% | 48.17% |
| TF-IDF + single operation | 1.01% | 0.90% |
| FinQANet, RoBERTa-base | 56.10% | 54.38% |
| FinQANet, RoBERTa-large (best) | 61.24% | 58.86% |

Caveat: the paper does not explicitly label Table 2 as the test set; we read it as test. These are context, not a controlled comparison with our system.

**Our metrics, what each one means, and our aim:**
| Area | Metric | What it means | Aim (test) | Dev so far |
|---|---|---|---|---|
| Answer quality | Execution accuracy | Run the predicted program; result (rounded to 5 decimals) must equal the official answer. Invalid or missing = wrong. Official FinQA rule. | **≥ 55%** (above the crowd, at least FinQANet RoBERTa-base) | 59.2% |
| Reasoning | Program accuracy | Predicted program is symbolically equivalent to the gold program (right steps, not just right number). | **≥ 52%** | 55.6% |
| Retrieval | All-gold recall@5 | Share of questions where **every** gold evidence fact is in the top 5 retrieved. A precondition for a correct answer. | **≥ 85%** | 87.0% (TF-IDF 66.0%) |
| Verifiability | Answers shown with facts + program + value | Every answer carries its evidence and calculation. | **100%** (M5 design requirement) | built into pipeline |
| Validity | Invalid-program rate | Share of outputs that fail to parse or execute. | **≤ 2%** | 0.8% |
| Grounding | Operand grounding | Share of numbers in the program that appear in the cited facts; catches invented numbers. | **≥ 95%** | 97.0% |
| Robustness | Accuracy drop under rewording / period change | How much accuracy falls when the question is rephrased or the period is perturbed. | **≤ 5 pts** | not yet measured (M4) |
| Abstention | Accuracy at stated coverage | The system may decline low-confidence questions; coverage = share it answers. Accuracy is measured on the answered ones. | **≥ 80% accuracy at ≥ 50% coverage** (provisional) | not yet measured (M4) |
| Latency | GPU time per question | Speed for interactive use (batched, T4). | **≤ 1 s** | 0.05 s retrieval + 0.19 s generation |
| Cost | Training compute | Reproducible on a free GPU. | **≤ 4 GPU-hours** | 2.6 GPU-hours |

**Why 55% and not higher:** the task is hard (crowd 50.68%, best published model 61.24%). Our dev score is optimistic because the checkpoint was chosen on dev, so the target leaves headroom. Expert level (91.16%) is the upper reference, and no target assumes it.

Say clearly: **targets, not results.** Robustness and abstention are not measured yet (M4).

### Slide 5 — Feasibility
| Area | Finding |
|---|---|
| Data | Verified: 8,281 labelled examples, programs + gold evidence for all, open licence |
| Technical | Measured on dev: retriever + T5 generator **59.2%** vs best rule-based **4.0%** |
| Evaluation | Our executor agrees with the official evaluator on all train/dev gold programs |
| Compute | 2.6 GPU-hours on a free Kaggle T4 (peak 9.55 GB) |
| Risks | Multi-step (3+) programs weak (28.8% dev); benchmark may not generalise; over-trust in answers |
| Scope | In: understanding, retrieval, reasoning, grounded answers. Out: advice, arbitrary documents, production |

Research questions: (1) evidence identification, (2) multi-step accuracy, (3) benefit over simple baseline, (4) dominant failures, (5) recognising unanswerable questions.

### Slide 6 — Proposed solution (answer to the problem)

**Images to use** (folder `screenshot/`): `pipeline_diagram.png`
Pipeline: **question + report page → evidence retriever → program generator → safe executor → answer shown with evidence and calculation.**
1. **Retriever:** fine-tuned `bert-base-uncased` cross-encoder scores every table row and sentence against the question; top 5 are kept.
2. **Program generator:** `t5-base` reads the question plus the top-5 facts and writes a FinQA-style program, e.g. `divide(100, 100), divide(3.8, #0)`.
3. **Executor:** a deterministic, non-`eval` interpreter runs the program (checked against the official FinQA evaluator on train/dev gold programs).
4. **Output:** answer + cited facts + program + executed value, so the analyst can verify it. Questions the system cannot support are meant to be flagged (abstention, planned for M4).
- Why this design: rule-based baselines reach only 0.6-4.0% dev execution accuracy; explicit retrieval plus an executable program gives both accuracy and an audit trail.
- Compute: 2.6 GPU-hours on a free Kaggle T4.

---

## PART B — The dataset (M2 starts here)

### Slide 7 — What is FinQA?
- Benchmark for **numerical reasoning over financial reports** (Chen et al., EMNLP 2021).
- Source: earnings-report pages of **S&P 500 companies, 1999–2019** (from FinTabNet).
- Questions written by **11 US finance experts** (CPAs, MBAs).
- Each example = one report page (text + table) + one question + the **reasoning program** that answers it + the **gold evidence** sentences/rows.
- Task: given question + page, produce the numeric answer *and* show the evidence and calculation.

### Slide 8 — Size and splits

**Images to use** (folder `screenshot/`): `dataset_splits.png`
| Split | Records | Share | File size |
|---|---:|---:|---:|
| Train | 6,251 | 75% | 78.2 MB |
| Dev | 883 | 10% | 11.0 MB |
| Test | 1,147 | 15% | 14.4 MB |
| **Total** | **8,281** | | over 2,789 report pages |

- Splits are by **report**: no input report is shared between splits (paper §4).
- Zero shared IDs across splits (verified).
- Acquisition: official repo, **pinned to commit `0f16e28`**, SHA-256 checksum verified on every load. Raw data is never committed or modified.
- Licence: repo is **MIT**; underlying FinTabNet data is **CDLA-Permissive**. Non-commercial research use; data not redistributed.

### Slide 9 — Structure of one record (11 top-level fields)

**Images to use** (folder `screenshot/`): `dataset_record_structure.png`
```
record
├── id, filename            → "ADI/2009/page_49.pdf-1"  (company / year / page – question no.)
├── pre_text   [list of sentences before the table]   (15 in the example)
├── post_text  [list of sentences after the table]    (35 in the example)
├── table      [list of rows, each a list of cell strings]
├── table_ori  [original un-normalised table]
├── table_retrieved / table_retrieved_all   ┐ derived by the original authors
├── text_retrieved  / text_retrieved_all    ┘ (excluded from our inputs)
└── qa  (12 fields)
    ├── question      "what is the the interest expense in 2009?"
    ├── answer        "380"      (display string; can be empty)
    ├── exe_ans       3.8        (executed answer: float or "yes"/"no")
    ├── program       "divide(100, 100), divide(3.8, #0)"
    ├── program_re    same program, nested form
    ├── steps         [{op, arg1, arg2, res}, …]
    ├── gold_inds     {"text_1": "if libor changes by 100 basis points …"}
    ├── ann_table_rows / ann_text_rows   annotated evidence positions
    ├── explanation   (empty in ~84% of records)
    ├── model_input, tfidftopn           derived by the original authors
```
Schema verified on all three splits: **no missing top-level or `qa` field in any record.**

### Slide 10 — A real example (train record `ADI/2009/page_49.pdf-1`)

**Images to use** (folder `screenshot/`): `dataset_example_record.png`, `dataset_example_table.png`
- **Text evidence:** "if libor changes by 100 basis points, our annual interest expense would change by $ 3.8 million."
- **Table:** 3 columns (label, Oct 31 2009, Nov 1 2008) × 4 rows of forward-exchange-contract fair values, e.g. `$ 6427`, `$ -23158 ( 23158 )`.
- **Question:** what is the interest expense in 2009?
- **Program:** `divide(100, 100), divide(3.8, #0)` → `#0` refers to the first step's result.
- **Gold evidence key:** `text_1` → zero-based index 1 in `pre_text + post_text`.
- Takeaway: the answer is not a span; it must be **computed**, and the evidence must be **found among ~50 sentences and rows**.

### Slide 11 — How evidence and programs are encoded

**Images to use** (folder `screenshot/`): `program_operations.png`, `gold_evidence_counts.png`
- Evidence keys: `table_n` = zero-based **row** n of `table`; `text_n` = zero-based sentence n of `pre_text + post_text`. Verified on real examples.
- Program = chain of operations; `#n` = result of step n; `const_n` = constants.
- Operations seen: `divide` (4,445 uses in train; 5,901 across all splits), `subtract` (2,739; 3,676), `add` (1,512; 1,952), `multiply` (567; 759), plus `greater`, `exp`, `table_average/max/min/sum`.
- Program length: median 1 operation, mean 1.54, max 6.
- Gold evidence counts: train 7,512 table + 3,180 text keys; dev 1,071 + 442; test 1,318 + 585.

### Slide 12 — Dataset at a glance (EDA)

**Images to use** (folder `screenshot/`): `nb02_figure1.png`, `nb02_figure2.png`
| | Train | Dev | Test |
|---|---:|---:|---:|
| Question words (median / mean) | 15 / 16.65 | 15 / 16.41 | 16 / 16.72 |
| Table rows (median / mean) | 6 / 6.34 | 6 / 6.27 | 6 / 6.55 |
| Table columns (median / mean) | 4 / 3.84 | 4 / 3.94 | 4 / 3.92 |
| Empty table cells | 1.83% | 1.65% | 1.71% |
| Numeric-looking cells | 74.8% | 75.8% | 75.7% |

Frequent question words: *total, percentage, change, net, percent, millions, december, average* → growth, change and ratio questions.

### Slide 13 — Why this data is hard (measured on train)

**Images to use** (folder `screenshot/`): `answer_types.png`
- **55.6%** of answers are percentages, **39.4%** other numbers.
- **40.5%** of programs need ≥ 2 operations.
- **54.4%** of questions need ≥ 2 evidence facts; **13.9%** mix table and text.
- **77.0%** mention a year → period must be resolved.
- Median context = **762 tokens**; **86.4% exceed 512** → evidence must be retrieved before reasoning.
- Messy number formats: `$ 6427` (space-tokenised, no commas), `( 23158 )` accounting parentheses, `-`, "n/a" markers, scale words.

---

## PART C — M2 (continued): Data Understanding & Preparation

### Slide 14 — Data card (summary)
Source, pinned commit, SHA-256 per split, schema, licence, privacy, limitations all documented in `dataset-card.md`. Open issue: provenance of author-derived fields (`table_retrieved`, `text_retrieved`, `model_input`, `tfidftopn`) → **excluded** from inputs.

### Slide 15 — Exploratory analysis & data quality

**Images to use** (folder `screenshot/`): `missing_fields.png`
| Finding | Evidence | Decision |
|---|---|---|
| Blank `answer` | 48 train / 12 dev / 14 test; all have `exe_ans` + program | Keep; use official `exe_ans` |
| Blank `explanation` | ~84% | Optional, never required |
| Empty `table_retrieved` / `text_retrieved` | 5–8% / 10–11% | Not used |
| Bad evidence key | 1 record: `RE/2010/page_120.pdf-2` has `text_-1` | Preserve and flag, don't repair |
| Repeated question text across splits | 16 train/dev, 7 train/test, 2 dev/test; 0 shared IDs; contexts differ | Keep official splits; report as caveat |
| Program grammar | Parser accepts 100% (6,251 / 883 / 1,147), non-executing | Parser only validates syntax |

Value formats found (string-match counts, train): currency 55,576; years 84,577; decimals 43,976; parentheses 14,348; percentages 13,479.

### Slide 16 — Data cleaning / preprocessing (what we did and did not do)

**Images to use** (folder `screenshot/`): `nb03_figure1.png`
- **Principle: preserve raw, derive separately.** Nothing deleted, nothing rewritten.
- `normalize_financial_value`: reversible candidate (currency, sign, percent, scale); ambiguous years/scale words stay unresolved.
- `parse_finqa_program`: no `eval`, safe parsing.
- `build_structured_input`: **allowlist** = `id, question, table, pre_text, post_text` only.
- `serialize_table_for_retrieval`: deterministic row/header rendering; verified to keep every non-empty cell on all 8,281 records.
- `audit_record_annotations`: flags issues without dropping records.
- Canonical answer: **official execution accuracy vs `exe_ans`** (display-answer comparator rejected correct values because answers are rounded and percentages scaled ×100).
- 17 tests at M2 (53 by M3).

### Slide 17 — Train / validation / test split
- **Official FinQA split kept unchanged**: 6,251 / 883 / 1,147.
- Roles: train fits models/indexes; dev for decisions; test **used once** in M4.
- Never fed as input: `program`, `program_re`, `exe_ans`, `answer`, `gold_inds`, `steps`, `ann_*`, and author-derived fields (a known label-leakage bug existed in the original `table_row_to_text`).
- **Statistical comparability (Notebook 12):** all KS statistics ≤ 0.077; Cramér's V ≤ 0.035; no significant train–dev label shift (smallest p = 0.074). Test labels were not analysed.

### Slide 18 — Privacy considerations

**Images to use** (folder `screenshot/`): `privacy_scan.png`
| Pattern | Train | Dev | Test |
|---|---:|---:|---:|
| SSN-like | 0 | 0 | 0 |
| Email | 0 | 0 | 1 (corporate) |
| Phone-like | 31 | 0 | 4 (mostly table-figure false positives) |
| URLs | 114 | 32 | 12 |
| Honorific + name | 14 | 0 | 0 |

- Public corporate disclosure; only named executives in public filings; no private individuals found.
- Regex screen, **not** a full audit (misses names without honorifics).
- Handling: data in git-ignored `data/`, never committed, no profiling of individuals, deletable and re-downloadable from the pinned commit.
- Use restriction: no financial advice.

### Slide 19 — Gate summary and hand-off
- M1 and M2: all five deliverables each done with executed evidence; **formal acceptance belongs to the project reviewer.**
- M2 exit condition met: clean documented splits, leakage checks, privacy recorded, no test tuning.
- Known limitations: regex privacy screen; derived-field provenance open; repeated question wording across splits; single seed.
- **Entry to later work:** M3 baselines were built on this foundation (best dev result 59.2% execution accuracy, labelled as dev, not test).

---

## BONUS — Early M3 result slide (BERT retriever, dev; source: experiment-log, Notebook 10)

**Images to use** (folder `screenshot/`): `dev_retrieval_recall.png`, `retriever_training_history.png`, `m3_dev_results.png`, `accuracy_by_program_length.png`

**Fine-tuned `bert-base-uncased` cross-encoder retriever** (3 random negatives per positive, 5 epochs, lr 2e-5, seed 42, best epoch 3 chosen on dev).

| k | BERT all-gold recall | TF-IDF all-gold recall |
|---:|---:|---:|
| 1 | 41.34% | 29.22% |
| 3 | **80.75%** | 53.45% |
| 5 | **86.98%** | 66.02% |
| 10 | 93.54% | 84.14% |

- "All-gold recall@k" = share of questions where **every** gold evidence fact is in the top k. It measures evidence availability, **not answer accuracy**.
- End-to-end execution accuracy with the T5 generator on top: **59.23%** dev (95% CI 56.06–62.51).
- Caveats: checkpoint selected on dev and reported on dev, so slightly optimistic; one seed; one GPU (T4).

---

## FINAL SLIDE — What we are working on next (M4 → M6)

**Images to use** (folder `screenshot/`): `roadmap.png`

Source: `roadmap.md`, `milestone-framework.md`, `milestone-status.md`. These are **plans**, not results.

**Now: M4 Evaluation & Optimization** (entry condition met: M3 reviewed, test split untouched)
1. **Categorized error analysis** of the 360 dev errors: retrieval misses, operand selection, period/unit confusion, multi-step composition, ambiguity. (Known weak spot: 3+ step programs at 28.8% dev accuracy; 115 dev records lack a gold fact in the top 5 and score only 27.8%.)
2. **Improvement iterations**, each tied to a hypothesis from the error analysis.
3. **Robustness tests:** question rewording, reporting-period and unit perturbations (target: drop ≤ 5 points).
4. **Abstention / uncertainty:** answer only when confident (target: ≥ 80% accuracy at ≥ 50% coverage; calibrated on dev).
5. **Single held-out test evaluation**, only after methods and targets are frozen. The retriever must first be retrained at commit `7028afc`, since its checkpoint was not kept.

**Next: M5 Deployment Prototype**
- Working app/API showing the answer, cited evidence, program and executed value (100% of answers).
- Local-serving instructions, monitoring plan (latency, errors, input quality, evidence failures), failure-handling policy for unsupported questions and bad inputs.
- Single-question latency measured (target ≤ 1 s GPU time).

**Last: M6 Final Delivery**
- Technical report, clean repository handover, live demo, business presentation, viva preparation.

**Entry gate to each step:** M5 starts only once M4 evaluation, error analysis and robustness evidence exist; no deployment-readiness claim before that.

---
## Suggested speaking order and time
1. M1: problem, users, objective, metrics, feasibility, proposed solution: ~4 min.
2. Dataset: structure first, then the real example: ~4 min.
3. Rest of M2 (quality, cleaning, split, privacy): ~3 min.
4. Early M3 result and next steps: ~2 min.

## Caveats to state out loud
- Test set not used yet; dev numbers are dev-selected.
- Targets are goals, not achieved results.
- Counts like "numeric-looking cells" are heuristic string matches.
