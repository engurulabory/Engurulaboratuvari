#!/bin/zsh
set -u
export PYTHONDONTWRITEBYTECODE=1
umask 077

CONTROL="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
PRODUCT="${ENGURU_PRODUCT_SOURCE:-$HOME/Enguru/Projects/enguru-mac-engineer}"

BRANCH="feat/mac-engineer-v08-product-engineering-operator"
EXPECTED_MAIN="2fd5553a55ce2a8c42163c81a4d21fc155bc0593"
EXPECTED_PRODUCT="0ca33cc7b70fee915d02de72946bbd4bb0e40065"

ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.8"
P08_ROOT="$ROOT/gate11-p08-stale-runtime-recovery"
P09_ROOT="$ROOT/gate11-p09-lifecycle"
P10_ROOT="$ROOT/gate11-p10-reliability"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN="$ROOT/gate11-p11-independent-verification/$STAMP"
mkdir -p "$RUN"

LOG="$RUN/p11-independent-verification.log"
TARGETED_LOG="$RUN/targeted-regression.log"
CONTROL_LOG="$RUN/full-control-plane-regression.log"
PRODUCT_LOG="$RUN/product-regression.log"
VERIFY_JSON="$RUN/p11-verification.json"
FINAL_JSON="$RUN/p11-final-acceptance.json"

exec > >(tee "$LOG") 2>&1

hold() {
  printf '\nSTATE=HOLD\n'
  printf 'CLAIM=%s\n' "$1"
  printf 'P11_EXECUTION=HOLD\n'
  printf 'SOURCE_MUTATION=0\n'
  printf 'REMOTE_MUTATION=0\n'
  printf 'NEW_CORE=false\n'
  printf 'EVIDENCE=%s\n' "$LOG"
  printf 'NEXT_ACTION=P11_SMALLEST_RESPONSIBLE_REPAIR\n'
  exit 2
}

printf '=== P11 AUTHORITY + SCOPE PRESTATE ===\n'

[ "$(git -C "$CONTROL" branch --show-current)" = "$BRANCH" ] \
  || hold "CONTROL_BRANCH_DRIFT"

CONTROL_HEAD="$(git -C "$CONTROL" rev-parse HEAD)"
CONTROL_REMOTE="$(git -C "$CONTROL" rev-parse "origin/$BRANCH")"
MAIN_HEAD="$(git -C "$CONTROL" rev-parse origin/main)"
PRODUCT_HEAD="$(git -C "$PRODUCT" rev-parse HEAD)"

[ "$CONTROL_HEAD" = "$CONTROL_REMOTE" ] \
  || hold "CONTROL_LOCAL_REMOTE_PARITY_FAILED"

[ "$MAIN_HEAD" = "$EXPECTED_MAIN" ] \
  || hold "ORIGIN_MAIN_DRIFT"

[ "$PRODUCT_HEAD" = "$EXPECTED_PRODUCT" ] \
  || hold "PRODUCT_HEAD_DRIFT"

[ -z "$(git -C "$CONTROL" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "CONTROL_WORKTREE_NOT_CLEAN"

[ -z "$(git -C "$PRODUCT" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "PRODUCT_WORKTREE_NOT_CLEAN"

printf 'SCOPE_CHECK_PASS=PASS\n'

printf '\n=== P10 GROUNDING ===\n'

LATEST_P10="$(
  find "$P10_ROOT" -mindepth 2 -maxdepth 2 \
    -name 'p10-final-acceptance.json' -print 2>/dev/null |
  sort | tail -n 1
)"

LATEST_P09="$(
  find "$P09_ROOT" -mindepth 2 -maxdepth 2 \
    -name 'p09-final-acceptance.json' -print 2>/dev/null |
  sort | tail -n 1
)"

LATEST_P08="$(
  find "$P08_ROOT" -mindepth 2 -maxdepth 2 \
    -name 'p08-final-acceptance.json' -print 2>/dev/null |
  sort | tail -n 1
)"

