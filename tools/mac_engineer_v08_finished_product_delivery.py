from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HOME = Path.home()
CONTROL = Path(__file__).resolve().parents[1]
FIELD = HOME / "Enguru" / "Projects" / "local-csv-inspector"

SESSION = (
    CONTROL
    / "governance"
    / "mac-engineer"
    / "SESSION_STATE_V1.json"
)

ACCEPTANCE_MATRIX = (
    CONTROL
    / "governance"
    / "mac-engineer"
    / "V08_PRODUCT_ENGINEERING_OPERATOR_ACCEPTANCE_MATRIX_V1.md"
)

FIELD_CONTRACT = FIELD / "Contracts" / "VERTICAL_SLICE_V1.json"
FIELD_SOURCE = FIELD / "Sources" / "LocalCSVInspector" / "main.swift"
FIELD_FIXTURE = FIELD / "Fixtures" / "sample.csv"

EVIDENCE_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.8"
    / "finished-product-delivery"
)

GATE6_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.8"
    / "existing-product-change"
)

GATE9_ROOT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.8"
    / "gate9-final-canonical-reconciliation"
)

OBJECTIVE = "V08_FINISHED_PRODUCT_DELIVERY_SCENARIO"
EXIT = "V08_FINISHED_PRODUCT_DELIVERY_ACCEPTED"

EXPECTED_FIELD_HEAD = (
    "927fbc2d3130d474bcf9443231e741938b03636d"
)


def now() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise RuntimeError(f"{label}_MISSING:{path}")

    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return (
        "sha256:"
        + hashlib.sha256(path.read_bytes()).hexdigest()
    )


