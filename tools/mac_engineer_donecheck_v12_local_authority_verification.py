#!/usr/bin/env python3
"""Gate 11 — DoneCheck™ v1.2 Local Authority Migration Verification.

This adapter does not implement verification semantics. It validates the
structural Gate 8–10 field Evidence, prepares criterion-scoped trusted producer
Evidence, and executes the canonical DoneCheck™ v1.2 verifier through the
existing Mac Engineer bridge.

External GitHub A09 remains a separate deferred evidence surface and is not
promoted by this local authority migration verification.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
BRIDGE_PATH = ROOT / "tools" / "mac_engineer_donecheck_v12_bridge.py"
EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.7"
    / "gate11-donecheck-local-authority"
)

SPEC = importlib.util.spec_from_file_location(
    "enguru_donecheck_v12_bridge",
    BRIDGE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("DONECHECK_V12_BRIDGE_IMPORT_SPEC_REQUIRED")
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)

DONECHECK_VERSION = bridge.DONECHECK_VERSION
DONECHECK_SHA = bridge.DONECHECK_SHA
DONECHECK_RUNTIME = bridge.DONECHECK_RUNTIME
PRODUCER_ID = bridge.PRODUCER_ID
VITEST_REPORTER = bridge.VITEST_REPORTER

CRITERIA = {
    "MAC-NATIVE-GATE-08": "Multi-repository Mac-native engineering authority field proof",
    "MAC-NATIVE-GATE-09": "Restart / recovery continuity and exactly-once field proof",
    "MAC-NATIVE-GATE-10": "Offline / GitVault reconciliation and no-second-truth field proof",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_REQUIRED:{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"{label}_INVALID:{type(exc).__name__}:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label}_OBJECT_REQUIRED:{path}")
    return value


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
    try:
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
    except subprocess.TimeoutExpired:
        return {"code": 124, "stdout": "", "stderr": "TIMEOUT"}


def require(result: dict[str, Any], label: str) -> None:
    if result["code"] != 0:
        tail = (
            str(result.get("stdout") or "")
            + "\n"
            + str(result.get("stderr") or "")
        )[-5000:]
        raise RuntimeError(f"{label}_FAILED:{tail}")


def resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return ROOT / path


def load_session() -> dict[str, Any]:
    return load_json(SESSION_STATE, "SESSION_STATE")


def gate8_source(v07: dict[str, Any]) -> Path:
    contract = (v07.get("verifiedFinishClosureContract") or {}).get("gate8") or {}
    value = str(contract.get("evidence") or "").strip()
    if not value:
        raise RuntimeError("GATE8_EVIDENCE_REFERENCE_REQUIRED")
    return resolve_path(value)


def gate9_source(v07: dict[str, Any]) -> Path:
    contract = (v07.get("verifiedFinishClosureContract") or {}).get("gate9") or {}
    value = str(contract.get("evidence") or "").strip()
    if not value:
        raise RuntimeError("GATE9_EVIDENCE_REFERENCE_REQUIRED")
    return resolve_path(value)


def gate10_source(v07: dict[str, Any]) -> Path:
    contract = (v07.get("verifiedFinishClosureContract") or {}).get("gate10") or {}
    value = str(contract.get("evidence") or "").strip()
    if not value:
        raise RuntimeError("GATE10_EVIDENCE_REFERENCE_REQUIRED")
    return resolve_path(value)


def validate_gate8(path: Path) -> dict[str, Any]:
    receipt = load_json(path, "GATE8_OPERATOR_RECEIPT")
    completed = set(receipt.get("completed") or [])
    required = {
        "MAC_NATIVE_AUTHORITY_MIGRATION_FIELD_PROOF_PASS",
        "MULTI_REPO_LOCAL_ENGINEERING_PASS",
        "REMOTE_PUSH_FALSE",
        "SECOND_CANONICAL_TRUTH_FALSE",
    }
    missing = sorted(required - completed)
    if missing:
        raise RuntimeError("GATE8_COMPLETION_REQUIRED:" + ",".join(missing))

    details = receipt.get("details") or {}
    proof = details.get("migration_proof") or {}
    if proof.get("state") != "PASS":
        raise RuntimeError("GATE8_MIGRATION_PROOF_PASS_REQUIRED")
    fields = proof.get("fields") or {}
    if fields.get("MULTI_REPO") != "PASS":
        raise RuntimeError("GATE8_MULTI_REPO_PASS_REQUIRED")
    if fields.get("REMOTE_PUSH") != "false":
        raise RuntimeError("GATE8_REMOTE_PUSH_FALSE_REQUIRED")
    if fields.get("SECOND_CANONICAL_TRUTH") != "false":
        raise RuntimeError("GATE8_SECOND_TRUTH_FALSE_REQUIRED")

    underlying = str(proof.get("evidence") or "").strip()
    if underlying:
        underlying_path = resolve_path(underlying)
        if not underlying_path.is_file():
            raise RuntimeError("GATE8_UNDERLYING_EVIDENCE_REQUIRED")
    else:
        underlying_path = path

    return {
        "criterion": "MAC-NATIVE-GATE-08",
        "source": str(underlying_path),
        "digest": f"sha256:{sha256(underlying_path)}",
        "validated": True,
        "content": (
            "[DONECHECK:PASS] Gate 8 verified multi-repository Mac-native "
            "engineering execution with remote push false and second canonical truth false."
        ),
    }


def validate_gate9(path: Path) -> dict[str, Any]:
    evidence = load_json(path, "GATE9_EVIDENCE")
    checks = {
        "state": evidence.get("state") == "PASS",
        "gate": evidence.get("gate") == 9,
        "processRestart": evidence.get("processRestart") == "PASS",
        "taskIdentityContinuity": evidence.get("taskIdentityContinuity") == "PASS",
        "checkpointResume": evidence.get("checkpointResume") == "PASS",
        "exactlyOnceDurableEffect": evidence.get("exactlyOnceDurableEffect") == "PASS",
        "durableEffectCount": evidence.get("durableEffectCount") == 1,
        "finalTaskState": evidence.get("finalTaskState") == "COMPLETE",
        "gitVaultMirrorUnchanged": evidence.get("gitVaultMirrorUnchanged") is True,
        "remotePush": evidence.get("remotePush") is False,
    }
    failed = [key for key, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("GATE9_STRUCTURAL_CHECK_FAILED:" + ",".join(failed))
    return {
        "criterion": "MAC-NATIVE-GATE-09",
        "source": str(path),
        "digest": f"sha256:{sha256(path)}",
        "validated": True,
        "content": (
            "[DONECHECK:PASS] Gate 9 verified process restart, same task identity, "
            "checkpoint resume, exactly-once durable effect, and final COMPLETE state."
        ),
    }


def validate_gate10(path: Path) -> dict[str, Any]:
    evidence = load_json(path, "GATE10_EVIDENCE")
    queue = evidence.get("offlineQueue") or {}
    gitvault = evidence.get("gitVault") or {}
    reconciliation = evidence.get("reconciliationReadiness") or {}
    checks = {
        "state": evidence.get("state") == "PASS",
        "gate": evidence.get("gate") == 10,
        "remotePush": evidence.get("remotePush") is False,
        "remoteMerge": evidence.get("remoteMerge") is False,
        "canonicalRemoteIdentityPreserved": evidence.get("canonicalRemoteIdentityPreserved") is True,
        "secondCanonicalTruthCreated": evidence.get("secondCanonicalTruthCreated") is False,
        "queueAuthority": queue.get("authority") == "PENDING_RECONCILIATION_NOT_CANONICAL",
        "queueRemoteMutation": queue.get("remoteMutation") is False,
        "queueSecondTruth": queue.get("secondCanonicalTruth") is False,
        "bundleVerify": queue.get("bundleVerify") == "PASS",
        "refsUnchanged": gitvault.get("refsUnchanged") is True,
        "fsckBefore": gitvault.get("fsckBefore") == "PASS",
        "fsckAfter": gitvault.get("fsckAfter") == "PASS",
        "applyCheck": reconciliation.get("patchApplyCheck") == "PASS",
        "reconciliationState": reconciliation.get("state") == "PASS",
    }
    failed = [key for key, ok in checks.items() if not ok]
    if failed:
        raise RuntimeError("GATE10_STRUCTURAL_CHECK_FAILED:" + ",".join(failed))
    return {
        "criterion": "MAC-NATIVE-GATE-10",
        "source": str(path),
        "digest": f"sha256:{sha256(path)}",
        "validated": True,
        "content": (
            "[DONECHECK:PASS] Gate 10 verified durable offline reconciliation artifacts, "
            "GitVault ref preservation, remote identity preservation, and no second canonical truth."
        ),
    }


def prepare_input(output_dir: Path) -> dict[str, Any]:
    bridge.require_current_fabric()
    session = load_session()
    v07 = session.get("currentV07") or {}
    closure = v07.get("verifiedFinishClosureContract") or {}

    passed = list(closure.get("passedGates") or [])
    if passed != list(range(1, 11)):
        raise RuntimeError(f"GATES_1_10_PASS_REQUIRED:{passed}")
    if closure.get("activeGate") != 11:
        raise RuntimeError("ACTIVE_GATE_11_REQUIRED")

    a09 = closure.get("githubA09") or {}
    if a09.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("EXTERNAL_A09_DEFERRED_BOUNDARY_REQUIRED")
    if a09.get("blockingLocalEngineering") is not False:
        raise RuntimeError("A09_LOCAL_ENGINEERING_NONBLOCKING_REQUIRED")

    validated = [
        validate_gate8(gate8_source(v07)),
        validate_gate9(gate9_source(v07)),
        validate_gate10(gate10_source(v07)),
    ]

    observed_at = now()
    task_id = "enguru-mac-v07-gate11-local-authority-migration"
    criteria = []
    for item in validated:
        criteria.append(
            {
                "gate": item["criterion"],
                "statement": CRITERIA[item["criterion"]],
                "source": item["source"],
                "artifactDigest": item["digest"],
                "content": item["content"],
                "expectedOutcome": "pass",
            }
        )

    payload = {
        "schema": "enguru.mac-engineer.donecheck-v1.2-local-authority-input/v1",
        "observedAt": observed_at,
        "task": {
            "id": task_id,
            "title": "ENGÜRÜ Mac-Native Engineering Authority™ migration verification",
            "requestText": (
                "Verify Gate 8 through Gate 10 local authority migration Evidence "
                "without changing the separate external GitHub A09 state."
            ),
            "status": "awaiting_review",
            "createdAt": observed_at,
        },
        "criteria": criteria,
        "producer": {"kind": "mac_engineer", "id": PRODUCER_ID},
        "policy": {
            "requireEvidenceProvenance": True,
            "trustedProducerIds": [PRODUCER_ID],
        },
        "expectedAggregateOutcome": "pass",
        "externalA09": {
            "state": a09.get("state"),
            "preserved": True,
            "promotedByThisVerification": False,
        },
        "doneCheck": {
            "version": DONECHECK_VERSION,
            "exactSha": DONECHECK_SHA,
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = output_dir / "input.json"
    input_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    payload["_inputPath"] = str(input_path)
    return payload


def integration_test_source() -> str:
    return '''import { readFileSync, writeFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  createProducerEvidence,
  verifyTask,
  type SuccessCriterion,
} from "../src/donecheck-core";

const inputPath = process.env.ENGURU_GATE11_INPUT;
const resultPath = process.env.ENGURU_GATE11_RESULT;
if (!inputPath || !resultPath) throw new Error("ENGURU_GATE11_INPUT/RESULT required.");

const input = JSON.parse(readFileSync(inputPath, "utf8"));

describe("ENGÜRÜ Mac-Native Authority Gate 11 -> DoneCheck v1.2", () => {
  it("verifies Gate 8-10 criterion-scoped migration evidence", () => {
    const criteria: SuccessCriterion[] = input.criteria.map((item: any) => ({
      id: item.gate,
      taskId: input.task.id,
      statement: item.statement,
      verificationInstruction: "Consume criterion-scoped trusted Mac-native authority Evidence.",
      kind: "objective",
      required: true,
    }));

    const evidence = input.criteria.map((item: any) =>
      createProducerEvidence({
        id: "evidence-" + item.gate,
        taskId: input.task.id,
        criterionId: item.gate,
        kind: "test_report",
        content: item.content,
        collectedAt: input.observedAt,
        producerKind: input.producer.kind,
        producerId: input.producer.id,
        executionId: "gate11:" + item.gate + ":" + input.doneCheck.exactSha,
        artifactDigest: item.artifactDigest,
        observedAt: input.observedAt,
        verificationRef: item.source,
      }),
    );

    const result = verifyTask({
      task: input.task,
      criteria,
      aiOutput: "ENGÜRÜ Mac-native authority supplied Gate 8-10 criterion-scoped Evidence.",
      evidence,
      resultId: "verification-enguru-mac-v07-gate11-local-authority",
      verifiedAt: input.observedAt,
      policy: input.policy,
    });

    const gateOutcomes = Object.fromEntries(
      result.criteria.map((criterion) => [criterion.criterionId, criterion.outcome]),
    );

    for (const item of input.criteria) {
      expect(gateOutcomes[item.gate]).toBe("pass");
    }
    expect(result.outcome).toBe("pass");
    expect(input.externalA09.state).toBe("EXTERNAL_BLOCKED_DEFERRED");
    expect(input.externalA09.promotedByThisVerification).toBe(false);

    writeFileSync(
      resultPath,
      JSON.stringify({
        schema: "enguru.mac-engineer.donecheck-v1.2-local-authority-result/v1",
        doneCheckVersion: input.doneCheck.version,
        doneCheckExactSha: input.doneCheck.exactSha,
        verificationResult: result,
        gateOutcomes,
        externalA09: input.externalA09,
      }, null, 2) + "\\n",
      "utf8",
    );
  });
});
'''


def execute_verification(
    input_payload: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    runtime = bridge.ensure_donecheck_runtime()
    if runtime.get("state") != "PASS":
        raise RuntimeError("DONECHECK_RUNTIME_PASS_REQUIRED")
    if runtime.get("version") != DONECHECK_VERSION:
        raise RuntimeError("DONECHECK_VERSION_REQUIRED")
    if runtime.get("exactSha") != DONECHECK_SHA:
        raise RuntimeError("DONECHECK_EXACT_SHA_REQUIRED")

    test_path = (
        DONECHECK_RUNTIME
        / "tests"
        / "enguru-mac-gate11-local-authority.integration.test.ts"
    )
    result_path = output_dir / "verification-result.json"
    test_path.write_text(integration_test_source(), encoding="utf-8")

    try:
        env = dict(os.environ)
        env["ENGURU_GATE11_INPUT"] = input_payload["_inputPath"]
        env["ENGURU_GATE11_RESULT"] = str(result_path)
        vitest = DONECHECK_RUNTIME / "node_modules" / ".bin" / "vitest"
        result = run(
            [
                str(vitest),
                "run",
                str(test_path.relative_to(DONECHECK_RUNTIME)),
                f"--reporter={VITEST_REPORTER}",
            ],
            cwd=DONECHECK_RUNTIME,
            timeout=1800,
            env=env,
        )
    finally:
        test_path.unlink(missing_ok=True)

    require(result, "DONECHECK_GATE11_INTEGRATION_TEST")
    if not result_path.is_file():
        raise RuntimeError("DONECHECK_GATE11_RESULT_REQUIRED")

    output = load_json(result_path, "DONECHECK_GATE11_RESULT")
    verification = output.get("verificationResult") or {}
    if verification.get("outcome") != "pass":
        raise RuntimeError(
            "DONECHECK_GATE11_OUTCOME_PASS_REQUIRED:"
            + str(verification.get("outcome"))
        )

    outcomes = output.get("gateOutcomes") or {}
    expected_ids = set(CRITERIA)
    if set(outcomes) != expected_ids:
        raise RuntimeError("DONECHECK_GATE11_CRITERIA_SET_REQUIRED")
    if any(outcomes.get(key) != "pass" for key in expected_ids):
        raise RuntimeError("DONECHECK_GATE11_ALL_CRITERIA_PASS_REQUIRED")

    external = output.get("externalA09") or {}
    if external.get("state") != "EXTERNAL_BLOCKED_DEFERRED":
        raise RuntimeError("DONECHECK_GATE11_EXTERNAL_A09_DEFERRED_REQUIRED")
    if external.get("promotedByThisVerification") is not False:
        raise RuntimeError("DONECHECK_GATE11_EXTERNAL_A09_NOT_PROMOTED_REQUIRED")

    status = run(["git", "status", "--porcelain"], cwd=DONECHECK_RUNTIME, timeout=30)
    require(status, "DONECHECK_RUNTIME_STATUS")
    if status["stdout"]:
        raise RuntimeError("DONECHECK_RUNTIME_CLEAN_REQUIRED:" + status["stdout"])

    return {
        "state": "PASS",
        "runtime": runtime,
        "resultPath": str(result_path),
        "gateOutcomes": outcomes,
        "aggregateOutcome": verification.get("outcome"),
        "externalA09": external,
    }


def perform() -> dict[str, Any]:
    output_dir = EVIDENCE_ROOT / stamp()
    payload = prepare_input(output_dir)
    execution = execute_verification(payload, output_dir)

    evidence = {
        "schema": "enguru.mac-engineer.v07-gate11-donecheck-v1.2/v1",
        "observedAt": now(),
        "state": "PASS",
        "gate": 11,
        "closureState": "LOCAL_AUTHORITY_MIGRATION_MACHINE_VERIFICATION_PASS",
        "doneCheck": {
            "repository": "engurulabory/donecheck",
            "version": DONECHECK_VERSION,
            "exactSha": DONECHECK_SHA,
        },
        "producer": PRODUCER_ID,
        "criteria": payload["criteria"],
        "gateOutcomes": execution["gateOutcomes"],
        "aggregateOutcome": execution["aggregateOutcome"],
        "verificationResultPath": execution["resultPath"],
        "inputPath": payload["_inputPath"],
        "runtime": execution["runtime"],
        "externalA09": {
            "state": execution["externalA09"]["state"],
            "preserved": True,
            "promotedByThisVerification": False,
        },
        "authorityBoundary": (
            "Gate 11 verifies only the Mac-native authority migration Evidence "
            "from Gates 8-10. External GitHub A09 remains deferred. "
            "Human Threshold and v0.7 version lock are not manufactured here."
        ),
        "nextAction": "V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY",
    }

    evidence_path = output_dir / "evidence.json"
    evidence["evidencePath"] = str(evidence_path)
    evidence_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    receipt = output_dir / "receipt.txt"
    receipt.write_text(
        "\n".join(
            [
                "STATE=PASS",
                "DONECHECK_VERSION=1.2.0",
                f"DONECHECK_EXACT_SHA={DONECHECK_SHA}",
                "GATE8=PASS",
                "GATE9=PASS",
                "GATE10=PASS",
                "AGGREGATE_OUTCOME=pass",
                "EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED",
                "EXTERNAL_A09_PROMOTED=false",
                "LOCAL_AUTHORITY_MIGRATION_MACHINE_VERIFICATION=PASS",
                f"EVIDENCE={evidence_path}",
                "NEXT_ACTION=V07_FINAL_CONSOLIDATED_MAC_CAMPAIGN_AND_VERIFY",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence


def main() -> int:
    try:
        result = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        print("NEXT_ACTION=RECONCILE_DONECHECK_V12_LOCAL_AUTHORITY_VERIFICATION")
        return 2

    print("STATE=PASS")
    print("DONECHECK_VERSION=1.2.0")
    print(f"DONECHECK_EXACT_SHA={DONECHECK_SHA}")
    print("GATE8=PASS")
    print("GATE9=PASS")
    print("GATE10=PASS")
    print("AGGREGATE_OUTCOME=pass")
    print("EXTERNAL_A09=EXTERNAL_BLOCKED_DEFERRED")
    print("EXTERNAL_A09_PROMOTED=false")
    print("LOCAL_AUTHORITY_MIGRATION_MACHINE_VERIFICATION=PASS")
    print(f"EVIDENCE={result['evidencePath']}")
    print(f"NEXT_ACTION={result['nextAction']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
