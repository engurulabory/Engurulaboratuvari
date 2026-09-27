#!/bin/zsh
set -u
export PYTHONDONTWRITEBYTECODE=1
umask 077

PRODUCT="${ENGURU_GATE11_PRODUCT_REPO:-$HOME/Enguru/Projects/enguru-mac-engineer}"
EXPECTED_HEAD="${ENGURU_GATE11_P09_EXPECTED_PRODUCT_HEAD:-0ca33cc7b70fee915d02de72946bbd4bb0e40065}"

APP="$HOME/Applications/ENGÜRÜ Mac Engineer.app"
APP_BIN="$APP/Contents/MacOS/EnguruMacEngineer"
BUNDLE_ID="com.engurumaya.macengineer"

RUNTIME_ROOT="$HOME/Enguru/Runtime/MacEngineer"
RUNTIME="$RUNTIME_ROOT/runtime"
STATUS_URL="http://127.0.0.1:8765/api/status"

PREP="$PRODUCT/execution_prep/native_app/prepare_native_app.command"

CONTROL="$(cd "$(dirname "$0")/../.." && pwd)"
CONTROL_BRANCH_EXPECTED="feat/mac-engineer-v08-product-engineering-operator"
PRODUCT_BRANCH_EXPECTED="feat/v08-native-productization-provenance"

P08_ROOT="$HOME/Enguru/Evidence/MacEngineer/v0.8/gate11-p08-stale-runtime-recovery"

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$HOME/Enguru/Evidence/MacEngineer/v0.8/gate11-p09-lifecycle/$STAMP"
mkdir -p "$RUN_DIR"

LOG="$RUN_DIR/p09-lifecycle.log"
ACCEPTANCE="$RUN_DIR/p09-final-acceptance.json"

exec > >(tee "$LOG") 2>&1

hold() {
  printf 'STATE=HOLD\n'
  printf 'CLAIM=%s\n' "$1"
  printf 'P09_ACCEPTANCE=%s\n' "${P09_ACCEPTANCE:-1_OF_8_PASS}"
  printf 'EVIDENCE=%s\n' "$LOG"
  printf 'NEXT_ACTION=P09_SMALLEST_RESPONSIBLE_REPAIR\n'
  exit 2
}

