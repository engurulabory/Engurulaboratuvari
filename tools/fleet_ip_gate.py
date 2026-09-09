#!/usr/bin/env python3
"""ENGÜRÜ IP & MODEL TRUST FLEET GATE™ — repository-level fail-closed enforcement."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path.cwd()
MANIFEST = ROOT / ".enguru" / "ip-model-trust.json"
VALID_CLASSES = {f"T{i}" for i in range(6)}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_secret_assignment": re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password|passwd|pwd)\b\s*[:=]\s*[\"']?(?!<SECRET>|REDACTED|CHANGE_ME|\$\{|process\.env)[A-Za-z0-9_./+\-=]{12,}"),
}
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "coverage", ".venv", "venv"}
MAX_BYTES = 1_000_000

def fail(reason: str, evidence=None) -> int:
    print(json.dumps({"gate":"ENGURU_IP_MODEL_TRUST_FLEET_V1","state":"BLOCKED","reason":reason,"evidence":evidence or []}, ensure_ascii=False))
    return 3

def main() -> int:
    if not MANIFEST.exists(): return fail("missing_manifest")
    try: data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc: return fail("invalid_manifest_json", [str(exc)])
    required = {"schemaVersion","governedBy","repository","defaultIpClass","crownJewelPaths","restrictedPaths","humanThresholdRequiredForT4Cloud"}
    missing = sorted(required - data.keys())
    if missing: return fail("manifest_missing_fields", missing)
    if data["schemaVersion"] != "1.0" or data["governedBy"] != "ENGURU_IP_MODEL_TRUST_GATE_V1": return fail("unknown_governance_contract")
    if data["defaultIpClass"] not in VALID_CLASSES: return fail("invalid_ip_class")
    if not isinstance(data["crownJewelPaths"], list) or not isinstance(data["restrictedPaths"], list): return fail("invalid_path_lists")
    hits=[]
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts): continue
        try:
            if path.stat().st_size > MAX_BYTES: continue
            text=path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError): continue
        rel=str(path.relative_to(ROOT))
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text): hits.append({"path":rel,"pattern":name})
    if hits: return fail("secret_zero_violation", hits[:50])
    print(json.dumps({"gate":"ENGURU_IP_MODEL_TRUST_FLEET_V1","state":"PASS","repository":data["repository"],"defaultIpClass":data["defaultIpClass"],"filesScanned":"repository_text_files","secretZero":"PASS"}, ensure_ascii=False))
    return 0

if __name__ == "__main__": sys.exit(main())
