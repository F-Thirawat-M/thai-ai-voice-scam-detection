#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZIP_PATH="$SCRIPT_DIR/pre_trained_DF_RawNet2.zip"
CHECKPOINT_DIR="$SCRIPT_DIR/checkpoints"
CHECKPOINT_PATH="$CHECKPOINT_DIR/pre_trained_DF_RawNet2.pth"
PYTHON_BIN=${RAWNET2_PYTHON:-/Users/draft/Desktop/python/.venv/bin/python}

mkdir -p "$CHECKPOINT_DIR"

if [ ! -f "$ZIP_PATH" ] || ! unzip -t "$ZIP_PATH" >/dev/null 2>&1; then
    echo "Downloading a complete checkpoint archive..."
    "$PYTHON_BIN" "$SCRIPT_DIR/download_checkpoint.py" --output "$ZIP_PATH"
fi

unzip -t "$ZIP_PATH" >/dev/null
unzip -o "$ZIP_PATH" -d "$CHECKPOINT_DIR" >/dev/null

if [ ! -s "$CHECKPOINT_PATH" ]; then
    echo "Checkpoint extraction failed: $CHECKPOINT_PATH" >&2
    exit 1
fi

EXPECTED_ZIP_SHA256=db0f3e4ba6fdba23752e6e57e1507cd5b3de344d6a36c9699d4439be142dfbf5
EXPECTED_PTH_SHA256=52d8ad5f524a0f600c7c876d7a157a8f06c44a03504d0b2795c852f5e42c9127
ACTUAL_ZIP_SHA256=$(shasum -a 256 "$ZIP_PATH" | awk '{print $1}')
ACTUAL_PTH_SHA256=$(shasum -a 256 "$CHECKPOINT_PATH" | awk '{print $1}')
if [ "$ACTUAL_ZIP_SHA256" != "$EXPECTED_ZIP_SHA256" ]; then
    echo "Checkpoint ZIP checksum mismatch" >&2
    exit 1
fi
if [ "$ACTUAL_PTH_SHA256" != "$EXPECTED_PTH_SHA256" ]; then
    echo "Checkpoint file checksum mismatch" >&2
    exit 1
fi

echo "Checkpoint ready: $CHECKPOINT_PATH"
