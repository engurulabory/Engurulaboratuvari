"""A05/A06: untrusted, read-only intake of genuine customer deployment and E5 files.

The caller supplies actual local files. SHA-256 verifies bytes against the
supplied digest, NEVER the issuer, signer, deployment, customer or verifier.
Official acceptance is owned exclusively by canonical DoneCheck/Human Threshold.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from tools.arge_block01_k12_batch_v1 import ORIGINAL_V19_IDENTITIES, V19_SHA

SCHEMA = "enguru.arge.block01.a05-a06-external-evidence/v1"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
MAX_FILE_BYTES = 25 * 1024 * 1024
CANDIDATE = "FILES_HASH_MATCH_REQUIRE_EXTERNAL_SIGNATURE_AUTHORITY"

def _date(value):
    if not isinstance(value, str):
        return False
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return t.tzinfo is not None and t.utcoffset() is not None
    except ValueError:
        return False

def file_pin(root, name, expected, *, kind="file"):
    """Verify bytes without following filesystem symlinks or leaving evidence root."""
    if not isinstance(name, str) or not name or not isinstance(expected, str) or not SHA256.fullmatch(expected):
        return "HOLD_FILE_NAME_OR_SHA256"
    p = Path(name)
    if p.is_absolute() or any(x in ("..", ".") for x in p.parts):
        return "HOLD_FILE_PATH_SCOPE"
    try:
        if root.is_symlink() or not root.is_dir():
            return "HOLD_ARTIFACT_ROOT"
        scope = root.resolve(strict=True)
        path = scope / p
        if any(x.is_symlink() for x in (path, *path.parents) if x != scope and scope in x.parents):
            return "HOLD_SYMLINK"
        target = path.resolve(strict=True)
        target.relative_to(scope)
        if not target.is_file() or target.stat().st_size > MAX_FILE_BYTES:
            return "HOLD_FILE_TYPE_OR_SIZE"
        h = hashlib.sha256()
        with target.open("rb") as stream:
            while block := stream.read(65536):
                h.update(block)
        if h.hexdigest() != expected:
            return "HOLD_FILE_SHA256_MISMATCH"
        if kind == "sbom":
            document = json.loads(target.read_text(encoding="utf-8"))
            if not isinstance(document, dict):
                return "HOLD_SBOM_SCHEMA"
            if not (document.get("bomFormat") == "CycloneDX" and document.get("specVersion")
                    or str(document.get("spdxVersion", "")).startswith("SPDX-")):
                return "HOLD_SBOM_FORMAT"
        return "BYTE_SHA256_MATCH_UNTRUSTED_SOURCE"
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        return "HOLD_FILE_READ_OR_SCHEMA"

def _bound_json(root, relative, required):
    """Parse an already hash-pinned JSON file and compare exact case bindings.

    A digest supplied by a packet is not an authenticated record. Binding only
    prevents accidental or adversarial swapping of genuine-looking artifacts.
    """
    try:
        doc = json.loads((Path(root) / relative).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, UnicodeError):
        return False
    return isinstance(doc, dict) and all(doc.get(k) == v for k, v in required.items())

def audit_case(case, evidence, root):
    cid = case["case_id"]
    result = {"case_id": cid, "customer": case["customer"], "technology": case["technology"],
              "a05": "HOLD_MISSING_DEPLOYMENT_EVIDENCE",
              "a06": "HOLD_MISSING_INDEPENDENT_E5_EVIDENCE"}
    if not isinstance(evidence, dict) or any(evidence.get(k) != case[k] for k in ("case_id", "customer", "technology")):
        result["a05"] = "HOLD_IDENTITY_DRIFT"
        result["a06"] = "HOLD_IDENTITY_DRIFT"
        return result

    deploy = evidence.get("deployment")
    if isinstance(deploy, dict):
        if not all(isinstance(deploy.get(k), str) and deploy[k].strip()
                   for k in ("release", "edition", "customer_owner_id")):
            result["a05"] = "HOLD_DEPLOYMENT_METADATA"
        elif not isinstance(deploy.get("source_commit"), str) or not COMMIT.fullmatch(deploy["source_commit"]):
            result["a05"] = "HOLD_SOURCE_COMMIT_FORMAT"
        else:
            fields = (("deployed_manifest", "manifest_sha256", "file"),
                      ("customer_sbom", "sbom_sha256", "sbom"),
                      ("customer_assertion", "customer_assertion_sha256", "file"),
                      ("customer_signature", "customer_signature_sha256", "file"))
            checks = [file_pin(root, deploy.get(name), deploy.get(digest), kind=kind)
                      for name, digest, kind in fields]
            if any(x != "BYTE_SHA256_MATCH_UNTRUSTED_SOURCE" for x in checks):
                result["a05"] = next(x for x in checks if x != "BYTE_SHA256_MATCH_UNTRUSTED_SOURCE")
            else:
                manifest_expected = {k: evidence[k] for k in ("case_id", "customer", "technology")}
                manifest_expected.update({k: deploy[k] for k in ("release", "edition", "source_commit")})
                owner_expected = {"case_id": cid, "customer": case["customer"],
                                  "owner_id": deploy["customer_owner_id"],
                                  "manifest_sha256": deploy["manifest_sha256"]}
                if (_bound_json(root, deploy["deployed_manifest"], manifest_expected)
                        and _bound_json(root, deploy["customer_assertion"], owner_expected)):
                    result["a05"] = CANDIDATE
                else:
                    result["a05"] = "HOLD_DEPLOYMENT_DOCUMENT_BINDING"

    e5 = evidence.get("e5")
    if isinstance(e5, dict):
        verifier = e5.get("verifier_identity")
        org = e5.get("verifier_organization")
        if not all(isinstance(x, str) and x.strip() for x in (verifier, org)):
            result["a06"] = "HOLD_VERIFIER_IDENTITY"
        elif org.strip().casefold() in (case["customer"].casefold(), case["technology"].casefold()):
            result["a06"] = "HOLD_DECLARED_VERIFIER_IS_CUSTOMER_OR_VENDOR"
        elif not _date(e5.get("observed_at")):
            result["a06"] = "HOLD_OBSERVATION_TIMESTAMP"
        else:
            fields = (("report", "report_sha256"),
                      ("verifier_assertion", "verifier_assertion_sha256"),
                      ("verifier_signature", "verifier_signature_sha256"))
            checks = [file_pin(root, e5.get(name), e5.get(digest)) for name, digest in fields]
            if any(x != "BYTE_SHA256_MATCH_UNTRUSTED_SOURCE" for x in checks):
                result["a06"] = next(x for x in checks if x != "BYTE_SHA256_MATCH_UNTRUSTED_SOURCE")
            elif result["a05"] != CANDIDATE:
                result["a06"] = "HOLD_DEPLOYMENT_EVIDENCE_DEPENDENCY"
            else:
                report_expected = {"case_id": cid, "customer": case["customer"],
                                   "technology": case["technology"],
                                   "observed_manifest_sha256": deploy["manifest_sha256"],
                                   "verifier_identity": verifier}
                assertion_expected = {"case_id": cid,
                                      "report_sha256": e5["report_sha256"],
                                      "verifier_identity": verifier}
                if (_bound_json(root, e5["report"], report_expected) and
                        _bound_json(root, e5["verifier_assertion"], assertion_expected)):
                    result["a06"] = CANDIDATE
                else:
                    result["a06"] = "HOLD_E5_DOCUMENT_BINDING"
    return result

def audit_packet(catalog, packet, root):
    """Never produce PASS for an untrusted packet, even when all 18 files match."""
    safe = {"state": "HOLD_INPUT_OR_SCOPE", "a05_official_verified": 0,
            "a06_independent_e5_verified": 0, "official_block01_pass": "0/9"}
    if not isinstance(catalog, dict) or not isinstance(packet, dict):
        return safe
    baseline = catalog.get("baseline", {})
    entries = catalog.get("cases")
    if not isinstance(baseline, dict) or baseline.get("sha256") != V19_SHA or baseline.get("rows") != 234:
        return dict(safe, state="HOLD_ORIGINAL_V19_BASELINE")
    if not isinstance(entries, list) or len(entries) != 18 or any(not isinstance(x, dict) for x in entries):
        return safe
    identities = tuple((c.get("case_id"), c.get("customer"), c.get("technology")) for c in entries)
    if identities != ORIGINAL_V19_IDENTITIES or packet.get("schema") != SCHEMA or packet.get("baseline_sha256") != V19_SHA:
        return dict(safe, state="HOLD_IDENTITY_OR_SCHEMA")
    incoming = packet.get("cases")
    if not isinstance(incoming, list) or len(incoming) != 18 or any(not isinstance(c, dict) for c in incoming):
        return dict(safe, state="HOLD_18_CASE_DELIVERY")
    ids = [x.get("case_id") for x in incoming]
    if any(not isinstance(x, str) for x in ids) or sorted(ids) != [x[0] for x in ORIGINAL_V19_IDENTITIES]:
        return dict(safe, state="HOLD_DUPLICATE_OR_UNKNOWN_CASE")
    by_id = {x["case_id"]: x for x in incoming}
    results = [audit_case(c, by_id[c["case_id"]], Path(root)) for c in entries]
    count_a05 = sum(c["a05"] == CANDIDATE for c in results)
    count_a06 = sum(c["a06"] == CANDIDATE for c in results)
    return {**safe, "state": "HOLD_EXTERNAL_SIGNATURE_AND_AUTHORITY",
            "cases": results, "case_count": 18,
            "a05_files_hash_matched_untrusted": count_a05,
            "a06_files_hash_matched_untrusted": count_a06,
            "required_next": "Verify canonical owner/issuer trust pins, cryptographic signatures, reviewer independence and observed customer deployment externally before submitting DoneCheck."}

def main():
    p = argparse.ArgumentParser(description="A05/A06 external evidence file intake, read-only")
    p.add_argument("--catalog", type=Path, required=True)
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--artifacts", type=Path, required=True)
    args = p.parse_args()
    try:
        r = audit_packet(json.loads(args.catalog.read_text(encoding="utf-8")),
                         json.loads(args.packet.read_text(encoding="utf-8")), args.artifacts)
    except (OSError, ValueError, UnicodeError) as exc:
        r = {"state": "HOLD_UNREADABLE_INPUT", "exception": type(exc).__name__,
             "a05_official_verified": 0, "a06_independent_e5_verified": 0}
    print(json.dumps(r, ensure_ascii=False, sort_keys=True))
    return 2  # A receipt or evidence intake is not an approval authority.

if __name__ == "__main__":
    raise SystemExit(main())
