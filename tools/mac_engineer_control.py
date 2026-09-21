#!/usr/bin/env python3
"""Single control-plane entry point for ENGÜRÜ Mac Engineer™ commissioning."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRODUCT_SOURCE = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"
RUNTIME_ROOT = Path.home() / "Enguru" / "Runtime" / "MacEngineer"
APP = Path.home() / "Applications" / "ENGÜRÜ Mac Engineer.app"
EVIDENCE_ROOT = Path.home() / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
BOOTSTRAP = ROOT / "tools" / "mac_engineer_bootstrap_product_source.py"
SOURCE_REVIEW = ROOT / "tools" / "mac_engineer_source_intake_review.py"
DELTA_REVIEW = ROOT / "tools" / "mac_engineer_delta_authority_review.py"
LAYOUT_AUDIT = ROOT / "tools" / "mac_engineer_layout_audit.py"
SESSION_CONTINUITY = ROOT / "tools" / "mac_engineer_session_continuity.py"
PRODUCT_CI_VERIFY = ROOT / "tools" / "mac_engineer_product_ci_verify.py"
REBUILD_PREFLIGHT = ROOT / "tools" / "mac_engineer_rebuild_install_preflight.py"
PREPARE_V06_ALIGNMENT = ROOT / "tools" / "mac_engineer_prepare_v06_alignment.py"
PUBLISH_V06_ALIGNMENT = ROOT / "tools" / "mac_engineer_publish_v06_alignment.py"


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git_state(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"available": False}
    out: dict[str, Any] = {"available": True}
    for key, cmd in {
        "head": ["git", "rev-parse", "HEAD"],
        "branch": ["git", "branch", "--show-current"],
        "status": ["git", "status", "--porcelain"],
        "origin": ["git", "remote", "get-url", "origin"],
        "origin_main": ["git", "rev-parse", "origin/main"],
    }.items():
        rc, stdout, stderr = run(cmd, cwd=path)
        out[key] = stdout if rc == 0 else None
        if rc != 0:
            out[key + "_error"] = stderr
    out["clean"] = not bool(out.get("status"))
    if out.get("head") and out.get("origin_main"):
        out["exact_origin_main"] = out["head"] == out["origin_main"]
    return out


def evidence_state(name: str) -> dict[str, Any]:
    path = EVIDENCE_ROOT / name
    if not path.exists():
        return {"exists": False, "path": str(path)}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return {
            "exists": True,
            "path": str(path),
            "state": payload.get("state"),
            "issues": payload.get("issues", []),
        }
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "exists": True,
            "path": str(path),
            "state": "INVALID",
            "error": type(exc).__name__,
        }


def process_state() -> list[dict[str, str]]:
    rc, out, err = run(["ps", "-axo", "pid=,command="])
    if rc != 0:
        return [{"error": err or "ps_failed"}]
    matches: list[dict[str, str]] = []
    for line in out.splitlines():
        lowered = line.lower()
        if "engurumacengineer" in lowered or "/enguru/runtime/macengineer/" in lowered:
            pid, _, command = line.strip().partition(" ")
            matches.append({"pid": pid.strip(), "command": command.strip()[:1000]})
    return matches


def status() -> dict[str, Any]:
    control = git_state(ROOT)
    product = git_state(PRODUCT_SOURCE)
    evidence = {
        "discovery": evidence_state("package6-local-discovery.json"),
        "provenance": evidence_state("package6-provenance-reconcile.json"),
        "source_intake": evidence_state("package6-source-intake-review.json"),
        "delta_authority": evidence_state("package6-delta-authority-review.json"),
    }
    processes = process_state()

    issues: list[str] = []
    next_action = ""

    if not control.get("available"):
        issues.append("CONTROL_PLANE_GIT_REQUIRED")
    elif control.get("clean") is not True:
        issues.append("CONTROL_PLANE_CLEAN_REQUIRED")
    elif control.get("exact_origin_main") is False:
        issues.append("CONTROL_PLANE_EXACT_MAIN_REQUIRED")

    if evidence["delta_authority"].get("state") != "PASS":
        issues.append("DELTA_AUTHORITY_PASS_REQUIRED")

    if not PRODUCT_SOURCE.exists():
        issues.append("PRODUCT_SOURCE_BOOTSTRAP_REQUIRED")
        next_action = "python3 tools/mac_engineer_control.py bootstrap-source"
    elif not product.get("available"):
        issues.append("PRODUCT_SOURCE_GIT_REQUIRED")
        next_action = "Inspect the prepared product source and initialize/publish canonical Git authority."
    elif not product.get("origin"):
        issues.append("PRODUCT_SOURCE_REMOTE_REQUIRED")
        next_action = "python3 tools/mac_engineer_control.py publish-source"
    elif product.get("clean") is not True:
        issues.append("PRODUCT_SOURCE_CLEAN_REQUIRED")
        next_action = "Reconcile product-source changes before continuing commissioning."
    else:
        next_action = (
            "Verify dedicated product exact-main CI, then rebuild/install runtime from the exact product-source SHA."
        )

    return {
        "state": "PASS" if not issues else "HOLD",
        "roles": {
            "chatgpt": "ENGINEERING_OPERATOR_INTERFACE",
            "labory": "CONTROL_PLANE",
            "product_source": "DEDICATED_PRODUCT_REPOSITORY",
            "mac_local": "EXECUTION_SURFACE",
            "evidence": "VERIFICATION_SURFACE",
        },
        "paths": {
            "control_plane": str(ROOT),
            "product_source": str(PRODUCT_SOURCE),
            "runtime": str(RUNTIME_ROOT),
            "installed_app": str(APP),
            "evidence": str(EVIDENCE_ROOT),
        },
        "control_plane": control,
        "product_source": product,
        "runtime": {
            "root_exists": RUNTIME_ROOT.exists(),
            "app_exists": APP.exists(),
            "processes": processes,
        },
        "evidence": evidence,
        "issues": issues,
        "next_action": next_action,
    }


def refresh_bootstrap_evidence() -> tuple[bool, dict[str, Any]]:
    evidence: dict[str, Any] = {}

    source_proc = subprocess.run(
        [sys.executable, str(SOURCE_REVIEW)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    evidence["source_review"] = {
        "returncode": source_proc.returncode,
        "stdout": source_proc.stdout[-12000:],
        "stderr": source_proc.stderr[-12000:],
    }
    source_state = evidence_state(
        "package6-source-intake-review.json"
    )
    evidence["source_review"]["evidence"] = source_state

    expected_source_hold = (
        source_state.get("state") == "HOLD"
        and source_state.get("issues")
        == ["RUNTIME_DELTA_AUTHORITY_REVIEW_REQUIRED"]
    )
    if source_proc.returncode not in {0, 2} or not (
        source_state.get("state") == "PASS"
        or expected_source_hold
    ):
        return False, evidence

    delta_proc = subprocess.run(
        [sys.executable, str(DELTA_REVIEW)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    evidence["delta_review"] = {
        "returncode": delta_proc.returncode,
        "stdout": delta_proc.stdout[-12000:],
        "stderr": delta_proc.stderr[-12000:],
        "evidence": evidence_state(
            "package6-delta-authority-review.json"
        ),
    }
    delta_state = evidence["delta_review"]["evidence"]
    if (
        delta_proc.returncode != 0
        or delta_state.get("state") != "PASS"
    ):
        return False, evidence

    return True, evidence


def bootstrap_source(publish: bool) -> int:
    if not publish:
        ok, refreshed = refresh_bootstrap_evidence()
        if not ok:
            print(
                json.dumps(
                    {
                        "state": "HOLD",
                        "reason": (
                            "BOOTSTRAP_EVIDENCE_REFRESH_FAILED"
                        ),
                        "refresh": refreshed,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 2

    cmd = [sys.executable, str(BOOTSTRAP)]
    if publish:
        cmd.append("--publish")
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    boot = sub.add_parser("bootstrap-source")
    boot.add_argument("--publish", action="store_true")
    sub.add_parser("publish-source")
    sub.add_parser("audit-layout")
    sub.add_parser("session-start")
    sub.add_parser("session-handoff")
    sub.add_parser("verify-product-ci")
    sub.add_parser("rebuild-preflight")
    sub.add_parser("prepare-v06-alignment")
    sub.add_parser("publish-v06-alignment")

    args = parser.parse_args()
    if args.command == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "bootstrap-source":
        return bootstrap_source(args.publish)
    if args.command == "publish-source":
        return bootstrap_source(True)
    if args.command == "audit-layout":
        proc = subprocess.run(
            [sys.executable, str(LAYOUT_AUDIT)],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    if args.command == "verify-product-ci":
        proc = subprocess.run(
            [sys.executable, str(PRODUCT_CI_VERIFY)],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    if args.command == "rebuild-preflight":
        proc = subprocess.run(
            [sys.executable, str(REBUILD_PREFLIGHT)],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    if args.command == "prepare-v06-alignment":
        proc = subprocess.run(
            [sys.executable, str(PREPARE_V06_ALIGNMENT)],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    if args.command == "publish-v06-alignment":
        proc = subprocess.run(
            [sys.executable, str(PUBLISH_V06_ALIGNMENT)],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    if args.command in {"session-start", "session-handoff"}:
        mode = "start" if args.command == "session-start" else "handoff"
        proc = subprocess.run(
            [sys.executable, str(SESSION_CONTINUITY), mode],
            cwd=str(ROOT),
            check=False,
        )
        return proc.returncode
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
