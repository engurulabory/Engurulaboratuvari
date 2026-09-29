#!/bin/zsh
set -e
ROOT="${0:A:h:h:h}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B tools/mac_engineer_package08_cap16_recovery_offline_continuity_field_proof.py
