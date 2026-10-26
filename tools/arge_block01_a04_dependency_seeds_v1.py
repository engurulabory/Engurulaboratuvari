#!/usr/bin/env python3
"""HYM2 A04: verify immutable upstream dependency *source bytes* (not SBOM/CVE).

Read-only source verification. Every verified SHA-256 is about the downloaded
manifest bytes; it cannot certify installed customer packages or vulnerability
status. Fail closed on a missing, changed, too-large or redirected source.
"""
import argparse
import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

HEX40 = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
LIMIT = 1_250_000
ORIGINAL = {
    "Meilisearch": ("Cargo.lock", "LOCK_FILE"),
    "Medusa": ("yarn.lock", "LOCK_FILE"),
    "Saleor": ("uv.lock", "LOCK_FILE"),
    "Supabase": ("package.json", "BUILD_MANIFEST_ONLY_MULTI_PACKAGE_SCOPE"),
    "Temporal": ("go.mod", "MODULE_MANIFEST_ONLY"),
    "OpenFGA": ("go.mod", "MODULE_MANIFEST_ONLY"),
    "LangGraph": ("libs/langgraph/pyproject.toml", "MODULE_MANIFEST_ONLY"),
}
POLICY = {
    "SOURCE_PINNED_SECURITY_POLICY": 3,
    "STANDARD_SECURITY_POLICY_PATHS_NOT_FOUND_AT_PIN": 4,
}


def blob_sha1(body):
    return hashlib.sha1(b"blob " + str(len(body)).encode("ascii") +
                        b"\x00" + body).hexdigest()


def fetch_remote(url, timeout):
    request = urllib.request.Request(
        url, headers={"User-Agent": "ENGURU-A04-pinned-dependency-source/1"})
    with urllib.request.urlopen(request, timeout=timeout) as reply:
        redirect = reply.geturl()
        if urllib.parse.urlparse(redirect).hostname != "raw.githubusercontent.com":
            raise ValueError("UNTRUSTED_REDIRECT")
        data = reply.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("SOURCE_SIZE_LIMIT")
    return data, redirect


def entries(manifest, upstream):
    if (manifest.get("schema") != "enguru.hym2.a04.dependency-source-seeds/v1"
        or manifest.get("research_scope") != "A04_7_UPSTREAM_TECHNOLOGIES_18_ORIGINAL_CASES"):
        raise ValueError("SCOPE")
    actual = manifest.get("sources")
    if not isinstance(actual, list) or len(actual) != 7:
        raise ValueError("SEVEN_SOURCES_REQUIRED")
    expected_upstream = upstream.get("tech")
    if (not isinstance(expected_upstream, list) or
        len(expected_upstream) != 7 or
        {x.get("name") for x in expected_upstream} != set(ORIGINAL)):
        raise ValueError("UPSTREAM_SCOPE")
    original = {x["name"]: x for x in expected_upstream}
    names, policies, out = set(), {}, []
    for item in actual:
        if not isinstance(item, dict):
            raise ValueError("SOURCE_RECORD")
        n = item.get("technology")
        if n not in ORIGINAL or n in names:
            raise ValueError("SOURCE_IDENTITY")
        names.add(n)
        up = original[n]
        repo, sha, path, dig = (item.get("repository"), item.get("source_commit_sha"),
                                item.get("dependency_path"), item.get("dependency_git_blob_sha1"))
        if (not isinstance(repo, str) or not REPO.fullmatch(repo)
            or not isinstance(sha, str) or not HEX40.fullmatch(sha)
            or not isinstance(dig, str) or not HEX40.fullmatch(dig)):
            raise ValueError("SOURCE_IDENTITY_OR_DIGEST")
        if repo != up["repository"] or sha != up["source_commit_sha"]:
            raise ValueError("UNPINNED_UPSTREAM_SOURCE")
        if (path, item.get("coverage")) != ORIGINAL[n]:
            raise ValueError("UNPINNED_DEPENDENCY_MANIFEST")
        policy = item.get("security_policy_status")
        if policy not in POLICY:
            raise ValueError("UNKNOWN_POLICY_PROVENANCE")
        if policy == "SOURCE_PINNED_SECURITY_POLICY" and not up.get("security_policy"):
            raise ValueError("MISSING_ACTUAL_SECURITY_FILE")
        if policy != "SOURCE_PINNED_SECURITY_POLICY" and up.get("security_policy"):
            raise ValueError("OMITTED_PINNED_SECURITY_FILE")
        policies[policy] = policies.get(policy, 0) + 1
        out.append((n, repo, sha, path, dig, item["coverage"]))
    if names != set(ORIGINAL) or policies != POLICY:
        raise ValueError("POLICY_AND_ROSTER_CHANGED")
    exp = manifest.get("expected", {})
    if not isinstance(exp, dict) or any(
        exp.get(k) != v for k,v in {
            "technologies": 7, "dependency_seeds": 7,
            "root_or_module_lockfiles": 3, "non_lock_manifests": 4,
            "source_pinned_standard_security_policies": 3,
            "standard_path_policy_gaps": 4}.items()
    ):
        raise ValueError("COUNT_REWRITTEN")
    return out


