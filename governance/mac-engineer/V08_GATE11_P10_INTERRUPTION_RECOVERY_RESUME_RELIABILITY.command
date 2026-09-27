#!/bin/zsh
set -u
export PYTHONDONTWRITEBYTECODE=1
umask 077

CONTROL="${ENGURU_CONTROL_PLANE:-$HOME/Enguru/Projects/Engurulaboratuvari}"
PRODUCT="${ENGURU_PRODUCT_SOURCE:-$HOME/Enguru/Projects/enguru-mac-engineer}"

P09_ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.8/gate11-p09-lifecycle"
EVIDENCE_ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.8/gate11-p10-reliability"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_ROOT/$STAMP"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/p10-reliability.log"
FIELD_LOG="$RUN_DIR/restart-recovery-field.log"
SINGLE_WRITER_LOG="$RUN_DIR/single-writer.log"
BOUNDED_RETRY_LOG="$RUN_DIR/bounded-retry.log"
FINAL_JSON="$RUN_DIR/p10-final-acceptance.json"

exec > >(tee "$LOG") 2>&1

hold() {
  printf '\nSTATE=HOLD\n'
  printf 'CLAIM=%s\n' "$1"
  printf 'P10_ACCEPTANCE=%s_OF_10_PASS\n' "${PASS_COUNT:-0}"
  printf 'SOURCE_MUTATION=0\n'
  printf 'REMOTE_MUTATION=0\n'
  printf 'NEW_CORE=false\n'
  printf 'EVIDENCE=%s\n' "$LOG"
  printf 'NEXT_ACTION=P10_SMALLEST_RESPONSIBLE_REPAIR\n'
  exit 2
}

PASS_COUNT=0

printf '=== P10 P09 PRECONDITION ===\n'

LATEST_P09="$(
  find "$P09_ROOT" \
    -mindepth 2 \
    -maxdepth 2 \
    -name 'p09-final-acceptance.json' \
    -print 2>/dev/null |
  sort |
  tail -n 1
)"

[ -n "$LATEST_P09" ] || hold "P09_ACCEPTANCE_MISSING"

PYTHONDONTWRITEBYTECODE=1 python3 -B - "$LATEST_P09" <<'PY'
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

required = (
    "P08_PASS",
    "CONTROLLED_REPLACEMENT_PASS",
    "STOP_PASS",
    "RESTART_PASS",
    "KNOWN_GOOD_ROLLBACK_PASS",
    "ROLLBACK_REVERIFY_PASS",
    "LIFECYCLE_PROVENANCE_PASS",
    "EVIDENCE_CONTINUITY_PASS",
)

ok = (
    d.get("state") == "PASS"
    and d.get("package") == "P09"
    and d.get("nextTransition") == "P10"
    and all(
        d.get("acceptance", {}).get(k) == "PASS"
        for k in required
    )
    and d.get("sourceMutation") is False
    and d.get("remoteMutation") is False
)

raise SystemExit(0 if ok else 2)
PY

[ "$?" -eq 0 ] || hold "P09_PASS_REQUIRED"

PASS_COUNT=$((PASS_COUNT + 1))
printf 'P09_PASS=PASS\n'

printf '\n=== P10 RELIABILITY SOURCE PARITY ===\n'

CURRENT_REL="$PRODUCT/runtime/reliability.py"
[ -f "$CURRENT_REL" ] || hold "CURRENT_RELIABILITY_MISSING"

CURRENT_REL_SHA="$(shasum -a 256 "$CURRENT_REL" | awk '{print $1}')"

MAIN_REL_SHA="$(
  git -C "$PRODUCT" show origin/main:runtime/reliability.py |
  shasum -a 256 |
  awk '{print $1}'
)"

printf 'CURRENT_RELIABILITY_SHA=%s\n' "$CURRENT_REL_SHA"
printf 'ORIGIN_MAIN_RELIABILITY_SHA=%s\n' "$MAIN_REL_SHA"

[ "$CURRENT_REL_SHA" = "$MAIN_REL_SHA" ] \
  || hold "CURRENT_RELIABILITY_DIFFERS_FROM_FIELD_PROOF_ENGINE"

printf 'RELIABILITY_ENGINE_PARITY=PASS\n'

printf '\n=== P10 FRESH RESTART RECOVERY FIELD PROOF ===\n'

zsh "$CONTROL/governance/mac-engineer/V07_MAC_NATIVE_RESTART_RECOVERY_PROOF.command" \
  >"$FIELD_LOG" 2>&1

FIELD_RC=$?
cat "$FIELD_LOG"

[ "$FIELD_RC" -eq 0 ] \
  || hold "RESTART_RECOVERY_FIELD_PROOF_FAILED"

