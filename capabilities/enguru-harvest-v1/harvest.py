"""ENGÜRÜ harvest gate: stdlib-only, conservative evidence decisions."""
import hashlib
import json
from pathlib import Path

LIBRARIES = ("skills", "advanced_prompts", "proven_sources", "data_knowledge", "engineering_recipes", "evidence")
STATES = ("CANDIDATE", "TESTED", "PROVEN", "ADOPTED")
PROOF = ("source_sha256", "license", "security_review", "test_receipt", "real_task_receipt", "independent_review", "human_authority")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def evaluate(record: dict) -> dict:
    """Never execute third-party content; only classify asserted evidence."""
    if not isinstance(record, dict):
        return {"state": "HOLD", "reason": "INVALID_RECORD"}
    required = ("id", "library", "source_url", "source_sha256", "license", "security_review", "mandatory_paid_api")
    if any(not record.get(k) and record.get(k) != 0 for k in required):
        return {"state": "HOLD", "reason": "MISSING_REQUIRED_SOURCE_OR_REVIEW"}
    if record["library"] not in LIBRARIES:
        return {"state": "HOLD", "reason": "UNKNOWN_LIBRARY"}
    digest = record["source_sha256"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        return {"state": "HOLD", "reason": "INVALID_SHA256"}
    if record["mandatory_paid_api"] != 0:
        return {"state": "HOLD", "reason": "PAID_DEPENDENCY"}
    if record["license"] in ("unknown", "unverified", "proprietary-restricted"):
        return {"state": "HOLD", "reason": "LICENSE_REVIEW"}
    if record["security_review"] != "PASS":
        return {"state": "HOLD", "reason": "SECURITY_REVIEW"}
    if record.get("test_receipt") is None:
        return {"state": "CANDIDATE", "reason": "AWAITING_REAL_TEST"}
    if record.get("real_task_receipt") is None:
        return {"state": "TESTED", "reason": "AWAITING_REAL_TASK"}
    if record.get("independent_review") != "PASS":
        return {"state": "TESTED", "reason": "INDEPENDENT_REVIEW_REQUIRED"}
    if record.get("human_authority") != "PASS":
        return {"state": "PROVEN", "reason": "HUMAN_THRESHOLD"}
    return {"state": "ADOPTED", "reason": "EVIDENCE_GATED"}

def verify_bytes(record: dict, source: bytes) -> dict:
    if not isinstance(record, dict) or sha256(source) != record.get("source_sha256"):
        return {"state": "HOLD", "reason": "SOURCE_HASH_MISMATCH"}
    return evaluate(record)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: harvest.py manifest.json")
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(data), ensure_ascii=False, sort_keys=True))
