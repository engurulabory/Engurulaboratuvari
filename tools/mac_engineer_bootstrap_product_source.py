#!/usr/bin/env python3
"""Bootstrap the dedicated ENGÜRÜ Mac Engineer™ product-source checkout.

Fail-closed:
- consumes only evidence-backed safe source + verified runtime delta authority;
- never copies excluded secret/binary/cache files;
- prepares in a temporary directory and promotes atomically;
- runs compile/tests before Git initialization;
- publishes only with explicit --publish and an authenticated GitHub CLI.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Iterable


REPO_TARGET = "engurulabory/enguru-mac-engineer"
PRODUCT_NAME = "ENGÜRÜ Mac Engineer™"
DEFAULT_DEST = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"
EVIDENCE_ROOT = Path.home() / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
SOURCE_REVIEW = EVIDENCE_ROOT / "package6-source-intake-review.json"
DELTA_REVIEW = EVIDENCE_ROOT / "package6-delta-authority-review.json"
PROVENANCE_REVIEW = EVIDENCE_ROOT / "package6-provenance-reconcile.json"


class BootstrapError(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "cwd": str(cwd) if cwd else "",
            "returncode": proc.returncode,
            "stdout": proc.stdout[-16000:],
            "stderr": proc.stderr[-16000:],
            "pass": proc.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "cwd": str(cwd) if cwd else "",
            "returncode": 124,
            "stdout": (exc.stdout or "")[-16000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-16000:] if isinstance(exc.stderr, str) else "",
            "pass": False,
            "reason": "TIMEOUT",
        }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BootstrapError(f"EVIDENCE_MISSING:{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BootstrapError(f"EVIDENCE_INVALID:{path}:{type(exc).__name__}") from exc


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_relative(value: str) -> Path:
    rel = Path(value)
    if rel.is_absolute() or not value.strip():
        raise BootstrapError(f"UNSAFE_RELATIVE_PATH:{value}")
    if any(part in {"..", ""} for part in rel.parts):
        raise BootstrapError(f"UNSAFE_RELATIVE_PATH:{value}")
    return rel


def ensure_under(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise BootstrapError(f"PATH_OUTSIDE_AUTHORITY:{resolved}") from exc
    return resolved


def copy_record(record: dict[str, Any], destination_root: Path, authority_root: Path) -> dict[str, Any]:
    source = ensure_under(Path(str(record["path"])), authority_root)
    if not source.is_file() or source.is_symlink():
        raise BootstrapError(f"SOURCE_FILE_INVALID:{source}")
    rel = safe_relative(str(record["relative_path"]))
    target = destination_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    digest = sha256_file(target)
    expected = str(record.get("sha256", ""))
    if expected and digest != expected:
        raise BootstrapError(f"COPY_HASH_MISMATCH:{rel}")
    return {"relative_path": str(rel), "sha256": digest, "authority": "HISTORICAL_SAFE_SOURCE"}


def choose_divergent_destination(row: dict[str, Any]) -> Path:
    candidates = row.get("source_candidates", [])
    if not isinstance(candidates, list) or not candidates:
        raise BootstrapError(
            f"DIVERGENT_SOURCE_MAPPING_MISSING:{row.get('runtime', {}).get('relative_path')}"
        )
    first = candidates[0]
    source = first.get("source", {}) if isinstance(first, dict) else {}
    rel = source.get("relative_path")
    if not rel:
        raise BootstrapError(
            f"DIVERGENT_SOURCE_MAPPING_INVALID:{row.get('runtime', {}).get('relative_path')}"
        )
    return safe_relative(str(rel))


def apply_runtime_authority(
    delta: dict[str, Any],
    destination_root: Path,
    runtime_root: Path,
) -> list[dict[str, Any]]:
    if delta.get("state") != "PASS":
        raise BootstrapError("DELTA_AUTHORITY_NOT_PASS")
    if delta.get("compile_result", {}).get("pass") is not True:
        raise BootstrapError("DELTA_COMPILE_NOT_PASS")
    if delta.get("test_result", {}).get("pass") is not True:
        raise BootstrapError("DELTA_TESTS_NOT_PASS")

    expected = set(
        delta.get("proposed_authority", {}).get("runtime_authority_candidate_files", [])
    )
    applied: list[dict[str, Any]] = []

    for row in delta.get("rows", []):
        if not isinstance(row, dict):
            continue
        classification = row.get("classification")
        authority = row.get("authority")
        runtime = row.get("runtime", {})
        runtime_rel_value = str(runtime.get("relative_path", ""))
        if classification not in {"DIVERGENT", "RUNTIME_ONLY"}:
            continue
        if authority != "RUNTIME_FIELD_CANDIDATE":
            raise BootstrapError(f"DELTA_AUTHORITY_HOLD:{runtime_rel_value}")
        if runtime_rel_value not in expected:
            raise BootstrapError(f"DELTA_AUTHORITY_SET_MISMATCH:{runtime_rel_value}")

        runtime_path = ensure_under(Path(str(runtime["path"])), runtime_root)
        if not runtime_path.is_file() or runtime_path.is_symlink():
            raise BootstrapError(f"RUNTIME_FILE_INVALID:{runtime_path}")
        runtime_rel = safe_relative(runtime_rel_value)
        destination_rel = (
            choose_divergent_destination(row)
            if classification == "DIVERGENT"
            else runtime_rel
        )
        target = destination_root / destination_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_path, target)
        digest = sha256_file(target)
        if runtime.get("sha256") and digest != runtime["sha256"]:
            raise BootstrapError(f"RUNTIME_COPY_HASH_MISMATCH:{runtime_rel}")
        applied.append(
            {
                "runtime_relative_path": str(runtime_rel),
                "destination_relative_path": str(destination_rel),
                "sha256": digest,
                "authority": "VERIFIED_CURRENT_FIELD_RUNTIME",
                "classification": classification,
            }
        )

    applied_names = {x["runtime_relative_path"] for x in applied}
    if applied_names != expected:
        missing = sorted(expected - applied_names)
        raise BootstrapError(
            f"DELTA_AUTHORITY_NOT_FULLY_APPLIED:{','.join(missing)}"
        )
    return applied


def write_metadata(
    destination_root: Path,
    *,
    provenance: dict[str, Any],
    source_review: dict[str, Any],
    delta_review: dict[str, Any],
    safe_copies: list[dict[str, Any]],
    runtime_overrides: list[dict[str, Any]],
) -> None:
    (destination_root / ".enguru").mkdir(parents=True, exist_ok=True)
    (destination_root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)

    gitignore = """# ENGÜRÜ Mac Engineer product-source ignore policy
