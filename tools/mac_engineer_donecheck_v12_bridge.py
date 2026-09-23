#!/usr/bin/env python3
"""ENGÜRÜ Mac Engineering™ → DoneCheck™ v1.2 integration bridge.

The bridge does not implement verification semantics. It prepares producer
inputs and executes the canonical DoneCheck v1.2 implementation from the
verified Mac Repository Fabric.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SESSION_STATE = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
FABRIC_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "repository-fabric.json"
DONECHECK_MIRROR = HOME / "Enguru" / "GitVault" / "RepositoryFabric" / "engurulabory" / "donecheck.git"
DONECHECK_RUNTIME = HOME / "Enguru" / "Runtime" / "DoneCheck" / "v1.2.0" / "source"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.7" / "a10-donecheck-v1.2"
DONECHECK_SHA = "8b90a8fc93453dd8a84994195d28d14b15e261cb"
DONECHECK_VERSION = "1.2.0"
PRODUCER_ID = "enguru.mac-engineer"

GATE_EVIDENCE = {
    "V07-A01": ROOT / "evidence" / "MAC_ENGINEER_V07_A01_A02_ENGINEERING_2026-09-22.md",
    "V07-A02": ROOT / "evidence" / "MAC_ENGINEER_V07_A01_A02_ENGINEERING_2026-09-22.md",
    "V07-A03": ROOT / "evidence" / "MAC_ENGINEER_V07_A03_A04_ENGINEERING_2026-09-22.md",
    "V07-A04": ROOT / "evidence" / "MAC_ENGINEER_V07_A03_A04_ENGINEERING_2026-09-22.md",
    "V07-A05": ROOT / "evidence" / "MAC_ENGINEER_V07_A05_A06_ENGINEERING_2026-09-22.md",
    "V07-A06": ROOT / "evidence" / "MAC_ENGINEER_V07_A05_A06_ENGINEERING_2026-09-22.md",
    "V07-A07": ROOT / "evidence" / "MAC_ENGINEER_V07_A07_A08_ENGINEERING_2026-09-22.md",
    "V07-A08": ROOT / "evidence" / "MAC_ENGINEER_V07_A07_A08_ENGINEERING_2026-09-22.md",
    "V07-A09": ROOT / "evidence" / "MAC_ENGINEER_V07_A09_ACTIONS_HOLD_2026-09-22.md",
}

GATE_LABELS = {
    "V07-A01": "Long-run task-state correctness",
    "V07-A02": "Durable resume",
    "V07-A03": "Idempotency stress",
    "V07-A04": "Single-writer concurrency",
    "V07-A05": "Bounded retry and watchdog",
    "V07-A06": "Provider/network/process recovery",
    "V07-A07": "Resource discipline",
    "V07-A08": "Evidence continuity",
    "V07-A09": "GitHub CI fault-injection external confirmation",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
    except Exception as exc:
        return {
            "code": 125,
            "stdout": "",
            "stderr": f"{type(exc).__name__}:{exc}",
        }


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"JSON_OBJECT_REQUIRED:{path}")
    return data


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_current_fabric() -> dict[str, Any]:
    if not FABRIC_STATE.is_file():
        raise RuntimeError("REPOSITORY_FABRIC_STATE_REQUIRED")
    state = load_json(FABRIC_STATE)
    if state.get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_PASS_REQUIRED")
    if state.get("repositoryCount") != 12 or state.get("mirrorPassCount") != 12:
        raise RuntimeError("REPOSITORY_FABRIC_12_OF_12_REQUIRED")
    queue = state.get("offlineQueueProof") or {}
    if queue.get("state") != "PASS":
        raise RuntimeError("REPOSITORY_FABRIC_OFFLINE_QUEUE_PASS_REQUIRED")
    return state


def canonical_gate_state() -> tuple[list[str], str]:
    session = load_json(SESSION_STATE)
    v07 = session.get("currentV07") or {}
    passed = list(v07.get("passedGates") or [])
    observed_a09 = session.get("observedV07A09LocalFallback") or {}
    a09_state = str(
        observed_a09.get("canonicalA09State")
        or v07.get("a09State")
        or "HOLD"
    )
    return passed, a09_state


def prepare_input(output_dir: Path) -> dict[str, Any]:
    require_current_fabric()
    passed, a09_state = canonical_gate_state()

    observed_at = now()
    task_id = "enguru-mac-v07-a10"
    criteria: list[dict[str, Any]] = []

    for gate in [f"V07-A{i:02d}" for i in range(1, 10)]:
        source = GATE_EVIDENCE[gate]
        if not source.is_file():
            raise RuntimeError(f"GATE_EVIDENCE_REQUIRED:{gate}:{source}")
        digest = f"sha256:{sha256(source)}"
        gate_pass = gate in passed
        if gate == "V07-A09":
            gate_pass = (
                a09_state == "PASS"
                or a09_state.startswith("PASS_")
                or a09_state.startswith("VERIFIED_PASS")
            )
        content = (
            f"[DONECHECK:PASS] {gate} canonical acceptance evidence is PASS."
            if gate_pass
            else f"{gate} remains pending canonical external confirmation; no automatic PASS assertion is permitted."
        )
        criteria.append(
            {
                "gate": gate,
                "statement": GATE_LABELS[gate],
                "source": str(source),
                "artifactDigest": digest,
                "content": content,
                "expectedOutcome": "pass" if gate_pass else "inconclusive",
            }
        )

    expected = "pass" if all(x["expectedOutcome"] == "pass" for x in criteria) else "inconclusive"
    payload = {
        "schema": "enguru.mac-engineer.donecheck-v1.2-input/v1",
        "observedAt": observed_at,
        "task": {
            "id": task_id,
            "title": "ENGÜRÜ Mac Engineering v0.7 A10 milestone verification",
            "requestText": "Verify V07-A01 through V07-A09 from criterion-scoped Mac Engineering evidence.",
            "status": "awaiting_review",
            "createdAt": observed_at,
        },
        "criteria": criteria,
        "producer": {"kind": "mac_engineer", "id": PRODUCER_ID},
        "policy": {
            "requireEvidenceProvenance": True,
            "trustedProducerIds": [PRODUCER_ID],
        },
        "expectedAggregateOutcome": expected,
        "a09CanonicalState": a09_state,
        "fabricEvidenceDigest": f"sha256:{sha256(FABRIC_STATE)}",
        "fabricState": str(FABRIC_STATE),
        "doneCheck": {"version": DONECHECK_VERSION, "exactSha": DONECHECK_SHA},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = output_dir / "input.json"
    input_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    payload["_inputPath"] = str(input_path)
    return payload


def ensure_donecheck_runtime() -> dict[str, Any]:
    if not DONECHECK_MIRROR.is_dir():
        raise RuntimeError("DONECHECK_FABRIC_MIRROR_REQUIRED")

    mirror_sha = run(
        ["git", "--git-dir", str(DONECHECK_MIRROR), "rev-parse", "refs/heads/main"],
        timeout=60,
    )
    if mirror_sha["code"] != 0 or mirror_sha["stdout"] != DONECHECK_SHA:
        raise RuntimeError(
            f"DONECHECK_MIRROR_EXACT_SHA_REQUIRED:observed={mirror_sha['stdout']}"
        )

    DONECHECK_RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    if not (DONECHECK_RUNTIME / ".git").exists():
        clone = run(
            ["git", "clone", str(DONECHECK_MIRROR), str(DONECHECK_RUNTIME)],
            timeout=600,
        )
        if clone["code"] != 0:
            raise RuntimeError(f"DONECHECK_RUNTIME_CLONE_FAILED:{clone['stderr'][-1000:]}")
    else:
        fetch = run(
            ["git", "fetch", str(DONECHECK_MIRROR), "+refs/*:refs/remotes/fabric/*"],
            cwd=DONECHECK_RUNTIME,
            timeout=300,
        )
        if fetch["code"] != 0:
            raise RuntimeError(f"DONECHECK_RUNTIME_FETCH_FAILED:{fetch['stderr'][-1000:]}")

    checkout = run(["git", "checkout", "--detach", DONECHECK_SHA], cwd=DONECHECK_RUNTIME, timeout=60)
    if checkout["code"] != 0:
        raise RuntimeError(f"DONECHECK_RUNTIME_CHECKOUT_FAILED:{checkout['stderr'][-1000:]}")

    reset = run(["git", "reset", "--hard", DONECHECK_SHA], cwd=DONECHECK_RUNTIME, timeout=60)
    if reset["code"] != 0:
        raise RuntimeError("DONECHECK_RUNTIME_RESET_FAILED")

    exclude = DONECHECK_RUNTIME / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing_exclude = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    required_excludes = ["node_modules/", "dist/"]
    missing_excludes = [item for item in required_excludes if item not in existing_exclude.splitlines()]
    if missing_excludes:
        with exclude.open("a", encoding="utf-8") as handle:
            if existing_exclude and not existing_exclude.endswith("\n"):
                handle.write("\n")
            for item in missing_excludes:
                handle.write(item + "\n")

    package = load_json(DONECHECK_RUNTIME / "package.json")
    if package.get("version") != DONECHECK_VERSION:
        raise RuntimeError(
            f"DONECHECK_VERSION_MISMATCH:{package.get('version')}:{DONECHECK_VERSION}"
        )

    vitest = DONECHECK_RUNTIME / "node_modules" / ".bin" / "vitest"
    install_state = "REUSED"
    if not vitest.is_file():
        install = run(
            ["npm", "install", "--package-lock=false", "--no-audit", "--no-fund"],
            cwd=DONECHECK_RUNTIME,
            timeout=1800,
        )
        if install["code"] != 0:
            raise RuntimeError(f"DONECHECK_NPM_INSTALL_FAILED:{install['stderr'][-2000:]}")
        install_state = "INSTALLED"

    suite = run(["npm", "test"], cwd=DONECHECK_RUNTIME, timeout=1800)
    if suite["code"] != 0:
        raise RuntimeError(
            "DONECHECK_CANONICAL_TEST_SUITE_FAILED:"
            + (suite["stdout"] + "\n" + suite["stderr"])[-3000:]
        )

    build = run(["npm", "run", "build"], cwd=DONECHECK_RUNTIME, timeout=1800)
    if build["code"] != 0:
        raise RuntimeError(
            "DONECHECK_CANONICAL_BUILD_FAILED:"
            + (build["stdout"] + "\n" + build["stderr"])[-3000:]
        )

    head = run(["git", "rev-parse", "HEAD"], cwd=DONECHECK_RUNTIME, timeout=30)
    return {
        "state": "PASS",
        "exactSha": head["stdout"],
        "version": package.get("version"),
        "dependencies": install_state,
        "canonicalTests": "PASS",
        "build": "PASS",
    }


def integration_test_source() -> str:
    return '''import { readFileSync, writeFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  createProducerEvidence,
  verifyTask,
  type SuccessCriterion,
} from "../src/donecheck-core";

const inputPath = process.env.ENGURU_A10_INPUT;
const resultPath = process.env.ENGURU_A10_RESULT;
if (!inputPath || !resultPath) throw new Error("ENGURU_A10_INPUT/RESULT required.");

const input = JSON.parse(readFileSync(inputPath, "utf8"));

describe("ENGÜRÜ Mac Engineering A10 -> DoneCheck v1.2", () => {
  it("consumes A01-A09 through canonical provenance-gated verification", () => {
    const criteria: SuccessCriterion[] = input.criteria.map((item: any) => ({
      id: item.gate,
      taskId: input.task.id,
      statement: item.statement,
      verificationInstruction: "Consume criterion-scoped trusted Mac Engineer Evidence.",
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
        executionId: "a10:" + item.gate + ":" + input.doneCheck.exactSha,
        artifactDigest: item.artifactDigest,
        observedAt: input.observedAt,
        verificationRef: item.source,
      }),
    );

    const result = verifyTask({
      task: input.task,
      criteria,
      aiOutput: "ENGÜRÜ Mac Engineering supplied criterion-scoped A01-A09 Evidence.",
      evidence,
      resultId: "verification-enguru-mac-v07-a10",
      verifiedAt: input.observedAt,
      policy: input.policy,
    });

    const gateOutcomes = Object.fromEntries(
      result.criteria.map((criterion) => [criterion.criterionId, criterion.outcome]),
    );

    for (const item of input.criteria) {
      expect(gateOutcomes[item.gate]).toBe(item.expectedOutcome);
    }
    expect(result.outcome).toBe(input.expectedAggregateOutcome);

    writeFileSync(
      resultPath,
      JSON.stringify({
        schema: "enguru.mac-engineer.donecheck-v1.2-result/v1",
        doneCheckVersion: input.doneCheck.version,
        doneCheckExactSha: input.doneCheck.exactSha,
        expectedAggregateOutcome: input.expectedAggregateOutcome,
        verificationResult: result,
        gateOutcomes,
      }, null, 2) + "\\n",
      "utf8",
    );
  });
});
'''


def execute_verification(input_payload: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    runtime = ensure_donecheck_runtime()
    test_path = DONECHECK_RUNTIME / "tests" / "enguru-mac-a10.integration.test.ts"
    result_path = output_dir / "verification-result.json"
    test_path.write_text(integration_test_source(), encoding="utf-8")

    try:
        env = dict(os.environ)
        env["ENGURU_A10_INPUT"] = input_payload["_inputPath"]
        env["ENGURU_A10_RESULT"] = str(result_path)
        vitest = DONECHECK_RUNTIME / "node_modules" / ".bin" / "vitest"
        result = run(
            [str(vitest), "run", str(test_path.relative_to(DONECHECK_RUNTIME)), "--reporter=basic"],
            cwd=DONECHECK_RUNTIME,
            timeout=1800,
            env=env,
        )
    finally:
        test_path.unlink(missing_ok=True)

    if result["code"] != 0:
        raise RuntimeError(
            "DONECHECK_A10_INTEGRATION_TEST_FAILED:"
            + (result["stdout"] + "\n" + result["stderr"])[-4000:]
        )
    if not result_path.is_file():
        raise RuntimeError("DONECHECK_A10_RESULT_REQUIRED")

    output = load_json(result_path)
    expected = input_payload["expectedAggregateOutcome"]
    actual = (output.get("verificationResult") or {}).get("outcome")
    if actual != expected:
        raise RuntimeError(f"DONECHECK_A10_OUTCOME_MISMATCH:{actual}:{expected}")

    git_status = run(["git", "status", "--porcelain"], cwd=DONECHECK_RUNTIME, timeout=30)
    if git_status["code"] != 0 or git_status["stdout"]:
        raise RuntimeError(f"DONECHECK_RUNTIME_DIRTY:{git_status['stdout']}")

    return {
        "state": "PASS",
        "runtime": runtime,
        "expectedOutcome": expected,
        "actualOutcome": actual,
        "resultPath": str(result_path),
    }


def perform() -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = EVIDENCE_ROOT / stamp
    payload = prepare_input(output_dir)
    execution = execute_verification(payload, output_dir)

    closure_state = (
        "MACHINE_VERIFICATION_PASS"
        if execution["actualOutcome"] == "pass"
        else "MILESTONE_CLOSURE_HOLD_A09_EXTERNAL_CONFIRMATION"
    )
    evidence = {
        "schema": "enguru.mac-engineer.v07-a10-donecheck-v1.2/v1",
        "observedAt": now(),
        "state": "INTEGRATION_PASS",
        "closureState": closure_state,
        "doneCheck": {
            "repository": "engurulabory/donecheck",
            "version": DONECHECK_VERSION,
            "exactSha": DONECHECK_SHA,
        },
        "producer": PRODUCER_ID,
        "integrationPass": True,
        "expectedAggregateOutcome": execution["expectedOutcome"],
        "actualAggregateOutcome": execution["actualOutcome"],
        "verificationResultPath": execution["resultPath"],
        "inputPath": payload["_inputPath"],
        "runtime": execution["runtime"],
        "authorityBoundary": (
            "A10 integration is proven. Canonical milestone closure remains HOLD while "
            "V07-A09 external confirmation is unresolved. Human review / Verified Finish "
            "is not manufactured by this machine integration proof."
        ),
    }
    evidence_path = output_dir / "evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    evidence["evidencePath"] = str(evidence_path)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify", "status"])
    args = parser.parse_args()

    try:
        if args.command == "status":
            candidates = sorted(EVIDENCE_ROOT.glob("*/evidence.json"))
            if not candidates:
                print("STATE=HOLD")
                print("HOLD=A10_EVIDENCE_REQUIRED")
                return 2
            result = load_json(candidates[-1])
            result["evidencePath"] = str(candidates[-1])
        else:
            result = perform()
    except Exception as exc:
        print("STATE=HOLD")
        print(f"HOLD={type(exc).__name__}:{exc}")
        return 2

    print(f"STATE={result['state']}")
    print(f"CLOSURE_STATE={result['closureState']}")
    print(f"DONECHECK_VERSION={result['doneCheck']['version']}")
    print(f"DONECHECK_EXACT_SHA={result['doneCheck']['exactSha']}")
    print(f"VERIFICATION_OUTCOME={result['actualAggregateOutcome']}")
    print(f"EVIDENCE={result['evidencePath']}")
    print(
        "NEXT_ACTION="
        + (
            "V07_A11_CONSOLIDATED_MAC_CAMPAIGN"
            if result["closureState"] == "MACHINE_VERIFICATION_PASS"
            else "V07_A09_EXTERNAL_CONFIRMATION_OR_LOCAL_CONTINUITY"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