[ -n "$LATEST_P10" ] || hold "P10_FINAL_ACCEPTANCE_MISSING"
[ -n "$LATEST_P09" ] || hold "P09_FINAL_ACCEPTANCE_MISSING"
[ -n "$LATEST_P08" ] || hold "P08_FINAL_ACCEPTANCE_MISSING"

printf '\n=== TARGETED REGRESSION ===\n'

: >"$TARGETED_LOG"

for PATTERN in \
  'test_mac_engineer_v08_gate11_p09_operator.py' \
  'test_mac_engineer_v08_gate11_p10_operator.py' \
  'test_mac_engineer_v08_gate11_p11_operator.py' \
  'test_mac_engineer_v08_gate11_handler.py' \
  'test_mac_engineer_v08_gate11_method_guard_v2.py'
do
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest discover \
    -s "$CONTROL/tests" \
    -p "$PATTERN" \
    -v >>"$TARGETED_LOG" 2>&1

  [ "$?" -eq 0 ] || {
    cat "$TARGETED_LOG"
    hold "TARGETED_REGRESSION_FAILED"
  }
done

cat "$TARGETED_LOG"
printf 'TARGETED_REGRESSION_PASS=PASS\n'

printf '\n=== FULL CONTROL PLANE REGRESSION ===\n'

(
  cd "$CONTROL" || exit 1
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest discover -s tests -v
) >"$CONTROL_LOG" 2>&1

CONTROL_RC=$?
cat "$CONTROL_LOG"

[ "$CONTROL_RC" -eq 0 ] \
  || hold "FULL_CONTROL_PLANE_REGRESSION_FAILED"

printf 'FULL_CONTROL_PLANE_REGRESSION_PASS=PASS\n'

printf '\n=== PRODUCT REGRESSION ===\n'

(
  cd "$PRODUCT" || exit 1
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest discover -s runtime/tests -v
) >"$PRODUCT_LOG" 2>&1

PRODUCT_RC=$?
cat "$PRODUCT_LOG"

[ "$PRODUCT_RC" -eq 0 ] \
  || hold "PRODUCT_REGRESSION_FAILED"

printf 'PRODUCT_REGRESSION_PASS=PASS\n'

printf '\n=== DIFF CHECK ===\n'

git -C "$CONTROL" diff --check \
  || hold "CONTROL_DIFF_CHECK_FAILED"

git -C "$PRODUCT" diff --check \
  || hold "PRODUCT_DIFF_CHECK_FAILED"

printf 'DIFF_CHECK_PASS=PASS\n'

printf '\n=== INDEPENDENT PROVENANCE / RECOVERY / EVIDENCE AUDIT ===\n'

PYTHONDONTWRITEBYTECODE=1 python3 -B - \
  "$ROOT" \
  "$LATEST_P08" \
  "$LATEST_P09" \
  "$LATEST_P10" \
  "$VERIFY_JSON" <<'PY'
import hashlib
import json
import os
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
p08 = Path(sys.argv[2])
p09 = Path(sys.argv[3])
p10 = Path(sys.argv[4])
out = Path(sys.argv[5])

issues = []

def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issues.append(f"JSON_INVALID:{path}:{exc}")
        return {}

d08 = load(p08)
d09 = load(p09)
d10 = load(p10)

p10_required = (
    "P09_PASS",
    "CHECKPOINT_CONTINUITY_PASS",
    "CONTROLLED_INTERRUPTION_PASS",
    "RESTART_RECOVERY_PASS",
    "SAME_TASK_RESUME_PASS",
    "IDEMPOTENCY_PASS",
    "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE",
    "SINGLE_WRITER_DISCIPLINE_PASS",
    "BOUNDED_RETRY_PASS",
    "RECOVERY_EVIDENCE_PASS",
)

a10 = d10.get("acceptance") or {}

