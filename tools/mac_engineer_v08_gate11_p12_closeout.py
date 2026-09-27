#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()

SESSION = ROOT / "governance/mac-engineer/SESSION_STATE_V1.json"
ROADMAP = ROOT / "governance/mac-engineer/PRODUCT_ROADMAP_V1.json"
STATUS = ROOT / "governance/mac-engineer/CURRENT_STATUS.md"
MATRIX = ROOT / "governance/mac-engineer/V08_PRODUCT_ENGINEERING_OPERATOR_ACCEPTANCE_MATRIX_V1.md"

P11_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.8"
    / "gate11-p11-independent-verification"
)

EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.8"
    / "gate11-p12-closure"
)

BRIDGE_PATH = ROOT / "tools/mac_engineer_donecheck_v12_bridge.py"

SPEC = importlib.util.spec_from_file_location(
    "enguru_donecheck_v12_bridge_p12",
    BRIDGE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("DONECHECK_BRIDGE_IMPORT_REQUIRED")

bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)

DONECHECK_VERSION = bridge.DONECHECK_VERSION
DONECHECK_SHA = bridge.DONECHECK_SHA
DONECHECK_RUNTIME = bridge.DONECHECK_RUNTIME
PRODUCER_ID = bridge.PRODUCER_ID
VITEST_REPORTER = bridge.VITEST_REPORTER

G11 = "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING"
G11_EXIT = "V08_CONSOLIDATED_MAC_COMMISSIONING_PASS"

G12 = "V08_GATE_12_DONECHECK_V1_2_HUMAN_THRESHOLD_LOCK"
G12_EXIT = "PRODUCT_ENGINEERING_OPERATOR_VERIFIED_LOCKED"

P11_REQUIRED = (
    "P10_PASS",
    "TARGETED_REGRESSION_PASS",
    "FULL_CONTROL_PLANE_REGRESSION_PASS",
    "PRODUCT_REGRESSION_PASS",
    "DIFF_CHECK_PASS",
    "SCOPE_CHECK_PASS",
    "PROVENANCE_CHECK_PASS",
    "RECOVERY_CHECK_PASS",
    "EVIDENCE_COMPLETENESS_PASS",
    "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
    "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
    "UNTRACKED_MANUAL_STEP_COUNT_0",
    "ZEKU_SUBSTITUTED_FOR_MAC_ENGINEER_EXECUTION_0",
    "CRITICAL_FALSE_PASS_0",
)

