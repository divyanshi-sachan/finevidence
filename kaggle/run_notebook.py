"""Kaggle GPU entry point that executes one repository notebook.

kaggle/launch.sh fills in the commit, notebook and model directory name. This clones the public
repository at that commit, installs it, copies the dev artifacts from the attached private
dataset, and executes the notebook with papermill. Everything under /kaggle/working is kept as
the kernel output: the executed notebook, the checkpoint and the prediction files.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/divyanshi-sachan/finevidence.git"
COMMIT = "__COMMIT__"
MODEL_DIR_NAME = "__MODEL_DIR_NAME__"
NOTEBOOK = "__NOTEBOOK__"

work = Path("/kaggle/working")
repo = work / "finevidence"
subprocess.run(["git", "clone", "--quiet", REPOSITORY, str(repo)], check=True)
subprocess.run(["git", "checkout", "--quiet", COMMIT], cwd=repo, check=True)
subprocess.run(
    [sys.executable, "-m", "pip", "install", "--quiet", "-e", ".[model]"], cwd=repo, check=True
)

# Kaggle ships torchao 0.10; recent peft refuses to import next to it. Nothing here uses it.
subprocess.run([sys.executable, "-m", "pip", "uninstall", "--quiet", "-y", "torchao"], check=False)

processed = repo / "data" / "processed"
processed.mkdir(parents=True, exist_ok=True)
for artifact in Path("/kaggle/input").rglob("*.jsonl"):
    shutil.copy(artifact, processed / artifact.name)
    print("input artifact:", artifact.name, flush=True)

environment = {
    **os.environ,
    "FINEVIDENCE_MODEL_DIR": str(work / "models" / MODEL_DIR_NAME),
}
subprocess.run(
    [
        sys.executable,
        "-m",
        "papermill",
        NOTEBOOK,
        str(work / (Path(NOTEBOOK).stem + "_executed.ipynb")),
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
