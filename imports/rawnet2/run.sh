#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON_BIN=${RAWNET2_PYTHON:-/Users/draft/Desktop/python/.venv/bin/python}

exec "$PYTHON_BIN" "$SCRIPT_DIR/infer.py" "$@"
