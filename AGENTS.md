# FinEvidence contributor guidance

## Project purpose

FinEvidence researches evidence-grounded financial question answering with numerical reasoning over financial-report tables and narrative text. The intended pipeline is modular NLP/ML software, not a collection of autonomous application agents. The primary dataset target is FinQA; its exact downloaded schema, license, and statistics must be verified from the acquired version before being stated as facts.

## Repository map

- `src/finevidence/`: reusable implementation. `data` validates and loads local data; later modules will own preprocessing, retrieval, reasoning, evaluation, and shared utilities.
- `notebooks/`: numbered research record. Keep notebooks linear, executable, and tied to an observed dataset or experiment.
- `tests/`: fast tests for stable reusable behavior.
- `configs/`: non-secret, versioned experiment settings.
- `data/`: ignored raw/intermediate/processed data and its acquisition guidance.
- `docs/`: durable project decisions, architecture, dataset notes, evaluation plan, roadmap, and experiment log.
- `.agents/skills/`: focused, repository-local Codex workflow skills.

## Working rules

1. Read this file and the relevant source, tests, configuration, and documentation before editing.
2. Prefer small, focused, testable changes. Preserve unrelated user changes.
3. Keep code straightforward Python: explicit names, small functions, type hints for public interfaces, and no premature abstractions.
4. Do not invent dataset facts, benchmark scores, outputs, citations, licensing conclusions, or completion claims. Label hypotheses and unverified items clearly.
5. When an interface, architecture, data assumption, or workflow changes, update the corresponding README or `docs/` record in the same change.

## Industry Track milestone governance

- Treat [docs/milestone-framework.md](docs/milestone-framework.md) as the delivery contract for M1–M6 and [docs/roadmap.md](docs/roadmap.md) as the current-stage tracker.
- Work in milestone order. Do not represent a milestone as complete until its required deliverables and exit evidence exist; explicitly record a justified exception when a deliverable cannot yet be produced.
- Keep a clear distinction between planned work, executed evidence, and a deliverable ready for review. Update the experiment log and the relevant document or notebook as work progresses.
- Do not begin modelling before M2 has documented clean, leak-free splits and data decisions. Do not claim deployment readiness before M4 evaluation, error analysis, and robustness evidence exist.
- Every milestone handoff must name the completed deliverables, validation performed, known limitations or risks, and the next milestone's entry condition.

## Data, leakage, and security

- Keep raw, interim, processed data, checkpoints, and outputs in their respective ignored directories. Never commit datasets, weights, credentials, or sensitive report material by default.
- Preserve official train/validation/test boundaries. Fit preprocessing, retrieval indexes, normalization rules learned from data, and model parameters only on training data unless a documented evaluation protocol says otherwise.
- Do not inspect test labels, reasoning programs, or evidence to tune systems. Record dataset version/source and split provenance for every experiment.
- Use environment variables for secrets; never print, commit, or place secrets in notebooks or configs.

## Reproducibility and notebooks

- Use explicit paths relative to the repository root, fixed seeds where randomness exists, versioned configurations, and the experiment log.
- Follow [notebooks/README.md](notebooks/README.md): combine concise Markdown with focused cells, inspect real examples, and interpret only observed outputs.
- Do not add notebook output JSON by hand. Save reusable or complex notebook logic under `src/finevidence/` and test it outside the notebook.

## Quality checks

- Target Python 3.11–3.13. Manage dependencies in `pyproject.toml`; justify additions and avoid heavyweight downloads during setup.
- Before handoff, run relevant checks: `ruff check .`, `ruff format --check .`, and `pytest`. State exactly what was run and any limitation.
- Add or update tests for changed stable behavior. Do not suppress lint or test failures without documenting why.

## Definition of done

A task is complete only when the requested behavior and documentation are implemented, relevant tests/checks have been run or their limitations reported, data-leakage and security implications are addressed, and no result is represented as observed when it was not executed.
