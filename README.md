# FinEvidence

FinEvidence answers numerical questions about financial reports and shows its work. For each question it retrieves the supporting table rows and sentences, generates an executable calculation program, and runs that program safely. The answer comes back with its evidence and its calculation, so an analyst can check it.

It is built and evaluated on [FinQA](https://github.com/czyssrs/FinQA): 8,281 questions written by finance experts over S&P 500 earnings reports. This repository contains code, configuration, notebooks and aggregate results only. Data and model weights are downloaded or trained locally and never committed.

## Status

M1–M3 are complete and awaiting review; M4 (evaluation and optimization) is next. See [docs/milestone-status.md](docs/milestone-status.md) for every deliverable and its evidence.

**Dev results** (883 questions, official FinQA execution accuracy, bootstrap 95% CI):

| System | Execution accuracy | Program accuracy |
| --- | --- | --- |
| Conservative arithmetic baseline | 3.96% [2.72, 5.32] | — |
| **Cross-encoder retriever + T5 program generator** | **59.23% [56.06, 62.51]** | **55.61%** |
| Same generator given only the gold facts (diagnostic) | 65.46% | 61.83% |

The retriever finds every gold fact in its top 5 for 87.0% of dev questions (TF-IDF: 66.0%). These are dev numbers from dev-selected checkpoints; the single held-out test evaluation is reserved for M4.

## Setup

Use Python 3.11–3.13.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,research]'
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The `model` extra (`torch`, `transformers`, `papermill`) is needed only to train models on a GPU (see below).

Download the pinned FinQA train and dev splits and verify their SHA-256 checksums. Existing files are verified, never overwritten; the test split is fetched only with `--include-test`.

```bash
python -m finevidence.data.acquisition
```

## Checks

```bash
ruff check .
ruff format --check .
pytest
```

## Reproducing the results

| Stage | How |
| --- | --- |
| Data audit and preprocessing (M2) | Run Notebooks 02–05 and 12 locally: `jupyter nbconvert --to notebook --execute --inplace notebooks/<name>.ipynb` |
| Baselines (M3) | Run Notebooks 06–09 locally (CPU, a few minutes each) |
| Retriever and generator (M3) | Run Notebooks 10–11 on a CUDA GPU, following [docs/gpu-setup.md](docs/gpu-setup.md) (Kaggle T4: about 0.5 h and 2.1 h) |

Every executed run is recorded in [docs/experiment-log.md](docs/experiment-log.md), with its command, commit, config, seed and observed metrics.

## Documentation

| Document | Contents |
| --- | --- |
| [problem-statement.md](docs/problem-statement.md) | M1: problem, users, business objective, success targets, feasibility |
| [dataset-card.md](docs/dataset-card.md) | Data source, schema, license, privacy, leakage rules |
| [m2-data-findings.md](docs/m2-data-findings.md) | Measured M2 audit findings |
| [preprocessing-plan.md](docs/preprocessing-plan.md) | Field contract and preprocessing decisions |
| [evaluation-plan.md](docs/evaluation-plan.md) | Split protocol, metric definitions, experiment protocols |
| [architecture.md](docs/architecture.md) | Pipeline and module responsibilities |
| [finqanet-baseline-plan.md](docs/finqanet-baseline-plan.md) | Design and step record for the retriever + generator |
| [experiment-log.md](docs/experiment-log.md) | Every executed experiment |
| [milestone-status.md](docs/milestone-status.md) | Deliverable-by-deliverable milestone evidence |
| [roadmap.md](docs/roadmap.md) | Current stage, M3 handoff, next task |
| [research-notes.md](docs/research-notes.md) | Verified external sources (paper, official code, license) |
| [notebooks/README.md](notebooks/README.md) | Notebook sequence and standards |

## Layout

```text
src/finevidence/   data, retrieval, generation, reasoning, evaluation packages
tests/             unit tests for reusable behavior
configs/           versioned experiment configurations
notebooks/         numbered, executed research record
docs/              project, data, evaluation and milestone records
data/, models/     local data and checkpoints (Git-ignored)
.agents/skills/    repository-local Codex workflow skills
```

Read [AGENTS.md](AGENTS.md) before contributing. The milestone contract is [docs/milestone-framework.md](docs/milestone-framework.md).

FinEvidence is a research prototype. It does not provide financial or investment advice.
