#!/bin/zsh
set -e

ROOT="${0:A:h:h:h}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1

exec python3 -B tools/mac_engineer_package08_cap19_internet_research_harvest_astra_field_proof.py