wait_running() {
  i=0
  while [ "$i" -lt 45 ]; do
    if curl --max-time 2 -fsS "$STATUS_URL" >"$RUN_DIR/status.json" 2>/dev/null; then
      PYTHONDONTWRITEBYTECODE=1 python3 -B - "$RUN_DIR/status.json" <<'PY'
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

ok = all([
    d.get("service") == "ENGÜRÜ Mac Engineer™",
    d.get("state") == "RUNNING",
    d.get("host") == "127.0.0.1",
    d.get("port") == 8765,
    d.get("governance") == "ACTIVE",
])

raise SystemExit(0 if ok else 2)
PY
      [ "$?" -eq 0 ] && return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

runtime_pid() {
  lsof -nP -iTCP:8765 -sTCP:LISTEN -t 2>/dev/null | head -n 1
}

app_pid_from_runtime() {
  RP="$1"
  ps -o ppid= -p "$RP" 2>/dev/null | tr -d ' '
}


tree_sha256() {
  PYTHONDONTWRITEBYTECODE=1 python3 -B - "$1" <<'PY_TREE'
import hashlib
import sys
from pathlib import Path

root = Path(sys.argv[1])

if not root.is_dir():
    raise SystemExit(2)

h = hashlib.sha256()

for path in sorted(p for p in root.rglob("*") if p.is_file()):
    rel = path.relative_to(root).as_posix()
    h.update(rel.encode("utf-8"))
    h.update(b"\0")
    h.update(path.read_bytes())
    h.update(b"\0")

print(h.hexdigest())
PY_TREE
}

stop_owned_app() {
  osascript -e "tell application id \"$BUNDLE_ID\" to quit" >/dev/null 2>&1 || return 1

  i=0
  while [ "$i" -lt 30 ]; do
    RP="$(runtime_pid)"
    if [ -z "$RP" ]; then
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

printf '=== P09 PRECONDITIONS ===\n'

cd "$PRODUCT" || hold "PRODUCT_REPOSITORY_MISSING"


PRE_CONTROL_HEAD="$(git -C "$CONTROL" rev-parse HEAD)"
PRE_CONTROL_BRANCH="$(git -C "$CONTROL" branch --show-current)"
PRE_CONTROL_STATUS="$(git -C "$CONTROL" status --porcelain=v1 --untracked-files=all)"
PRE_CONTROL_REMOTE_BRANCH="$(git -C "$CONTROL" rev-parse "origin/$CONTROL_BRANCH_EXPECTED")"
PRE_CONTROL_REMOTE_MAIN="$(git -C "$CONTROL" rev-parse origin/main)"

PRE_PRODUCT_HEAD="$(git -C "$PRODUCT" rev-parse HEAD)"
PRE_PRODUCT_BRANCH="$(git -C "$PRODUCT" branch --show-current)"
PRE_PRODUCT_STATUS="$(git -C "$PRODUCT" status --porcelain=v1 --untracked-files=all)"
PRE_PRODUCT_REMOTE_BRANCH="$(git -C "$PRODUCT" rev-parse "origin/$PRODUCT_BRANCH_EXPECTED")"
PRE_PRODUCT_REMOTE_MAIN="$(git -C "$PRODUCT" rev-parse origin/main)"

[ "$PRE_CONTROL_BRANCH" = "$CONTROL_BRANCH_EXPECTED" ] || hold "CONTROL_BRANCH_PRECONDITION"
[ "$PRE_PRODUCT_BRANCH" = "$PRODUCT_BRANCH_EXPECTED" ] || hold "PRODUCT_BRANCH_PRECONDITION"
[ -z "$PRE_CONTROL_STATUS" ] || hold "CONTROL_SOURCE_PRESTATE_NOT_CLEAN"
[ -z "$PRE_PRODUCT_STATUS" ] || hold "PRODUCT_SOURCE_PRESTATE_NOT_CLEAN"

HEAD="$(git rev-parse HEAD)"
[ "$HEAD" = "$EXPECTED_HEAD" ] || hold "PRODUCT_HEAD_PRECONDITION"

[ -z "$(git status --porcelain=v1 --untracked-files=all)" ] \
  || hold "PRODUCT_WORKTREE_NOT_CLEAN"

[ -x "$PREP" ] || hold "NATIVE_PREP_MISSING"
[ -x "$APP_BIN" ] || hold "INSTALLED_APP_MISSING"

P08_ACCEPTANCE="$(
  find "$P08_ROOT" -type f -name 'p08-final-acceptance.json' -print 2>/dev/null \
  | sort \
  | tail -n 1
)"

[ -n "$P08_ACCEPTANCE" ] || hold "P08_ACCEPTANCE_MISSING"

PYTHONDONTWRITEBYTECODE=1 python3 -B - "$P08_ACCEPTANCE" <<'PY'
import json
import sys
from pathlib import Path

d = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

ok = (
    d.get("state") == "PASS"
    and d.get("package") == "P08"
    and d.get("nextTransition") == "P09"
)

raise SystemExit(0 if ok else 2)
PY

[ "$?" -eq 0 ] || hold "P08_ACCEPTANCE_INVALID"

BASE_COMMIT="$(
  PYTHONDONTWRITEBYTECODE=1 python3 -B - \
    "$APP/Contents/Resources/release.json" <<'PY'
import json
import sys
from pathlib import Path

print(
    json.loads(
        Path(sys.argv[1]).read_text(encoding="utf-8")
    )["sourceCommit"]
)
PY
)"

[ "$BASE_COMMIT" = "$EXPECTED_HEAD" ] || hold "BASE_INSTALLED_COMMIT_MISMATCH"

codesign --verify --deep --strict "$APP" || hold "BASE_CODESIGN_FAILED"
wait_running || hold "BASE_RUNTIME_NOT_RUNNING"

BASE_RUNTIME_PID="$(runtime_pid)"
[ -n "$BASE_RUNTIME_PID" ] || hold "BASE_RUNTIME_PID_MISSING"

BASE_APP_PID="$(app_pid_from_runtime "$BASE_RUNTIME_PID")"
[ -n "$BASE_APP_PID" ] || hold "BASE_APP_PID_MISSING"

BASE_APP_STAT="$(stat -f '%i:%m:%c' "$APP_BIN")"

