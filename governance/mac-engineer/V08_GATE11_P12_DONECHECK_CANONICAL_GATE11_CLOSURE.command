#!/bin/zsh
set -u
export PYTHONDONTWRITEBYTECODE=1

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

exec python3 -B \
  "$ROOT/tools/mac_engineer_v08_gate11_p12_closeout.py" \
  execute
