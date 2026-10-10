#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCHEMA = "enguru.language.pre-send-linter/v1"

PROHIBITION_PATTERNS = [
    re.compile(r"^\s*(do not|don't|never)\b", re.I),
    re.compile(r"^\s*(yapma|yapmayın|etme|etmeyin|kullanma|kullanmayın|varsayma|varsaymayın)\b", re.I),
    re.compile(r"\b(varsayılmayacak|yapılmayacak|edilmeyecek|kullanılmayacak)\b", re.I),
]
VERDICT_RE = re.compile(r"\b(?:STATE|VERDICT)\s*[:=]\s*(PASS|HOLD|BLOCKED)\b", re.I)
CLOSURE_RE = re.compile(r"\b(PASS|DONE|FINISHED|VERIFIED(?:\s+FINAL)?|PRODUCTION[-_ ]?READY|100/100)\b", re.I)
OBSERVABLE_EVIDENCE_RE = re.compile(r"\b(test(?:s)?|CI|SHA|receipt|proof|verified by|doğruland[ıi]|kanıt|gözlem|exit code|status check)\b", re.I)
EVIDENCE_CONTENT_RE = re.compile(r"(?mi)^\s*EVIDENCE\s*[:—=-]\s*\S.+$")
PLACEHOLDER_RE = re.compile(r"\b(TODO_EVIDENCE|TBD_EVIDENCE|PLACEHOLDER_EVIDENCE|FAKE_EVIDENCE)\b", re.I)

STATE_PREFIX_RE = re.compile(r"^\s*(STATE|EVIDENCE|OBSERVATION|FACT)\s*[:—=-]", re.I)
GOVERNED_FIELD_RE = re.compile(r"(?mi)^\s*(STATE|CLAIM|EVIDENCE|NEXT(?:_| )ACTION)\s*[:—=-]")


def finding(rule: str, severity: str, line: int, message: str, next_action: str) -> dict:
    return {
        "rule": rule,
        "severity": severity,
        "line": line,
        "message": message,
        "next_action": next_action,
    }


def has_evidence_signal(text: str) -> bool:
    return bool(EVIDENCE_CONTENT_RE.search(text) or OBSERVABLE_EVIDENCE_RE.search(text))


def lint(text: str, strict: bool = False) -> dict:
    lines = text.splitlines()
    findings: list[dict] = []
    checked = ["L01", "L03", "L04", "L06", "L10", "L11"]

    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        if not STATE_PREFIX_RE.search(line):
            for pattern in PROHIBITION_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        finding(
                            "L01",
                            "MATERIAL",
                            idx,
                            "Prohibition-first instruction detected.",
                            "Express the valid state or correct action directly.",
                        )
                    )
                    break
        if PLACEHOLDER_RE.search(line):
            findings.append(
                finding(
                    "L11",
                    "CRITICAL",
                    idx,
                    "Placeholder evidence marker detected.",
                    "Replace the marker with actual observable Evidence or classify the state HOLD.",
                )
            )

    governed_fields = [m.group(1).upper().replace(" ", "_") for m in GOVERNED_FIELD_RE.finditer(text)]
    if len(set(governed_fields)) >= 2:
        required = {
            "STATE": bool(re.search(r"(?mi)^\s*STATE\s*[:—=-]", text)),
            "CLAIM": bool(re.search(r"(?mi)^\s*CLAIM\s*[:—=-]", text)),
            "EVIDENCE": bool(re.search(r"(?mi)^\s*EVIDENCE\s*[:—=-]", text)),
        }
        missing = [name for name, ok in required.items() if not ok]
        if missing:
            findings.append(
                finding(
                    "L03",
                    "MATERIAL",
                    0,
                    "Governed block is missing required field(s): " + ", ".join(missing),
                    "Keep STATE, CLAIM and EVIDENCE distinct.",
                )
            )

    for match in CLOSURE_RE.finditer(text):
        start = max(0, match.start() - 350)
        end = min(len(text), match.end() + 350)
        window = text[start:end]
        if not has_evidence_signal(window):
            line = text.count("\n", 0, match.start()) + 1
            findings.append(
                finding(
                    "L04",
                    "CRITICAL" if strict else "MATERIAL",
                    line,
                    f"Closure term '{match.group(1)}' has no nearby Evidence signal.",
                    "Add scope-matched verifiable Evidence or change the state to HOLD.",
                )
            )

    verdict_values = [m.group(1).upper() for m in VERDICT_RE.finditer(text)]
    malformed = re.findall(r"(?mi)^\s*(?:STATE|VERDICT)\s*[:=]\s*([A-Z_]+)", text)
    for value in malformed:
        if value not in {"PASS", "HOLD", "BLOCKED"}:
            findings.append(
                finding(
                    "L06",
                    "MATERIAL",
                    0,
                    f"Non-canonical verdict value '{value}'.",
                    "Use PASS, HOLD or BLOCKED for governed verdict state.",
                )
            )

    if strict and "PASS" in verdict_values and not has_evidence_signal(text):
        findings.append(
            finding(
                "L04",
                "CRITICAL",
                0,
                "Strict-mode PASS requires explicit Evidence semantics.",
                "Provide verifiable Evidence before PASS.",
            )
        )

    dedup = []
    seen = set()
    for item in findings:
        key = (item["rule"], item["line"], item["message"])
        if key not in seen:
            seen.add(key)
            dedup.append(item)

    return {
        "schema": SCHEMA,
        "state": "HOLD" if dedup else "PASS",
        "finding_count": len(dedup),
        "findings": dedup,
        "checked_rules": checked,
        "semantic_review_required": bool(strict),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ENGÜRÜ Language Governance Pre-Send Linter")
    parser.add_argument("path", nargs="?", help="UTF-8 text file. Omit to read stdin.")
    parser.add_argument("--strict", action="store_true", help="Use canonical/execution package strict mode.")
    args = parser.parse_args()

    try:
        if args.path:
            text = Path(args.path).read_text(encoding="utf-8")
        else:
            text = sys.stdin.read()
    except Exception as exc:
        print(json.dumps({"schema": SCHEMA, "state": "HOLD", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 30

    if not text.strip():
        print(json.dumps({"schema": SCHEMA, "state": "HOLD", "error": "empty_input"}, ensure_ascii=False, indent=2))
        return 30

    result = lint(text, strict=args.strict)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["state"] == "PASS" else 20


if __name__ == "__main__":
    raise SystemExit(main())
