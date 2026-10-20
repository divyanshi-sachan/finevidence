---
name: dataset-audit
description: "Audit a local research dataset for schema, quality, split integrity, and leakage risks before preprocessing or modeling."
---

# Dataset audit

Use when inspecting FinQA or another newly acquired dataset, especially before deciding on a schema or writing preprocessing.

1. Identify the exact source files, revision, acquisition date, and official split files. Do not assume field names or record counts.
2. Inspect a small, representative sample; report observed types, missingness, duplicate candidates, table/text structure, and parse failures.
3. Check split overlap without using held-out labels or evidence to tune behavior. Flag possible near duplicates rather than silently removing benchmark records.
4. Keep raw data immutable. Put derived inspection results in ignored data directories or clearly documented, small summaries.
5. Separate observed findings from hypotheses and write only reproducible claims to the dataset card or experiment log.

Do not download data, change official splits, or claim license terms are verified unless the task explicitly includes those actions and evidence is available.
