#!/usr/bin/env python3
"""ENGÜRÜ Mac Repository Fabric™ — full-history local mirror and offline continuity."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home()
MANIFEST = ROOT / "governance" / "mac-engineer" / "MAC_REPOSITORY_FABRIC_V1.json"
RUNTIME_STATE = HOME / "Enguru" / "Runtime" / "MacEngineer" / "state" / "repository-fabric.json"
EVIDENCE_ROOT = HOME / "Enguru" / "Evidence" / "MacEngineer" / "repository-fabric"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 600,
) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"code": 124, "stdout": "", "stderr": "TIMEOUT"}
    except Exception as exc:
        return {
            "code": 125,
            "stdout": "",
            "stderr": f"{type(exc).__name__}:{exc}",
        }


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    repos = data.get("repositories")
    if not isinstance(repos, list) or not repos:
        raise RuntimeError("REPOSITORY_FABRIC_MANIFEST_EMPTY")
    return data


def expand(value: str) -> Path:
    return Path(value).expanduser()


def mirror_path(root: Path, name: str) -> Path:
    return root / f"{name}.git"


def git_output(args: list[str], *, cwd: Path | None = None) -> str | None:
    result = run(args, cwd=cwd, timeout=120)
    return result["stdout"] if result["code"] == 0 else None


def mirror_sync(record: dict[str, Any], root: Path) -> dict[str, Any]:
    name = str(record["name"])
    clone_url = str(record["cloneUrl"])
    expected = str(record["exactMain"])
    default_branch = str(record.get("defaultBranch") or "main")
    mirror = mirror_path(root, name)
    mirror.parent.mkdir(parents=True, exist_ok=True)

    if not mirror.exists():
        result = run(
            ["git", "clone", "--mirror", clone_url, str(mirror)],
            timeout=1200,
        )
        action = "CREATED"
    else:
        if not (mirror / "HEAD").exists():
            return {
                "repository": f"engurulabory/{name}",
                "state": "HOLD",
                "reason": "MIRROR_PATH_NOT_GIT",
                "mirror": str(mirror),
            }
        set_url = run(
            ["git", "--git-dir", str(mirror), "remote", "set-url", "origin", clone_url],
            timeout=60,
        )
        if set_url["code"] != 0:
            return {
                "repository": f"engurulabory/{name}",
                "state": "HOLD",
                "reason": "MIRROR_REMOTE_SET_URL_FAILED",
                "mirror": str(mirror),
                "error": set_url["stderr"],
            }
        result = run(
            ["git", "--git-dir", str(mirror), "remote", "update", "--prune"],
            timeout=1200,
        )
        action = "UPDATED"

    if result["code"] != 0:
        return {
            "repository": f"engurulabory/{name}",
            "state": "HOLD",
            "reason": "MIRROR_SYNC_FAILED",
            "mirror": str(mirror),
            "error": result["stderr"][-4000:],
        }

    observed = git_output(
        ["git", "--git-dir", str(mirror), "rev-parse", f"refs/heads/{default_branch}"]
    )
    bare = git_output(
        ["git", "--git-dir", str(mirror), "rev-parse", "--is-bare-repository"]
    )
    fsck = run(
        ["git", "--git-dir", str(mirror), "fsck", "--full", "--no-dangling"],
        timeout=600,
    )

    state = "PASS"
    reason = None
    if bare != "true":
        state = "HOLD"
        reason = "MIRROR_NOT_BARE"
    elif observed != expected:
        state = "HOLD"
        reason = "MANIFEST_REMOTE_MAIN_DRIFT"
    elif fsck["code"] != 0:
        state = "HOLD"
        reason = "MIRROR_FSCK_FAILED"

    return {
        "repository": f"engurulabory/{name}",
        "role": record.get("role"),
        "visibility": record.get("visibility"),
        "state": state,
        "reason": reason,
        "action": action,
        "mirror": str(mirror),
        "bare": bare == "true",
        "expectedMain": expected,
        "observedMain": observed,
        "exactMain": observed == expected,
        "fsck": "PASS" if fsck["code"] == 0 else "HOLD",
        "authority": "FULL_HISTORY_OFFLINE_SOURCE_CACHE_NOT_SECOND_TRUTH",
    }


def normalize_remote(url: str | None) -> str | None:
    if not url:
        return None
    value = url.strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    if value.endswith(".git"):
        value = value[:-4]
    return value.lower()


def checkout_candidates(record: dict[str, Any]) -> list[Path]:
    name = str(record["name"])
    values: list[Path] = []
    known = record.get("knownCheckout")
    if isinstance(known, str) and known:
        values.append(expand(known))
    values.extend(
        [
            HOME / "Enguru" / "Projects" / name,
            HOME / "Enguru" / "Cores" / name,
            HOME / "Enguru" / name,
        ]
    )
    unique: list[Path] = []
    seen: set[str] = set()
    for value in values:
        key = str(value)
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


def inspect_checkout(record: dict[str, Any]) -> dict[str, Any]:
    expected_remote = normalize_remote(str(record["cloneUrl"]))
    for path in checkout_candidates(record):
        inside = git_output(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"])
        if inside != "true":
            continue
        origin = git_output(["git", "-C", str(path), "remote", "get-url", "origin"])
        head = git_output(["git", "-C", str(path), "rev-parse", "HEAD"])
        branch = git_output(["git", "-C", str(path), "branch", "--show-current"])
        status = git_output(["git", "-C", str(path), "status", "--porcelain"]) or ""
        origin_main = git_output(["git", "-C", str(path), "rev-parse", "origin/main"])
        ahead = git_output(
            ["git", "-C", str(path), "rev-list", "--count", "origin/main..HEAD"]
        )
        behind = git_output(
            ["git", "-C", str(path), "rev-list", "--count", "HEAD..origin/main"]
        )
        return {
            "state": "PASS" if normalize_remote(origin) == expected_remote else "HOLD",
            "path": str(path),
            "origin": origin,
            "originMatchesManifest": normalize_remote(origin) == expected_remote,
            "head": head,
            "branch": branch,
            "clean": status == "",
            "dirtyPaths": [
                line[3:] if len(line) > 3 else line
                for line in status.splitlines()
                if line.strip()
            ],
            "originMain": origin_main,
            "aheadOriginMain": int(ahead) if ahead and ahead.isdigit() else None,
            "behindOriginMain": int(behind) if behind and behind.isdigit() else None,
            "authority": "WORKING_CHECKOUT_PENDING_RECONCILIATION_WHEN_AHEAD",
        }
    return {
        "state": "NOT_MATERIALIZED",
        "path": None,
        "authority": "MIRROR_IS_SUFFICIENT_FOR_OFFLINE_SOURCE_PRESERVATION",
    }


def offline_queue_proof(mirror_root: Path) -> dict[str, Any]:
    source = mirror_path(mirror_root, "donecheck")
    if not source.exists():
        return {"state": "HOLD", "reason": "DONECHECK_MIRROR_REQUIRED"}

    with tempfile.TemporaryDirectory(prefix="enguru-fabric-proof-") as td:
        fixture = Path(td) / "donecheck-fixture"
        clone = run(["git", "clone", str(source), str(fixture)], timeout=300)
        if clone["code"] != 0:
            return {
                "state": "HOLD",
                "reason": "LOCAL_MIRROR_CLONE_FAILED",
                "error": clone["stderr"],
            }

        base = git_output(["git", "-C", str(fixture), "rev-parse", "HEAD"])
        run(["git", "-C", str(fixture), "switch", "-c", "enguru-offline-proof"], timeout=60)
        run(["git", "-C", str(fixture), "config", "user.name", "ENGURU Fabric Proof"], timeout=30)
        run(["git", "-C", str(fixture), "config", "user.email", "fabric-proof@invalid.local"], timeout=30)
        proof = fixture / ".enguru-offline-proof"
        proof.write_text("offline queue proof\n", encoding="utf-8")
        add = run(["git", "-C", str(fixture), "add", ".enguru-offline-proof"], timeout=30)
        commit = run(
            ["git", "-C", str(fixture), "commit", "-m", "test: offline queue proof"],
            timeout=60,
        )
        if add["code"] != 0 or commit["code"] != 0:
            return {
                "state": "HOLD",
                "reason": "OFFLINE_FIXTURE_COMMIT_FAILED",
                "error": commit["stderr"],
            }

        head = git_output(["git", "-C", str(fixture), "rev-parse", "HEAD"])
        ahead = git_output(
            ["git", "-C", str(fixture), "rev-list", "--count", f"{base}..HEAD"]
        )
        mirror_after = git_output(
            ["git", "--git-dir", str(source), "rev-parse", "refs/heads/main"]
        )
        return {
            "state": "PASS"
            if base and head and head != base and ahead == "1" and mirror_after == base
            else "HOLD",
            "base": base,
            "fixtureCommit": head,
            "ahead": int(ahead) if ahead and ahead.isdigit() else None,
            "mirrorMainUnchanged": mirror_after == base,
            "fixturePushed": False,
            "authority": "LOCAL_COMMIT_QUEUE_PROOF_ONLY_NO_CANONICAL_MUTATION",
        }


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sync_fabric() -> dict[str, Any]:
    manifest = load_manifest()
    mirror_root = expand(str(manifest["mirrorRoot"]))
    mirror_root.mkdir(parents=True, exist_ok=True)

    mirrors = []
    checkouts = []
    for record in manifest["repositories"]:
        mirrors.append(mirror_sync(record, mirror_root))
        checkouts.append(
            {
                "repository": f"engurulabory/{record['name']}",
                **inspect_checkout(record),
            }
        )

    queue_proof = offline_queue_proof(mirror_root)

    mirror_pass = all(item["state"] == "PASS" for item in mirrors)
    mirror_count = sum(1 for item in mirrors if item["state"] == "PASS")
    state = "PASS" if mirror_pass and queue_proof.get("state") == "PASS" else "HOLD"

    payload = {
        "schema": "enguru.mac-engineer.repository-fabric-evidence/v1",
        "observedAt": now(),
        "state": state,
        "repositoryCount": len(manifest["repositories"]),
        "mirrorPassCount": mirror_count,
        "mirrorRoot": str(mirror_root),
        "mirrors": mirrors,
        "workingCheckouts": checkouts,
        "offlineQueueProof": queue_proof,
        "authority": manifest["authority"],
        "doneCheck": manifest.get("doneCheck"),
        "nextAction": (
            "MAC_REPOSITORY_FABRIC_RECONCILIATION"
            if state == "PASS"
            else "REPAIR_REPOSITORY_FABRIC_HOLD"
        ),
    }

    RUNTIME_STATE.parent.mkdir(parents=True, exist_ok=True)
    RUNTIME_STATE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_dir = EVIDENCE_ROOT / stamp
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence = evidence_dir / "evidence.json"
    evidence.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    receipt = evidence_dir / "receipt.txt"
    receipt.write_text(
        "\n".join(
            [
                f"STATE={state}",
                f"REPOSITORIES={len(manifest['repositories'])}",
                f"MIRRORS_PASS={mirror_count}_OF_{len(manifest['repositories'])}",
                f"OFFLINE_QUEUE={queue_proof.get('state')}",
                f"RUNTIME_STATE={RUNTIME_STATE}",
                f"EVIDENCE={evidence}",
                f"NEXT_ACTION={payload['nextAction']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    payload["evidencePath"] = str(evidence)
    payload["receiptPath"] = str(receipt)
    payload["evidenceSha256"] = file_sha256(evidence)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["sync", "status"])
    args = parser.parse_args()

    if args.command == "status":
        if not RUNTIME_STATE.is_file():
            print("STATE=HOLD")
            print("HOLD=REPOSITORY_FABRIC_STATE_MISSING")
            return 2
        payload = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    else:
        payload = sync_fabric()

    print(f"STATE={payload['state']}")
    print(f"REPOSITORIES={payload['repositoryCount']}")
    print(f"MIRRORS_PASS={payload['mirrorPassCount']}_OF_{payload['repositoryCount']}")
    print(f"OFFLINE_QUEUE={payload['offlineQueueProof'].get('state')}")
    print(f"RUNTIME_STATE={RUNTIME_STATE}")
    if payload.get("evidencePath"):
        print(f"EVIDENCE={payload['evidencePath']}")
    print(f"NEXT_ACTION={payload['nextAction']}")
    return 0 if payload["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