def verify(manifest, upstream, fetch=fetch_remote, timeout=15.0):
    result = {
        "state": "HOLD", "expected": 7, "checked": 0, "matched": 0,
        "security_policies_with_pinned_files": 3,
        "standard_path_policy_gaps": 4, "sources": [],
        "source_proof_level": "PINNED_MANIFEST_BYTES_ONLY",
        "complete_sbom": "HOLD",
        "exact_version_cve_review": "HOLD",
        "legal_clearance": "HOLD",
        "kasifi_runtime_scope": "HOLD",
        "independent_e5": "HOLD_0_OF_18",
        "a04_official": "HOLD", "verified_finish": "HOLD",
    }
    try:
        all_entries = entries(manifest, upstream)
    except (TypeError, ValueError, KeyError) as err:
        result["reason"] = "HOLD_SOURCE_SCHEMA_" + str(err)
        return result
    for name,repo,sha,path,dig,coverage in all_entries:
        uri = "https://raw.githubusercontent.com/" + repo + "/" + sha + "/" + urllib.parse.quote(path)
        row = {"technology": name, "repository": repo, "commit": sha,
               "dependency_path": path, "coverage": coverage,
               "expected_git_blob_sha1": dig}
        try:
            body, final = fetch(uri, timeout)
            if urllib.parse.urlparse(final).hostname != "raw.githubusercontent.com":
                raise ValueError("UNTRUSTED_REDIRECT")
            if not isinstance(body, bytes) or not body or len(body) > LIMIT:
                raise ValueError("BAD_SOURCE_BYTES")
            row["observed_git_blob_sha1"] = blob_sha1(body)
            row["observed_file_sha256"] = hashlib.sha256(body).hexdigest()
            row["state"] = ("PASS_SOURCE_BYTES" if row["observed_git_blob_sha1"] == dig
                            else "HOLD_BLOB_MISMATCH")
        except (OSError, ValueError, TimeoutError) as err:
            row["state"] = "HOLD_SOURCE_UNAVAILABLE"
            row["error_type"] = type(err).__name__
        result["sources"].append(row)
        result["checked"] += 1
        result["matched"] += int(row["state"] == "PASS_SOURCE_BYTES")
    if result["checked"] == result["matched"] == 7:
        result["state"] = "PASS_7_PINNED_DEPENDENCY_SEEDS_ONLY"
    return result


def _no_duplicate_keys(pairs):
    obj = {}
    for k,v in pairs:
        if k in obj:
            raise ValueError("DUPLICATE_JSON_KEY")
        obj[k] = v
    return obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--upstream", type=Path, required=True)
    args = p.parse_args()
    try:
        m = json.loads(args.manifest.read_text(encoding="utf-8"),
                       object_pairs_hook=_no_duplicate_keys)
        u = json.loads(args.upstream.read_text(encoding="utf-8"),
                       object_pairs_hook=_no_duplicate_keys)
        result = verify(m, u)
    except (OSError, TypeError, ValueError, UnicodeError) as err:
        result = {"state": "HOLD_INPUT", "error_type": type(err).__name__}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["state"] == "PASS_7_PINNED_DEPENDENCY_SEEDS_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
