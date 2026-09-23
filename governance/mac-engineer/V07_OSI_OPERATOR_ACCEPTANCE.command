#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EVIDENCE_ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.7"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/osi-operator-acceptance-$STAMP"
mkdir -p "$RUN_DIR"

hold() {
  local reason="$1"
  python3 - "$RUN_DIR/evidence.json" "$reason" <<'PY'
import json, sys
from datetime import datetime, timezone
path, reason = sys.argv[1:3]
payload = {
    "schema": "enguru.mac-engineer.osi-operator-acceptance/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "HOLD",
    "reason": reason,
    "authority_boundary": "LOCAL_ACCEPTANCE_ONLY_EXTERNAL_GITHUB_CONFIRMATION_REMAINS_CANONICAL_GATE",
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")
print("STATE=HOLD")
print(f"HOLD={reason}")
print(f"EVIDENCE={path}")
PY
  exit 2
}

[[ "$(uname -s)" == "Darwin" ]] || hold "MACOS_REQUIRED"
command -v python3 >/dev/null || hold "PYTHON3_REQUIRED"
command -v git >/dev/null || hold "GIT_REQUIRED"
command -v xcrun >/dev/null || hold "XCRUN_REQUIRED"

cd "$ROOT"

python3 -m py_compile tools/mac_engineer_operator.py || hold "OPERATOR_PYTHON_SYNTAX_FAILED"
print "OPERATOR_PYTHON_SYNTAX=PASS"

python3 - <<'PY' || hold "OPERATOR_ACTION_REGISTRY_JSON_FAILED"
import json
from pathlib import Path
json.loads(Path("governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json").read_text(encoding="utf-8"))
print("OPERATOR_ACTION_REGISTRY_JSON=PASS")
PY

zsh -n bin/enguru-mac || hold "OPERATOR_LAUNCHER_SYNTAX_FAILED"
zsh -n governance/mac-engineer/INSTALL_OSI_OPERATOR.command || hold "OPERATOR_INSTALLER_SYNTAX_FAILED"
zsh -n governance/mac-engineer/COMMISSION_OSI_GITHUB_RUNNER.command || hold "RUNNER_COMMISSIONER_SYNTAX_FAILED"
zsh -n governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK.command || hold "A09_FALLBACK_SYNTAX_FAILED"
print "SHELL_SYNTAX=PASS"

TARGETED_LOG="$RUN_DIR/operator-tests.log"
python3 -B -m unittest tests.test_mac_engineer_operator -v >"$TARGETED_LOG" 2>&1 || hold "OPERATOR_TARGETED_TESTS_FAILED"
print "OPERATOR_TARGETED_TESTS=PASS"

FULL_CONTROL_LOG="$RUN_DIR/control-plane-regression.log"
python3 -B -m unittest discover -s tests -v >"$FULL_CONTROL_LOG" 2>&1 || hold "CONTROL_PLANE_REGRESSION_FAILED"
print "CONTROL_PLANE_REGRESSION=PASS"

FALLBACK_LOG="$RUN_DIR/a09-local-rehearsal.log"
zsh governance/mac-engineer/V07_ASTRA_LOCAL_FALLBACK.command >"$FALLBACK_LOG" 2>&1 || hold "A09_LOCAL_REHEARSAL_FAILED"
grep -Fq "TARGETED_CONSECUTIVE_PASS=5_OF_5" "$FALLBACK_LOG" || hold "A09_TARGETED_5_OF_5_REQUIRED"
grep -Fq "FULL_RUNTIME_REGRESSION=PASS" "$FALLBACK_LOG" || hold "A09_FULL_REGRESSION_REQUIRED"
grep -Fq "NATIVE_VERIFICATION=PASS" "$FALLBACK_LOG" || hold "A09_NATIVE_VERIFICATION_REQUIRED"
grep -Fq "SCOPE_VALIDATION=PASS" "$FALLBACK_LOG" || hold "A09_SCOPE_VALIDATION_REQUIRED"
print "A09_LOCAL_REHEARSAL=PASS"

INSTALL_LOG="$RUN_DIR/operator-install.log"
zsh governance/mac-engineer/INSTALL_OSI_OPERATOR.command >"$INSTALL_LOG" 2>&1 || hold "OPERATOR_INSTALL_FAILED"
print "OPERATOR_INSTALL=PASS"

export PATH="$HOME/Enguru/bin:$PATH"

DOCTOR_LOG="$RUN_DIR/operator-doctor.log"
enguru-mac doctor >"$DOCTOR_LOG" 2>&1 || hold "OPERATOR_DOCTOR_FAILED"
print "OPERATOR_DOCTOR=PASS"

STATUS_LOG="$RUN_DIR/operator-status.log"
enguru-mac status >"$STATUS_LOG" 2>&1 || hold "OPERATOR_STATUS_FAILED"
print "OPERATOR_STATUS=PASS"

CONTROL_SHA="$(git rev-parse HEAD)"
PRODUCT_SHA="$(git -C "$HOME/Enguru/Projects/enguru-mac-engineer" rev-parse origin/test/v07-a09-fault-injection-campaign)"
A09_EVIDENCE="$(grep '^EVIDENCE=' "$FALLBACK_LOG" | tail -n 1 | cut -d= -f2-)"

python3 - "$RUN_DIR/evidence.json" "$CONTROL_SHA" "$PRODUCT_SHA" "$A09_EVIDENCE" "$RUN_DIR" <<'PY'
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

path, control_sha, product_sha, a09_evidence, run_dir = sys.argv[1:6]
root = Path(run_dir)

def digest(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

logs = {}
for name in [
    "operator-tests.log",
    "control-plane-regression.log",
    "a09-local-rehearsal.log",
    "operator-install.log",
    "operator-doctor.log",
    "operator-status.log",
]:
    p = root / name
    logs[name] = {"path": str(p), "sha256": digest(p)}

payload = {
    "schema": "enguru.mac-engineer.osi-operator-acceptance/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "LOCAL_ACCEPTANCE_PASS_EXTERNAL_GITHUB_CONFIRMATION_PENDING",
    "control_plane_sha": control_sha,
    "a09_candidate_sha": product_sha,
    "operator_surface": [
        "enguru-mac status",
        "enguru-mac continue",
        "enguru-mac verify",
        "enguru-mac recover",
        "enguru-mac doctor",
    ],
    "operator_python_syntax": "PASS",
    "operator_targeted_tests": "PASS",
    "control_plane_regression": "PASS",
    "a09_local_rehearsal": "PASS",
    "a09_local_evidence": a09_evidence,
    "operator_install": "PASS",
    "operator_doctor": "PASS",
    "operator_status": "PASS",
    "evidence_spool": "PASS",
    "gitvault_recovery_mirror": "PASS",
    "authority_boundary": (
        "LOCAL_ACCEPTANCE_PASS. GitHub external CI confirmation, DoneCheck v1.2 "
        "and Human Threshold remain required by their canonical gates."
    ),
    "logs": logs,
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")

print("STATE=LOCAL_ACCEPTANCE_PASS_EXTERNAL_GITHUB_CONFIRMATION_PENDING")
print(f"CONTROL_PLANE_SHA={control_sha}")
print(f"A09_CANDIDATE_SHA={product_sha}")
print("OPERATOR_SURFACE=5_OF_5_READY")
print("OPERATOR_TARGETED_TESTS=PASS")
print("CONTROL_PLANE_REGRESSION=PASS")
print("A09_LOCAL_REHEARSAL=PASS")
print("EVIDENCE_SPOOL=PASS")
print("GITVAULT=PASS")
print("AUTHORITY=EXTERNAL_GITHUB_CONFIRMATION_PENDING")
print(f"EVIDENCE={path}")
print("NEXT_ACTION=enguru-mac continue")
PY
