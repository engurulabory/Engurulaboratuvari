#!/bin/zsh
set -euo pipefail
ROOT="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
DECISION="${1:-REVIEW}"
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B "$ROOT/tools/mac_engineer_v07_human_threshold.py" --decision "$DECISION"
