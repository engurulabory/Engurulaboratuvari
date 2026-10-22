#!/usr/bin/env python3
"""Verify the user-approved universal ENGÜRÜ V3 source is identical to SHA-256 lock.

Read-only. This verifies document bytes and Git blob identity, not acceptance
of an ENGÜRÜ product or independent human reviewer approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SHA1 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PATH = "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"


def verify(root: Path = ROOT, lock_path: Path | None = None) -> dict:
    path = lock_path if lock_path is not None else root / LOCK.relative_to(ROOT)
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("schema") != "enguru.universal.verifiable-finish.contract-lock/v1":
        raise ValueError("HOLD_SCHEMA")
    if record.get("version") != "V3" or record.get("canonical_path") != EXPECTED_PATH:
        raise ValueError("HOLD_SOURCE_SCOPE")
    expected = record.get("sha256")
    git_blob = record.get("git_blob_sha1")
    if not isinstance(expected, str) or not SHA256.fullmatch(expected):
        raise ValueError("HOLD_SHA256_FORMAT")
    if not isinstance(git_blob, str) or not SHA1.fullmatch(git_blob):
        raise ValueError("HOLD_GIT_BLOB_FORMAT")
    doc_path = root / EXPECTED_PATH
    if doc_path.is_symlink():
        raise ValueError("HOLD_SYMLINK_SOURCE")
    data = doc_path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError("HOLD_SHA256_SOURCE_DRIFT")
    actual_blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
    if actual_blob != git_blob:
        raise ValueError("HOLD_GIT_BLOB_MISMATCH")
    text = data.decode("utf-8")
    for required in (
        "## 1. KALICI SABİT HEDEF",
        "## 2. HAKİKATİ VE SABİT KABUL MATRİSİNİ BELİRLE",
        "## 5. ZORUNLU EKSİK TAMAMLAMA VE ÖLÇÜLEBİLİR DURMA KARARI",
        "## 6. BAĞIMSIZ DOĞRULAMA VE KANIT OTORİTESİ",
        "## 8. OTURUMLAR ARASI KANIT SÜREKLİLİĞİ",
        "K8=NIHAI_KABUL",
        "VERIFIED_FINISH → BITTI_DUR",
    ):
        if required not in text:
            raise ValueError("HOLD_V3_REQUIRED_SECTION")
    return {
        "state": "PASS_V3_SOURCE_SHA256_LOCK_READ_ONLY",
        "source_sha256": actual,
        "source_git_blob": actual_blob,
        "theoretical_design": record.get("design", {}).get("assessment"),
        "official_field_acceptance": "NOT_ASSERTED",
        "source_writes": 0,
    }


def main() -> int:
    try:
        print(json.dumps(verify(), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError, UnicodeError) as error:
        print(f"STATE=HOLD_UNIVERSAL_V3_LOCK {error}", file=sys.stderr)
        return 50


if __name__ == "__main__":
    sys.exit(main())
