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
REUSE_ADAPTER = "__REUSE__" == "reuse"

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

model_dir = work / "models" / MODEL_DIR_NAME
if REUSE_ADAPTER:
    adapter = next(Path("/kaggle/input").rglob("adapter_model.safetensors"))
    (model_dir / "best").mkdir(parents=True, exist_ok=True)
    for item in adapter.parent.iterdir():
        if item.is_file() and item.name != "dataset-metadata.json":
            name = "history.json" if item.name == "history.json" else f"best/{item.name}"
            target = model_dir / name
            shutil.copy(item, target)
    print("reusing adapter:", sorted(p.name for p in (model_dir / "best").iterdir()), flush=True)

environment = {
    **os.environ,
    "FINEVIDENCE_MODEL_DIR": str(model_dir),
    "FINEVIDENCE_REUSE_ADAPTER": "1" if REUSE_ADAPTER else "0",
    # Reduces CUDA memory fragmentation with variable-length batches.
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
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
