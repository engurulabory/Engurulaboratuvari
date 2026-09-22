#!/usr/bin/env python3
"""Read-only diagnostic for ENGÜRÜ Mac Engineering™ repository discovery."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from typing import Any


HOME = Path.home()
RUNTIME = HOME / "Enguru" / "Runtime" / "MacEngineer" / "runtime"
REPO_MANAGER = RUNTIME / "repo_manager.py"
APP = RUNTIME / "app.py"
PROJECTS = HOME / "Enguru" / "Projects"
FIXTURE = PROJECTS / "mac-engineering-v06-field-fixture"
EVIDENCE = (
    HOME
    / "Enguru"
    / "Evidence"
    / "MacEngineer"
    / "v0.6"
    / "package6-real-task-repo-discovery-diagnostic.json"
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )
    return {
        "cmd": cmd,
        "returncode": p.returncode,
        "pass": p.returncode == 0,
        "stdout": p.stdout.strip(),
        "stderr": p.stderr.strip(),
    }


def git_probe(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "git_dir": (path / ".git").exists(),
    }
    if not (path / ".git").exists():
        return result

    for key, cmd in {
        "branch": ["git", "branch", "--show-current"],
        "head": ["git", "rev-parse", "HEAD"],
        "status": ["git", "status", "--porcelain"],
        "origin": ["git", "remote", "get-url", "origin"],
        "remotes": ["git", "remote"],
    }.items():
        r = run(cmd, path)
        result[key] = r["stdout"] if r["pass"] else None
        if not r["pass"]:
            result[f"{key}_error"] = r["stderr"]

    return result


def source_functions(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "path": str(path), "functions": []}

    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source)
    lines = source.splitlines()

    functions: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = getattr(node, "end_lineno", node.lineno)
        body = "\n".join(lines[node.lineno - 1 : end])
        lower = body.lower()
        if any(
            term in lower
            for term in (
                "repo",
                "project",
                "discover",
                "scan",
                "git",
                "local_state",
                "origin",
            )
        ):
            functions.append(
                {
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": end,
                    "source": body,
                }
            )

    return {
        "exists": True,
        "path": str(path),
        "functions": functions,
        "signals": {
            "mentions_origin": "origin" in source.lower(),
            "mentions_projects": "projects" in source.lower(),
            "mentions_dot_git": ".git" in source.lower(),
            "mentions_git_remote": "git remote" in source.lower(),
            "mentions_repo_count": "repo_count" in source.lower(),
        },
    }


def project_inventory() -> list[dict[str, Any]]:
    if not PROJECTS.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for child in sorted(PROJECTS.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        probe = git_probe(child)
        probe["name"] = child.name
        rows.append(probe)
    return rows


def infer_contract(repo_source: dict[str, Any], app_source: dict[str, Any]) -> dict[str, Any]:
    joined = "\n".join(
        fn["source"]
        for source in (repo_source, app_source)
        for fn in source.get("functions", [])
    ).lower()

    observations: list[str] = []
    if "remote" in joined or "origin" in joined:
        observations.append("DISCOVERY_MAY_REQUIRE_REMOTE_OR_ORIGIN")
    if ".git" in joined:
        observations.append("DISCOVERY_CHECKS_GIT_REPOSITORY")
    if "projects" in joined:
        observations.append("DISCOVERY_REFERENCES_PROJECTS_ROOT")
    if "manifest" in joined:
        observations.append("DISCOVERY_REFERENCES_MANIFEST")
    if "registry" in joined:
        observations.append("DISCOVERY_REFERENCES_REGISTRY")

    return {
        "observations": observations,
        "truth_boundary": (
            "These are static source observations only. They do not by themselves "
            "prove which condition excluded the fixture."
        ),
    }


def main() -> int:
    repo_source = source_functions(REPO_MANAGER)
    app_source = source_functions(APP)
    fixture = git_probe(FIXTURE)
    inventory = project_inventory()
    inferred = infer_contract(repo_source, app_source)

    issues: list[str] = []
    if not repo_source.get("exists"):
        issues.append("RUNTIME_REPO_MANAGER_SOURCE_REQUIRED")
    if not app_source.get("exists"):
        issues.append("RUNTIME_APP_SOURCE_REQUIRED")
    if not fixture.get("git_dir"):
        issues.append("FIELD_FIXTURE_GIT_REQUIRED")

    payload = {
        "schema": "enguru.mac-engineering.repo-discovery-diagnostic/v1",
        "observed_at": now(),
        "state": "PASS" if not issues else "HOLD",
        "issues": issues,
        "fixture": fixture,
        "projects_inventory": inventory,
        "repo_manager": repo_source,
        "app": app_source,
        "inferred_contract": inferred,
        "truth_boundary": (
            "Read-only diagnostic. No repository, runtime, app, task or fixture "
            "content is changed."
        ),
        "next_action": (
            "Use the observed runtime discovery contract to align only the field harness."
            if not issues
            else "Resolve only the missing diagnostic prerequisite."
        ),
    }

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "state": payload["state"],
                "issues": issues,
                "fixture": fixture,
                "inferred_contract": inferred,
                "repo_manager_functions": [
                    {
                        "name": item["name"],
                        "line_start": item["line_start"],
                        "line_end": item["line_end"],
                        "source": item["source"],
                    }
                    for item in repo_source.get("functions", [])
                ],
                "app_functions": [
                    {
                        "name": item["name"],
                        "line_start": item["line_start"],
                        "line_end": item["line_end"],
                        "source": item["source"],
                    }
                    for item in app_source.get("functions", [])
                ],
                "evidence": str(EVIDENCE),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
