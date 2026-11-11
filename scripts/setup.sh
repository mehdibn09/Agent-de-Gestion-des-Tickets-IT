#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x .venv/bin/python ]]; then
 interpreter=""
 for candidate in python3.11 python3.12; do
  if command -v "$candidate" >/dev/null 2>&1; then interpreter="$candidate"; break; fi
 done
 [[ -n "$interpreter" ]] || { echo "Python 3.11 ou 3.12 requis" >&2; exit 1; }
 "$interpreter" -m venv .venv
fi
.venv/bin/python -c 'import sys; assert sys.version_info[:2] in [(3,11),(3,12)]'
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
[[ -f .env ]] || .venv/bin/python -m ticket_agent config
.venv/bin/python -m ticket_agent train
.venv/bin/python -m ticket_agent evaluate
.venv/bin/python scripts/check_setup.py
