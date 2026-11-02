"""Kaggle GPU entry point for M4 iteration 2 (Notebook 15).

The launch script replaces __COMMIT__ with the pushed commit to run. This clones the public
repository at that commit, installs it, copies the dev artifacts from the attached private
dataset, and executes Notebook 15 with papermill. Everything under /kaggle/working is kept as
the kernel output: the executed notebook, the checkpoint and the prediction files.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/divyanshi-sachan/finevidence.git"
COMMIT = "__COMMIT__"
NOTEBOOK = "notebooks/15_hard_distractor_generator.ipynb"

work = Path("/kaggle/working")
repo = work / "finevidence"
subprocess.run(["git", "clone", "--quiet", REPOSITORY, str(repo)], check=True)
subprocess.run(["git", "checkout", "--quiet", COMMIT], cwd=repo, check=True)
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--quiet", "-e", ".[model]"], cwd=repo, check=True
)

processed = repo / "data" / "processed"
processed.mkdir(parents=True, exist_ok=True)
for artifact in Path("/kaggle/input").rglob("*.jsonl"):
    shutil.copy(artifact, processed / artifact.name)
    print("input artifact:", artifact.name, flush=True)

environment = {
    **os.environ,
    "FINEVIDENCE_MODEL_DIR": str(work / "models" / "generator-t5-base-hard-v1"),
}
subprocess.run(
    [
        sys.executable,
        "-m",
        "papermill",
        NOTEBOOK,
        str(work / "15_hard_distractor_generator_executed.ipynb"),
        "--log-output",
        "--cwd",
        "notebooks",
        "-k",
        "python3",
    ],
    cwd=repo,
    env=environment,
    check=True,
)
