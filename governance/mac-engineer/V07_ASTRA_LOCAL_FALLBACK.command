#!/bin/zsh
set -euo pipefail

PRODUCT_REPO="${PRODUCT_REPO:-$HOME/Enguru/Projects/enguru-mac-engineer}"
EVIDENCE_DIR="${EVIDENCE_DIR:-$HOME/Enguru/Evidence/MacEngineer/v0.7}"
A09_BRANCH="${A09_BRANCH:-test/v07-a09-fault-injection-campaign}"
EXPECTED_SCOPE=

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_DIR/astra-fallback-$STAMP"
WORKTREE="$RUN_DIR/worktree"
mkdir -p "$RUN_DIR"

hold() {
  local reason="$1"
  python3 - "$RUN_DIR/evidence.json" "$reason" <<'PY'
import json, sys
from datetime import datetime, timezone
path, reason = sys.argv[1], sys.argv[2]
data = {
    "schema": "enguru.mac-engineer.v07-astra-local-fallback/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "HOLD",
    "reason": reason,
    "authority_boundary": "LOCAL_REHEARSAL_ONLY_EXTERNAL_GITHUB_CI_CONFIRMATION_REQUIRED",
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")
print(f"STATE=HOLD")
print(f"REASON={reason}")
print(f"EVIDENCE={path}")
PY
  exit 2
}

[[ -d "$PRODUCT_REPO/.git" ]] || hold "PRODUCT_REPOSITORY_NOT_FOUND"

git -C "$PRODUCT_REPO" fetch origin --prune

MAIN_SHA="$(git -C "$PRODUCT_REPO" rev-parse origin/main)"
CANDIDATE_SHA="$(git -C "$PRODUCT_REPO" rev-parse "origin/$A09_BRANCH")"

git -C "$PRODUCT_REPO" merge-base --is-ancestor "$MAIN_SHA" "$CANDIDATE_SHA" ||   hold "CANDIDATE_NOT_BASED_ON_CURRENT_MAIN"

ACTUAL_SCOPE="$(git -C "$PRODUCT_REPO" diff --name-only "$MAIN_SHA...$CANDIDATE_SHA" | sort)"
[[ "$ACTUAL_SCOPE" == "$EXPECTED_SCOPE" ]] || hold "CANDIDATE_SCOPE_MISMATCH"

git -C "$PRODUCT_REPO" worktree add --detach "$WORKTREE" "$CANDIDATE_SHA" >/dev/null

cleanup() {
  git -C "$PRODUCT_REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
}
trap cleanup EXIT

[[ -z "$(git -C "$WORKTREE" status --porcelain)" ]] || hold "DISPOSABLE_WORKTREE_NOT_CLEAN_AT_START"

(
  cd "$WORKTREE"
  python3 -B -m compileall -q runtime
) || hold "RUNTIME_COMPILE_FAILED"
print "RUNTIME_COMPILE=PASS"

TARGETED_LOGS=()
for run in 1 2 3 4 5; do
  log="$RUN_DIR/targeted-$run.log"
  (
    cd "$WORKTREE"
    PYTHONPATH="$WORKTREE/runtime"       python3 -B -m unittest discover         -s runtime/tests         -p 'test_v07_long_running_reliability.py'         -v
  ) >"$log" 2>&1 || hold "TARGETED_RUN_${run}_FAILED"
  TARGETED_LOGS+=("$log")
  print "TARGETED_RUN_${run}=PASS"
done

FULL_LOG="$RUN_DIR/full-regression.log"
(
  cd "$WORKTREE"
  PYTHONPATH="$WORKTREE/runtime"     python3 -B -m unittest discover -s runtime/tests -v
) >"$FULL_LOG" 2>&1 || hold "FULL_RUNTIME_REGRESSION_FAILED"
print "FULL_RUNTIME_REGRESSION=PASS"

zsh -n "$WORKTREE/execution_prep/native_app/prepare_native_app.command" ||   hold "NATIVE_PREP_SYNTAX_FAILED"
print "NATIVE_PREP_SYNTAX=PASS"

SWIFT_OUT="$RUN_DIR/EnguruMacEngineer"
xcrun swiftc -parse-as-library   "$WORKTREE/execution_prep/native_app/EnguruMacEngineerApp.swift"   -o "$SWIFT_OUT"   -framework SwiftUI   -framework WebKit   -framework AppKit || hold "NATIVE_SWIFT_BUILD_FAILED"
[[ -x "$SWIFT_OUT" ]] || hold "NATIVE_SWIFT_BUILD_OUTPUT_MISSING"
print "NATIVE_SWIFT_BUILD=PASS"

git -C "$WORKTREE" diff --check "$MAIN_SHA...HEAD" || hold "DIFF_CHECK_FAILED"
print "DIFF_CHECK=PASS"

FINAL_SCOPE="$(git -C "$WORKTREE" diff --name-only "$MAIN_SHA...HEAD" | sort)"
[[ "$FINAL_SCOPE" == "$EXPECTED_SCOPE" ]] || hold "FINAL_SCOPE_MISMATCH"
print "SCOPE_VALIDATION=PASS"

[[ -z "$(git -C "$WORKTREE" status --porcelain)" ]] || hold "DISPOSABLE_WORKTREE_DIRTY_AT_CLOSEOUT"
print "WORKTREE_CLOSEOUT=CLEAN"

python3 - "$RUN_DIR/evidence.json" "$MAIN_SHA" "$CANDIDATE_SHA" "$RUN_DIR" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

evidence_path, main_sha, candidate_sha, run_dir = sys.argv[1:5]
root = Path(run_dir)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

targeted = []
for index in range(1, 6):
    path = root / f"targeted-{index}.log"
    targeted.append({
        "run": index,
        "state": "PASS",
        "log": str(path),
        "sha256": sha256(path),
    })

full = root / "full-regression.log"
data = {
    "schema": "enguru.mac-engineer.v07-astra-local-fallback/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING",
    "main_sha": main_sha,
    "candidate_sha": candidate_sha,
    "candidate_scope": [
        ".github/workflows/product-ci.yml",
        ".github/workflows/v07-a09-full-regression.yml",
        ".github/workflows/v07-reliability-campaign.yml",
    ],
    "runtime_compile": "PASS",
    "targeted_consecutive_passes": 5,
    "targeted_runs": targeted,
    "full_runtime_regression": {
        "state": "PASS",
        "log": str(full),
        "sha256": sha256(full),
    },
    "native_prep_syntax": "PASS",
    "native_swift_build": "PASS",
    "diff_check": "PASS",
    "scope_validation": "PASS",
    "disposable_worktree_closeout": "CLEAN",
    "authority_boundary": "LOCAL_REHEARSAL_ONLY_EXTERNAL_GITHUB_CI_CONFIRMATION_REQUIRED",
    "canonical_judgment": "V07_A09_REMAINS_HOLD_UNTIL_EXTERNAL_GITHUB_CI_CONFIRMATION",
}
with open(evidence_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")

print("STATE=LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING")
print(f"MAIN_SHA={main_sha}")
print(f"CANDIDATE_SHA={candidate_sha}")
print("RUNTIME_COMPILE=PASS")
print("TARGETED_CONSECUTIVE_PASS=5_OF_5")
print("FULL_RUNTIME_REGRESSION=PASS")
print("NATIVE_VERIFICATION=PASS")
print("SCOPE_VALIDATION=PASS")
print("AUTHORITY=EXTERNAL_GITHUB_CI_CONFIRMATION_PENDING")
print(f"EVIDENCE={evidence_path}")
PY
.github/workflows/product-ci.yml\n.github/workflows/v07-a09-full-regression.yml\n.github/workflows/v07-reliability-campaign.yml'

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$EVIDENCE_DIR/astra-fallback-$STAMP"
WORKTREE="$RUN_DIR/worktree"
mkdir -p "$RUN_DIR"

hold() {
  local reason="$1"
  python3 - "$RUN_DIR/evidence.json" "$reason" <<'PY'
import json, sys
from datetime import datetime, timezone
path, reason = sys.argv[1], sys.argv[2]
data = {
    "schema": "enguru.mac-engineer.v07-astra-local-fallback/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "HOLD",
    "reason": reason,
    "authority_boundary": "LOCAL_REHEARSAL_ONLY_EXTERNAL_GITHUB_CI_CONFIRMATION_REQUIRED",
}
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")
print(f"STATE=HOLD")
print(f"REASON={reason}")
print(f"EVIDENCE={path}")
PY
  exit 2
}

[[ -d "$PRODUCT_REPO/.git" ]] || hold "PRODUCT_REPOSITORY_NOT_FOUND"

git -C "$PRODUCT_REPO" fetch origin --prune

MAIN_SHA="$(git -C "$PRODUCT_REPO" rev-parse origin/main)"
CANDIDATE_SHA="$(git -C "$PRODUCT_REPO" rev-parse "origin/$A09_BRANCH")"

git -C "$PRODUCT_REPO" merge-base --is-ancestor "$MAIN_SHA" "$CANDIDATE_SHA" ||   hold "CANDIDATE_NOT_BASED_ON_CURRENT_MAIN"

ACTUAL_SCOPE="$(git -C "$PRODUCT_REPO" diff --name-only "$MAIN_SHA...$CANDIDATE_SHA" | sort)"
[[ "$ACTUAL_SCOPE" == "$EXPECTED_SCOPE" ]] || hold "CANDIDATE_SCOPE_MISMATCH"

git -C "$PRODUCT_REPO" worktree add --detach "$WORKTREE" "$CANDIDATE_SHA" >/dev/null

cleanup() {
  git -C "$PRODUCT_REPO" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true
}
trap cleanup EXIT

[[ -z "$(git -C "$WORKTREE" status --porcelain)" ]] || hold "DISPOSABLE_WORKTREE_NOT_CLEAN_AT_START"

(
  cd "$WORKTREE"
  python3 -B -m compileall -q runtime
) || hold "RUNTIME_COMPILE_FAILED"
print "RUNTIME_COMPILE=PASS"

TARGETED_LOGS=()
for run in 1 2 3 4 5; do
  log="$RUN_DIR/targeted-$run.log"
  (
    cd "$WORKTREE"
    PYTHONPATH="$WORKTREE/runtime"       python3 -B -m unittest discover         -s runtime/tests         -p 'test_v07_long_running_reliability.py'         -v
  ) >"$log" 2>&1 || hold "TARGETED_RUN_${run}_FAILED"
  TARGETED_LOGS+=("$log")
  print "TARGETED_RUN_${run}=PASS"
done

FULL_LOG="$RUN_DIR/full-regression.log"
(
  cd "$WORKTREE"
  PYTHONPATH="$WORKTREE/runtime"     python3 -B -m unittest discover -s runtime/tests -v
) >"$FULL_LOG" 2>&1 || hold "FULL_RUNTIME_REGRESSION_FAILED"
print "FULL_RUNTIME_REGRESSION=PASS"

zsh -n "$WORKTREE/execution_prep/native_app/prepare_native_app.command" ||   hold "NATIVE_PREP_SYNTAX_FAILED"
print "NATIVE_PREP_SYNTAX=PASS"

SWIFT_OUT="$RUN_DIR/EnguruMacEngineer"
xcrun swiftc -parse-as-library   "$WORKTREE/execution_prep/native_app/EnguruMacEngineerApp.swift"   -o "$SWIFT_OUT"   -framework SwiftUI   -framework WebKit   -framework AppKit || hold "NATIVE_SWIFT_BUILD_FAILED"
[[ -x "$SWIFT_OUT" ]] || hold "NATIVE_SWIFT_BUILD_OUTPUT_MISSING"
print "NATIVE_SWIFT_BUILD=PASS"

git -C "$WORKTREE" diff --check "$MAIN_SHA...HEAD" || hold "DIFF_CHECK_FAILED"
print "DIFF_CHECK=PASS"

FINAL_SCOPE="$(git -C "$WORKTREE" diff --name-only "$MAIN_SHA...HEAD" | sort)"
[[ "$FINAL_SCOPE" == "$EXPECTED_SCOPE" ]] || hold "FINAL_SCOPE_MISMATCH"
print "SCOPE_VALIDATION=PASS"

[[ -z "$(git -C "$WORKTREE" status --porcelain)" ]] || hold "DISPOSABLE_WORKTREE_DIRTY_AT_CLOSEOUT"
print "WORKTREE_CLOSEOUT=CLEAN"

python3 - "$RUN_DIR/evidence.json" "$MAIN_SHA" "$CANDIDATE_SHA" "$RUN_DIR" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

evidence_path, main_sha, candidate_sha, run_dir = sys.argv[1:5]
root = Path(run_dir)

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

targeted = []
for index in range(1, 6):
    path = root / f"targeted-{index}.log"
    targeted.append({
        "run": index,
        "state": "PASS",
        "log": str(path),
        "sha256": sha256(path),
    })

full = root / "full-regression.log"
data = {
    "schema": "enguru.mac-engineer.v07-astra-local-fallback/v1",
    "observed_at": datetime.now(timezone.utc).isoformat(),
    "state": "LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING",
    "main_sha": main_sha,
    "candidate_sha": candidate_sha,
    "candidate_scope": [
        ".github/workflows/v07-a09-full-regression.yml",
        ".github/workflows/v07-reliability-campaign.yml",
    ],
    "runtime_compile": "PASS",
    "targeted_consecutive_passes": 5,
    "targeted_runs": targeted,
    "full_runtime_regression": {
        "state": "PASS",
        "log": str(full),
        "sha256": sha256(full),
    },
    "native_prep_syntax": "PASS",
    "native_swift_build": "PASS",
    "diff_check": "PASS",
    "scope_validation": "PASS",
    "disposable_worktree_closeout": "CLEAN",
    "authority_boundary": "LOCAL_REHEARSAL_ONLY_EXTERNAL_GITHUB_CI_CONFIRMATION_REQUIRED",
    "canonical_judgment": "V07_A09_REMAINS_HOLD_UNTIL_EXTERNAL_GITHUB_CI_CONFIRMATION",
}
with open(evidence_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    f.write("\n")

print("STATE=LOCAL_REHEARSAL_PASS_EXTERNAL_CONFIRMATION_PENDING")
print(f"MAIN_SHA={main_sha}")
print(f"CANDIDATE_SHA={candidate_sha}")
print("RUNTIME_COMPILE=PASS")
print("TARGETED_CONSECUTIVE_PASS=5_OF_5")
print("FULL_RUNTIME_REGRESSION=PASS")
print("NATIVE_VERIFICATION=PASS")
print("SCOPE_VALIDATION=PASS")
print("AUTHORITY=EXTERNAL_GITHUB_CI_CONFIRMATION_PENDING")
print(f"EVIDENCE={evidence_path}")
PY
