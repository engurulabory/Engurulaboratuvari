#!/usr/bin/env python3
"""Verify the exact ENGURU eight-stage positive-method SHA lock, not product finish."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = Path("governance/enguru-suzgeci")
SOURCE = BASE / "ENGURU_KALICI_CALISMA_DISIPLINI_V1.md"
LOCK = BASE / "ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json"
CANONICAL = BASE / "ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
CANONICAL_LOCK = BASE / "ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json"
PRODUCT = Path("governance/plive/ENGURU_PILIVE_URUN_HEDEFI_V4.md")
STAGES = (
    "Hakikati gör",
    "Değeri koru",
    "Eksikleri ve ihtiyaçları tespit et",
    "Gerekli farkı üret",
    "Eksikleri tamamla",
    "Kanıtla",
    "Sonraki ihtiyaçları belirle",
    "İlerlet",
)
PASS_WORDS = (
    "Eksikleri tamamla",
    "Pozitif Dil Evreni",
    "Kalıcı sabit hedef",
    "GÜVENLİ_DUR",
    "VERIFIED_FINISH",
)
PRODUCT_REQUIREMENTS = (
    "BAŞARISIZ GÖRSEL DENEME",
    "Genel Durum", "Şimdi", "Projeler",
    "Motor", "Çekirdek", "Web", "App", "Agent",
    "G3", "12/12", "4/4", "7/7",
    "U01", "U12", "HOLD",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def verify(root: Path = ROOT) -> dict:
    errors = []
    lock = {}
    try:
        lock = json.loads((root / LOCK).read_bytes())
        source_bytes = (root / SOURCE).read_bytes()
        text = source_bytes.decode("utf-8")
        actual = sha(source_bytes)
        if lock.get("schema") != "enguru.method.eight-stage-positive-discipline-lock/v1":
            errors.append("LOCK_SCHEMA")
        if lock.get("sha256") != actual:
            errors.append("SHA256_SOURCE_DRIFT")
        if lock.get("source_path") != SOURCE.as_posix():
            errors.append("SOURCE_PATH")
        if lock.get("stage_count") != 8 or lock.get("stage_ids") != [f"K{i}" for i in range(1, 9)]:
            errors.append("EIGHT_STAGE_IDS")
        match = re.search(
            r"## Kalıcı sekiz aşama — tam sıralı ifade\n(.*?)\n## Pozitif Dil Evreni",
            text, re.DOTALL,
        )
        rows = re.findall(r"(?m)^([1-8])\. (.+)$", match.group(1)) if match else []
        if rows != [(str(i), STAGES[i-1]) for i in range(1, 9)]:
            errors.append("EIGHT_STAGE_ORDER")
        if not all(word in text for word in PASS_WORDS):
            errors.append("POSITIVE_COMPLETION_SEMANTICS")
        if ("TASARIM 100/100 → TEORİ 100/100 → GITHUB HAZIRLIĞI 5×100/100"
                not in text or "OSİ DEVİR HAZIRLIĞI 100/100" not in text):
            errors.append("FOUR_STAGE_WORKFLOW")
        previous = json.loads((root / CANONICAL_LOCK).read_bytes())
        v3raw = (root / CANONICAL).read_bytes()
        if (sha(v3raw) != previous.get("sha256")
                or sha(v3raw) != lock.get("canonical_v3_sha256")):
            errors.append("CANONICAL_V3_LOCK")
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        entry = (root / BASE / "ENGURU_GITHUB_METHOD_ENTRY_V2.md").read_text(encoding="utf-8")
        if SOURCE.as_posix() not in agents or "ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json" not in agents:
            errors.append("AGENTS_LINK")
        if "ENGURU_KALICI_CALISMA_DISIPLINI_V1.md" not in entry:
            errors.append("METHOD_ENTRY_LINK")
        product = (root / PRODUCT).read_text(encoding="utf-8")
        official_acceptance = (
            "**P02 12/12 özgün iş + 4/4 DoneCheck + 7/7 saha şartı + "
            "G3 gerçek owner/issuer/exact grant/durable writer + Human Threshold + native Verified Finish**"
        )
        if (not all(word in product for word in PRODUCT_REQUIREMENTS)
                or official_acceptance not in product):
            errors.append("PILIVE_TARGET_CONTRACT")
    except (OSError, ValueError, UnicodeError, TypeError, KeyError) as exc:
        errors.append("SOURCE_UNREADABLE:" + type(exc).__name__)
    return {
        "schema": "enguru.eight-stage-positive-lock-verification/v1",
        "status": "PASS_METHOD_TEXT_LOCK" if not errors else "HOLD",
        "source": SOURCE.as_posix(),
        "sourceSha256": lock.get("sha256"),
        "stages": list(STAGES),
        "canonicalV3Integrity": "PASS" if not any("CANONICAL" in x for x in errors) and not errors else "REVIEW_IF_HOLD",
        "errors": errors,
        "realMacUserAcceptance": "HOLD",
        "productOfficialVerifiedFinish": "HOLD",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.root)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS_METHOD_TEXT_LOCK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