if not (
    d10.get("state") == "PASS"
    and d10.get("package") == "P10"
    and all(a10.get(k) == "PASS" for k in p10_required)
    and d10.get("sourceMutation") is False
    and d10.get("remoteMutation") is False
    and d10.get("newCore") is False
    and d10.get("nextTransition") == "P11"
):
    issues.append("P10_ACCEPTANCE_INVALID")

p09_required = (
    "P08_PASS",
    "CONTROLLED_REPLACEMENT_PASS",
    "STOP_PASS",
    "RESTART_PASS",
    "KNOWN_GOOD_ROLLBACK_PASS",
    "ROLLBACK_REVERIFY_PASS",
    "LIFECYCLE_PROVENANCE_PASS",
    "EVIDENCE_CONTINUITY_PASS",
)

a09 = d09.get("acceptance") or {}

if not (
    d09.get("state") == "PASS"
    and d09.get("package") == "P09"
    and all(a09.get(k) == "PASS" for k in p09_required)
    and d09.get("finalKnownGood") == "P08_VERIFIED"
    and d09.get("sourceMutation") is False
    and d09.get("remoteMutation") is False
    and d09.get("nextTransition") == "P10"
):
    issues.append("P09_ACCEPTANCE_INVALID")

if not (
    d08.get("state") == "PASS"
    and d08.get("package") == "P08"
    and d08.get("nextTransition") == "P09"
):
    issues.append("P08_ACCEPTANCE_INVALID")

recovery_path_raw = d10.get(
    "freshRestartRecoveryEvidence",
    "",
)
recovery_path = (
    Path(recovery_path_raw)
    if recovery_path_raw
    else None
)

recovery_sha_expected = d10.get(
    "freshRestartRecoveryEvidenceSha256"
)

recovery_sha_actual = None

if recovery_path and recovery_path.is_file():
    recovery_sha_actual = hashlib.sha256(
        recovery_path.read_bytes()
    ).hexdigest()
else:
    issues.append("P10_RECOVERY_EVIDENCE_MISSING")

if recovery_sha_actual != recovery_sha_expected:
    issues.append("P10_RECOVERY_EVIDENCE_SHA_MISMATCH")

package_evidence = {}

for number in range(1, 11):
    token = f"gate11-p{number:02d}-"
    dirs = sorted(
        p for p in root.iterdir()
        if p.is_dir() and p.name.startswith(token)
    )

    file_count = sum(
        1
        for d in dirs
        for p in d.rglob("*")
        if p.is_file()
    )

    package_evidence[f"P{number:02d}"] = {
        "directories": [str(p) for p in dirs],
        "fileCount": file_count,
        "present": bool(dirs and file_count),
    }

    if not dirs or file_count == 0:
        issues.append(
            f"P{number:02d}_EVIDENCE_MISSING"
        )

counter_names = (
    "HUMAN_MANUAL_SOURCE_EDIT_COUNT",
    "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT",
    "UNTRACKED_MANUAL_STEP_COUNT",
    "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION",
)

counter_values = {
    name: []
    for name in counter_names
}

allowed_suffixes = {
    ".log",
    ".txt",
    ".json",
    ".md",
    ".tsv",
    ".receipt",
}

patterns = {
    name: re.compile(
        rf"(?m)^{re.escape(name)}\s*=\s*(\d+)\s*$"
    )
    for name in counter_names
}

for base, _, files in os.walk(root):
    for name in files:
        p = Path(base) / name

        if p.suffix.lower() not in allowed_suffixes:
            continue

        try:
            text = p.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception:
            continue

        for counter, pattern in patterns.items():
            for match in pattern.finditer(text):
                counter_values[counter].append(
                    int(match.group(1))
                )

for counter, values in counter_values.items():
    if not values:
        issues.append(
            f"{counter}_NO_EVIDENCE"
        )
    elif any(value != 0 for value in values):
        issues.append(
            f"{counter}_NONZERO"
        )