.DS_Store
__pycache__/
*.py[cod]
.venv/
venv/
.env
.env.*
runtime-state/
Evidence/
build/
dist/
*.app/
DerivedData/
"""
    (destination_root / ".gitignore").write_text(gitignore, encoding="utf-8")

    manifest = {
        "schema": "enguru.labory.product-manifest/v1",
        "canonicalName": PRODUCT_NAME,
        "assetType": "PRODUCT",
        "sourceAuthority": "GITHUB_EXACT_MAIN",
        "repository": REPO_TARGET,
        "controlPlane": "engurulabory/Engurulaboratuvari",
        "localCheckout": "~/Enguru/Projects/enguru-mac-engineer",
        "runtimeRoot": "~/Enguru/Runtime/MacEngineer",
        "installedApp": "~/Applications/ENGÜRÜ Mac Engineer.app",
        "evidenceRoot": "~/Enguru/Evidence/MacEngineer",
        "humanThresholdPreserved": True,
    }
    (destination_root / ".enguru" / "labory-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    provenance_manifest = {
        "schema": "enguru.mac-engineer.product-source-provenance/v1",
        "generatedAt": now(),
        "product": PRODUCT_NAME,
        "repositoryTarget": REPO_TARGET,
        "historicalSource": {
            "name": "ENGURU_Mac_Engineer_Project_Handoff_v1",
            "baseline": "baseline_v0.4",
            "provenanceReviewState": provenance.get("state"),
        },
        "sourceIntake": {
            "safeFileCount": source_review.get("source", {}).get("safe_file_count"),
            "secretFindingCount": len(
                source_review.get("source", {}).get("secret_findings", [])
            ),
        },
        "deltaAuthority": {
            "state": delta_review.get("state"),
            "compilePass": delta_review.get("compile_result", {}).get("pass"),
            "testsPass": delta_review.get("test_result", {}).get("pass"),
            "verifiedRuntimeAuthorityCandidates": len(runtime_overrides),
        },
        "files": {
            "historicalSafeCopied": safe_copies,
            "verifiedRuntimeOverrides": runtime_overrides,
        },
        "truthBoundary": (
            "This manifest proves the local canonical-source bootstrap composition. "
            "Remote GitHub authority begins only after this exact tree is pushed and exact-main is verified."
        ),
    }
    (destination_root / "PROVENANCE.json").write_text(
        json.dumps(provenance_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    canonical_doc = """# ENGÜRÜ Mac Engineer™ — Canonical Product Source

