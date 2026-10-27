# GPU runtime setup (Colab, Kaggle, or local)

Notebooks 10–11 train models and need a CUDA GPU. Everything else, including `pytest`, runs on CPU without the `model` extra. These steps have not yet been run on a hosted runtime; record the first run in the experiment log.

## 1. Get the code at a recorded commit

The runtime clones from `origin` (`https://github.com/divyanshi-sachan/finevidence.git`), so the commit you want must be pushed first. Use a specific commit rather than a moving branch, and write that hash into the experiment log.

```python
!git clone https://github.com/divyanshi-sachan/finevidence.git
%cd finevidence
!git checkout <commit-hash>
```

If the repository is private, store a fine-grained read-only token in the platform's secret store (Colab "Secrets", Kaggle "Add-ons → Secrets") and read it with the platform API at runtime. Never paste a token into a notebook cell, config file or URL that is saved with the notebook.

## 2. Install

```python
!pip install -q -e '.[model,research]'
```

Colab and Kaggle already ship a CUDA build of `torch`, and the `model` extra only sets lower bounds, so pip should keep the existing build. If `import finevidence` fails right after an editable install, restart the runtime once and re-run from the `%cd` cell.

## 3. Fetch and verify data

```python
!python -m finevidence.data.acquisition
```

This downloads only the commit-pinned `train` and `dev` splits, checks their SHA-256 values against [dataset-card.md](dataset-card.md), and never overwrites existing files. M3 development doesn't need the official test split, and it isn't downloaded unless you pass `--include-test`; reserve that for the final M4 run.

## 4. Persist checkpoints outside the runtime

Hosted runtimes are temporary. Point the model directory at persistent storage through an environment variable; it overrides `[output].model_dir` in `configs/retriever_bert_base.toml`.

```python
# Colab
import os

from google.colab import drive

drive.mount("/content/drive")
os.environ["FINEVIDENCE_MODEL_DIR"] = "/content/drive/MyDrive/finevidence/retriever-v1"
```

On Kaggle, use `/kaggle/working/...` and save the notebook version so the outputs are kept. Checkpoints and predictions must never be committed to Git.

## 5. Run a training notebook with live progress

Use papermill (installed by the `model` extra). It streams each cell's output while the run is in progress and saves the executed notebook at the end. Notebook 10 prints about 20 progress lines per epoch, showing step, loss, elapsed time and time left, plus an estimate for the remaining epochs after each one. It also rewrites `history.json` after every epoch.

```python
!papermill notebooks/10_retriever_training.ipynb /kaggle/working/10_retriever_training_executed.ipynb --log-output --cwd notebooks -k python3
```

`jupyter nbconvert --execute` also works, but it shows nothing until the whole notebook finishes.

### Notebook 11 also needs the Notebook 10 dev rankings

`data/processed/` is not in Git, so upload `retriever_bert_base_dev_rankings.jsonl` to the runtime. On Kaggle: **Add Input → Upload → New Dataset**, then use the path Kaggle shows under `/kaggle/input/...`. Then run:

```python
import os

os.environ["FINEVIDENCE_RANKINGS_PATH"] = (
    "/kaggle/input/<dataset>/retriever_bert_base_dev_rankings.jsonl"
)
os.environ["FINEVIDENCE_MODEL_DIR"] = "/kaggle/working/generator-t5-base-dev-v1"
```

The notebook refuses a rankings file whose SHA-256 differs from `configs/generator_t5_base.toml`.

## 6. Record the environment

The first cell of each training notebook should print, and the experiment log should record, the commit hash, Python, `torch` and `transformers` versions, `torch.cuda.get_device_name(0)`, the seed, and wall-clock training time.

```python
import platform
import subprocess

import torch
import transformers

commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
print(commit.stdout.strip())
print(platform.python_version(), torch.__version__, transformers.__version__)
print(torch.cuda.is_available() and torch.cuda.get_device_name(0))
```

Results can differ slightly across GPU types and library versions even with fixed seeds, so compare runs only when their environment records match.
