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
import sys
from typing import Any, Iterable


REPO_TARGET = "engurulabory/enguru-mac-engineer"
PRODUCT_NAME = "ENGÜRÜ Mac Engineer™"
DEFAULT_DEST = Path.home() / "Enguru" / "Projects" / "enguru-mac-engineer"
EVIDENCE_ROOT = Path.home() / "Enguru" / "Evidence" / "MacEngineer" / "v0.6"
SOURCE_REVIEW = EVIDENCE_ROOT / "package6-source-intake-review.json"
DELTA_REVIEW = EVIDENCE_ROOT / "package6-delta-authority-review.json"
PROVENANCE_REVIEW = EVIDENCE_ROOT / "package6-provenance-reconcile.json"

NATIVE_SOURCE_PREFIX = "execution_prep/native_app/"
REQUIRED_NATIVE_FILES = {
    "EnguruMacEngineerApp.swift",
    "Info.plist",
    "prepare_native_app.command",
}


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


def copy_verified_file(
    source: Path,
    target: Path,
    expected_sha256: str,
) -> str:
    if not source.is_file() or source.is_symlink():
        raise BootstrapError(f"SOURCE_FILE_INVALID:{source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    digest = sha256_file(target)
    if expected_sha256 and digest != expected_sha256:
        raise BootstrapError(f"COPY_HASH_MISMATCH:{target}")
    return digest


def copy_native_sources(
    source_review: dict[str, Any],
    destination_root: Path,
    source_root: Path,
) -> list[dict[str, Any]]:
    safe_files = source_review.get("source", {}).get("safe_files", [])
    selected: dict[str, dict[str, Any]] = {}

    for record in safe_files:
        if not isinstance(record, dict):
            continue
        rel_value = str(record.get("relative_path", ""))
        rel = safe_relative(rel_value)
        if not rel_value.startswith(NATIVE_SOURCE_PREFIX):
            continue
        if rel.name in REQUIRED_NATIVE_FILES:
            selected[rel.name] = record

    missing = sorted(REQUIRED_NATIVE_FILES - set(selected))
    if missing:
        raise BootstrapError(
            "REQUIRED_NATIVE_SOURCE_MISSING:" + ",".join(missing)
        )

    copied: list[dict[str, Any]] = []
    native_root = destination_root / "execution_prep" / "native_app"
    for name in sorted(REQUIRED_NATIVE_FILES):
        record = selected[name]
        source = ensure_under(Path(str(record["path"])), source_root)
        target = native_root / name
        digest = copy_verified_file(
            source,
            target,
            str(record.get("sha256", "")),
        )
        copied.append(
            {
                "historical_relative_path": str(record["relative_path"]),
                "product_relative_path": str(
                    target.relative_to(destination_root)
                ),
                "sha256": digest,
                "authority": "HISTORICAL_NATIVE_SOURCE",
            }
        )

    prep = native_root / "prepare_native_app.command"
    text = prep.read_text(encoding="utf-8")
    old = '$SRC_DIR/../../baseline_v0.4/runtime'
    new = '$SRC_DIR/../../runtime'
    if old in text:
        text = text.replace(old, new)
        prep.write_text(text, encoding="utf-8")
    elif new not in text:
        raise BootstrapError("NATIVE_PREP_RUNTIME_SOURCE_MAPPING_UNKNOWN")

    for item in copied:
        if item["product_relative_path"].endswith(
            "prepare_native_app.command"
        ):
            item["sha256"] = sha256_file(prep)
            item["derived_change"] = (
                "runtime source normalized from historical "
                "baseline_v0.4/runtime to canonical product runtime/"
            )
    return copied


def current_runtime_records(
    source_review: dict[str, Any],
) -> list[dict[str, Any]]:
    comparison = source_review.get("runtime_comparison", {})
    records: list[dict[str, Any]] = []
    classifications = (
        ("exact", "HISTORICAL_EXACT"),
        ("divergent", "VERIFIED_FIELD_DELTA"),
        ("runtime_only", "VERIFIED_FIELD_ADDITION"),
    )

    seen: set[str] = set()
    for section, authority in classifications:
        rows = comparison.get(section, [])
        if not isinstance(rows, list):
            raise BootstrapError(
                f"RUNTIME_COMPARISON_INVALID:{section}"
            )
        for row in rows:
            if not isinstance(row, dict):
                continue
            runtime = row.get("runtime", {})
            rel_value = str(runtime.get("relative_path", ""))
            rel = safe_relative(rel_value)
            if rel_value in seen:
                raise BootstrapError(
                    f"DUPLICATE_RUNTIME_RECORD:{rel_value}"
                )
            seen.add(rel_value)
            records.append(
                {
                    "path": str(runtime.get("path", "")),
                    "relative_path": str(rel),
                    "sha256": str(runtime.get("sha256", "")),
                    "authority": authority,
                    "classification": section.upper(),
                }
            )

    expected_total = comparison.get("counts", {}).get("runtime_total")
    if expected_total is not None and len(records) != int(expected_total):
        raise BootstrapError(
            "RUNTIME_RECORD_COUNT_MISMATCH:"
            f"{len(records)}!={expected_total}"
        )
    if not records:
        raise BootstrapError("CURRENT_RUNTIME_SOURCE_EMPTY")
    return records


def validate_delta_authority(
    source_review: dict[str, Any],
    delta_review: dict[str, Any],
) -> set[str]:
    if delta_review.get("state") != "PASS":
        raise BootstrapError("DELTA_AUTHORITY_NOT_PASS")
    if delta_review.get("compile_result", {}).get("pass") is not True:
        raise BootstrapError("DELTA_COMPILE_NOT_PASS")
    if delta_review.get("test_result", {}).get("pass") is not True:
        raise BootstrapError("DELTA_TESTS_NOT_PASS")

    expected = set(
        delta_review.get("proposed_authority", {}).get(
            "runtime_authority_candidate_files", []
        )
    )
    comparison = source_review.get("runtime_comparison", {})
    observed: set[str] = set()
    for section in ("divergent", "runtime_only"):
        for row in comparison.get(section, []):
            if isinstance(row, dict):
                rel = str(
                    row.get("runtime", {}).get(
                        "relative_path", ""
                    )
                )
                if rel:
                    observed.add(rel)

    if expected != observed:
        raise BootstrapError(
            "DELTA_AUTHORITY_SET_MISMATCH:"
            f"expected={sorted(expected)}:"
            f"observed={sorted(observed)}"
        )
    return expected


def copy_current_runtime(
    source_review: dict[str, Any],
    delta_review: dict[str, Any],
    destination_root: Path,
    runtime_root: Path,
) -> list[dict[str, Any]]:
    validate_delta_authority(source_review, delta_review)
    records = current_runtime_records(source_review)
    copied: list[dict[str, Any]] = []

    for record in records:
        source = ensure_under(
            Path(record["path"]),
            runtime_root,
        )
        rel = safe_relative(record["relative_path"])
        target = destination_root / "runtime" / rel
        digest = copy_verified_file(
            source,
            target,
            record["sha256"],
        )
        copied.append(
            {
                "runtime_relative_path": str(rel),
                "product_relative_path": str(
                    target.relative_to(destination_root)
                ),
                "sha256": digest,
                "authority": record["authority"],
                "classification": record["classification"],
            }
        )

    return copied

def write_metadata(
    destination_root: Path,
    *,
    provenance: dict[str, Any],
    source_review: dict[str, Any],
    delta_review: dict[str, Any],
    native_sources: list[dict[str, Any]],
    runtime_sources: list[dict[str, Any]],
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
            "verifiedRuntimeAuthorityCandidates": len(
                delta_review.get("proposed_authority", {}).get(
                    "runtime_authority_candidate_files", []
                )
            ),
            "canonicalRuntimeSourceFiles": len(runtime_sources),
            "nativeSourceFiles": len(native_sources),
        },
        "files": {
            "nativeSources": native_sources,
            "runtimeSources": runtime_sources,
        },
        "composition": (
            "historical native source + current verified runtime "
            "snapshot (13 exact historical continuities + "
            "13 compile/test-verified field deltas)"
        ),
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
      - name: Install Python requirements
        shell: bash
        run: |
          if [ -f runtime/requirements.txt ]; then python -m pip install -r runtime/requirements.txt; fi
      - name: Runtime compile
        run: python -m compileall -q runtime
      - name: Runtime tests
        env:
          PYTHONPATH: ${{ github.workspace }}/runtime
        run: python -m unittest discover -s runtime/tests -v
      - name: Native prep syntax
        run: zsh -n execution_prep/native_app/prepare_native_app.command
      - name: Native Swift typecheck
        run: xcrun swiftc -typecheck execution_prep/native_app/EnguruMacEngineerApp.swift -framework SwiftUI -framework WebKit -framework AppKit
"""
    (destination_root / ".github" / "workflows" / "product-ci.yml").write_text(
        workflow, encoding="utf-8"
    )


def verification_issues(result: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for key in ("runtime_compile", "runtime_tests"):
        item = result.get(key, {})
        if item.get("pass") is not True:
            issues.append(key)
    native = result.get("native", {})
    for key, item in native.items():
        if isinstance(item, dict) and item.get("pass") is not True:
            issues.append(f"native:{key}")
    return issues


def verify_tree(root: Path) -> dict[str, Any]:
    runtime = root / "runtime"
    tests = runtime / "tests"
    if not runtime.is_dir():
        return {
            "pass": False,
            "runtime_compile": {
                "pass": False,
                "reason": "RUNTIME_SOURCE_DIRECTORY_REQUIRED",
            },
            "runtime_tests": {
                "pass": False,
                "reason": "RUNTIME_TEST_DIRECTORY_REQUIRED",
            },
            "native": {},
        }
    if not tests.is_dir():
        return {
            "pass": False,
            "runtime_compile": run(
                ["python3", "-m", "compileall", "-q", str(runtime)],
                cwd=root,
            ),
            "runtime_tests": {
                "pass": False,
                "reason": "RUNTIME_TEST_DIRECTORY_REQUIRED",
            },
            "native": {},
        }

    env = dict(os.environ)
    paths = [str(runtime)]
    if env.get("PYTHONPATH"):
        paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(paths)

    compile_result = run(
        ["python3", "-m", "compileall", "-q", str(runtime)],
        cwd=root,
        env=env,
    )
    test_result = run(
        [
            "python3",
            "-m",
            "unittest",
            "discover",
            "-s",
            str(tests),
            "-v",
        ],
        cwd=root,
        env=env,
        timeout=300,
    )

    native: dict[str, Any] = {}
    prep = root / "execution_prep" / "native_app" / (
        "prepare_native_app.command"
    )
    swift = root / "execution_prep" / "native_app" / (
        "EnguruMacEngineerApp.swift"
    )

    if sys.platform == "darwin":
        native["zsh_syntax"] = run(
            ["zsh", "-n", str(prep)],
            cwd=root,
        )
        native["swift_typecheck"] = run(
            [
                "xcrun",
                "swiftc",
                "-typecheck",
                str(swift),
                "-framework",
                "SwiftUI",
                "-framework",
                "WebKit",
                "-framework",
                "AppKit",
            ],
            cwd=root,
            timeout=300,
        )

    passed = (
        compile_result["pass"]
        and test_result["pass"]
        and all(
            item.get("pass") is True
            for item in native.values()
        )
    )
    return {
        "runtime_compile": compile_result,
        "runtime_tests": test_result,
        "native": native,
        "pass": passed,
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

    source_root = Path(
        str(source_review.get("source_root", ""))
    ).expanduser()
    runtime_root = Path(
        str(source_review.get("runtime_root", ""))
    ).expanduser()
    if not source_root.is_dir():
        raise BootstrapError(f"SOURCE_ROOT_MISSING:{source_root}")
    if not runtime_root.is_dir():
        raise BootstrapError(f"RUNTIME_ROOT_MISSING:{runtime_root}")

    destination = destination.expanduser()
    if destination.exists():
        raise BootstrapError(
            f"DESTINATION_ALREADY_EXISTS:{destination}"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)

    staging = destination.parent / (
        f".{destination.name}.bootstrap-{os.getpid()}"
    )
    if staging.exists():
        raise BootstrapError(
            f"STAGING_ALREADY_EXISTS:{staging}"
        )
    staging.mkdir()

    try:
        native_sources = copy_native_sources(
            source_review,
            staging,
            source_root,
        )
        runtime_sources = copy_current_runtime(
            source_review,
            delta_review,
            staging,
            runtime_root,
        )
        write_metadata(
            staging,
            provenance=provenance,
            source_review=source_review,
            delta_review=delta_review,
            native_sources=native_sources,
            runtime_sources=runtime_sources,
        )

        verification = verify_tree(staging)
        if not verification["pass"]:
            failure = {
                "schema": (
                    "enguru.mac-engineer."
                    "product-source-bootstrap-failure/v1"
                ),
                "observedAt": now(),
                "state": "HOLD",
                "issues": verification_issues(verification),
                "verification": verification,
                "staging": str(staging),
                "truthBoundary": (
                    "Staging was not promoted and will be "
                    "removed after this receipt is written."
                ),
            }
            EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
            failure_path = (
                EVIDENCE_ROOT
                / "product-source-bootstrap-failure.json"
            )
            failure_path.write_text(
                json.dumps(
                    failure,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            raise BootstrapError(
                "PREPARED_SOURCE_VERIFICATION_FAILED:"
                + ",".join(failure["issues"])
                + f":evidence={failure_path}"
            )

        staging.rename(destination)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise

    return {
        "destination": str(destination),
        "native_source_files": len(native_sources),
        "runtime_source_files": len(runtime_sources),
        "verification": verification,
        "composition": (
            "3 historical native source files + "
            "26 current verified runtime source files"
        ),
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
