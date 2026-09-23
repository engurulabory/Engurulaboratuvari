#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EVIDENCE_ROOT="$HOME/Enguru/Evidence/MacEngineer/repository-fabric"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/acceptance-$STAMP"
mkdir -p "$RUN_DIR"

hold() {
  local reason="$1"
  print "STATE=HOLD"
  print "HOLD=$reason"
  print "RUN_DIR=$RUN_DIR"
  exit 2
}

cd "$ROOT"

python3 -m py_compile tools/mac_repository_fabric.py || hold "FABRIC_PYTHON_SYNTAX_FAILED"
print "FABRIC_PYTHON_SYNTAX=PASS"

python3 - <<'PY' || exit 20
import json
from pathlib import Path
p = Path("governance/mac-engineer/MAC_REPOSITORY_FABRIC_V1.json")
data = json.loads(p.read_text(encoding="utf-8"))
assert data["repositoryCount"] == 12
assert len(data["repositories"]) == 12
assert len({x["name"] for x in data["repositories"]}) == 12
print("FABRIC_MANIFEST=12_OF_12_PASS")
PY
[[ "$?" -eq 0 ]] || hold "FABRIC_MANIFEST_FAILED"

TARGETED="$RUN_DIR/targeted-tests.log"
python3 -B -m unittest tests.test_mac_repository_fabric -v >"$TARGETED" 2>&1 || {
  tail -n 80 "$TARGETED" || true
  hold "FABRIC_TARGETED_TESTS_FAILED"
}
print "FABRIC_TARGETED_TESTS=PASS"

FULL="$RUN_DIR/control-plane-regression.log"
python3 -B -m unittest discover -s tests -v >"$FULL" 2>&1 || {
  tail -n 80 "$FULL" || true
  hold "CONTROL_PLANE_REGRESSION_FAILED"
}
print "CONTROL_PLANE_REGRESSION=PASS"

SYNC="$RUN_DIR/fabric-sync.log"
if ! python3 tools/mac_repository_fabric.py sync >"$SYNC" 2>&1; then
  tail -n 120 "$SYNC" || true
  hold "REPOSITORY_FABRIC_SYNC_FAILED"
fi
cat "$SYNC"

grep -Fq "STATE=PASS" "$SYNC" || hold "FABRIC_STATE_PASS_REQUIRED"
grep -Fq "REPOSITORIES=12" "$SYNC" || hold "FABRIC_REPOSITORY_COUNT_REQUIRED"
grep -Fq "MIRRORS_PASS=12_OF_12" "$SYNC" || hold "FABRIC_12_OF_12_MIRRORS_REQUIRED"
grep -Fq "OFFLINE_QUEUE=PASS" "$SYNC" || hold "FABRIC_OFFLINE_QUEUE_REQUIRED"

EVIDENCE="$(grep '^EVIDENCE=' "$SYNC" | tail -n 1 | cut -d= -f2-)"
[[ -f "$EVIDENCE" ]] || hold "FABRIC_EVIDENCE_REQUIRED"

print "STATE=MAC_REPOSITORY_FABRIC_LOCAL_ACCEPTANCE_PASS"
print "REPOSITORIES=12"
print "MIRRORS=12_OF_12_PASS"
print "OFFLINE_QUEUE=PASS"
print "CONTROL_PLANE_REGRESSION=PASS"
print "EVIDENCE=$EVIDENCE"
print "NEXT_ACTION=MAC_REPOSITORY_FABRIC_RECONCILIATION"
