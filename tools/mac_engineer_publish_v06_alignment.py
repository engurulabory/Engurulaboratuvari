#!/usr/bin/env python3
"""Publish the verified local v0.6 alignment branch and open/reuse its product PR."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
PRODUCT = HOME / "Enguru" / "Projects" / "enguru-mac-engineer"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
PREPARED = EVIDENCE_ROOT / "package6-product-v06-alignment-prepared.json"
OUTPUT = EVIDENCE_ROOT / "package6-product-v06-alignment-publication.json"

REPOSITORY = "engurulabory/enguru-mac-engineer"
BRANCH = "feature/v06-version-branding-alignment"
BASE = "main"
TITLE = "Mac Engineer v0.6 — align product version and branding asset"


class PublishError(RuntimeError):
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
        raise PublishError(
            f"GIT_FAILED:{' '.join(args)}:{r['stderr']}"
        )
    return str(r["stdout"])


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise PublishError(f"EVIDENCE_REQUIRED:{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def gh_json(args: list[str]) -> Any:
    r = run(["gh", *args])
    if not r["pass"]:
        raise PublishError(
            f"GH_FAILED:{' '.join(args)}:{r['stderr']}"
        )
    text = str(r["stdout"])
    return json.loads(text) if text else {}


def main() -> int:
    try:
        prepared = load_json(PREPARED)
        if prepared.get("state") != "PASS":
            raise PublishError("ALIGNMENT_PREPARED_PASS_REQUIRED")
        if prepared.get("branch") != BRANCH:
            raise PublishError("ALIGNMENT_BRANCH_MISMATCH")

        branch = git("branch", "--show-current")
        head = git("rev-parse", "HEAD")
        status = git("status", "--porcelain")
        base_main = git("rev-parse", "origin/main")

        if branch != BRANCH:
            raise PublishError(f"PRODUCT_BRANCH_REQUIRED:{BRANCH}")
        if status:
            raise PublishError("PRODUCT_SOURCE_CLEAN_REQUIRED")
        if head != prepared.get("commit"):
            raise PublishError("ALIGNMENT_COMMIT_MISMATCH")
        if base_main != prepared.get("base_main"):
            raise PublishError("ALIGNMENT_BASE_MAIN_DRIFT")

        auth = run(["gh", "auth", "status"])
        if not auth["pass"]:
            raise PublishError("GH_AUTH_REQUIRED")

        push = run(["git", "push", "-u", "origin", BRANCH])
        if not push["pass"]:
            raise PublishError(
                f"ALIGNMENT_BRANCH_PUSH_FAILED:{push['stderr']}"
            )

        pr_list = gh_json([
            "pr",
            "list",
            "--repo",
            REPOSITORY,
            "--head",
            BRANCH,
            "--base",
            BASE,
            "--state",
            "open",
            "--json",
            "number,url,headRefName,baseRefName,headRefOid,title",
        ])

        if pr_list:
            pr = pr_list[0]
            created = False
        else:
            body = (
                "Canonical v0.6 product-source alignment.\n\n"
                "- Info.plist: 0.4 → 0.6\n"
                "- promote runtime/static/engineer-emblem.png into product source\n"
                "- local runtime compile PASS\n"
                "- 25 runtime tests PASS\n"
                "- native zsh syntax PASS\n"
                "- native Swift build PASS\n\n"
                "No runtime replacement or installed-app mutation is part of this PR."
            )
            create = run([
                "gh",
                "pr",
                "create",
                "--repo",
                REPOSITORY,
                "--base",
                BASE,
                "--head",
                BRANCH,
                "--title",
                TITLE,
                "--body",
                body,
            ])
            if not create["pass"]:
                raise PublishError(
                    f"PRODUCT_PR_CREATE_FAILED:{create['stderr']}"
                )
            pr_list = gh_json([
                "pr",
                "list",
                "--repo",
                REPOSITORY,
                "--head",
                BRANCH,
                "--base",
                BASE,
                "--state",
                "open",
                "--json",
                "number,url,headRefName,baseRefName,headRefOid,title",
            ])
            if not pr_list:
                raise PublishError("PRODUCT_PR_LOOKUP_FAILED")
            pr = pr_list[0]
            created = True

        if pr.get("headRefOid") != head:
            raise PublishError("PRODUCT_PR_HEAD_SHA_MISMATCH")

        payload = {
            "schema": "enguru.mac-engineer.product-v06-alignment-publication/v1",
            "observed_at": now(),
            "state": "PASS",
            "issues": [],
            "repository": REPOSITORY,
            "branch": BRANCH,
            "base": BASE,
            "head": head,
            "base_main": base_main,
            "push": "PASS",
            "pr": pr,
            "pr_created": created,
            "truth_boundary": (
                "Alignment branch is published and PR exists at the exact verified head. "
                "This does not claim Product CI PASS or merge."
            ),
            "next_action": (
                "Verify Product CI on the exact PR head; merge only after success, "
                "then verify exact-main and rerun rebuild preflight."
            ),
        }
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 0
    except (PublishError, json.JSONDecodeError) as exc:
        payload = {
            "schema": "enguru.mac-engineer.product-v06-alignment-publication/v1",
            "observed_at": now(),
            "state": "HOLD",
            "issues": [str(exc)],
            "truth_boundary": "Fail-closed; no merge or runtime/install mutation was performed.",
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps({**payload, "evidence": str(OUTPUT)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
