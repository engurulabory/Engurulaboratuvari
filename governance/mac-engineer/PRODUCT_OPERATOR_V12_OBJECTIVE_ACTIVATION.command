#!/bin/zsh
set -euo pipefail

ROOT="${0:A:h:h:h}"
exec /usr/bin/env PYTHONDONTWRITEBYTECODE=1 python3 -B \
  "$ROOT/tools/mac_engineer_product_operator_v12_foundation.py"
