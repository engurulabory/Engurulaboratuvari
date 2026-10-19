#!/usr/bin/env python3
"""P02 six-gate dependency reconciliation. Evidence planning, never authority.

This module accepts engineering-review signals only. A status marked 'ready'
does not mean native accepted. Production writer, signer, grant and human
threshold are outside this module's authority.
"""
from __future__ import annotations
import json

GATES = (
    "G3A_SIGNER", "G3B_GRANT", "G3C_DURABLE_WRITER",
    "G3D_FIRST_NATIVE_ITEM", "P02_FIELD_ACCEPTANCE", "HUMAN_VERIFIED_FINISH",
)
PREREQUISITES = {
    GATES[0]: (),
    GATES[1]: (GATES[0],),
    GATES[2]: (GATES[0], GATES[1]),
    GATES[3]: (GATES[0], GATES[1], GATES[2]),
    GATES[4]: (GATES[3],),
    GATES[5]: (GATES[4],),
}
REQUIRED_CHECKS = {
    GATES[0]: ("sourceBinaryBinding", "codesignIdentity", "eligibleProfile", "secureKeyHumanPresence", "independentTrust"),
    GATES[1]: ("issuerChain", "revocation", "exactGrantScope", "signature", "nonceExpiry"),
    GATES[2]: ("singleCanonicalWriter", "compareAndSwap", "durableNonce", "appendOnlyReceipt", "crashRecovery", "independentSecurity"),
    GATES[3]: ("authorizedPilot", "beforeReadback", "afterReadback"),
    GATES[4]: ("native12of12", "doneChecks4of4", "fieldPrerequisites7of7", "g03G04", "independentSecurity"),
    GATES[5]: ("separateHumanApproval", "nativeVerifiedReadback"),
}

def reconcile(evidence: dict) -> dict:
    """An exhaustive, deterministic readiness matrix from strictly typed signals."""
    result = {"schema": "enguru.p02.six-gate.dependency-matrix/v1",
              "state": "HOLD", "officialP02": "HOLD",
              "verifiedFinish": "HOLD", "authorizedToWrite": False,
              "gates": [], "blockingChecks": [], "canonicalWrites": 0}
    if not isinstance(evidence, dict) or set(evidence) != set(GATES):
        result["reason"] = "EXACT_GATE_SET_REQUIRED"
        return result
    valid = True
    for name in GATES:
        checks = evidence[name]
        required = REQUIRED_CHECKS[name]
        if not isinstance(checks, dict) or set(checks) != set(required) or any(type(v) is not bool for v in checks.values()):
            valid = False
            result["blockingChecks"].append(name + ":INVALID_CHECK_SHAPE")
            result["gates"].append({"name": name, "engineeringReady": False,
                                    "fieldAccepted": False, "state": "HOLD_INPUT"})
            continue
        missing = [key for key in required if checks[key] is False]
        result["blockingChecks"].extend(name + ":" + key for key in missing)
        result["gates"].append({"name": name,
                                "engineeringReady": not missing,
                                "fieldAccepted": False,
                                "prerequisites": list(PREREQUISITES[name]),
                                "state": "REVIEW_READY_NATIVE_HOLD" if not missing else "HOLD_ENGINEERING_GAP"})
    result["state"] = "PASS_ENGINEERING_MATRIX_OFFICIAL_HOLD" if valid else "HOLD_INVALID_EVIDENCE"
    return result

def main() -> int:
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--evidence", required=True, type=Path)
    args = p.parse_args()
    path = args.evidence
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        print(json.dumps({"state": "HOLD_INVALID_EVIDENCE_PATH"}))
        return 50
    try:
        def no_duplicate(pairs):
            obj = {}
            for k, v in pairs:
                if k in obj:
                    raise ValueError("DUPLICATE_KEY")
                obj[k] = v
            return obj
        evidence = json.loads(path.read_bytes(), object_pairs_hook=no_duplicate,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE")))
    except (ValueError, UnicodeError):
        print(json.dumps({"state": "HOLD_INVALID_JSON"}))
        return 50
    outcome = reconcile(evidence)
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return 0 if outcome["state"].startswith("PASS_ENGINEERING") else 50

if __name__ == "__main__":
    raise SystemExit(main())