historical_reconciliation = {
    "historicalRejectedFalsePassClaimCount": 1,
    "historicalRejectedFalsePassCanonicalized": False,
    "historicalDisposition":
        "PRESERVED_AS_REJECTED_SECOND_LOOK_INCIDENT",
    "criterionSemantics":
        "CURRENT_UNRESOLVED_CANONICAL_CRITICAL_FALSE_PASS_COUNT",
}

critical_issues = list(issues)

current_unresolved = (
    0
    if not critical_issues
    else len(critical_issues)
)

payload = {
    "schema":
        "enguru.gate11.p11-independent-verification/v1",
    "p10Pass":
        "PASS"
        if "P10_ACCEPTANCE_INVALID" not in issues
        else "HOLD",
    "provenanceCheck":
        "PASS"
        if not any(
            x in issues
            for x in (
                "P08_ACCEPTANCE_INVALID",
                "P09_ACCEPTANCE_INVALID",
                "P10_ACCEPTANCE_INVALID",
            )
        )
        else "HOLD",
    "recoveryCheck":
        "PASS"
        if not any(
            x.startswith("P10_RECOVERY_")
            for x in issues
        )
        else "HOLD",
    "evidenceCompleteness":
        "PASS"
        if not any(
            x.endswith("_EVIDENCE_MISSING")
            for x in issues
        )
        else "HOLD",
    "packageEvidence":
        package_evidence,
    "counterValues":
        counter_values,
    "historicalFalsePassReconciliation":
        historical_reconciliation,
    "currentUnresolvedCriticalFalsePassCount":
        current_unresolved,
    "issues":
        issues,
    "state":
        "PASS"
        if not issues
        else "HOLD",
}

out.write_text(
    json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

print(
    json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )
)

raise SystemExit(0 if not issues else 2)
PY

VERIFY_RC=$?

[ "$VERIFY_RC" -eq 0 ] \
  || hold "P11_INDEPENDENT_EVIDENCE_AUDIT_FAILED"

printf 'P10_PASS=PASS\n'
printf 'PROVENANCE_CHECK_PASS=PASS\n'
printf 'RECOVERY_CHECK_PASS=PASS\n'
printf 'EVIDENCE_COMPLETENESS_PASS=PASS\n'

printf '\n=== FINAL SCOPE RECHECK ===\n'

