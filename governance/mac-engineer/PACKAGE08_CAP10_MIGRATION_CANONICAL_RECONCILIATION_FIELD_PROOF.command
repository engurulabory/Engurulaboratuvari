#!/bin/zsh
set -euo pipefail

ROOT="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"

export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT:$ROOT/tools"

exec python3 -B \
  "$ROOT/tools/mac_engineer_package08_cap10_migration_canonical_reconciliation_field_proof.py"
