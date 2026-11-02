#!/usr/bin/env bash
# Launch M4 iteration 2 (Notebook 15) as a private Kaggle GPU kernel.
#
# Needs KAGGLE_USERNAME and a Kaggle API token in KAGGLE_API_TOKEN (KAGGLE_API_KEY is accepted
# too). Prints no secret. The current commit must already be pushed: the kernel clones it.
# Uploads two dev artifacts (retriever rankings and Notebook 11 predictions: record ids, keys,
# programs and scores) as a private dataset, then pushes the kernel.
set -euo pipefail

: "${KAGGLE_USERNAME:?set KAGGLE_USERNAME to your Kaggle username}"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-${KAGGLE_API_KEY:?set KAGGLE_API_TOKEN or KAGGLE_API_KEY}}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KAGGLE="${KAGGLE:-$ROOT/.venv/bin/kaggle}"
COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
DATASET="$KAGGLE_USERNAME/finevidence-dev-artifacts"
KERNEL="$KAGGLE_USERNAME/finevidence-m4-iteration2"

git -C "$ROOT" fetch --quiet origin
if [ -z "$(git -C "$ROOT" branch -r --contains "$COMMIT")" ]; then
  echo "Commit $COMMIT is not on GitHub yet; push it first." >&2
  exit 1
fi

STAGE="$(mktemp -d)"
mkdir "$STAGE/data" "$STAGE/kernel"
cp "$ROOT/data/processed/retriever_bert_base_dev_rankings.jsonl" \
   "$ROOT/data/processed/generator-t5-base-dev-v1_dev_retrieved_predictions.jsonl" "$STAGE/data/"
cat > "$STAGE/data/dataset-metadata.json" <<JSON
{"title": "finevidence-dev-artifacts", "id": "$DATASET", "licenses": [{"name": "other"}]}
JSON
if "$KAGGLE" datasets status "$DATASET" >/dev/null 2>&1; then
  "$KAGGLE" datasets version -p "$STAGE/data" -m "artifacts for $COMMIT" --quiet
else
  "$KAGGLE" datasets create -p "$STAGE/data" --quiet
fi
until [ "$("$KAGGLE" datasets status "$DATASET" 2>/dev/null)" = "ready" ]; do sleep 15; done

sed "s/__COMMIT__/$COMMIT/" "$ROOT/kaggle/iteration2/run.py" > "$STAGE/kernel/run.py"
cat > "$STAGE/kernel/kernel-metadata.json" <<JSON
{
  "id": "$KERNEL",
  "title": "finevidence-m4-iteration2",
  "code_file": "run.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": true,
  "dataset_sources": ["$DATASET"],
  "competition_sources": [],
  "kernel_sources": []
}
JSON
"$KAGGLE" kernels push -p "$STAGE/kernel"
echo "Pushed $KERNEL at commit $COMMIT. Check: $KAGGLE kernels status $KERNEL"