This repository is the product source surface for ENGÜRÜ Mac Engineer™.

Authority:
- Labory (engurulabory/Engurulaboratuvari) governs WORKLIST, cross-product governance and aggregate Evidence.
- This repository owns Mac Engineer native/runtime product source.
- ~/Enguru/Runtime/MacEngineer is an execution output/state surface.
- ~/Applications/ENGÜRÜ Mac Engineer.app is an installed artifact.
- Runtime field deltas return through Evidence + tests + a product-source PR before they become canonical.

Build/install provenance must always record the exact product-source Git SHA.
"""
    (destination_root / "CANONICAL_SOURCE.md").write_text(
        canonical_doc, encoding="utf-8"
    )

    workflow = """name: ENGURU Mac Engineer Product CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  product-ci:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.14"
      - name: Install Python requirements when present
        shell: bash
        run: |
          if [ -f requirements.txt ]; then python -m pip install -r requirements.txt; fi
          if [ -f runtime/requirements.txt ]; then python -m pip install -r runtime/requirements.txt; fi
      - name: Python compile
        run: python -m compileall -q .
      - name: Python tests
        shell: bash
        run: |
          found=0
          while IFS= read -r testdir; do
            found=1
            parent="$(dirname "$testdir")"
            PYTHONPATH="$PWD:$PWD/runtime:$PWD/$parent" python -m unittest discover -s "$testdir" -v
          done < <(find . -type d -name tests -not -path './.git/*' | sort)
          if [ "$found" -eq 0 ]; then echo "No unittest directory found"; fi
      - name: Swift parse
        shell: bash
        run: |
          files="$(find . -type f -name '*.swift' -not -path './.git/*' | sort)"
          if [ -n "$files" ]; then xcrun swiftc -parse $files; fi
