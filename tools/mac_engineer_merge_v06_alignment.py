#!/usr/bin/env python3
"""Verify exact-head product CI and merge the canonical v0.6 alignment PR."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
PUBLICATION = EVIDENCE_ROOT / "package6-product-v06-alignment-publication.json"
OUTPUT = EVIDENCE_ROOT / "package6-product-v06-alignment-merge.json"

REPOSITORY = "engurulabory/enguru-mac-engineer"
WORKFLOW = "ENGURU Mac Engineer Product CI"


class MergeGateError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str]) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=str(PRODUCT),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def git(*args: str) -> str:
    r = run(["git", *args])
    if not r["pass"]:
        raise MergeGateError(
            f"GIT_FAILED:{' '.join(args)}:{r['stderr']}"
        )
    return str(r["stdout"])


def gh_api(
    endpoint: str,
    *,
    method: str = "GET",
    fields: dict[str, str] | None = None,
) -> Any:
    cmd = ["gh", "api"]
    if method != "GET":
        cmd += ["--method", method]
    cmd.append(endpoint)
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"]
    r = run(cmd)
    if not r["pass"]:
        raise MergeGateError(
            f"GH_API_FAILED:{endpoint}:{r['stderr']}"
        )
    try:
        return json.loads(str(r["stdout"]))
    except json.JSONDecodeError as exc:
        raise MergeGateError(
            f"GH_API_JSON_INVALID:{endpoint}"
        ) from exc


def load_publication() -> dict[str, Any]:
    if not PUBLICATION.is_file():
        raise MergeGateError(
            f"PUBLICATION_EVIDENCE_REQUIRED:{PUBLICATION}"
        )
    try:
        data = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise MergeGateError("PUBLICATION_EVIDENCE_INVALID") from exc
    if data.get("state") != "PASS":
        raise MergeGateError("PUBLICATION_PASS_REQUIRED")
    return data


def select_exact_product_ci(
    runs: list[dict[str, Any]],
    head: str,
) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for item in runs:
        if str(item.get("head_sha", "")) != head:
            continue
        name = str(item.get("name", ""))
        path = str(item.get("path", ""))
        if name == WORKFLOW or "product-ci" in path:
            candidates.append(item)
    candidates.sort(
        key=lambda x: int(x.get("run_number") or 0),
        reverse=True,
    )
    return candidates[0] if candidates else None


def main() -> int:
    try:
        publication = load_publication()
        pr_meta = publication.get("pr", {})
        pr_number = int(pr_meta.get("number"))
        expected_head = str(publication.get("head", ""))
        expected_base = str(publication.get("base_main", ""))

        if not expected_head or not expected_base:
            raise MergeGateError("PUBLICATION_SHA_CONTRACT_REQUIRED")

        local_branch = git("branch", "--show-current")
        local_head = git("rev-parse", "HEAD")
        local_status = git("status", "--porcelain")
        origin_main_before = git("rev-parse", "origin/main")

        if local_status:
            raise MergeGateError("PRODUCT_SOURCE_CLEAN_REQUIRED")
        if local_head != expected_head:
            raise MergeGateError("LOCAL_PRODUCT_HEAD_MISMATCH")
        if origin_main_before != expected_base:
            raise MergeGateError("PRODUCT_BASE_MAIN_DRIFT")

        pr = gh_api(
            f"/repos/{REPOSITORY}/pulls/{pr_number}"
        )
        if pr.get("state") != "open":
            raise MergeGateError(
                f"PRODUCT_PR_OPEN_REQUIRED:{pr.get('state')}"
            )
        if pr.get("draft") is True:
            raise MergeGateError("PRODUCT_PR_READY_REQUIRED")
        if pr.get("base", {}).get("ref") != "main":
            raise MergeGateError("PRODUCT_PR_BASE_MAIN_REQUIRED")
        remote_head = str(
            pr.get("head", {}).get("sha", "")
        )
        if remote_head != expected_head:
            raise MergeGateError("PRODUCT_PR_HEAD_SHA_MISMATCH")

        runs_payload = gh_api(
            f"/repos/{REPOSITORY}/actions/runs"
            f"?head_sha={expected_head}&per_page=30"
        )
        runs = (
            runs_payload.get("workflow_runs", [])
            if isinstance(runs_payload, dict)
            else []
        )
        selected = select_exact_product_ci(runs, expected_head)
        if selected is None:
            raise MergeGateError(
                "PRODUCT_PR_EXACT_HEAD_CI_REQUIRED"
            )
        if selected.get("status") != "completed":
            raise MergeGateError(
                "PRODUCT_PR_EXACT_HEAD_CI_COMPLETION_REQUIRED"
            )
        if selected.get("conclusion") != "success":
            raise MergeGateError(
                "PRODUCT_PR_EXACT_HEAD_CI_SUCCESS_REQUIRED"
            )

        merge = gh_api(
            f"/repos/{REPOSITORY}/pulls/{pr_number}/merge",
            method="PUT",
            fields={
                "sha": expected_head,
                "merge_method": "merge",
            },
        )
        if merge.get("merged") is not True:
            raise MergeGateError(
                "PRODUCT_PR_MERGE_FAILED:"
                + str(merge.get("message", "unknown"))
            )

        merge_sha = str(merge.get("sha", ""))
        if not merge_sha:
            raise MergeGateError("PRODUCT_MERGE_SHA_REQUIRED")

        fetch = run(["git", "fetch", "origin", "main"])
        if not fetch["pass"]:
            raise MergeGateError(
                f"PRODUCT_MAIN_FETCH_FAILED:{fetch['stderr']}"
            )
        switch = run(["git", "switch", "main"])
        if not switch["pass"]:
            raise MergeGateError(
                f"PRODUCT_MAIN_SWITCH_FAILED:{switch['stderr']}"
            )
        pull = run(["git", "pull", "--ff-only", "origin", "main"])
        if not pull["pass"]:
            raise MergeGateError(
                f"PRODUCT_MAIN_FF_ONLY_FAILED:{pull['stderr']}"
            )

        local_main = git("rev-parse", "HEAD")
        origin_main_after = git("rev-parse", "origin/main")
        status_after = git("status", "--porcelain")
        branch_after = git("branch", "--show-current")

        if branch_after != "main":
            raise MergeGateError("PRODUCT_MAIN_BRANCH_REQUIRED_AFTER_MERGE")
        if status_after:
            raise MergeGateError("PRODUCT_MAIN_CLEAN_REQUIRED_AFTER_MERGE")
        if local_main != origin_main_after:
            raise MergeGateError("PRODUCT_MAIN_EXACT_ORIGIN_REQUIRED_AFTER_MERGE")
        if local_main != merge_sha:
            raise MergeGateError("PRODUCT_MERGE_SHA_LOCAL_MAIN_MISMATCH")

        # Exact-main CI commonly starts after the merge. Observe but do not
        # manufacture PASS before the run completes.
        main_runs_payload = gh_api(
            f"/repos/{REPOSITORY}/actions/runs"
            f"?head_sha={merge_sha}&branch=main&per_page=20"
        )
        main_runs = (
            main_runs_payload.get("workflow_runs", [])
            if isinstance(main_runs_payload, dict)
            else []
        )
        exact_main_ci = select_exact_product_ci(
            main_runs,
            merge_sha,
        )
        exact_main_state = "PENDING"
        if exact_main_ci:
            if (
                exact_main_ci.get("status") == "completed"
                and exact_main_ci.get("conclusion") == "success"
            ):
                exact_main_state = "PASS"
            elif exact_main_ci.get("status") == "completed":
                exact_main_state = "FAILURE"

        payload = {
            "schema": (
                "enguru.mac-engineer."
                "product-v06-alignment-merge/v1"
            ),
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "repository": REPOSITORY,
            "pr_number": pr_number,
            "pr_head": expected_head,
            "pr_ci": {
                "run_id": selected.get("id"),
                "run_number": selected.get("run_number"),
                "status": selected.get("status"),
                "conclusion": selected.get("conclusion"),
                "head_sha": selected.get("head_sha"),
                "event": selected.get("event"),
            },
            "merge_sha": merge_sha,
            "local_product": {
                "branch_before": local_branch,
                "branch_after": branch_after,
                "head_before": local_head,
                "main_after": local_main,
                "origin_main_after": origin_main_after,
                "clean_after": status_after == "",
            },
            "exact_main_ci_observed": exact_main_ci,
            "exact_main_ci_state": exact_main_state,
            "truth_boundary": (
                "The exact PR head passed Product CI and was merged with SHA protection. "
                "Local product main is synced exactly to remote main. "
                "Exact-main Product CI is separately required before rebuild."
            ),
            "next_action": (
                "Verify Product CI success on the exact merged main SHA, "
                "then rerun rebuild preflight."
            ),
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {**payload, "evidence": str(OUTPUT)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except (MergeGateError, TypeError, ValueError) as exc:
        payload = {
            "schema": (
                "enguru.mac-engineer."
                "product-v06-alignment-merge/v1"
            ),
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": (
                "Fail-closed. No merge is attempted unless the exact PR head "
                "has successful Product CI and the local product contract matches."
            ),
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(
            json.dumps(
                {**payload, "evidence": str(OUTPUT)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