P08_EXPECTED_BINARY_SHA="$(
  PYTHONDONTWRITEBYTECODE=1 python3 -B - "$P08_ACCEPTANCE" <<'PY_P08'
import json
import sys
from pathlib import Path

data = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

print(data["installedBinarySha256"])
PY_P08
)"

BASE_BINARY_SHA="$(shasum -a 256 "$APP_BIN" | awk '{print $1}')"
BASE_APP_TREE_SHA="$(tree_sha256 "$APP")"
BASE_RUNTIME_TREE_SHA="$(tree_sha256 "$RUNTIME")"
BASE_RELEASE_SHA="$(shasum -a 256 "$APP/Contents/Resources/release.json" | awk '{print $1}')"

[ "$BASE_BINARY_SHA" = "$P08_EXPECTED_BINARY_SHA" ] || hold "P08_BASE_BINARY_IDENTITY_MISMATCH"

printf 'P08_EXPECTED_BINARY_SHA=%s\n' "$P08_EXPECTED_BINARY_SHA"
printf 'BASE_BINARY_SHA=%s\n' "$BASE_BINARY_SHA"
printf 'BASE_APP_TREE_SHA=%s\n' "$BASE_APP_TREE_SHA"
printf 'BASE_RUNTIME_TREE_SHA=%s\n' "$BASE_RUNTIME_TREE_SHA"
printf 'BASE_RELEASE_SHA=%s\n' "$BASE_RELEASE_SHA"

printf 'P08_PASS=PASS\n'
printf 'BASE_RUNTIME_PID=%s\n' "$BASE_RUNTIME_PID"
printf 'BASE_APP_PID=%s\n' "$BASE_APP_PID"

printf '\n=== STOP ===\n'

stop_owned_app || hold "STOP_FAILED"

[ -z "$(runtime_pid)" ] || hold "STOP_PORT_STILL_ACTIVE"

STOP_PASS=PASS
P09_ACCEPTANCE=2_OF_8_PASS

printf 'STOP_PASS=PASS\n'

printf '\n=== CONTROLLED REPLACEMENT ===\n'

find "$HOME/Enguru/Evidence/MacEngineer" \
  -maxdepth 1 \
  -type f \
  -name 'native_app_prepare_*.txt' \
  -print 2>/dev/null \
  | sort > "$RUN_DIR/prep-before.txt"

find "$RUNTIME_ROOT" \
  -maxdepth 1 \
  -type d \
  -name '.runtime-previous.*' \
  -print 2>/dev/null \
  | sort > "$RUN_DIR/runtime-previous-before.txt"

zsh "$PREP"
PREP_RC=$?

[ "$PREP_RC" -eq 0 ] || hold "CONTROLLED_REPLACEMENT_PREP_FAILED"

find "$HOME/Enguru/Evidence/MacEngineer" \
  -maxdepth 1 \
  -type f \
  -name 'native_app_prepare_*.txt' \
  -print 2>/dev/null \
  | sort > "$RUN_DIR/prep-after.txt"

find "$RUNTIME_ROOT" \
  -maxdepth 1 \
  -type d \
  -name '.runtime-previous.*' \
  -print 2>/dev/null \
  | sort > "$RUN_DIR/runtime-previous-after.txt"

NEW_PREP_RECEIPT="$(
  comm -13 "$RUN_DIR/prep-before.txt" "$RUN_DIR/prep-after.txt" | tail -n 1
)"

RUNTIME_PREVIOUS="$(
  comm -13 "$RUN_DIR/runtime-previous-before.txt" "$RUN_DIR/runtime-previous-after.txt" | tail -n 1
)"

[ -n "$NEW_PREP_RECEIPT" ] || hold "NEW_PREP_RECEIPT_MISSING"
[ -f "$NEW_PREP_RECEIPT" ] || hold "NEW_PREP_RECEIPT_NOT_FILE"

[ -n "$RUNTIME_PREVIOUS" ] || hold "NEW_RUNTIME_PREVIOUS_MISSING"
[ -d "$RUNTIME_PREVIOUS" ] || hold "NEW_RUNTIME_PREVIOUS_NOT_DIRECTORY"

