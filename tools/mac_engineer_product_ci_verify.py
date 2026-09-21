#!/usr/bin/env python3
"""Verify ENGÜRÜ Mac Engineer dedicated product repository exact-main CI via local gh CLI."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from typing import Any
from datetime import datetime, timezone


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
EVIDENCE = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6" / "package6-product-ci-exact-main.json"
REPOSITORY = "engurulabory/enguru-mac-engineer"
REQUIRED_WORKFLOW = "ENGURU Mac Engineer Product CI"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git_value(*args: str) -> str:
    rc, out, _ = run(["git", *args], cwd=PRODUCT)
    return out if rc == 0 else ""


def gh_json(endpoint: str) -> tuple[int, Any, str]:
    rc, out, err = run(["gh", "api", endpoint], cwd=PRODUCT)
    if rc != 0:
        return rc, None, err
    try:
        return 0, json.loads(out), ""
    except json.JSONDecodeError:
        return 3, None, "GH_JSON_DECODE_FAILED"


def evaluate(
    *,
    local_head: str,
    local_origin_main: str,
    local_clean: bool,
    repo_meta: dict[str, Any] | None,
    branch_meta: dict[str, Any] | None,
    workflow_runs: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    issues: list[str] = []

    if not local_head:
        issues.append("LOCAL_PRODUCT_HEAD_REQUIRED")
    if local_head != local_origin_main:
        issues.append("LOCAL_PRODUCT_EXACT_ORIGIN_MAIN_REQUIRED")
    if not local_clean:
        issues.append("LOCAL_PRODUCT_CLEAN_REQUIRED")

    if not repo_meta:
        issues.append("REMOTE_PRODUCT_REPOSITORY_REQUIRED")
    else:
        if repo_meta.get("private") is not True:
            issues.append("REMOTE_PRODUCT_REPOSITORY_PRIVATE_REQUIRED")
        if repo_meta.get("default_branch") != "main":
            issues.append("REMOTE_PRODUCT_DEFAULT_MAIN_REQUIRED")

    remote_head = ""
    if not branch_meta:
        issues.append("REMOTE_MAIN_REQUIRED")
    else:
        remote_head = str(branch_meta.get("commit", {}).get("sha", ""))
        if remote_head != local_head:
            issues.append("REMOTE_MAIN_SHA_MISMATCH")

    exact_runs = []
    for item in workflow_runs or []:
        if str(item.get("head_sha", "")) != local_head:
            continue
        name = str(item.get("name") or item.get("workflow_name") or "")
        path = str(item.get("path") or "")
        if REQUIRED_WORKFLOW in name or "product-ci" in path:
            exact_runs.append(item)

    exact_runs.sort(key=lambda x: int(x.get("run_number") or 0), reverse=True)
    selected = exact_runs[0] if exact_runs else None

    if selected is None:
        issues.append("EXACT_MAIN_PRODUCT_CI_RUN_REQUIRED")
    else:
        if selected.get("status") != "completed":
            issues.append("EXACT_MAIN_PRODUCT_CI_COMPLETION_REQUIRED")
        if selected.get("conclusion") != "success":
            issues.append("EXACT_MAIN_PRODUCT_CI_SUCCESS_REQUIRED")

    return {
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "local_head": local_head,
        "local_origin_main": local_origin_main,
        "remote_main": remote_head,
        "repository_private": repo_meta.get("private") if repo_meta else None,
        "default_branch": repo_meta.get("default_branch") if repo_meta else None,
        "selected_run": selected,
        "exact_run_count": len(exact_runs),
        "next_action": (
            "Bind product-source SHA + exact-main CI evidence into Labory, then rebuild/install from that exact SHA."
            if not issues
            else "Resolve only the reported exact-main product CI difference."
        ),
    }


def main() -> int:
    local_head = git_value("rev-parse", "HEAD")
    local_origin_main = git_value("rev-parse", "origin/main")
    local_status = git_value("status", "--porcelain")

    repo_rc, repo_meta, repo_err = gh_json(f"/repos/{REPOSITORY}")
    branch_rc, branch_meta, branch_err = gh_json(f"/repos/{REPOSITORY}/branches/main")
    runs_rc, runs_payload, runs_err = gh_json(
        f"/repos/{REPOSITORY}/actions/runs?branch=main&head_sha={local_head}&per_page=20"
    )

    workflow_runs = (
        runs_payload.get("workflow_runs", [])
        if isinstance(runs_payload, dict)
        else []
    )

    result = evaluate(
        local_head=local_head,
        local_origin_main=local_origin_main,
        local_clean=(local_status == ""),
        repo_meta=repo_meta if repo_rc == 0 else None,
        branch_meta=branch_meta if branch_rc == 0 else None,
        workflow_runs=workflow_runs if runs_rc == 0 else None,
    )

    transport = {
        "repo_query": {"returncode": repo_rc, "error": repo_err},
        "branch_query": {"returncode": branch_rc, "error": branch_err},
        "runs_query": {"returncode": runs_rc, "error": runs_err},
    }
    if repo_rc != 0 and "REMOTE_PRODUCT_REPOSITORY_REQUIRED" not in result["issues"]:
        result["issues"].append("REMOTE_PRODUCT_REPOSITORY_QUERY_FAILED")
    if branch_rc != 0 and "REMOTE_MAIN_REQUIRED" not in result["issues"]:
        result["issues"].append("REMOTE_MAIN_QUERY_FAILED")
    if runs_rc != 0 and "EXACT_MAIN_PRODUCT_CI_RUN_REQUIRED" not in result["issues"]:
        result["issues"].append("PRODUCT_CI_QUERY_FAILED")
    result["state"] = "PASS" if not result["issues"] else "HOLD"

    payload = {
        "schema": "enguru.mac-engineer.product-ci-exact-main/v1",
        "observed_at": now(),
        "repository": REPOSITORY,
        **result,
        "transport": transport,
        "truth_boundary": (
            "This evidence proves remote private repository main SHA and exact-head product CI only. "
            "It does not prove installed runtime/app was rebuilt from that SHA."
        ),
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({**payload, "evidence": str(EVIDENCE)}, ensure_ascii=False, indent=2))
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
