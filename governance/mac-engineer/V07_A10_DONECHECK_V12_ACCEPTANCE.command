#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EVIDENCE_ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.7/a10-acceptance"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$STAMP"
mkdir -p "$RUN_DIR"

hold() {
  local reason="$1"
  print "STATE=HOLD"
  print "HOLD=$reason"
  print "RUN_DIR=$RUN_DIR"
  exit 2
}

cd "$ROOT"

python3 -m py_compile tools/mac_engineer_donecheck_v12_bridge.py || hold "A10_BRIDGE_PYTHON_SYNTAX_FAILED"
print "A10_BRIDGE_PYTHON_SYNTAX=PASS"

TARGETED="$RUN_DIR/targeted-tests.log"
python3 -B -m unittest tests.test_mac_engineer_donecheck_v12_bridge -v >"$TARGETED" 2>&1 || {
  tail -n 80 "$TARGETED" || true
  hold "A10_BRIDGE_TARGETED_TESTS_FAILED"
}
print "A10_BRIDGE_TARGETED_TESTS=PASS"

FULL="$RUN_DIR/control-plane-regression.log"
python3 -B -m unittest discover -s tests -v >"$FULL" 2>&1 || {
  tail -n 80 "$FULL" || true
  hold "CONTROL_PLANE_REGRESSION_FAILED"
}
print "CONTROL_PLANE_REGRESSION=PASS"

VERIFY="$RUN_DIR/donecheck-v12-verification.log"
if ! python3 tools/mac_engineer_donecheck_v12_bridge.py verify >"$VERIFY" 2>&1; then
  tail -n 120 "$VERIFY" || true
  hold "DONECHECK_V12_INTEGRATION_EXECUTION_FAILED"
fi
cat "$VERIFY"

grep -Fq "STATE=INTEGRATION_PASS" "$VERIFY" || hold "A10_INTEGRATION_PASS_REQUIRED"
grep -Fq "DONECHECK_VERSION=1.2.0" "$VERIFY" || hold "DONECHECK_V12_REQUIRED"
grep -Fq "DONECHECK_EXACT_SHA=8b90a8fc93453dd8a84994195d28d14b15e261cb" "$VERIFY" || hold "DONECHECK_EXACT_SHA_REQUIRED"
OUTCOME="$(grep '^VERIFICATION_OUTCOME=' "$VERIFY" | tail -n 1 | cut -d= -f2-)"
CLOSURE="$(grep '^CLOSURE_STATE=' "$VERIFY" | tail -n 1 | cut -d= -f2-)"

case "$OUTCOME:$CLOSURE" in
  inconclusive:MILESTONE_CLOSURE_HOLD_A09_EXTERNAL_CONFIRMATION)
    EXPECTED_A09="inconclusive"
    FINAL_STATE="A10_INTEGRATION_PASS_CLOSURE_HOLD_A09_EXTERNAL_CONFIRMATION"
    NEXT="LOCAL_FINISHER_REHEARSAL_OR_A09_EXTERNAL_CONFIRMATION"
    ;;
  pass:MACHINE_VERIFICATION_PASS)
    EXPECTED_A09="pass"
    FINAL_STATE="A10_MACHINE_VERIFICATION_PASS"
    NEXT="V07_A11_CONSOLIDATED_MAC_CAMPAIGN"
    ;;
  *)
    hold "A10_UNEXPECTED_VERIFICATION_STATE"
    ;;
esac

BRIDGE_EVIDENCE="$(grep '^EVIDENCE=' "$VERIFY" | tail -n 1 | cut -d= -f2-)"
[[ -f "$BRIDGE_EVIDENCE" ]] || hold "A10_EVIDENCE_REQUIRED"

python3 - "$BRIDGE_EVIDENCE" "$EXPECTED_A09" "$OUTCOME" "$CLOSURE" <<'PY' || hold "A10_RESULT_CONTRACT_FAILED"
import json
import sys
from pathlib import Path

evidence = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected_a09, expected_outcome, expected_closure = sys.argv[2:5]
result_path = Path(evidence["verificationResultPath"])
result = json.loads(result_path.read_text(encoding="utf-8"))
gates = result["gateOutcomes"]

for i in range(1, 9):
    gate = f"V07-A{i:02d}"
    assert gates[gate] == "pass", (gate, gates[gate])

assert gates["V07-A09"] == expected_a09, gates["V07-A09"]
assert result["verificationResult"]["outcome"] == expected_outcome
assert evidence["state"] == "INTEGRATION_PASS"
assert evidence["closureState"] == expected_closure
print("A10_GATE_OUTCOMES=PASS")
PY

print "STATE=$FINAL_STATE"
print "DONECHECK=V1.2.0_EXACT_SHA_VERIFIED"
print "A01_A08=PASS"
print "A09=$EXPECTED_A09"
print "A10_INTEGRATION=PASS"
print "MILESTONE_CLOSURE=$CLOSURE"
print "EVIDENCE=$BRIDGE_EVIDENCE"
print "NEXT_ACTION=$NEXT"