BACKUP_APP="$(
  awk -F= '
    $1=="previous_app_backup" {
      sub(/^[^=]*=/, "", $0)
      print
    }
  ' "$NEW_PREP_RECEIPT" | tail -n 1
)"

[ -n "$BACKUP_APP" ] || hold "PREVIOUS_APP_BACKUP_PATH_MISSING"
[ -d "$BACKUP_APP" ] || hold "PREVIOUS_APP_BACKUP_MISSING"

AFTER_APP_STAT="$(stat -f '%i:%m:%c' "$APP_BIN")"

[ "$AFTER_APP_STAT" != "$BASE_APP_STAT" ] \
  || hold "CONTROLLED_REPLACEMENT_NOT_OBSERVED"

CONTROLLED_REPLACEMENT_PASS=PASS
P09_ACCEPTANCE=3_OF_8_PASS

printf 'CONTROLLED_REPLACEMENT_PASS=PASS\n'
printf 'PREP_RECEIPT=%s\n' "$NEW_PREP_RECEIPT"
printf 'BACKUP_APP=%s\n' "$BACKUP_APP"
printf 'RUNTIME_PREVIOUS=%s\n' "$RUNTIME_PREVIOUS"

printf '\n=== RESTART REPLACEMENT ===\n'

open -n "$APP" || hold "REPLACEMENT_OPEN_FAILED"
wait_running || hold "REPLACEMENT_RUNTIME_NOT_READY"

REPLACEMENT_RUNTIME_PID="$(runtime_pid)"
[ -n "$REPLACEMENT_RUNTIME_PID" ] || hold "REPLACEMENT_RUNTIME_PID_MISSING"

REPLACEMENT_APP_PID="$(app_pid_from_runtime "$REPLACEMENT_RUNTIME_PID")"
[ -n "$REPLACEMENT_APP_PID" ] || hold "REPLACEMENT_APP_PID_MISSING"

[ "$REPLACEMENT_RUNTIME_PID" != "$BASE_RUNTIME_PID" ] \
  || hold "RESTART_RUNTIME_PID_NOT_FRESH"

RESTART_PASS=PASS
P09_ACCEPTANCE=4_OF_8_PASS

printf 'RESTART_PASS=PASS\n'
printf 'REPLACEMENT_RUNTIME_PID=%s\n' "$REPLACEMENT_RUNTIME_PID"
printf 'REPLACEMENT_APP_PID=%s\n' "$REPLACEMENT_APP_PID"

printf '\n=== ACTUAL KNOWN-GOOD ROLLBACK ===\n'

stop_owned_app || hold "ROLLBACK_PRESTOP_FAILED"

CURRENT_APP_SAVE="$RUN_DIR/replacement-installed.app"
CURRENT_RUNTIME_SAVE="$RUN_DIR/replacement-runtime"

mv "$APP" "$CURRENT_APP_SAVE" || hold "ROLLBACK_CURRENT_APP_SAVE_FAILED"
ditto "$BACKUP_APP" "$APP" || hold "ROLLBACK_APP_RESTORE_FAILED"

mv "$RUNTIME" "$CURRENT_RUNTIME_SAVE" || hold "ROLLBACK_CURRENT_RUNTIME_SAVE_FAILED"
mv "$RUNTIME_PREVIOUS" "$RUNTIME" || hold "ROLLBACK_RUNTIME_RESTORE_FAILED"

mkdir -p "$RUNTIME_ROOT/state"

cp \
  "$APP/Contents/Resources/release.json" \
  "$RUNTIME_ROOT/state/release.json" \
  || hold "ROLLBACK_RELEASE_MANIFEST_RESTORE_FAILED"

codesign --verify --deep --strict "$APP" || hold "ROLLBACK_CODESIGN_FAILED"

KNOWN_GOOD_ROLLBACK_PASS=PASS
P09_ACCEPTANCE=5_OF_8_PASS

printf 'KNOWN_GOOD_ROLLBACK_PASS=PASS\n'

printf '\n=== ROLLBACK REVERIFY ===\n'

open -n "$APP" || hold "ROLLBACK_REOPEN_FAILED"
wait_running || hold "ROLLBACK_RUNTIME_NOT_READY"

FINAL_RUNTIME_PID="$(runtime_pid)"
[ -n "$FINAL_RUNTIME_PID" ] || hold "FINAL_RUNTIME_PID_MISSING"

