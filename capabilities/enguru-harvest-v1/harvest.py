"""ENGÜRÜ source candidate classification. External claims never grant adoption.

Only metadata filtering and verified source-byte matching are provided here.
Independent issuer/reviewer and Human Threshold remain canonical authority.
"""
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

LIBRARIES = ("skills", "advanced_prompts", "proven_sources", "data_knowledge", "engineering_recipes", "evidence")
STATES = ("CANDIDATE", "TESTED", "PROVEN", "ADOPTED")

def sha256(data: bytes) -> str:
    if not isinstance(data, bytes):
        raise TypeError("source bytes required")
    return hashlib.sha256(data).hexdigest()

def _valid_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)

def _valid_https_url(value):
    if not isinstance(value, str) or any(c.isspace() for c in value):
        return False
    try:
        url = urlsplit(value)
        return url.scheme == "https" and bool(url.hostname) and not url.username and not url.password and not url.fragment
    except ValueError:
        return False

def evaluate(record: dict) -> dict:
    """Return candidate or HOLD, never a self-declared PROVEN/ADOPTED."""
    if not isinstance(record, dict):
        return {"state": "HOLD", "reason": "INVALID_RECORD"}
    required = ("id", "library", "source_url", "source_sha256", "license", "security_review", "mandatory_paid_api")
    if any(key not in record for key in required):
        return {"state": "HOLD", "reason": "MISSING_REQUIRED_SOURCE_OR_REVIEW"}
    if not isinstance(record["id"], str) or not record["id"].strip():
        return {"state": "HOLD", "reason": "INVALID_ID"}
    if not isinstance(record["library"], str) or record["library"] not in LIBRARIES:
        return {"state": "HOLD", "reason": "UNKNOWN_LIBRARY"}
    if not _valid_https_url(record["source_url"]):
        return {"state": "HOLD", "reason": "INVALID_SOURCE_URL"}
    if not _valid_digest(record["source_sha256"]):
        return {"state": "HOLD", "reason": "INVALID_SHA256"}
    if type(record["mandatory_paid_api"]) is not int or record["mandatory_paid_api"] != 0:
        return {"state": "HOLD", "reason": "PAID_OR_UNKNOWN_DEPENDENCY"}
    license_name = record["license"]
    if not isinstance(license_name, str) or not license_name.strip() or license_name.lower() in ("unknown", "unverified", "proprietary-restricted"):
        return {"state": "HOLD", "reason": "LICENSE_REVIEW"}
    if record["security_review"] != "PASS":
        return {"state": "HOLD", "reason": "SECURITY_REVIEW"}
    # Claims such as test_receipt, independent_review or human_authority from
    # an untrusted manifest cannot authenticate themselves.
    return {"state": "CANDIDATE", "reason": "CLAIMS_PRESENT; BYTE_AND_AUTHORITY_EVIDENCE_REQUIRED"}

def verify_bytes(record: dict, source: bytes) -> dict:
    if not isinstance(record, dict) or not isinstance(source, bytes):
        return {"state": "HOLD", "reason": "SOURCE_BYTES_REQUIRED"}
    if sha256(source) != record.get("source_sha256"):
        return {"state": "HOLD", "reason": "SOURCE_HASH_MISMATCH"}
    return evaluate(record)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: harvest.py manifest.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(data), ensure_ascii=False, sort_keys=True))