"""
    (destination_root / ".github" / "workflows" / "product-ci.yml").write_text(
        workflow, encoding="utf-8"
    )


def iter_test_dirs(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("tests")):
        if path.is_dir() and ".git" not in path.parts and "__pycache__" not in path.parts:
            yield path


def verify_tree(root: Path) -> dict[str, Any]:
    env = dict(os.environ)
    python_paths = [str(root)]
    if (root / "runtime").exists():
        python_paths.append(str(root / "runtime"))
    if env.get("PYTHONPATH"):
        python_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    compile_result = run(
        ["python3", "-m", "compileall", "-q", str(root)],
        cwd=root,
        env=env,
    )
    test_results: list[dict[str, Any]] = []
    for test_dir in iter_test_dirs(root):
        local_env = dict(env)
        test_paths = [str(root), str(root / "runtime"), str(test_dir.parent)]
        if env.get("PYTHONPATH"):
            test_paths.append(env["PYTHONPATH"])
        local_env["PYTHONPATH"] = os.pathsep.join(test_paths)
        test_results.append(
            run(
                ["python3", "-m", "unittest", "discover", "-s", str(test_dir), "-v"],
                cwd=root,
                env=local_env,
                timeout=300,
            )
        )
    return {
        "compile": compile_result,
        "tests": test_results,
        "pass": compile_result["pass"] and all(x["pass"] for x in test_results),
    }


def git_initialize(root: Path) -> dict[str, Any]:
    steps = [
        run(["git", "init", "-b", "main"], cwd=root),
        run(["git", "add", "-A"], cwd=root),
        run(
            ["git", "commit", "-m", "feat: canonicalize ENGÜRÜ Mac Engineer product source"],
            cwd=root,
        ),
    ]
    return {"steps": steps, "pass": all(x["pass"] for x in steps)}


def publish(root: Path) -> dict[str, Any]:
    gh = run(["gh", "--version"], cwd=root)
    if not gh["pass"]:
        return {"pass": False, "reason": "GITHUB_CLI_REQUIRED", "gh": gh}
    auth = run(["gh", "auth", "status"], cwd=root)
    if not auth["pass"]:
        return {
            "pass": False,
            "reason": "GITHUB_CLI_AUTH_REQUIRED",
            "gh": gh,
            "auth": auth,
        }

    exists = run(
        ["gh", "repo", "view", REPO_TARGET, "--json", "nameWithOwner"], cwd=root
    )
    steps: list[dict[str, Any]] = [gh, auth, exists]

    if exists["pass"]:
        remote = run(["git", "remote", "get-url", "origin"], cwd=root)
        if not remote["pass"]:
            remote = run(
                [
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{REPO_TARGET}.git",
                ],
                cwd=root,
            )
        steps.append(remote)
        push = run(["git", "push", "-u", "origin", "main"], cwd=root)
        steps.append(push)
        return {
            "pass": push["pass"],
            "repository": REPO_TARGET,
            "steps": steps,
        }

    create = run(
        [
            "gh",
            "repo",
            "create",
            REPO_TARGET,
            "--private",
            "--source",
            str(root),
            "--remote",
            "origin",
            "--push",
        ],
        cwd=root,
        timeout=300,
    )
    steps.append(create)
    return {
        "pass": create["pass"],
        "repository": REPO_TARGET,
        "steps": steps,
    }


def prepare_tree(
    destination: Path,
    *,
    source_review_path: Path = SOURCE_REVIEW,
    delta_review_path: Path = DELTA_REVIEW,
    provenance_review_path: Path = PROVENANCE_REVIEW,
) -> dict[str, Any]:
    source_review = load_json(source_review_path)
    delta_review = load_json(delta_review_path)
    provenance = load_json(provenance_review_path)

    if provenance.get("state") != "PASS":
        raise BootstrapError("HISTORICAL_PROVENANCE_NOT_PASS")
    source = source_review.get("source", {})
    if source.get("secret_findings"):
        raise BootstrapError("SOURCE_SECRET_FINDINGS_PRESENT")
    if int(source.get("safe_file_count", 0)) <= 0:
        raise BootstrapError("NO_SAFE_SOURCE_FILES")
    if delta_review.get("state") != "PASS":
        raise BootstrapError("DELTA_AUTHORITY_NOT_PASS")

    source_root = Path(str(source_review.get("source_root", ""))).expanduser()
    runtime_root = Path(str(source_review.get("runtime_root", ""))).expanduser()
    if not source_root.is_dir():
        raise BootstrapError(f"SOURCE_ROOT_MISSING:{source_root}")
    if not runtime_root.is_dir():
        raise BootstrapError(f"RUNTIME_ROOT_MISSING:{runtime_root}")

    destination = destination.expanduser()
    if destination.exists():
        raise BootstrapError(f"DESTINATION_ALREADY_EXISTS:{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    staging = destination.parent / f".{destination.name}.bootstrap-{os.getpid()}"
    if staging.exists():
        raise BootstrapError(f"STAGING_ALREADY_EXISTS:{staging}")
    staging.mkdir()

    try:
        safe_copies = [
            copy_record(record, staging, source_root)
            for record in source.get("safe_files", [])
        ]
        overrides = apply_runtime_authority(delta_review, staging, runtime_root)
        write_metadata(
            staging,
            provenance=provenance,
            source_review=source_review,
            delta_review=delta_review,
            safe_copies=safe_copies,
            runtime_overrides=overrides,
        )

        verification = verify_tree(staging)
        if not verification["pass"]:
            raise BootstrapError("PREPARED_SOURCE_VERIFICATION_FAILED")

        staging.rename(destination)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise

    return {
        "destination": str(destination),
        "safe_source_files": len(safe_copies),
        "runtime_overrides": len(overrides),
        "verification": verification,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, default=DEFAULT_DEST)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    output: dict[str, Any] = {
        "state": "HOLD",
        "product": PRODUCT_NAME,
        "repositoryTarget": REPO_TARGET,
        "destination": str(args.destination.expanduser()),
    }
    try:
        destination = args.destination.expanduser()

        if destination.exists():
            if not args.publish:
                raise BootstrapError(f"DESTINATION_ALREADY_EXISTS:{destination}")
            if not (destination / ".git").exists():
                raise BootstrapError("EXISTING_PRODUCT_SOURCE_GIT_REQUIRED")
            if not (destination / "PROVENANCE.json").exists():
                raise BootstrapError("EXISTING_PRODUCT_SOURCE_PROVENANCE_REQUIRED")

            verification = verify_tree(destination)
            output["prepared"] = {
                "destination": str(destination),
                "existing": True,
                "verification": verification,
            }
            if not verification["pass"]:
                raise BootstrapError("EXISTING_PRODUCT_SOURCE_VERIFICATION_FAILED")

            status = run(["git", "status", "--porcelain"], cwd=destination)
            if not status["pass"] or status["stdout"]:
                raise BootstrapError("EXISTING_PRODUCT_SOURCE_CLEAN_REQUIRED")

            head = run(["git", "rev-parse", "HEAD"], cwd=destination)
            if not head["pass"]:
                raise BootstrapError("EXISTING_PRODUCT_SOURCE_HEAD_REQUIRED")
            output["localSourceHead"] = head.get("stdout", "")
            output["git"] = {"pass": True, "existing": True}
        else:
            prepared = prepare_tree(destination)
            output["prepared"] = prepared

            git_result = git_initialize(destination)
            output["git"] = git_result
            if not git_result["pass"]:
                output["reason"] = "LOCAL_GIT_INITIALIZATION_FAILED"
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return 2

            head = run(["git", "rev-parse", "HEAD"], cwd=destination)
            output["localSourceHead"] = head.get("stdout", "")

        if args.publish:
            remote = publish(destination)
            output["publish"] = remote
            if not remote["pass"]:
                output["reason"] = remote.get(
                    "reason", "REMOTE_PUBLICATION_FAILED"
                )
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return 2
            output["state"] = "PASS"
            output["reason"] = (
                "LOCAL_PRODUCT_SOURCE_BOOTSTRAPPED_AND_PUBLISHED"
            )
            output["next_action"] = (
                "Verify dedicated product repository exact-main CI, then rebuild/install from that exact product-source SHA."
            )
        else:
            output["state"] = "PASS"
            output["reason"] = "LOCAL_PRODUCT_SOURCE_BOOTSTRAPPED"
            output["next_action"] = (
                "Review the prepared local source, then run the same control entry point with --publish; the verified tree will be reused without reconstruction."
            )

        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except BootstrapError as exc:
        output["reason"] = str(exc)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
