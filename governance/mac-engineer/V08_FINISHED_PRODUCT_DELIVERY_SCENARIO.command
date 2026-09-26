#!/bin/zsh
set -euo pipefail

ROOT="$HOME/Enguru/Projects/Engurulaboratuvari"

export PYTHONDONTWRITEBYTECODE=1

exec python3 -B \
  "$ROOT/tools/mac_engineer_v08_finished_product_delivery.py"
