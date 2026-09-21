#!/usr/bin/env python3
"""Reconcile the already-observed v0.6 field recovery chain."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
SESSION = ROOT / "governance" / "mac-engineer" / "SESSION_STATE_V1.json"
SUCCESS = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "package6-exact-sha-rebuild-install.json"
)
OUTPUT = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "package6-recovery-reconciliation.json"
)


class RecoveryError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RecoveryError(f"JSON_REQUIRED:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryError(f"JSON_INVALID:{path}") from exc


def main() -> int:
    try:
        session = load_json(SESSION)
        success = load_json(SUCCESS)

        attempt = session.get("observedExactShaInstallAttempt1", {})
        if attempt.get("state") != "HOLD_RECOVERED":
            raise RecoveryError("RECOVERED_FIELD_FAILURE_REQUIRED")
        if attempt.get("rollbackPrepared") is not True:
            raise RecoveryError("ROLLBACK_PREPARED_REQUIRED")
        if attempt.get("rollbackUsed") is not True:
            raise RecoveryError("ROLLBACK_USED_REQUIRED")
        if attempt.get("relaunch") != "PASS":
            raise RecoveryError("ROLLBACK_RELAUNCH_PASS_REQUIRED")

        issue = str(attempt.get("issue", "")).strip()
        root_cause = str(attempt.get("rootCause", "")).strip()
        if not issue:
            raise RecoveryError("RECOVERY_FAILURE_EVIDENCE_REQUIRED")
        if not root_cause:
            raise RecoveryError("RECOVERY_ROOT_CAUSE_REQUIRED")

        if success.get("state") != "PASS":
            raise RecoveryError("RECOVERY_REVERIFY_INSTALL_PASS_REQUIRED")
        if success.get("version") != "0.6":
            raise RecoveryError("RECOVERY_REVERIFY_VERSION_V06_REQUIRED")
        if success.get("rollback", {}).get("used") is not False:
            raise RecoveryError("RECOVERY_RETRY_SHOULD_NOT_USE_ROLLBACK")
        if success.get("live_status", {}).get("pass") is not True:
            raise RecoveryError("RECOVERY_REVERIFY_LIVE_STATUS_REQUIRED")
        if success.get("process_verification", {}).get("pass") is not True:
            raise RecoveryError("RECOVERY_REVERIFY_PROCESS_PASS_REQUIRED")

        bounded_correction = (
            "Normalize macOS Unicode command/path comparison to NFC and use a "
            "bounded readiness wait for installed-app/runtime process detection."
        )

        payload = {
            "schema": "enguru.mac-engineering.recovery-reconciliation/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "failure_observed": True,
            "failure": issue,
            "root_cause": root_cause,
            "bounded_correction": bounded_correction,
            "rollback_prepared": True,
            "rollback_used": True,
            "rollback_relaunch": "PASS",
            "reverified": True,
            "reverification": {
                "install_state": success.get("state"),
                "version": success.get("version"),
                "live_status": success.get("live_status", {}).get("pass"),
                "process_verification": success.get(
                    "process_verification", {}
                ).get("pass"),
                "retry_rollback_used": success.get("rollback", {}).get("used"),
            },
            "evidence_refs": [
                "governance/mac-engineer/SESSION_STATE_V1.json#observedExactShaInstallAttempt1",
                "evidence/MAC_ENGINEER_V06_INSTALL_ATTEMPT1_RECOVERY_2026-09-21.md",
                str(SUCCESS),
            ],
            "truth_boundary": (
                "This reuses a real bounded field failure already observed during "
                "v0.6 exact-SHA installation. It does not fabricate a second failure."
            ),
            "next_action": "Build the local commissioning bundle after continuity PASS.",
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (RecoveryError, OSError) as exc:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema": "enguru.mac-engineering.recovery-reconciliation/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed. Recovery PASS requires observed failure, bounded correction and successful reverify.",
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