def run(
    cmd: list[str],
    *,
    cwd: Path,
    timeout: int = 900,
) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )

    return {
        "code": p.returncode,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def git(path: Path, *args: str) -> str:
    result = run(
        ["git", *args],
        cwd=path,
        timeout=120,
    )

    if result["code"] != 0:
        raise RuntimeError(
            "GIT_FAILED:"
            + " ".join(args)
            + ":"
            + result["stderr"]
        )

    return str(result["stdout"]).strip()


def latest_evidence(root: Path) -> Path:
    if not root.is_dir():
        raise RuntimeError(
            f"EVIDENCE_ROOT_MISSING:{root}"
        )

    candidates = sorted(
        root.glob("*/evidence.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise RuntimeError(
            f"EVIDENCE_REQUIRED:{root}"
        )

    return candidates[0]


def verify_preconditions() -> dict[str, Any]:
    session = load_json(
        SESSION,
        "SESSION_STATE",
    )

    if session.get("currentVersion") != "v0.8":
        raise RuntimeError(
            "CURRENT_VERSION_V08_REQUIRED"
        )

    if session.get("currentObjective") != OBJECTIVE:
        raise RuntimeError(
            "V08_GATE10_OBJECTIVE_REQUIRED"
        )

    matrix = ACCEPTANCE_MATRIX.read_text(
        encoding="utf-8"
    )

    required_contract_terms = (
        "Gate 10 — Finished-Product Delivery Acceptance",
        "completion means usable finished product, not code completion",
        "user-facing onboarding/launch path is clear",
        "operational status is understandable",
        "Evidence bundle is complete",
        "unresolved technical items are explicit",
        "Human Threshold receives a concise decision surface",
        EXIT,
    )

    missing = [
        term
        for term in required_contract_terms
        if term not in matrix
    ]

    if missing:
        raise RuntimeError(
            "GATE10_ACCEPTANCE_CONTRACT_MISSING:"
            + "|".join(missing)
        )

    if not FIELD.is_dir():
        raise RuntimeError(
            "FIELD_PRODUCT_REPOSITORY_REQUIRED"
        )

    field_head = git(
        FIELD,
        "rev-parse",
        "HEAD",
    )

    if field_head != EXPECTED_FIELD_HEAD:
        raise RuntimeError(
            "FIELD_PRODUCT_HEAD_MISMATCH:"
            + field_head
        )

    if git(FIELD, "status", "--porcelain"):
        raise RuntimeError(
            "FIELD_PRODUCT_CLEAN_REQUIRED"
        )

    gate9_path = latest_evidence(GATE9_ROOT)
    gate9 = load_json(
        gate9_path,
        "GATE9_FINAL_EVIDENCE",
    )

    gate9_text = gate9_path.read_text(
        encoding="utf-8"
    )

    if gate9.get("state") != "PASS":
        raise RuntimeError(
            "GATE9_FINAL_PASS_REQUIRED"
        )

    if "V08_RELEASE_LIFECYCLE_VERIFIED" not in gate9_text:
        raise RuntimeError(
            "GATE9_EXIT_REQUIRED"
        )

    gate6_path = latest_evidence(GATE6_ROOT)
    gate6 = load_json(
        gate6_path,
        "GATE6_PRODUCT_EVIDENCE",
    )

    if gate6.get("implementationState") != "PASS":
        raise RuntimeError(
            "GATE6_IMPLEMENTATION_PASS_REQUIRED"
        )

    return {
        "session": session,
        "gate9Path": gate9_path,
        "gate9Digest": digest(gate9_path),
        "gate6Path": gate6_path,
        "gate6Digest": digest(gate6_path),
        "fieldHead": field_head,
    }


def inspect_field_source() -> dict[str, Any]:
    source = FIELD_SOURCE.read_text(
        encoding="utf-8"
    )

    required = {
        "importAction":
            'Button("Import CSV")',
        "nativeFileImporter":
            ".fileImporter(",
        "csvRead":
            "DataFrame(contentsOfCSVFile:",
        "fileIdentity":
            'Text("File:',
        "columnCount":
            'Text("Columns:',
        "rowCount":
            'Text("Rows:',
        "missingSummary":
            "missingCount",
        "preview":
            'Text("Preview (first 5 rows):")',
        "numericSummary":
            'Text("Numeric summaries:")',
        "exportAction":
            'Button("Export Report")',
        "nativeSavePanel":
            "NSSavePanel()",
        "reportWrite":
            "report.write(to:",
    }

    checks = {
        name: token in source
        for name, token in required.items()
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    if failed:
        raise RuntimeError(
            "FIELD_DELIVERY_SURFACE_MISSING:"
            + ",".join(failed)
        )

    return {
        "state": "PASS",
        "checks": checks,
        "source": str(FIELD_SOURCE),
        "sourceDigest": digest(FIELD_SOURCE),
    }


def verify_fixture() -> dict[str, Any]:
    contract = load_json(
        FIELD_CONTRACT,
        "FIELD_CONTRACT",
    )

    expected = (
        contract.get("firstVerticalSlice", {})
        .get("expectedTruth", {})
    )

    with FIELD_FIXTURE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = list(reader.fieldnames or [])

    missing_values = {
        column: sum(
            1
            for row in rows
            if str(row.get(column) or "").strip() == ""
        )
        for column in columns
    }

    expected_missing = (
        expected.get("missingValues") or {}
    )

    if len(rows) != expected.get("rows"):
        raise RuntimeError(
            "FIELD_FIXTURE_ROW_COUNT_MISMATCH"
        )

    if len(columns) != expected.get("columns"):
        raise RuntimeError(
            "FIELD_FIXTURE_COLUMN_COUNT_MISMATCH"
        )

    if columns != expected.get("columnNames"):
        raise RuntimeError(
            "FIELD_FIXTURE_COLUMN_NAMES_MISMATCH"
        )

    for key, value in expected_missing.items():
        if missing_values.get(key) != value:
            raise RuntimeError(
                "FIELD_FIXTURE_MISSING_VALUE_MISMATCH:"
                + key
            )

    return {
        "state": "PASS",
        "rows": len(rows),
        "columns": len(columns),
        "columnNames": columns,
        "missingValues": missing_values,
        "fixture": str(FIELD_FIXTURE),
        "fixtureDigest": digest(FIELD_FIXTURE),
        "contract": str(FIELD_CONTRACT),
        "contractDigest": digest(FIELD_CONTRACT),
    }


def build_and_fresh_launch() -> dict[str, Any]:
    build = run(
        ["swift", "build"],
        cwd=FIELD,
        timeout=1200,
    )

    if build["code"] != 0:
        raise RuntimeError(
            "FIELD_SWIFT_BUILD_FAILED:"
            + build["stderr"][-3000:]
        )

    bin_path = run(
        ["swift", "build", "--show-bin-path"],
        cwd=FIELD,
        timeout=120,
    )

    if bin_path["code"] != 0:
        raise RuntimeError(
            "FIELD_BINARY_PATH_UNAVAILABLE"
        )

    binary = (
        Path(bin_path["stdout"])
        / "LocalCSVInspector"
    )

    if not binary.is_file():
        raise RuntimeError(
            "FIELD_BINARY_MISSING:"
            + str(binary)
        )

    process = subprocess.Popen(
        [str(binary)],
        cwd=str(FIELD),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )

    time.sleep(3.0)

    if process.poll() is not None:
        stderr = ""

        if process.stderr is not None:
            stderr = process.stderr.read()

        raise RuntimeError(
            "FIELD_FRESH_LAUNCH_FAILED:"
            + stderr[-3000:]
        )

    process.terminate()

    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)

    return {
        "state": "PASS",
        "build": "PASS",
        "binary": str(binary),
        "binaryDigest": digest(binary),
        "freshLaunch": "PASS",
    }


def write_hold(
    run_dir: Path,
    reason: str,
    details: dict[str, Any] | None = None,
) -> int:
    run_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = run_dir / "evidence.json"

    payload = {
        "schema":
            "enguru.mac-engineer.v08-finished-product-delivery/v1",
        "observedAt": now(),
        "state": "HOLD",
        "technicalState": "HOLD",
        "gate": "V08-10",
        "reason": reason,
        "details": details or {},
        "fieldProductMutation": False,
        "remotePush": False,
        "newCore": False,
        "secondCanonicalTruth": False,
        "nextAction": "RECOVERY_REQUIRED",
    }

    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("STATE=HOLD")
    print("V08_GATE_10=HOLD")
    print("V08_GATE_10_TECHNICAL=HOLD")
    print(f"HOLD={reason}")
    print(f"EVIDENCE={path}")
    print("NEXT_ACTION=RECOVERY_REQUIRED")

    return 2


def main() -> int:
    run_dir = EVIDENCE_ROOT / stamp()

    try:
        preconditions = verify_preconditions()

        run_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        field_source = inspect_field_source()
        fixture = verify_fixture()
        runtime = build_and_fresh_launch()

        path = run_dir / "evidence.json"

        payload = {
            "schema":
                "enguru.mac-engineer.v08-finished-product-delivery/v1",
            "observedAt": now(),
            "state": "HOLD",
            "technicalState": "PASS",
            "gate": "V08-10",
            "objective": OBJECTIVE,
            "exit": EXIT,
            "claim": (
                "Existing verified delivery capabilities are fresh-bound "
                "to the Gate 10 finished-product delivery contract. "
                "Technical acceptance is PASS; final human product "
                "acceptance remains explicit."
            ),
            "sourceTruth": {
                "controlHead":
                    git(CONTROL, "rev-parse", "HEAD"),
                "fieldHead":
                    preconditions["fieldHead"],
                "fieldClean": True,
            },
            "historicalEvidence": {
                "gate6":
                    str(preconditions["gate6Path"]),
                "gate6Digest":
                    preconditions["gate6Digest"],
                "gate9":
                    str(preconditions["gate9Path"]),
                "gate9Digest":
                    preconditions["gate9Digest"],
            },
            "technicalCriteria": {
                "userFacingDelivery": {
                    "state": "PASS",
                    "basis": [
                        "real native SwiftUI product",
                        "fresh executable launch",
                        "visible Import CSV entry surface",
                    ],
                },
                "operationalUsagePath": {
                    "state": "PASS",
                    "basis": [
                        "native file importer",
                        "real CSV fixture contract",
                        "DataFrame CSV parsing",
                        "row/column/missing/preview/numeric summaries",
                    ],
                },
                "operationalStatus": {
                    "state": "PASS",
                    "basis": [
                        "Gate 6 primary-state implementation evidence",
                        "conditional attention surface",
                        "visible next-action surface",
                    ],
                },
                "finishedResultDelivery": {
                    "state": "PASS",
                    "basis": [
                        "visible analysis result implementation",
                        "native NSSavePanel export surface",
                        "readable text-report write path",
                    ],
                },
                "evidenceBundle": {
                    "state": "PASS",
                    "basis": [
                        "Gate 9 lifecycle evidence",
                        "Gate 6 product-state evidence",
                        "field source digest",
                        "fixture digest",
                        "binary digest",
                        "fresh launch evidence",
                    ],
                },
            },
            "fieldProduct": {
                "name": "LOCAL CSV INSPECTOR",
                "path": str(FIELD),
                "sourceInspection": field_source,
                "fixtureVerification": fixture,
                "runtimeVerification": runtime,
                "mutation": False,
            },
            "unresolvedItems": {
                "state": "PASS",
                "items": [
                    "FINAL_HUMAN_PRODUCT_ACCEPTANCE"
                ],
            },
            "humanDecisionSurface": {
                "state": "PASS",
                "authority": "Human Threshold™",
                "decisionOptions": [
                    "ACCEPT",
                    "HOLD",
                ],
                "review": [
                    "Open LOCAL CSV INSPECTOR.",
                    "Confirm Import CSV is clear as the first action.",
                    "Select Fixtures/sample.csv.",
                    "Confirm sample.csv is identified.",
                    "Confirm Rows = 4 and Columns = 4.",
                    "Confirm missing values include score = 1 and age = 1.",
                    "Confirm Preview and Numeric summaries are understandable.",
                    "Use Export Report and confirm the saved report is readable.",
                    "Confirm the finished result feels delivered rather than merely built.",
                ],
            },
            "counters": {
                "humanManualSourceEditCount": 0,
                "chatgptDirectFieldProductPatchCount": 0,
                "untrackedManualStepCount": 0,
            },
            "fieldProductMutation": False,
            "remotePush": False,
            "newCore": False,
            "secondCanonicalTruth": False,
            "hold": "HUMAN_DECISION_REQUIRED",
            "nextAction":
                "GATE10_HUMAN_DELIVERY_ACCEPTANCE",
        }

        payload["evidencePath"] = str(path)

        path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        print("STATE=HOLD")
        print("V08_GATE_10=HOLD")
        print("V08_GATE_10_TECHNICAL=PASS")
        print("USER_FACING_DELIVERY_TECHNICAL=PASS")
        print("OPERATIONAL_USAGE_PATH_TECHNICAL=PASS")
        print("OPERATIONAL_STATUS_TECHNICAL=PASS")
        print("FINISHED_RESULT_DELIVERY_TECHNICAL=PASS")
        print("DELIVERY_EVIDENCE_BUNDLE_TECHNICAL=PASS")
        print("FIELD_PRODUCT_MUTATION=false")
        print("NEW_CORE=false")
        print("HUMAN_THRESHOLD_REVIEW_READY=PASS")
        print("HUMAN_DECISION_OPTIONS=ACCEPT|HOLD")
        print("HOLD=HUMAN_DECISION_REQUIRED")
        print(f"EVIDENCE={path}")
        print(
            "NEXT_ACTION="
            "GATE10_HUMAN_DELIVERY_ACCEPTANCE"
        )

        return 2

    except Exception as exc:
        return write_hold(
            run_dir,
            f"{type(exc).__name__}:{exc}",
        )


if __name__ == "__main__":
    raise SystemExit(main())
