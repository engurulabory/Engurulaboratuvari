from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any

from tools.enguru_language_pre_send_linter import lint as suzgec_lint
from tools.enguru_holistic_finish_gate_v22 import verify_pre as v22_verify_pre, verify_post as v22_verify_post


ROOT = Path(__file__).resolve().parents[1]
SUZGEC_BOOT_GUARD = ROOT / "tools/enguru_language_governance_boot_guard.py"


class PackageGuardError(ValueError):
    pass


PRE_REQUIRED = (
    "packageName",
    "objective",
    "currentTruth",
    "boundary",
    "preservedValue",
    "necessaryDifference",
    "acceptance",
    "negativeGuards",
    "authority",
    "evidencePlan",
    "doneCheck",
    "progressImpact",
    "nextPackage",
    "allowedMutationPaths",
    "suzgecPre",
    "zekuPassReady",
)


SUZGEC_REQUIRED = (
    "STATE",
    "CLAIM",
    "EVIDENCE",
    "JUDGMENT",
    "NEXT_ACTION",
)


PASS_READY_REQUIRED = (
    "PACKAGE_DESIGN",
    "BLOCK_BOUNDARIES",
    "BLOCK_DEPENDENCIES",
    "KNOWN_FAILURES_REVIEWED",
    "ACCEPTANCE_COVERAGE",
    "NEGATIVE_GUARDS",
    "MUTATION_SCOPE",
    "DONECHECK_DESIGN",
    "PROGRESS_TRANSITION",
    "JUDGMENT",
)


POST_REQUIRED = (
    "STATE",
    "CLAIM",
    "EVIDENCE",
    "PRESERVED_VALUE",
    "NECESSARY_DIFFERENCE",
    "JUDGMENT",
    "NEXT_ACTION",
    "PACKAGE_DONECHECK",
    "PROGRESS_RECONCILIATION",
    "STATE_DRIFT",
    "UNVERIFIED_PASS",
)


def _require(mapping, keys, prefix):
    if not isinstance(mapping, dict):
        raise PackageGuardError(
            f"{prefix}_OBJECT_REQUIRED"
        )

    for key in keys:
        if key not in mapping:
            raise PackageGuardError(
                f"{prefix}_MISSING:{key}"
            )

        value = mapping[key]

        if value is None:
            raise PackageGuardError(
                f"{prefix}_EMPTY:{key}"
            )

        if isinstance(value, str) and not value.strip():
            raise PackageGuardError(
                f"{prefix}_EMPTY:{key}"
            )

        if isinstance(value, (list, tuple, dict)) and not value:
            raise PackageGuardError(
                f"{prefix}_EMPTY:{key}"
            )



def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _require_suzgec_authority() -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SUZGEC_BOOT_GUARD),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    try:
        receipt = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PackageGuardError(
            "SUZGEC_BOOT_RECEIPT_REQUIRED"
        ) from exc

    if (
        completed.returncode != 0
        or receipt.get("state") != "PASS"
        or receipt.get("authority_state") != "PASS"
    ):
        raise PackageGuardError(
            "SUZGEC_AUTHORITY_HOLD"
        )

    return receipt


def _suzgec_sequence(
    *,
    state: str,
    claim: Any,
    preserved_value: Any,
    necessary_difference: Any,
    reuse_execution: Any,
    evidence: Any,
    closure: Any,
    next_action: Any,
    closure_contract: Any = None,
) -> str:
    lines = [
        "SUZGEC_SEQUENCE=ENFORCED",
        "PRESERVED_VALUE: " + _text(preserved_value),
        "NECESSARY_DIFFERENCE: " + _text(necessary_difference),
        "REUSE_EXECUTION: " + _text(reuse_execution),
        "EVIDENCE: " + _text(evidence),
        "CLOSURE: " + _text(closure),
        "PACKAGE_STATE=" + _text(state),
        "CLAIM: " + _text(claim),
        "NEXT_ACTION: " + _text(next_action),
    ]

    if closure_contract is not None:
        lines.append(
            "CLOSURE_CONTRACT: "
            + _text(closure_contract)
        )

    return "\n".join(lines) + "\n"


def _require_suzgec_semantics(
    stage: str,
    payload: str,
) -> dict[str, Any]:
    result = suzgec_lint(
        payload,
        strict=True,
    )

    if result.get("state") != "PASS":
        rules = ",".join(
            sorted(
                {
                    str(item.get("rule"))
                    for item in result.get(
                        "findings",
                        [],
                    )
                    if item.get("rule")
                }
            )
        )

        raise PackageGuardError(
            f"SUZGEC_{stage}_HOLD:"
            f"{rules or 'SEMANTIC'}"
        )

    return result


