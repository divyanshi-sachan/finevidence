# FinEvidence

FinEvidence is a research and engineering project for evidence-grounded financial question answering with numerical reasoning. It will investigate how questions over financial reports can be answered from cited table and narrative evidence, while preserving the calculations, periods, and units behind each answer.

The initial dataset target is [FinQA](https://finqasite.github.io/). This repository does not include the dataset, model weights, or benchmark results.

## Requirements and setup

Use Python 3.11 through 3.13. Create an isolated environment, then install the local package with development and research tools:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,research]'
```

On Windows PowerShell, activate with `.venv\\Scripts\\Activate.ps1`.

## Development commands

```bash
ruff check .
ruff format --check .
pytest
```

Run `ruff format .` only when you intend to apply formatting changes.

## Research notebooks

Install the `research` extra above, then launch JupyterLab from the repository root:

```bash
jupyter lab
```

Download or verify the official public FinQA splits from the **Download or verify the official public splits** cell in Notebook 02. It uses a commit-pinned official URL, validates JSON before finalizing a new file, and never overwrites existing raw files:

```bash
jupyter lab notebooks/02_finQA_eda.ipynb
```

Run the executed EDA notebook afresh after a verified download:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/02_finQA_eda.ipynb
```

The initial M1 scaffold is [notebooks/01_problem_and_dataset.ipynb](notebooks/01_problem_and_dataset.ipynb). The executed M2 audit is [notebooks/02_finQA_eda.ipynb](notebooks/02_finQA_eda.ipynb), followed by the [preprocessing analysis](notebooks/03_finqa_preprocessing_analysis.ipynb), [tested preprocessing implementation](notebooks/04_data_preprocessing.ipynb), dev-only lexical and arithmetic runs (Notebooks 06–08), and the [baseline-selection inspection](notebooks/09_baseline_selection_inspection.ipynb) that adopts official execution accuracy. The planned M3 baseline is in [docs/finqanet-baseline-plan.md](docs/finqanet-baseline-plan.md). The notebook sequence, expected milestones, and reproducibility standards are documented in [notebooks/README.md](notebooks/README.md). Notebooks that depend on later milestones are intentionally not pre-filled.

## Layout

```text
src/finevidence/       Reusable package code
tests/                 Automated tests for stable package behavior
configs/               Versioned, non-secret experiment configuration
data/                  Local data layout and acquisition guidance (data ignored)
docs/                  Problem, architecture, data, evaluation, and roadmap records
notebooks/             Research-first, ordered Jupyter notebooks
.agents/skills/        Repository-local Codex workflow skills
```

Read [AGENTS.md](AGENTS.md) before contributing. The required Industry Track deliverables and milestone exit conditions are in [docs/milestone-framework.md](docs/milestone-framework.md); use [docs/roadmap.md](docs/roadmap.md) to track current work and [docs/experiment-log.md](docs/experiment-log.md) for executed experiments.
