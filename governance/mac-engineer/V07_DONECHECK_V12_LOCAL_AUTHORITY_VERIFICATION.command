#!/bin/zsh
set -euo pipefail
ROOT="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B "$ROOT/tools/mac_engineer_donecheck_v12_local_authority_verification.py"