def precheck(
    package: dict[str, Any],
    canonical_state: dict[str, Any],
) -> dict[str, Any]:

    _require(
        package,
        PRE_REQUIRED,
        "PACKAGE_PRECHECK",
    )

    _require(
        package["suzgecPre"],
        SUZGEC_REQUIRED,
        "SUZGEC_PRECHECK",
    )

    _require(
        package["zekuPassReady"],
        PASS_READY_REQUIRED,
        "ZEKU_PASS_READY",
    )

    _require_suzgec_authority()

    _require_suzgec_semantics(
        "PRE_EXECUTION",
        _suzgec_sequence(
            state="PASS",
            claim=package["suzgecPre"]["CLAIM"],
            preserved_value=package["preservedValue"],
            necessary_difference=package["necessaryDifference"],
            reuse_execution="ENGURU_PACKAGE_EXECUTION_GUARD",
            evidence=package["suzgecPre"]["EVIDENCE"],
            closure="PRE_EXECUTION_SUZGEC_GATE",
            next_action=package["suzgecPre"]["NEXT_ACTION"],
        ),
    )

    active_package = canonical_state.get(
        "activePackage"
    )

    active_item = canonical_state.get(
        "activeItem"
    )

    if package["packageName"] != active_package:
        raise PackageGuardError(
            "ACTIVE_PACKAGE_BOUNDARY_MISMATCH"
        )

    framework = canonical_state.get(
        "operatingFramework"
    )

    if not isinstance(framework, dict):
        raise PackageGuardError(
            "OPERATING_FRAMEWORK_STATE_REQUIRED"
        )

    if framework.get(
        "packageExecutionReadiness"
    ) != "PASS":
        raise PackageGuardError(
            "PACKAGE_EXECUTION_READINESS_REQUIRED"
        )

    if framework.get(
        "executionMode"
    ) != "PACKAGE_COMPLETION":
        raise PackageGuardError(
            "PACKAGE_COMPLETION_MODE_REQUIRED"
        )

    gate = (
        framework
        .get("packageExecutionMethod", {})
        .get("zekuPassReadyGate")
    )

    if not isinstance(gate, dict):
        raise PackageGuardError(
            "ZEKU_PASS_READY_GATE_REQUIRED"
        )

    if gate.get("state") != "PASS":
        raise PackageGuardError(
            "ZEKU_PASS_READY_GATE_PASS_REQUIRED"
        )

    if gate.get("canonicalStateDriven") is not True:
        raise PackageGuardError(
            "CANONICAL_STATE_DRIVEN_GATE_REQUIRED"
        )

    pass_ready = package["zekuPassReady"]

    for key in PASS_READY_REQUIRED[:-1]:
        if pass_ready[key] != "PASS":
            raise PackageGuardError(
                f"ZEKU_PASS_READY_REQUIRED:{key}"
            )

    if (
        pass_ready["JUDGMENT"]
        != "PASS_READY_FOR_EXECUTION"
    ):
        raise PackageGuardError(
            "ZEKU_PASS_READY_JUDGMENT_REQUIRED"
        )

    # v2.2 is activated only by canonical state; historic packages remain compatible.
    v22_policy = framework.get("holisticFinishV22")
    if v22_policy is not None:
        v22_verify_pre(package, canonical_state, v22_policy)

    if not package["allowedMutationPaths"]:
        raise PackageGuardError(
            "BOUNDED_MUTATION_SCOPE_REQUIRED"
        )

    return {
        "state":
            "PASS",

        "suzgec":
            "PASS",

        "zekuPassReady":
            "PASS",

        "packageBoundary":
            "PASS",

        "activePackage":
            active_package,

        "activeItem":
            active_item,

        "readiness":
            "PASS",

        "decision":
            "EXECUTE",
    }


def postcheck(
    result: dict[str, Any],
    canonical_state: dict[str, Any] | None = None,
) -> dict[str, Any]:

    _require(
        result,
        POST_REQUIRED,
        "PACKAGE_POSTCHECK",
    )

    _require_suzgec_authority()

    _require_suzgec_semantics(
        "PRE_CLOSURE",
        _suzgec_sequence(
            state=result["STATE"],
            claim=result["CLAIM"],
            preserved_value=result["PRESERVED_VALUE"],
            necessary_difference=result["NECESSARY_DIFFERENCE"],
            reuse_execution="PACKAGE_DONECHECK+PROGRESS_RECONCILIATION",
            evidence=result["EVIDENCE"],
            closure="PRE_CLOSURE_SUZGEC_GATE",
            next_action=result["NEXT_ACTION"],
            closure_contract=result.get("CLOSURE_CONTRACT"),
        ),
    )

    if result["STATE"] != "PASS":
        raise PackageGuardError(
            "PACKAGE_RESULT_PASS_REQUIRED"
        )

    if result["PACKAGE_DONECHECK"] != "PASS":
        raise PackageGuardError(
            "PACKAGE_DONECHECK_PASS_REQUIRED"
        )

    if (
        result["PROGRESS_RECONCILIATION"]
        != "PASS"
    ):
        raise PackageGuardError(
            "PROGRESS_RECONCILIATION_PASS_REQUIRED"
        )

    if result["STATE_DRIFT"] != "NONE":
        raise PackageGuardError(
            "STATE_DRIFT_NONE_REQUIRED"
        )

    if result["UNVERIFIED_PASS"] != 0:
        raise PackageGuardError(
            "UNVERIFIED_PASS_ZERO_REQUIRED"
        )

    # The final gate must not infer enforcement from a user-supplied receipt alone.
    # In v2.2 mode the caller must supply the same canonical state used at precheck.
    if canonical_state is not None:
        if not isinstance(canonical_state, dict):
            raise PackageGuardError("V22_CANONICAL_STATE_INVALID")
        framework = canonical_state.get("operatingFramework")
        if not isinstance(framework, dict):
            raise PackageGuardError("V22_CANONICAL_FRAMEWORK_REQUIRED")
        policy = framework.get("holisticFinishV22")
        if policy is not None:
            if not isinstance(policy, dict) or policy.get("state") != "ENFORCE":
                raise PackageGuardError("V22_POLICY_INVALID")
            if "holisticV22" not in result:
                raise PackageGuardError("V22_POST_RECEIPT_MISSING")
            v22_verify_post(result)
        elif "holisticV22" in result:
            raise PackageGuardError("V22_UNAUTHORIZED_RECEIPT")
    elif "holisticV22" in result:
        # Legacy callers may omit state; never treat an unbound receipt as validated.
        raise PackageGuardError("V22_CANONICAL_STATE_REQUIRED")

    return {
        "state":
            "PASS",

        "suzgec":
            "PASS",

        "doneCheck":
            "PASS",

        "progressReconciliation":
            "PASS",

        "decision":
            "ADVANCE",
    }
