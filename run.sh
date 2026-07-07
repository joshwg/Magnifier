#!/bin/sh
# Launch the Magnifier in its own .venv.
# Uses the venv's python directly (no activation needed) so it works
# regardless of what shell / PATH you invoke it from.

# Resolve this script's directory (portable across macOS/Linux).
DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

VENV_PY="$DIR/.venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
    echo "No .venv found at $DIR/.venv" >&2
    echo "Create it with:" >&2
    echo "  python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

exec "$VENV_PY" "$DIR/magnifier.py" "$@"