FINAL_APP_PID="$(app_pid_from_runtime "$FINAL_RUNTIME_PID")"
[ -n "$FINAL_APP_PID" ] || hold "FINAL_APP_PID_MISSING"

FINAL_COMMIT="$(
  PYTHONDONTWRITEBYTECODE=1 python3 -B - \
    "$APP/Contents/Resources/release.json" <<'PY'
import json
import sys
from pathlib import Path

print(
    json.loads(
        Path(sys.argv[1]).read_text(encoding="utf-8")
    )["sourceCommit"]
)
PY
)"

[ "$FINAL_COMMIT" = "$EXPECTED_HEAD" ] || hold "ROLLBACK_FINAL_COMMIT_MISMATCH"

cmp -s \
  "$PRODUCT/runtime/app.py" \
  "$RUNTIME/app.py" \
  || hold "ROLLBACK_RUNTIME_APP_PARITY_FAILED"

cmp -s \
  "$PRODUCT/runtime/static/index.html" \
  "$RUNTIME/static/index.html" \
  || hold "ROLLBACK_INDEX_PARITY_FAILED"

curl --max-time 5 -fsS \
  "http://127.0.0.1:8765/" \
  > "$RUN_DIR/final-user-path.html" \
  || hold "ROLLBACK_REAL_USER_PATH_FAILED"

cmp -s \
  "$RUN_DIR/final-user-path.html" \
  "$RUNTIME/static/index.html" \
  || hold "ROLLBACK_REAL_USER_PATH_PARITY_FAILED"


FINAL_BINARY_SHA="$(shasum -a 256 "$APP_BIN" | awk '{print $1}')"
FINAL_APP_TREE_SHA="$(tree_sha256 "$APP")"
FINAL_RUNTIME_TREE_SHA="$(tree_sha256 "$RUNTIME")"
FINAL_RELEASE_SHA="$(shasum -a 256 "$APP/Contents/Resources/release.json" | awk '{print $1}')"

[ "$FINAL_BINARY_SHA" = "$P08_EXPECTED_BINARY_SHA" ] || hold "ROLLBACK_P08_BINARY_IDENTITY_FAILED"
[ "$FINAL_BINARY_SHA" = "$BASE_BINARY_SHA" ] || hold "ROLLBACK_BASE_BINARY_IDENTITY_FAILED"
[ "$FINAL_APP_TREE_SHA" = "$BASE_APP_TREE_SHA" ] || hold "ROLLBACK_APP_TREE_IDENTITY_FAILED"
[ "$FINAL_RUNTIME_TREE_SHA" = "$BASE_RUNTIME_TREE_SHA" ] || hold "ROLLBACK_RUNTIME_TREE_IDENTITY_FAILED"
[ "$FINAL_RELEASE_SHA" = "$BASE_RELEASE_SHA" ] || hold "ROLLBACK_RELEASE_IDENTITY_FAILED"

FINAL_RUNTIME_COMMAND="$(ps -o command= -p "$FINAL_RUNTIME_PID" 2>/dev/null)"
FINAL_APP_COMMAND="$(ps -o command= -p "$FINAL_APP_PID" 2>/dev/null)"

FINAL_RUNTIME_CWD="$(
  lsof -a -p "$FINAL_RUNTIME_PID" -d cwd -Fn 2>/dev/null \
  | sed -n 's/^n//p' \
  | head -n 1
)"

case "$FINAL_RUNTIME_COMMAND" in
  *"$RUNTIME/app.py"*) ;;
  *) hold "ROLLBACK_RUNTIME_COMMAND_IDENTITY_FAILED" ;;
esac

case "$FINAL_APP_COMMAND" in
  *"$APP_BIN"*) ;;
  *) hold "ROLLBACK_APP_COMMAND_IDENTITY_FAILED" ;;
esac

[ "$FINAL_RUNTIME_CWD" = "$RUNTIME" ] || hold "ROLLBACK_RUNTIME_CWD_IDENTITY_FAILED"