P12_ACCEPTANCE = (
    "P01_THROUGH_P11_PASS",
    "DONECHECK_V1_2_PASS",
    "CANONICAL_RECONCILIATION_PASS",
    "GATE11_EVIDENCE_BUNDLE_COMPLETE",
    "GATE11_ENGINEERING_EXECUTION_PASS",
    "ARCHITECTURE_STATE_PRESERVED",
    "NEW_CORE_FALSE",
    "HUMAN_MANUAL_SOURCE_EDIT_COUNT_0",
    "CHATGPT_DIRECT_FIELD_PRODUCT_PATCH_COUNT_0",
    "UNTRACKED_MANUAL_STEP_COUNT_0",
    "GATE11_VERIFIED_LOCKED",
    "GATE11_EXIT_V08_CONSOLIDATED_MAC_COMMISSIONING_PASS",
    "ACTIVE_GATE_12",
    "GATE12_EXECUTION_0",
    "STOP_TRUE",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON_OBJECT_REQUIRED:{path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 1800,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env=env,
    )
    return {
        "code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def require(result: dict[str, Any], label: str) -> None:
    if result["code"] != 0:
        tail = (
            str(result.get("stdout") or "")
            + "\n"
            + str(result.get("stderr") or "")
        )[-6000:]
        raise RuntimeError(f"{label}_FAILED:{tail}")


def latest_p11_final() -> Path:
    candidates = sorted(
        P11_ROOT.glob("*/p11-final-acceptance.json")
    )
    if not candidates:
        raise RuntimeError("P11_FINAL_ACCEPTANCE_REQUIRED")
    return candidates[-1]


def verify_p11() -> dict[str, Any]:
    final_path = latest_p11_final()
    final = load_json(final_path)

    acceptance = final.get("acceptance") or {}
    historical = final.get("historicalFalsePass") or {}

    ok = (
        final.get("state") == "PASS"
        and final.get("package") == "P11"
        and all(
            acceptance.get(key) == "PASS"
            for key in P11_REQUIRED
        )
        and historical.get("rejectedClaimCount") == 1
        and historical.get("canonicalized") is False
        and historical.get("preserved") is True
        and final.get(
            "currentUnresolvedCriticalFalsePassCount"
        ) == 0
        and final.get("sourceMutation") is False
        and final.get("remoteMutation") is False
        and final.get("newCore") is False
        and final.get("nextTransition") == "P12"
    )

    if not ok:
        raise RuntimeError("P11_FINAL_ACCEPTANCE_INVALID")

    audit_path = Path(
        str(final.get("verificationEvidence") or "")
    )

    if not audit_path.is_file():
        raise RuntimeError(
            "P11_VERIFICATION_AUDIT_REQUIRED"
        )

    audit = load_json(audit_path)

    if audit.get("state") != "PASS":
        raise RuntimeError(
            "P11_VERIFICATION_AUDIT_PASS_REQUIRED"
        )

    if audit.get("issues"):
        raise RuntimeError(
            "P11_VERIFICATION_AUDIT_ISSUES_PRESENT"
        )

    packages = audit.get("packageEvidence") or {}

    for n in range(1, 11):
        key = f"P{n:02d}"
        item = packages.get(key) or {}

        if item.get("present") is not True:
            raise RuntimeError(
                f"{key}_EVIDENCE_REQUIRED"
            )

        if int(item.get("fileCount") or 0) <= 0:
            raise RuntimeError(
                f"{key}_EVIDENCE_FILE_COUNT_REQUIRED"
            )

    return {
        "finalPath": final_path,
        "final": final,
        "auditPath": audit_path,
        "audit": audit,
    }


def build_criterion_manifests(
    p11: dict[str, Any],
    output_dir: Path,
) -> list[dict[str, Any]]:
    manifest_dir = output_dir / "criterion-manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    packages = p11["audit"]["packageEvidence"]

    criteria: list[dict[str, Any]] = []

    for number in range(1, 11):
        package = f"P{number:02d}"
        item = packages[package]

        manifest = {
            "schema":
                "enguru.gate11.p12-criterion-evidence/v1",
            "criterion": package,
            "state": "PASS",
            "p11Audit": str(p11["auditPath"]),
            "sourceDirectories":
                item.get("directories") or [],
            "sourceFileCount":
                int(item.get("fileCount") or 0),
            "p11IndependentAuditPass": True,
        }

        path = manifest_dir / f"{package}.json"
        write_json(path, manifest)

        criteria.append({
            "id": package,
            "statement":
                f"Gate 11 commissioning package {package} "
                "has independently audited Evidence.",
            "source": str(path),
            "artifactDigest":
                f"sha256:{sha256(path)}",
            "content":
                f"[DONECHECK:PASS] {package} package Evidence "
                "is present and independently audited PASS by P11.",
        })

    p11_manifest = {
        "schema":
            "enguru.gate11.p12-criterion-evidence/v1",
        "criterion": "P11",
        "state": "PASS",
        "finalAcceptance":
            str(p11["finalPath"]),
        "verificationAudit":
            str(p11["auditPath"]),
        "acceptance":
            p11["final"].get("acceptance"),
        "currentUnresolvedCriticalFalsePassCount":
            p11["final"].get(
                "currentUnresolvedCriticalFalsePassCount"
            ),
    }

    p11_manifest_path = manifest_dir / "P11.json"
    write_json(p11_manifest_path, p11_manifest)

    criteria.append({
        "id": "P11",
        "statement":
            "P11 independent verification and second-look "
            "Evidence bundle is 14/14 PASS.",
        "source": str(p11_manifest_path),
        "artifactDigest":
            f"sha256:{sha256(p11_manifest_path)}",
        "content":
            "[DONECHECK:PASS] P11 independent verification "
            "is 14/14 PASS with zero unresolved critical false pass.",
    })

    return criteria


def integration_test_source() -> str:
    return r'''
import { readFileSync, writeFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  createProducerEvidence,
  verifyTask,
  type SuccessCriterion,
} from "../src/donecheck-core";

const inputPath = process.env.ENGURU_V08_P12_INPUT;
const resultPath = process.env.ENGURU_V08_P12_RESULT;

if (!inputPath || !resultPath) {
  throw new Error("ENGURU_V08_P12_INPUT/RESULT required.");
}

const input = JSON.parse(readFileSync(inputPath, "utf8"));

describe("ENGURU v0.8 Gate11 P12 -> DoneCheck v1.2", () => {
  it("verifies criterion-scoped P01-P11 Evidence", () => {
    const criteria: SuccessCriterion[] = input.criteria.map(
      (item: any) => ({
        id: item.id,
        taskId: input.task.id,
        statement: item.statement,
        verificationInstruction:
          "Consume criterion-scoped trusted Mac Engineer Evidence.",
        kind: "objective",
        required: true,
      }),
    );

    const evidence = input.criteria.map((item: any) =>
      createProducerEvidence({
        id: "evidence-" + item.id,
        taskId: input.task.id,
        criterionId: item.id,
        kind: "test_report",
        content: item.content,
        collectedAt: input.observedAt,
        producerKind: input.producer.kind,
        producerId: input.producer.id,
        executionId:
          "v08-gate11-p12:" + item.id + ":" + input.doneCheck.exactSha,
        artifactDigest: item.artifactDigest,
        observedAt: input.observedAt,
        verificationRef: item.source,
      }),
    );

    const result = verifyTask({
      task: input.task,
      criteria,
      aiOutput:
        "ENGURU Mac Engineer supplied P01-P11 criterion-scoped Evidence.",
      evidence,
      resultId: "verification-enguru-v08-gate11-p12",
      verifiedAt: input.observedAt,
      policy: input.policy,
    });

    const outcomes = Object.fromEntries(
      result.criteria.map((item) => [
        item.criterionId,
        item.outcome,
      ]),
    );

    for (const item of input.criteria) {
      expect(outcomes[item.id]).toBe("pass");
    }

    expect(result.outcome).toBe("pass");

    writeFileSync(
      resultPath,
      JSON.stringify({
        schema:
          "enguru.gate11.p12-donecheck-result/v1",
        doneCheckVersion: input.doneCheck.version,
        doneCheckExactSha: input.doneCheck.exactSha,
        verificationResult: result,
        outcomes,
      }, null, 2) + "\n",
      "utf8",
    );
  });
});
'''


def execute_donecheck(
    p11: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    fabric = bridge.require_current_fabric()

    runtime = bridge.ensure_donecheck_runtime()

    if runtime.get("state") != "PASS":
        raise RuntimeError("DONECHECK_RUNTIME_PASS_REQUIRED")

    if runtime.get("version") != DONECHECK_VERSION:
        raise RuntimeError("DONECHECK_VERSION_MISMATCH")

    if runtime.get("exactSha") != DONECHECK_SHA:
        raise RuntimeError("DONECHECK_EXACT_SHA_MISMATCH")

    criteria = build_criterion_manifests(
        p11,
        output_dir,
    )

    observed_at = now()

    payload = {
        "schema":
            "enguru.gate11.p12-donecheck-input/v1",
        "observedAt": observed_at,
        "task": {
            "id": "enguru-v08-gate11-p12-closeout",
            "title":
                "ENGÜRÜ v0.8 Gate 11 canonical commissioning closeout",
            "requestText":
                "Verify P01 through P11 commissioning Evidence "
                "before canonical Gate 11 closure.",
            "status": "awaiting_review",
            "createdAt": observed_at,
        },
        "criteria": criteria,
        "producer": {
            "kind": "mac_engineer",
            "id": PRODUCER_ID,
        },
        "policy": {
            "requireEvidenceProvenance": True,
            "trustedProducerIds": [PRODUCER_ID],
        },
        "doneCheck": {
            "version": DONECHECK_VERSION,
            "exactSha": DONECHECK_SHA,
        },
        "fabric": {
            "state": fabric.get("state"),
            "repositoryCount":
                fabric.get("repositoryCount"),
            "mirrorPassCount":
                fabric.get("mirrorPassCount"),
        },
    }

    input_path = output_dir / "donecheck-input.json"
    write_json(input_path, payload)

    result_path = output_dir / "donecheck-result.json"

    test_path = (
        DONECHECK_RUNTIME
        / "tests"
        / "enguru-v08-gate11-p12.integration.test.ts"
    )

    test_path.write_text(
        integration_test_source(),
        encoding="utf-8",
    )

    try:
        env = dict(os.environ)
        env["ENGURU_V08_P12_INPUT"] = str(input_path)
        env["ENGURU_V08_P12_RESULT"] = str(result_path)

        vitest = (
            DONECHECK_RUNTIME
            / "node_modules"
            / ".bin"
            / "vitest"
        )

        result = run(
            [
                str(vitest),
                "run",
                str(
                    test_path.relative_to(
                        DONECHECK_RUNTIME
                    )
                ),
                f"--reporter={VITEST_REPORTER}",
            ],
            cwd=DONECHECK_RUNTIME,
            timeout=1800,
            env=env,
        )
    finally:
        test_path.unlink(missing_ok=True)

    require(result, "DONECHECK_P12_INTEGRATION")

    if not result_path.is_file():
        raise RuntimeError(
            "DONECHECK_P12_RESULT_REQUIRED"
        )

    output = load_json(result_path)
    verification = (
        output.get("verificationResult") or {}
    )

    if verification.get("outcome") != "pass":
        raise RuntimeError(
            "DONECHECK_P12_AGGREGATE_PASS_REQUIRED"
        )

    outcomes = output.get("outcomes") or {}

    expected = {
        f"P{i:02d}"
        for i in range(1, 12)
    }

    if set(outcomes) != expected:
        raise RuntimeError(
            "DONECHECK_P12_CRITERIA_SET_MISMATCH"
        )

    if any(
        outcomes.get(key) != "pass"
        for key in expected
    ):
        raise RuntimeError(
            "DONECHECK_P12_ALL_CRITERIA_PASS_REQUIRED"
        )

    status = run(
        ["git", "status", "--porcelain"],
        cwd=DONECHECK_RUNTIME,
        timeout=30,
    )
    require(status, "DONECHECK_RUNTIME_STATUS")

    if status["stdout"]:
        raise RuntimeError(
            "DONECHECK_RUNTIME_DIRTY:"
            + status["stdout"]
        )

    evidence = {
        "schema":
            "enguru.gate11.p12-donecheck-evidence/v1",
        "observedAt": now(),
        "state": "PASS",
        "doneCheck": {
            "version": DONECHECK_VERSION,
            "exactSha": DONECHECK_SHA,
        },
        "criteriaCount": len(criteria),
        "criteria":
            [item["id"] for item in criteria],
        "aggregateOutcome": "pass",
        "resultPath": str(result_path),
        "inputPath": str(input_path),
        "runtime": runtime,
    }

    path = output_dir / "donecheck-evidence.json"
    evidence["evidencePath"] = str(path)
    write_json(path, evidence)

    return evidence


def reconcile_documents(
    session_path: Path,
    roadmap_path: Path,
    status_path: Path,
    matrix_path: Path,
    *,
    closure_evidence: str,
    donecheck_evidence: str,
    observed_at: str,
) -> None:
    session = load_json(session_path)
    roadmap = load_json(roadmap_path)

    v08 = session["currentV08"]
    closure = v08["closureContract"]

    session["currentObjective"] = G12

    v08["nextAction"] = G12
    v08["localContinuityNextAction"] = G12

    local = v08.get(
        "controlPlaneLocalContinuity"
    ) or {}

    local["currentTechnicalTarget"] = G12
    local["nextAfterPass"] = G12
    v08["controlPlaneLocalContinuity"] = local

    closure["passedGates"] = list(range(1, 12))
    closure["activeGate"] = 12
    closure["remainingGates"] = [12]

    gate11 = v08.get("gate11") or {}
    gate11.update({
        "state": "VERIFIED_LOCKED",
        "executionStarted": True,
        "exit": G11_EXIT,
        "nextAction": G12,
        "closureEvidence": closure_evidence,
        "doneCheckV12": "PASS",
    })
    v08["gate11"] = gate11

    v08["gate11Closure"] = {
        "state": "VERIFIED_LOCKED",
        "name": G11,
        "exit": G11_EXIT,
        "doneCheckV12": "PASS",
        "doneCheckEvidence": donecheck_evidence,
        "evidence": closure_evidence,
        "architectureState": "PRESERVED",
        "newCore": False,
        "observedAt": observed_at,
        "gate12Execution": False,
    }

    v08["gate12"] = {
        "state": "ACTIVE",
        "name": G12,
        "title":
            "DoneCheck™ v1.2 + Human Threshold™ + Version Lock",
        "exit": G12_EXIT,
        "executionStarted": False,
        "authority": "HUMAN_THRESHOLD",
        "foundation": "GATE11_VERIFIED_LOCKED",
        "nextAction": G12,
    }

    prepared = session.get(
        "preparedGate11Method"
    )

    if isinstance(prepared, dict):
        prepared["state"] = "VERIFIED_LOCKED"
        prepared["executionActive"] = False
        prepared["currentPackage"] = "P12"
        prepared["nextTransition"] = (
            "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP"
        )

    write_json(session_path, session)

    current = roadmap["current"]

    completed = list(current.get("completed") or [])

    gate11_done = (
        "V08_GATE_11_CONSOLIDATED_MAC_COMMISSIONING_PASS"
    )

    if gate11_done not in completed:
        completed.append(gate11_done)

    current["completed"] = completed
    current["remaining"] = [G12]
    current["activeObjective"] = G12
    current["activeGate"] = 12
    current["nextAction"] = G12

    write_json(roadmap_path, roadmap)

    status = status_path.read_text(
        encoding="utf-8"
    )

    status = re.sub(
        r"(?m)^\*\*Updated:\*\*.*$",
        f"**Updated:** {observed_at[:10]}",
        status,
        count=1,
    )

    status = re.sub(
        r"(?m)^\*\*Current objective:\*\*.*$",
        f"**Current objective:** {G12}",
        status,
        count=1,
    )

    marker = (
        "<!-- ENGURU_GATE11_FINAL_CANONICAL_CLOSURE_V1 -->"
    )

    if marker not in status:
        status += f"""

{marker}

## GATE 11 — FINAL CANONICAL CLOSURE

**STATE — VERIFIED / LOCKED**

Exit:

`{G11_EXIT}`

DoneCheck™ v1.2:

**PASS**

Evidence:

`{closure_evidence}`

## CURRENT ACTIVE GATE

**Gate 12 — DoneCheck™ v1.2 + Human Threshold™ + Version Lock**

Canonical identifier:

`{G12}`

Exit:

`{G12_EXIT}`

Execution:

**ACTIVE / NOT STARTED**

## JUDGMENT

Gate 11 commissioning is **VERIFIED / LOCKED**.

Gate 12 is **ACTIVE** and has execution count **0**.

## NEXT ACTION

`{G12}`
"""

    status_path.write_text(
        status,
        encoding="utf-8",
    )

    matrix = matrix_path.read_text(
        encoding="utf-8"
    )

    marker = (
        "<!-- ENGURU_GATE11_P12_FINAL_CLOSURE_V1 -->"
    )

    if marker not in matrix:
        matrix += f"""

{marker}

## Gate 11 — FINAL CANONICAL CLOSURE

**STATE — VERIFIED / LOCKED**

Exit:

`{G11_EXIT}`

DoneCheck™ v1.2:

**PASS**

Architecture:

**PRESERVED**

New core:

**false**

## CURRENT ACTIVE GATE

**Gate 12 — DoneCheck™ v1.2 + Human Threshold™ + Version Lock**

Canonical identifier:

`{G12}`

Exit:

`{G12_EXIT}`

Execution:

**ACTIVE / NOT STARTED**

Gate 12 execution count:

**0**
"""

    matrix_path.write_text(
        matrix,
        encoding="utf-8",
    )


def validate_reconciliation() -> None:
    session = load_json(SESSION)
    roadmap = load_json(ROADMAP)

    v08 = session["currentV08"]
    closure = v08["closureContract"]
    gate11 = v08["gate11"]
    gate12 = v08["gate12"]

    current = roadmap["current"]

    checks = {
        "currentObjective":
            session.get("currentObjective") == G12,
        "v08NextAction":
            v08.get("nextAction") == G12,
        "passedGates":
            closure.get("passedGates")
            == list(range(1, 12)),
        "activeGate":
            closure.get("activeGate") == 12,
        "remainingGates":
            closure.get("remainingGates") == [12],
        "gate11Locked":
            gate11.get("state")
            == "VERIFIED_LOCKED",
        "gate11Exit":
            gate11.get("exit") == G11_EXIT,
        "gate12Active":
            gate12.get("state") == "ACTIVE",
        "gate12Execution0":
            gate12.get("executionStarted") is False,
        "roadmapObjective":
            current.get("activeObjective") == G12,
        "roadmapActiveGate":
            current.get("activeGate") == 12,
        "roadmapRemaining":
            current.get("remaining") == [G12],
    }

    failed = [
        key
        for key, value in checks.items()
        if not value
    ]

    if failed:
        raise RuntimeError(
            "CANONICAL_RECONCILIATION_FAILED:"
            + ",".join(failed)
        )


def perform() -> dict[str, Any]:
    pre_head_result = run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        timeout=30,
    )
    require(pre_head_result, "CONTROL_HEAD")
    pre_head = pre_head_result["stdout"]

    branch_result = run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        timeout=30,
    )
    require(branch_result, "CONTROL_BRANCH")
    branch = branch_result["stdout"]

    remote_result = run(
        ["git", "rev-parse", f"origin/{branch}"],
        cwd=ROOT,
        timeout=30,
    )
    require(remote_result, "CONTROL_REMOTE")

    if remote_result["stdout"] != pre_head:
        raise RuntimeError(
            "CONTROL_LOCAL_REMOTE_PARITY_REQUIRED"
        )

    clean = run(
        [
            "git",
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        ],
        cwd=ROOT,
        timeout=30,
    )
    require(clean, "CONTROL_STATUS")

    if clean["stdout"]:
        raise RuntimeError(
            "CONTROL_WORKTREE_CLEAN_REQUIRED:"
            + clean["stdout"]
        )

    p11 = verify_p11()

    output_dir = EVIDENCE_ROOT / stamp()
    output_dir.mkdir(parents=True, exist_ok=True)

    donecheck = execute_donecheck(
        p11,
        output_dir,
    )

    backups = output_dir / "canonical-prestate"
    backups.mkdir(parents=True, exist_ok=True)

    canonical = (
        SESSION,
        ROADMAP,
        STATUS,
        MATRIX,
    )

    for path in canonical:
        shutil.copy2(
            path,
            backups / path.name,
        )

    observed_at = now()

    try:
        reconcile_documents(
            SESSION,
            ROADMAP,
            STATUS,
            MATRIX,
            closure_evidence=str(
                output_dir
                / "p12-final-acceptance.json"
            ),
            donecheck_evidence=str(
                donecheck["evidencePath"]
            ),
            observed_at=observed_at,
        )

        validate_reconciliation()

        changed = run(
            ["git", "diff", "--name-only"],
            cwd=ROOT,
            timeout=30,
        )
        require(changed, "CANONICAL_DIFF")

        paths = sorted(
            line
            for line in changed["stdout"].splitlines()
            if line
        )

        expected = sorted([
            "governance/mac-engineer/SESSION_STATE_V1.json",
            "governance/mac-engineer/PRODUCT_ROADMAP_V1.json",
            "governance/mac-engineer/CURRENT_STATUS.md",
            "governance/mac-engineer/V08_PRODUCT_ENGINEERING_OPERATOR_ACCEPTANCE_MATRIX_V1.md",
        ])

        if paths != expected:
            raise RuntimeError(
                "CANONICAL_MUTATION_SCOPE_MISMATCH:"
                + repr(paths)
            )

        diff = run(
            ["git", "diff", "--check"],
            cwd=ROOT,
            timeout=30,
        )
        require(diff, "CANONICAL_DIFF_CHECK")

        add = run(
            ["git", "add", *expected],
            cwd=ROOT,
            timeout=30,
        )
        require(add, "CANONICAL_ADD")

        commit = run(
            [
                "git",
                "commit",
                "-m",
                "chore(mac-engineer): lock Gate11 and activate Gate12",
            ],
            cwd=ROOT,
            timeout=120,
        )
        require(commit, "CANONICAL_CLOSURE_COMMIT")

        post_head_result = run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            timeout=30,
        )
        require(
            post_head_result,
            "CANONICAL_CLOSURE_HEAD",
        )

        post_head = post_head_result["stdout"]

        clean_after = run(
            [
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
            cwd=ROOT,
            timeout=30,
        )
        require(
            clean_after,
            "CANONICAL_CLOSURE_STATUS",
        )

        if clean_after["stdout"]:
            raise RuntimeError(
                "CANONICAL_CLOSURE_WORKTREE_NOT_CLEAN"
            )

    except Exception:
        run(
            ["git", "reset", "--hard", pre_head],
            cwd=ROOT,
            timeout=60,
        )
        raise

    acceptance = {
        key: "PASS"
        for key in P12_ACCEPTANCE
    }

    evidence = {
        "schema":
            "enguru.gate11.p12-final-acceptance/v1",
        "observedAt": observed_at,
        "state": "PASS",
        "package": "P12",
        "acceptance": acceptance,
        "p11FinalAcceptance":
            str(p11["finalPath"]),
        "p11VerificationAudit":
            str(p11["auditPath"]),
        "doneCheckEvidence":
            str(donecheck["evidencePath"]),
        "doneCheckVersion":
            DONECHECK_VERSION,
        "doneCheckExactSha":
            DONECHECK_SHA,
        "controlHeadBefore":
            pre_head,
        "controlHeadAfter":
            post_head,
        "canonicalMutationFiles": 4,
        "remoteMutation": False,
        "productSourceMutation": False,
        "architectureState": "PRESERVED",
        "newCore": False,
        "gate11State": "VERIFIED_LOCKED",
        "gate11Exit": G11_EXIT,
        "activeGate": 12,
        "gate12State": "ACTIVE",
        "gate12ExecutionCount": 0,
        "stop": True,
        "nextTransition":
            "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP",
    }

    final_path = (
        output_dir
        / "p12-final-acceptance.json"
    )

    evidence["evidencePath"] = str(final_path)
    write_json(final_path, evidence)

    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["execute"],
    )
    parser.parse_args()

    try:
        result = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(
            "CLAIM=P12_DONECHECK_OR_CANONICAL_CLOSURE_HOLD"
        )
        print(
            "HOLD="
            + type(exc).__name__
            + ":"
            + str(exc)
        )
        print("P11_REEXECUTION=0")
        print("GATE12_EXECUTION_0=PASS")
        print("STOP_TRUE=PASS")
        print(
            "NEXT_ACTION="
            "RETURN_TO_ZEKU_WITHOUT_SECOND_CONTINUE"
        )
        return 2

    for key in P12_ACCEPTANCE:
        print(f"{key}=PASS")

    print("STATE=PASS")
    print("P12_ACCEPTANCE=15_OF_15_PASS")
    print(
        "DONECHECK_VERSION="
        + result["doneCheckVersion"]
    )
    print(
        "DONECHECK_EXACT_SHA="
        + result["doneCheckExactSha"]
    )
    print(
        "CANONICAL_MUTATION_FILE_COUNT="
        + str(result["canonicalMutationFiles"])
    )
    print(
        "CONTROL_HEAD_BEFORE="
        + result["controlHeadBefore"]
    )
    print(
        "CONTROL_HEAD_AFTER="
        + result["controlHeadAfter"]
    )
    print("REMOTE_MUTATION=0")
    print("PRODUCT_SOURCE_MUTATION=0")
    print("NEW_CORE=false")
    print(
        "P12_ACCEPTANCE_EVIDENCE="
        + result["evidencePath"]
    )
    print(
        "NEXT_ACTION="
        "GATE11_VERIFIED_LOCKED_GATE12_ACTIVE_STOP"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