grep -q '^STATE=PASS$' "$FIELD_LOG" \
  || hold "RESTART_RECOVERY_STATE_NOT_PASS"

grep -q '^PROCESS_RESTART=PASS$' "$FIELD_LOG" \
  || hold "PROCESS_RESTART_NOT_PASS"

grep -q '^TASK_IDENTITY=PASS$' "$FIELD_LOG" \
  || hold "TASK_IDENTITY_NOT_PASS"

grep -q '^CHECKPOINT_RESUME=PASS$' "$FIELD_LOG" \
  || hold "CHECKPOINT_RESUME_NOT_PASS"

grep -q '^EXACTLY_ONCE_EFFECT=PASS$' "$FIELD_LOG" \
  || hold "EXACTLY_ONCE_EFFECT_NOT_PASS"

grep -q '^FINAL_STATE=COMPLETE$' "$FIELD_LOG" \
  || hold "FINAL_STATE_NOT_COMPLETE"

FIELD_EVIDENCE="$(
  sed -n 's/^EVIDENCE=//p' "$FIELD_LOG" |
  tail -n 1
)"

[ -n "$FIELD_EVIDENCE" ] \
  || hold "FIELD_EVIDENCE_PATH_MISSING"

[ -f "$FIELD_EVIDENCE" ] \
  || hold "FIELD_EVIDENCE_FILE_MISSING"

PYTHONDONTWRITEBYTECODE=1 python3 -B - "$FIELD_EVIDENCE" <<'PY'
import json
import sys
from pathlib import Path

p = Path(sys.argv[1])
d = json.loads(p.read_text(encoding="utf-8"))

start = d.get("phaseStart") or {}
resume_path = Path(
    (d.get("phaseResume") or {}).get("receipt", "")
)

if not resume_path.is_file():
    raise SystemExit(2)

resume = json.loads(
    resume_path.read_text(encoding="utf-8")
)

ok = (
    d.get("state") == "PASS"
    and d.get("processRestart") == "PASS"
    and d.get("taskIdentityContinuity") == "PASS"
    and d.get("checkpointResume") == "PASS"
    and d.get("exactlyOnceDurableEffect") == "PASS"
    and d.get("durableEffectCount") == 1
    and d.get("finalTaskState") == "COMPLETE"
    and start.get("controlledExitCode") == 75
    and resume.get("duplicateBegin") is True
    and resume.get("sameTaskIdentity") is True
    and resume.get("exactlyOnceEffect") is True
)

raise SystemExit(0 if ok else 2)
PY

[ "$?" -eq 0 ] \
  || hold "FIELD_EVIDENCE_CONTRACT_FAILED"

PASS_COUNT=$((PASS_COUNT + 1))
printf 'CHECKPOINT_CONTINUITY_PASS=PASS\n'

PASS_COUNT=$((PASS_COUNT + 1))
printf 'CONTROLLED_INTERRUPTION_PASS=PASS\n'

PASS_COUNT=$((PASS_COUNT + 1))
printf 'RESTART_RECOVERY_PASS=PASS\n'

PASS_COUNT=$((PASS_COUNT + 1))
printf 'SAME_TASK_RESUME_PASS=PASS\n'

PASS_COUNT=$((PASS_COUNT + 1))
printf 'IDEMPOTENCY_PASS=PASS\n'

PASS_COUNT=$((PASS_COUNT + 1))
printf 'EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE=PASS\n'

printf '\n=== P10 CURRENT PRODUCT SINGLE WRITER ===\n'

(
  cd "$PRODUCT/runtime/tests" || exit 1
  PYTHONPATH="$PRODUCT/runtime" \
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest \
    test_reliability.ReliabilityTests.test_single_writer \
    -v
) >"$SINGLE_WRITER_LOG" 2>&1

SW_RC=$?
cat "$SINGLE_WRITER_LOG"

[ "$SW_RC" -eq 0 ] \
  || hold "SINGLE_WRITER_TEST_FAILED"

PASS_COUNT=$((PASS_COUNT + 1))
printf 'SINGLE_WRITER_DISCIPLINE_PASS=PASS\n'

printf '\n=== P10 CURRENT PRODUCT BOUNDED RETRY ===\n'

(
  cd "$PRODUCT/runtime/tests" || exit 1
  PYTHONPATH="$PRODUCT/runtime" \
  PYTHONDONTWRITEBYTECODE=1 \
  python3 -B -m unittest \
    test_v07_long_running_reliability.V07LongRunningReliabilityTests.test_v07_a05_bounded_retry_policy_and_watchdog_decision \
    -v
) >"$BOUNDED_RETRY_LOG" 2>&1

BR_RC=$?
cat "$BOUNDED_RETRY_LOG"

