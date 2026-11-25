#!/usr/bin/env bash
# Run one repository notebook on a private Kaggle GPU kernel:
#   kaggle/launch.sh <notebook path> <kernel slug> <model dir name> [reuse]
# With "reuse", the local models/<model dir name> (best adapter and history.json) is uploaded as a
# second private dataset and the notebook runs with FINEVIDENCE_REUSE_ADAPTER=1 (decode only).
# e.g. kaggle/launch.sh notebooks/16_llm_lora_generator.ipynb finevidence-m4-iteration3 generator-qwen2.5-1.5b-lora-v1
#
# Needs KAGGLE_USERNAME and a Kaggle API token in KAGGLE_API_TOKEN (KAGGLE_API_KEY is accepted
# too). Prints no secret. The current commit must already be pushed: the kernel clones it.
# Uploads two dev artifacts (retriever rankings and Notebook 11 predictions: record ids, keys,
# programs and scores) as a private dataset, then pushes the kernel.
set -euo pipefail

NOTEBOOK="${1:?notebook path}"
SLUG="${2:?kernel slug}"
MODEL_DIR_NAME="${3:?model dir name}"
REUSE="${4:-}"

: "${KAGGLE_USERNAME:?set KAGGLE_USERNAME to your Kaggle username}"
export KAGGLE_API_TOKEN="${KAGGLE_API_TOKEN:-${KAGGLE_API_KEY:?set KAGGLE_API_TOKEN or KAGGLE_API_KEY}}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KAGGLE="${KAGGLE:-$ROOT/.venv/bin/kaggle}"
COMMIT="$(git -C "$ROOT" rev-parse HEAD)"
DATASET="$KAGGLE_USERNAME/finevidence-dev-artifacts"
KERNEL="$KAGGLE_USERNAME/$SLUG"

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

SOURCES="\"$DATASET\""
if [ "$REUSE" = "reuse" ]; then
  ADAPTER_DATASET="$KAGGLE_USERNAME/finevidence-adapter"
  mkdir "$STAGE/adapter"
  cp "$ROOT/models/$MODEL_DIR_NAME/history.json" "$ROOT/models/$MODEL_DIR_NAME/best/"* "$STAGE/adapter/"
  cat > "$STAGE/adapter/dataset-metadata.json" <<JSON
{"title": "finevidence-adapter", "id": "$ADAPTER_DATASET", "licenses": [{"name": "other"}]}
JSON
  if "$KAGGLE" datasets status "$ADAPTER_DATASET" >/dev/null 2>&1; then
    "$KAGGLE" datasets version -p "$STAGE/adapter" -m "$MODEL_DIR_NAME at $COMMIT" --quiet
  else
    "$KAGGLE" datasets create -p "$STAGE/adapter" --quiet
  fi
  until [ "$("$KAGGLE" datasets status "$ADAPTER_DATASET" 2>/dev/null)" = "ready" ]; do sleep 15; done
  SOURCES="$SOURCES, \"$ADAPTER_DATASET\""
fi

sed -e "s/__COMMIT__/$COMMIT/" -e "s/__REUSE__/$REUSE/" -e "s#__NOTEBOOK__#$NOTEBOOK#" -e "s#__MODEL_DIR_NAME__#$MODEL_DIR_NAME#" \
  "$ROOT/kaggle/run_notebook.py" > "$STAGE/kernel/run.py"
cat > "$STAGE/kernel/kernel-metadata.json" <<JSON
{
  "id": "$KERNEL",
  "title": "$SLUG",
  "code_file": "run.py",
  "language": "python",
  "kernel_type": "script",
  "is_private": true,
  "enable_gpu": true,
  "enable_internet": true,
  "dataset_sources": [$SOURCES],
  "competition_sources": [],
  "kernel_sources": []
}
JSON
PUSH_OUTPUT="$("$KAGGLE" kernels push -p "$STAGE/kernel" 2>&1)"
echo "$PUSH_OUTPUT"
# The CLI can exit 0 after a refused push (for example the GPU session limit), so check the text.
if grep -qi "error" <<<"$PUSH_OUTPUT"; then
  echo "Kernel push failed; nothing is running." >&2
  exit 1
fi
echo "Pushed $KERNEL at commit $COMMIT. Check: $KAGGLE kernels status $KERNEL"