[ -z "$(git -C "$CONTROL" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "CONTROL_MUTATION_OBSERVED"

[ -z "$(git -C "$PRODUCT" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "PRODUCT_MUTATION_OBSERVED"

[ "$(git -C "$CONTROL" rev-parse HEAD)" = "$CONTROL_HEAD" ] \
  || hold "CONTROL_HEAD_CHANGED"

[ "$(git -C "$CONTROL" rev-parse "origin/$BRANCH")" = "$CONTROL_REMOTE" ] \
  || hold "CONTROL_REMOTE_CHANGED"

[ "$(git -C "$PRODUCT" rev-parse HEAD)" = "$PRODUCT_HEAD" ] \
  || hold "PRODUCT_HEAD_CHANGED"

printf 'SCOPE_CHECK_PASS=PASS\n'

printf '\n=== GOVERNANCE COUNTERS + FALSE PASS RECONCILIATION ===\n'

printf 'HUMAN_MANUAL_SOURCE_EDIT_COUNT_0=PASS\n'
printf 'CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0=PASS\n'
printf 'UNTRACKED_MANUAL_STEP_COUNT_0=PASS\n'
printf 'ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0=PASS\n'
printf 'HISTORICAL_REJECTED_FALSE_PASS_CLAIM_COUNT=1\n'
printf 'HISTORICAL_REJECTED_FALSE_PASS_CANONICALIZED=false\n'
printf 'CURRENT_UNRESOLVED_CRITICAL_FALSE_PASS_COUNT=0\n'
printf 'CRITICAL_FALSE_PASS_0=PASS\n'

PYTHONDONTWRITEBYTECODE=1 python3 -B - \
  "$FINAL_JSON" \
  "$VERIFY_JSON" \
  "$TARGETED_LOG" \
  "$CONTROL_LOG" \
  "$PRODUCT_LOG" \
  "$CONTROL_HEAD" \
  "$PRODUCT_HEAD" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(sys.argv[1])
verification = Path(sys.argv[2])
targeted = Path(sys.argv[3])
control_log = Path(sys.argv[4])
product_log = Path(sys.argv[5])
control_head = sys.argv[6]
product_head = sys.argv[7]

acceptance = {
    "P10_PASS": "PASS",
    "TARGETED_REGRESSION_PASS": "PASS",
    "FULL_CONTROL_PLANE_REGRESSION_PASS": "PASS",
    "PRODUCT_REGRESSION_PASS": "PASS",
    "DIFF_CHECK_PASS": "PASS",
    "SCOPE_CHECK_PASS": "PASS",
    "PROVENANCE_CHECK_PASS": "PASS",
    "RECOVERY_CHECK_PASS": "PASS",
    "EVIDENCE_COMPLETENESS_PASS": "PASS",
    "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0": "PASS",
    "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0": "PASS",
    "UNTRACKED_MANUAL_STEP_COUNT_0": "PASS",
    "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0": "PASS",
    "CRITICAL_FALSE_PASS_0": "PASS",
}

payload = {
    "schema":
        "enguru.gate11.p11-final-acceptance/v1",
    "observedAt":
        datetime.now(timezone.utc).isoformat(),
    "state": "PASS",
    "package": "P11",
    "acceptance": acceptance,
    "controlHead": control_head,
    "productHead": product_head,
    "verificationEvidence": str(verification),
    "targetedRegressionEvidence": str(targeted),
    "controlRegressionEvidence": str(control_log),
    "productRegressionEvidence": str(product_log),
    "historicalFalsePass": {
        "rejectedClaimCount": 1,
        "canonicalized": False,
        "preserved": True,
    },
    "currentUnresolvedCriticalFalsePassCount": 0,
    "sourceMutation": False,
    "remoteMutation": False,
    "newCore": False,
    "nextTransition": "P12",
}

out.write_text(
    json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)
PY

printf '\nSTATE=PASS\n'
printf 'CLAIM=P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE_VERIFIED\n'
printf 'P11_ACCEPTANCE=14_OF_14_PASS\n'
printf 'P10_PASS=PASS\n'
printf 'TARGETED_REGRESSION_PASS=PASS\n'
printf 'FULL_CONTROL_PLANE_REGRESSION_PASS=PASS\n'
printf 'PRODUCT_REGRESSION_PASS=PASS\n'
printf 'DIFF_CHECK_PASS=PASS\n'
printf 'SCOPE_CHECK_PASS=PASS\n'
printf 'PROVENANCE_CHECK_PASS=PASS\n'
printf 'RECOVERY_CHECK_PASS=PASS\n'
printf 'EVIDENCE_COMPLETENESS_PASS=PASS\n'
printf 'HUMAN_MANUAL_SOURCE_EDIT_COUNT_0=PASS\n'
printf 'CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0=PASS\n'
printf 'UNTRACKED_MANUAL_STEP_COUNT_0=PASS\n'
printf 'ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0=PASS\n'
printf 'CRITICAL_FALSE_PASS_0=PASS\n'
printf 'HISTORICAL_REJECTED_FALSE_PASS_CLAIM_COUNT=1\n'
printf 'CURRENT_UNRESOLVED_CRITICAL_FALSE_PASS_COUNT=0\n'
printf 'SOURCE_MUTATION=0\n'
printf 'REMOTE_MUTATION=0\n'
printf 'NEW_CORE=false\n'
printf 'P11_ACCEPTANCE_EVIDENCE=%s\n' "$FINAL_JSON"
printf 'EVIDENCE=%s\n' "$LOG"
printf 'NEXT_ACTION=P12_DONECHECK_CANONICAL_GATE11_CLOSURE\n'
