# Data layout

Do not commit downloaded datasets here. The repository ignores these directories:

- `raw/`: unchanged source downloads, e.g. an official FinQA release.
- `interim/`: temporary conversion or inspection files.
- `processed/`: derived, versioned-ready inputs for experiments.

Before placing a dataset under `raw/`, record its source URL, access date, revision/commit if available, license or permitted-use status, and checksum when practical. Confirm its actual files and schema in `notebooks/01_problem_and_dataset.ipynb`; do not rely on assumed FinQA field names.
