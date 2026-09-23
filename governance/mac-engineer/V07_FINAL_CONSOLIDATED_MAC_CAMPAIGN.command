#!/bin/zsh
set -euo pipefail
ROOT="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
export PYTHONDONTWRITEBYTECODE=1
if command -v caffeinate >/dev/null 2>&1; then
  exec caffeinate -i -m python3 -B "$ROOT/tools/mac_engineer_v07_final_consolidated_campaign.py"
fi
exec python3 -B "$ROOT/tools/mac_engineer_v07_final_consolidated_campaign.py"
