#!/usr/bin/env python3
"""ENGÜRÜ IP & MODEL TRUST FLEET GATE™ — repository-level fail-closed enforcement."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path.cwd()
MANIFEST = ROOT / ".enguru" / "ip-model-trust.json"
VALID_CLASSES = {f"T{i}" for i in range(6)}
KNOWN_SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
}
SECRET_NAME = r"(?:api[_-]?key|access[_-]?token|secret|password|passwd|pwd)"
QUOTED_SECRET = re.compile(rf"(?i)\b{SECRET_NAME}\b\s*[:=]\s*([\"'])(?!<SECRET>|REDACTED|CHANGE_ME)([^\"'\n]{{12,}})\1")
DOTENV_SECRET = re.compile(rf"(?im)^\s*(?:export\s+)?[A-Z0-9_]*{SECRET_NAME}[A-Z0-9_]*\s*=\s*(?!<SECRET>|REDACTED|CHANGE_ME|\$\{{)([^\s#]{{12,}})\s*(?:#.*)?$")
SYMBOLIC_ENV_NAME = re.compile(r"^[A-Z][A-Z0-9_]{5,}$")
NON_PROD_GENERIC_DIRS = {"test", "tests", "__tests__", "docs", "examples", "fixtures", "fixture"}
TEST_FILE_MARKERS = (".test.", ".spec.", "_test.", "_spec.")
ENV_EXAMPLE_SUFFIXES = (".example", ".sample", ".template")
SKIP_DIRS = {".git", "node_modules", ".next", "dist", "build", "coverage", ".venv", "venv"}
MAX_BYTES = 1_000_000

def fail(reason: str, evidence=None) -> int:
    print(json.dumps({"gate":"ENGURU_IP_MODEL_TRUST_FLEET_V1_2","state":"BLOCKED","reason":reason,"evidence":evidence or []}, ensure_ascii=False))
    return 3

def is_fixture_surface(path: Path) -> bool:
    name = path.name.lower()
    return any(part.lower() in NON_PROD_GENERIC_DIRS for part in path.parts) or any(marker in name for marker in TEST_FILE_MARKERS)

def is_real_env_file(path: Path) -> bool:
    name = path.name.lower()
    if any(name.endswith(suffix) for suffix in ENV_EXAMPLE_SUFFIXES): return False
    return name == ".env" or name.startswith(".env.") or path.suffix.lower() == ".env"

def secret_hits(path: Path, text: str) -> list[str]:
    hits = [name for name, pattern in KNOWN_SECRET_PATTERNS.items() if pattern.search(text)]
    if not is_fixture_surface(path):
        for match in QUOTED_SECRET.finditer(text):
            value = match.group(2).strip()
            if SYMBOLIC_ENV_NAME.fullmatch(value): continue
            hits.append("hardcoded_quoted_secret")
            break
    if is_real_env_file(path) and DOTENV_SECRET.search(text): hits.append("dotenv_secret_assignment")
    return sorted(set(hits))

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
        for pattern_name in secret_hits(path, text): hits.append({"path":rel,"pattern":pattern_name})
    if hits: return fail("secret_zero_violation", hits[:50])
    print(json.dumps({"gate":"ENGURU_IP_MODEL_TRUST_FLEET_V1_2","state":"PASS","repository":data["repository"],"defaultIpClass":data["defaultIpClass"],"filesScanned":"repository_text_files","secretZero":"PASS"}, ensure_ascii=False))
    return 0

if __name__ == "__main__": sys.exit(main())
