#!/bin/zsh
set -euo pipefail
ROOT="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B "$ROOT/tools/mac_engineer_v08_self_engineering_baseline.py"