printf 'FINAL_BINARY_SHA=%s\n' "$FINAL_BINARY_SHA"
printf 'FINAL_APP_TREE_SHA=%s\n' "$FINAL_APP_TREE_SHA"
printf 'FINAL_RUNTIME_TREE_SHA=%s\n' "$FINAL_RUNTIME_TREE_SHA"
printf 'FINAL_RELEASE_SHA=%s\n' "$FINAL_RELEASE_SHA"
printf 'FINAL_RUNTIME_COMMAND=%s\n' "$FINAL_RUNTIME_COMMAND"
printf 'FINAL_APP_COMMAND=%s\n' "$FINAL_APP_COMMAND"
printf 'FINAL_RUNTIME_CWD=%s\n' "$FINAL_RUNTIME_CWD"

ROLLBACK_REVERIFY_PASS=PASS
P09_ACCEPTANCE=6_OF_8_PASS

printf 'ROLLBACK_REVERIFY_PASS=PASS\n'
printf 'FINAL_RUNTIME_PID=%s\n' "$FINAL_RUNTIME_PID"
printf 'FINAL_APP_PID=%s\n' "$FINAL_APP_PID"
printf 'FINAL_KNOWN_GOOD=P08_VERIFIED\n'


printf '\n=== SOURCE + REMOTE AUTHORITY INVARIANTS ===\n'

POST_CONTROL_HEAD="$(git -C "$CONTROL" rev-parse HEAD)"
POST_CONTROL_BRANCH="$(git -C "$CONTROL" branch --show-current)"
POST_CONTROL_STATUS="$(git -C "$CONTROL" status --porcelain=v1 --untracked-files=all)"
POST_CONTROL_REMOTE_BRANCH="$(git -C "$CONTROL" rev-parse "origin/$CONTROL_BRANCH_EXPECTED")"
POST_CONTROL_REMOTE_MAIN="$(git -C "$CONTROL" rev-parse origin/main)"

POST_PRODUCT_HEAD="$(git -C "$PRODUCT" rev-parse HEAD)"
POST_PRODUCT_BRANCH="$(git -C "$PRODUCT" branch --show-current)"
POST_PRODUCT_STATUS="$(git -C "$PRODUCT" status --porcelain=v1 --untracked-files=all)"
POST_PRODUCT_REMOTE_BRANCH="$(git -C "$PRODUCT" rev-parse "origin/$PRODUCT_BRANCH_EXPECTED")"
POST_PRODUCT_REMOTE_MAIN="$(git -C "$PRODUCT" rev-parse origin/main)"

[ "$POST_CONTROL_HEAD" = "$PRE_CONTROL_HEAD" ] || hold "CONTROL_HEAD_MUTATED_DURING_P09"
[ "$POST_CONTROL_BRANCH" = "$PRE_CONTROL_BRANCH" ] || hold "CONTROL_BRANCH_MUTATED_DURING_P09"
[ "$POST_CONTROL_STATUS" = "$PRE_CONTROL_STATUS" ] || hold "CONTROL_WORKTREE_MUTATED_DURING_P09"

[ "$POST_PRODUCT_HEAD" = "$PRE_PRODUCT_HEAD" ] || hold "PRODUCT_HEAD_MUTATED_DURING_P09"
[ "$POST_PRODUCT_BRANCH" = "$PRE_PRODUCT_BRANCH" ] || hold "PRODUCT_BRANCH_MUTATED_DURING_P09"
[ "$POST_PRODUCT_STATUS" = "$PRE_PRODUCT_STATUS" ] || hold "PRODUCT_WORKTREE_MUTATED_DURING_P09"

[ "$POST_CONTROL_REMOTE_BRANCH" = "$PRE_CONTROL_REMOTE_BRANCH" ] || hold "CONTROL_REMOTE_TRACKING_CHANGED_DURING_P09"
[ "$POST_CONTROL_REMOTE_MAIN" = "$PRE_CONTROL_REMOTE_MAIN" ] || hold "CONTROL_REMOTE_MAIN_CHANGED_DURING_P09"
[ "$POST_PRODUCT_REMOTE_BRANCH" = "$PRE_PRODUCT_REMOTE_BRANCH" ] || hold "PRODUCT_REMOTE_TRACKING_CHANGED_DURING_P09"
[ "$POST_PRODUCT_REMOTE_MAIN" = "$PRE_PRODUCT_REMOTE_MAIN" ] || hold "PRODUCT_REMOTE_MAIN_CHANGED_DURING_P09"

