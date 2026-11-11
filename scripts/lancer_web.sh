#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -x .venv/bin/python ]] || { echo "Lancez bash scripts/setup.sh" >&2; exit 1; }
.venv/bin/python -m ticket_agent serve &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM
.venv/bin/python -m ticket_agent ui