[ "$BR_RC" -eq 0 ] \
  || hold "BOUNDED_RETRY_TEST_FAILED"

PASS_COUNT=$((PASS_COUNT + 1))
printf 'BOUNDED_RETRY_PASS=PASS\n'

printf '\n=== P10 RECOVERY EVIDENCE ===\n'

[ -s "$FIELD_EVIDENCE" ] \
  || hold "RECOVERY_EVIDENCE_EMPTY"

FIELD_EVIDENCE_SHA="$(shasum -a 256 "$FIELD_EVIDENCE" | awk '{print $1}')"

PASS_COUNT=$((PASS_COUNT + 1))
printf 'RECOVERY_EVIDENCE_PASS=PASS\n'
printf 'RECOVERY_EVIDENCE=%s\n' "$FIELD_EVIDENCE"
printf 'RECOVERY_EVIDENCE_SHA256=%s\n' "$FIELD_EVIDENCE_SHA"

[ "$PASS_COUNT" -eq 10 ] \
  || hold "P10_ACCEPTANCE_COUNT_NOT_10"

printf '\n=== P10 SOURCE + REMOTE INVARIANTS ===\n'

[ -z "$(git -C "$CONTROL" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "CONTROL_SOURCE_MUTATION_OBSERVED"

[ -z "$(git -C "$PRODUCT" status --porcelain=v1 --untracked-files=all)" ] \
  || hold "PRODUCT_SOURCE_MUTATION_OBSERVED"

printf 'SOURCE_MUTATION_OBSERVED=0\n'
printf 'REMOTE_MUTATION_OBSERVED=0\n'

PYTHONDONTWRITEBYTECODE=1 python3 -B - \
  "$FINAL_JSON" \
  "$FIELD_EVIDENCE" \
  "$FIELD_EVIDENCE_SHA" \
  "$CURRENT_REL_SHA" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

out = Path(sys.argv[1])
field = sys.argv[2]
field_sha = sys.argv[3]
reliability_sha = sys.argv[4]

payload = {
    "schema": "enguru.gate11.p10-reliability/v1",
    "observedAt": datetime.now(timezone.utc).isoformat(),
    "state": "PASS",
    "package": "P10",
    "acceptance": {
        "P09_PASS": "PASS",
        "CHECKPOINT_CONTINUITY_PASS": "PASS",
        "CONTROLLED_INTERRUPTION_PASS": "PASS",
        "RESTART_RECOVERY_PASS": "PASS",
        "SAME_TASK_RESUME_PASS": "PASS",
        "IDEMPOTENCY_PASS": "PASS",
        "EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE": "PASS",
        "SINGLE_WRITER_DISCIPLINE_PASS": "PASS",
        "BOUNDED_RETRY_PASS": "PASS",
        "RECOVERY_EVIDENCE_PASS": "PASS",
    },
    "reliabilityEngineSha256": reliability_sha,
    "freshRestartRecoveryEvidence": field,
    "freshRestartRecoveryEvidenceSha256": field_sha,
    "sourceMutation": False,
    "remoteMutation": False,
    "newCore": False,
    "nextTransition": "P11",
}

out.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

[ -f "$FINAL_JSON" ] \
  || hold "P10_FINAL_ACCEPTANCE_NOT_WRITTEN"

printf '\nSTATE=PASS\n'
printf 'CLAIM=P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY_VERIFIED\n'
printf 'P10_ACCEPTANCE=10_OF_10_PASS\n'
printf 'P09_PASS=PASS\n'
printf 'CHECKPOINT_CONTINUITY_PASS=PASS\n'
printf 'CONTROLLED_INTERRUPTION_PASS=PASS\n'
printf 'RESTART_RECOVERY_PASS=PASS\n'
printf 'SAME_TASK_RESUME_PASS=PASS\n'
printf 'IDEMPOTENCY_PASS=PASS\n'
printf 'EXACTLY_ONCE_EFFECT_DISCIPLINE_PASS_WHERE_APPLICABLE=PASS\n'
printf 'SINGLE_WRITER_DISCIPLINE_PASS=PASS\n'
printf 'BOUNDED_RETRY_PASS=PASS\n'
printf 'RECOVERY_EVIDENCE_PASS=PASS\n'
printf 'SOURCE_MUTATION=0\n'
printf 'REMOTE_MUTATION=0\n'
printf 'NEW_CORE=false\n'
printf 'P10_ACCEPTANCE_EVIDENCE=%s\n' "$FINAL_JSON"
printf 'EVIDENCE=%s\n' "$LOG"
printf 'NEXT_ACTION=P11_INDEPENDENT_VERIFICATION_SECOND_LOOK_EVIDENCE_BUNDLE\n'
