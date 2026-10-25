#!/usr/bin/env python3
"""A04: authenticate pinned upstream LICENSE/SECURITY bytes; no product authority.

Public GitHub raw bytes are independently fetched at immutable upstream commits.
The result proves file-byte identity only, not license clearance, CVE/SBOM review,
a customer deployment, Kâşifi runtime or official Ar-Ge acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
EXPECTED_TECH = frozenset({
    "Meilisearch", "Medusa", "Saleor", "Supabase",
    "Temporal", "OpenFGA", "LangGraph",
})
MAX_BYTES = 100_000


def _blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") +
                        b"\0" + payload).hexdigest()


def _fetch(url: str, timeout: float) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "ENGURU-A04-read-only-provenance/1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final_url = response.geturl()
        if urllib.parse.urlparse(final_url).hostname != "raw.githubusercontent.com":
            raise ValueError("REDIRECTED_SOURCE")
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("SOURCE_TOO_LARGE")
    return payload, final_url


def _valid_path(path: object) -> bool:
    return (isinstance(path, str) and path in
            {"LICENSE", "LICENSE-EE", "LICENSE-MIT",
             "ENTERPRISE-LICENSE.md", "SECURITY.md", ".github/SECURITY.md"})


def _entries(manifest: dict) -> list[dict]:
    if manifest.get("scope") != "A04_PINNED_UPSTREAM_LICENSE_SOURCE_ONLY":
        raise ValueError("SCOPE_CHANGED")
    tech = manifest.get("tech")
    if not isinstance(tech, list) or len(tech) != 7:
        raise ValueError("TECH_SCOPE")
    if {x.get("name") for x in tech if isinstance(x, dict)} != EXPECTED_TECH:
        raise ValueError("TECH_IDENTITIES")
    case_ids, entries, seen = [], [], set()
    for record in tech:
        repo, commit = record.get("repository"), record.get("source_commit_sha")
        if not isinstance(repo, str) or not REPO.fullmatch(repo):
            raise ValueError("REPOSITORY_ID")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            raise ValueError("IMMUTABLE_COMMIT")
        ids = record.get("case_ids")
        if not isinstance(ids, list) or not all(isinstance(cid, str) for cid in ids):
            raise ValueError("CASE_IDS")
        case_ids.extend(ids)
        files = [(record.get("license_path"), record.get("license_git_blob_sha"),
                  "LICENSE")]
        extras = record.get("additional_license_files", [])
        if not isinstance(extras, list):
            raise ValueError("LICENSE_EXTRA")
        files.extend((f.get("path"), f.get("git_blob_sha"), "EXTRA_LICENSE")
                     for f in extras if isinstance(f, dict))
        if len(files) != 1 + len(extras):
            raise ValueError("EXTRA_LICENSE_FORMAT")
        policy = record.get("security_policy")
        if policy is not None:
            if not isinstance(policy, dict):
                raise ValueError("SECURITY_POLICY_FORMAT")
            files.append((policy.get("path"), policy.get("git_blob_sha"), "SECURITY_POLICY"))
        for path, expected, kind in files:
            if not _valid_path(path) or not isinstance(expected, str) or not HEX40.fullmatch(expected):
                raise ValueError("FILE_PIN_INVALID")
            if (repo, commit, path) in seen:
                raise ValueError("DUPLICATE_PIN")
            seen.add((repo, commit, path))
            entries.append({"technology": record["name"], "kind": kind,
                            "repository": repo, "commit": commit, "path": path,
                            "expected_blob_sha1": expected})
    if sorted(case_ids) != [f"{i:02}" for i in range(1, 19)]:
        raise ValueError("CASE_ROSTER")
    if (sum(e["kind"] == "LICENSE" for e in entries) != 7 or
        sum(e["kind"] == "EXTRA_LICENSE" for e in entries) != 3 or
        sum(e["kind"] == "SECURITY_POLICY" for e in entries) != 3):
        raise ValueError("REQUIRED_13_PIN_SET")
    return entries


def verify_upstream(manifest: dict, *, fetch=_fetch, timeout: float = 12) -> dict:
    """Read and hash real remote bytes. Any missing/mismatched pin => HOLD."""
    result = {"schema": "enguru.hym2.a04.live-source-reconciliation/v1",
              "state": "HOLD", "checked": 0, "matched": 0, "expected": 13,
              "files": [], "scope": "UPSTREAM_PUBLIC_FILE_BYTES_ONLY",
              "legal_clearance": "HOLD", "cve": "HOLD", "sbom": "HOLD",
              "customer_deployment": "HOLD_0_OF_18",
              "independent_e5": "HOLD_0_OF_18",
              "a04_official": "HOLD", "verified_finish": "HOLD"}
    try:
        entries = _entries(manifest)
    except (KeyError, TypeError, ValueError) as exc:
        result["reason"] = "HOLD_MANIFEST_" + str(exc)
        return result
    for entry in entries:
        repo, sha, path = entry["repository"], entry["commit"], entry["path"]
        url = "https://raw.githubusercontent.com/" + repo + "/" + sha + "/" + urllib.parse.quote(path)
        item = {k: entry[k] for k in ("technology", "kind", "repository", "commit", "path", "expected_blob_sha1")}
        try:
            raw, actual_url = fetch(url, timeout)
            if urllib.parse.urlparse(actual_url).hostname != "raw.githubusercontent.com":
                raise ValueError("UNTRUSTED_REDIRECT")
            if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
                raise ValueError("INVALID_BYTES")
            item["actual_blob_sha1"] = _blob_sha1(raw)
            item["bytes_sha256"] = hashlib.sha256(raw).hexdigest()
            item["state"] = "PASS_PINNED_BYTES" if item["actual_blob_sha1"] == entry["expected_blob_sha1"] else "HOLD_BLOB_MISMATCH"
        except (OSError, ValueError, TimeoutError) as exc:
            item["state"] = "HOLD_SOURCE_UNAVAILABLE"
            item["error_type"] = type(exc).__name__
        result["checked"] += 1
        result["matched"] += int(item["state"] == "PASS_PINNED_BYTES")
        result["files"].append(item)
    if result["matched"] == result["checked"] == 13:
        result["state"] = "PASS_PINNED_PUBLIC_BYTES_ONLY"
    return result


def _unique_pairs(pairs):
    result = {}
    for k, value in pairs:
        if k in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[k] = value
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--timeout", type=float, default=12)
    args = ap.parse_args()
    try:
        if not 0 < args.timeout <= 30:
            raise ValueError("TIMEOUT_RANGE")
        doc = json.loads(args.manifest.read_text(encoding="utf-8"),
                         object_pairs_hook=_unique_pairs)
        verdict = verify_upstream(doc, timeout=args.timeout)
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        verdict = {"state": "HOLD_MANIFEST_INPUT", "error_type": type(exc).__name__}
    print(json.dumps(verdict, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if verdict["state"] == "PASS_PINNED_PUBLIC_BYTES_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