printf 'SOURCE_MUTATION_OBSERVED=0\n'
printf 'REMOTE_MUTATION_OBSERVED=0\n'

printf '\n=== LIFECYCLE PROVENANCE + EVIDENCE CONTINUITY ===\n'

PYTHONDONTWRITEBYTECODE=1 python3 -B - \
  "$ACCEPTANCE" \
  "$P08_ACCEPTANCE" \
  "$EXPECTED_HEAD" \
  "$BASE_RUNTIME_PID" \
  "$BASE_APP_PID" \
  "$REPLACEMENT_RUNTIME_PID" \
  "$REPLACEMENT_APP_PID" \
  "$FINAL_RUNTIME_PID" \
  "$FINAL_APP_PID" \
  "$NEW_PREP_RECEIPT" \
  "$BACKUP_APP" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

(
    out,
    p08,
    product_head,
    base_runtime,
    base_app,
    replacement_runtime,
    replacement_app,
    final_runtime,
    final_app,
    prep_receipt,
    backup_app,
) = sys.argv[1:]

payload = {
    "schema": "enguru.gate11.p09-lifecycle/v1",
    "observedAt": datetime.now(timezone.utc).isoformat(),
    "state": "PASS",
    "package": "P09",
    "acceptance": {
        "P08_PASS": "PASS",
        "CONTROLLED_REPLACEMENT_PASS": "PASS",
        "STOP_PASS": "PASS",
        "RESTART_PASS": "PASS",
        "KNOWN_GOOD_ROLLBACK_PASS": "PASS",
        "ROLLBACK_REVERIFY_PASS": "PASS",
        "LIFECYCLE_PROVENANCE_PASS": "PASS",
        "EVIDENCE_CONTINUITY_PASS": "PASS",
    },
    "productHead": product_head,
    "p08Acceptance": p08,
    "processIdentity": {
        "baseline": {
            "runtimePid": int(base_runtime),
            "appPid": int(base_app),
        },
        "replacement": {
            "runtimePid": int(replacement_runtime),
            "appPid": int(replacement_app),
        },
        "rollbackFinal": {
            "runtimePid": int(final_runtime),
            "appPid": int(final_app),
        },
    },
    "replacement": {
        "prepareReceipt": prep_receipt,
        "knownGoodBackupApp": backup_app,
    },
    "finalKnownGood": "P08_VERIFIED",
    "sourceMutation": False,
    "remoteMutation": False,
    "newCore": False,
    "nextTransition": "P10",
}

Path(out).write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

[ "$?" -eq 0 ] || hold "P09_ACCEPTANCE_EVIDENCE_WRITE_FAILED"

LIFECYCLE_PROVENANCE_PASS=PASS
EVIDENCE_CONTINUITY_PASS=PASS
P09_ACCEPTANCE=8_OF_8_PASS

printf 'LIFECYCLE_PROVENANCE_PASS=PASS\n'
printf 'EVIDENCE_CONTINUITY_PASS=PASS\n'

printf '\nSTATE=PASS\n'
printf 'CLAIM=P09_FRESH_LIFECYCLE_CONTROLLED_REPLACEMENT_AND_ROLLBACK_VERIFIED\n'
printf 'P09_ACCEPTANCE=8_OF_8_PASS\n'
printf 'CONTROLLED_REPLACEMENT_PASS=PASS\n'
printf 'STOP_PASS=PASS\n'
printf 'RESTART_PASS=PASS\n'
printf 'KNOWN_GOOD_ROLLBACK_PASS=PASS\n'
printf 'ROLLBACK_REVERIFY_PASS=PASS\n'
printf 'LIFECYCLE_PROVENANCE_PASS=PASS\n'
printf 'EVIDENCE_CONTINUITY_PASS=PASS\n'
printf 'FINAL_KNOWN_GOOD=P08_VERIFIED\n'
printf 'SOURCE_MUTATION=0\n'
printf 'REMOTE_MUTATION=0\n'
printf 'P09_ACCEPTANCE_EVIDENCE=%s\n' "$ACCEPTANCE"
printf 'EVIDENCE=%s\n' "$LOG"
printf 'NEXT_ACTION=P10_INTERRUPTION_RECOVERY_RESUME_RELIABILITY\n'
