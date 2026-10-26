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
VERDICT_RE = re.compile(
    r"\b(?:[A-Z][A-Z0-9_]*_STATE|STATE|VERDICT)\s*[:=—-]\s*(PASS|HOLD|BLOCKED|FAIL)\b",
    re.I,
)
SCOPED_STATE_RE = re.compile(
    r"(?mi)^\s*([A-Z][A-Z0-9_]+_STATE)\s*[:=—-]\s*(PASS|HOLD|BLOCKED|FAIL)\b"
)
BARE_STATE_RE = re.compile(
    r"(?mi)^\s*(STATE|VERDICT)\s*[:=—-]\s*(PASS|HOLD|BLOCKED|FAIL)\b"
)
NEXT_ACTION_CONTENT_RE = re.compile(
    r"(?mi)^\s*NEXT(?:_| )ACTION\s*[:=—-]\s*\S.+$"
)
UNLOCK_CONDITION_RE = re.compile(
    r"(?mi)^\s*UNLOCK(?:_| )CONDITION\s*[:=—-]\s*\S.+$"
)
UNBLOCK_CONDITION_RE = re.compile(
    r"(?mi)^\s*UNBLOCK(?:_| )CONDITION\s*[:=—-]\s*\S.+$"
)

VERIFIED_FINISH_ASSERTION_RE = re.compile(
    r"(?mi)^\s*(?:"
    r"VERIFIED_FINISH_STATE\s*[:=—-]\s*PASS\b"
    r"|CLAIM\s*[:=—-].*\bVerified Finish\b.*"
    r"\b(?:complete|completed|ready|locked|finished|PASS|VERIFIED FINAL)\b"
    r")"
)

CLOSURE_CONTRACT_SIGNAL_RE = re.compile(
    r"(?mi)^\s*(?:"
    r"CLOSURE(?:_| )CONTRACT"
    r"|CLOSURE(?:_| )CRITERIA"
    r"|ACCEPTANCE(?:_| )CONTRACT"
    r")\s*[:=—-]\s*\S.+$"
)

SUZGEC_SEQUENCE_TRIGGER_RE = re.compile(
    r"(?mi)^\s*SUZGEC(?:_| )SEQUENCE\s*[:=—-]\s*ENFORCED\s*$"
)

SUZGEC_SEQUENCE_FIELDS = (
    ("PRESERVED_VALUE", re.compile(
        r"(?mi)^\s*PRESERVED(?:_| )VALUE\s*[:=—-]\s*\S.+$"
    )),
    ("NECESSARY_DIFFERENCE", re.compile(
        r"(?mi)^\s*NECESSARY(?:_| )DIFFERENCE\s*[:=—-]\s*\S.+$"
    )),
    ("REUSE_EXECUTION", re.compile(
        r"(?mi)^\s*REUSE(?:_| )EXECUTION\s*[:=—-]\s*\S.+$"
    )),
    ("EVIDENCE", re.compile(
        r"(?mi)^\s*EVIDENCE\s*[:=—-]\s*\S.+$"
    )),
    ("CLOSURE", re.compile(
        r"(?mi)^\s*CLOSURE\s*[:=—-]\s*\S.+$"
    )),
)


CLOSURE_RE = re.compile(r"\b(PASS|DONE|FINISHED|VERIFIED(?:\s+FINAL)?|PRODUCTION[-_ ]?READY|100/100)\b", re.I)
OBSERVABLE_EVIDENCE_RE = re.compile(r"\b(test(?:s)?|CI|SHA|receipt|proof|verified by|doğruland[ıi]|kanıt|gözlem|exit code|status check)\b", re.I)
EVIDENCE_CONTENT_RE = re.compile(r"(?mi)^\s*EVIDENCE\s*[:—=-]\s*\S.+$")
PLACEHOLDER_RE = re.compile(r"\b(TODO_EVIDENCE|TBD_EVIDENCE|PLACEHOLDER_EVIDENCE|FAKE_EVIDENCE)\b", re.I)

STATE_PREFIX_RE = re.compile(r"^\s*(STATE|EVIDENCE|OBSERVATION|FACT)\s*[:—=-]", re.I)
GOVERNED_FIELD_RE = re.compile(r"(?mi)^\s*(STATE|CLAIM|EVIDENCE|NEXT(?:_| )ACTION)\s*[:—=-]")
PRESERVATION_FIRST_RE = re.compile(r"\bbozmadan\b", re.I)


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
    checked = ["L01", "L03", "L04", "L06", "L10", "L11", "L13", "L14", "L15", "L16", "L17", "L18"]
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

        if PRESERVATION_FIRST_RE.search(line):
            findings.append(
                finding(
                    "L13",
                    "MATERIAL",
                    idx,
                    "Risk-first wording 'bozmadan' detected.",
                    "Express the preservation-first action with 'koruyarak'.",
                )
            )

    governed_fields = [m.group(1).upper().replace(" ", "_") for m in GOVERNED_FIELD_RE.finditer(text)]
    if len(set(governed_fields)) >= 2:
        required = {
            "STATE": bool(
                re.search(
                    r"(?mi)^\s*(?:[A-Z][A-Z0-9_]*_STATE|STATE|VERDICT)\s*[:—=-]",
                    text,
                )
            ),
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
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end == -1:
            line_end = len(text)
        line_text = text[line_start:line_end]

        term = match.group(1).upper()

        # "verified" may describe an observed fact/barrier in natural STATE
        # prose. Treat it as closure only when it is used as a governed
        # verdict/value rather than as an adjective inside the STATE text.
        if term.startswith("VERIFIED"):
            natural_state = bool(STATE_PREFIX_RE.search(line_text))
            governed_verified_value = bool(
                re.search(
                    r"(?i)^\s*(?:STATE|VERDICT|[A-Z][A-Z0-9_]*_STATE)"
                    r"\s*[:=—-]\s*VERIFIED(?:\s+FINAL)?\s*$",
                    line_text,
                )
            )
            if natural_state and not governed_verified_value:
                continue

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

    hold_present = any(value == "HOLD" for value in verdict_values)
    if hold_present and not (
        NEXT_ACTION_CONTENT_RE.search(text)
        or UNLOCK_CONDITION_RE.search(text)
    ):
        findings.append(
            finding(
                "L14",
                "MATERIAL",
                0,
                "Governed HOLD has no concrete unlock condition or next action.",
                "State the smallest NEXT_ACTION or observable UNLOCK_CONDITION that opens progression.",
            )
        )

    blocked_present = any(value == "BLOCKED" for value in verdict_values)
    if blocked_present and not (
        NEXT_ACTION_CONTENT_RE.search(text)
        or UNBLOCK_CONDITION_RE.search(text)
    ):
        findings.append(
            finding(
                "L16",
                "MATERIAL",
                0,
                "Governed BLOCKED has no concrete removal path.",
                "State the smallest NEXT_ACTION or observable UNBLOCK_CONDITION that can remove the barrier.",
            )
        )

    verified_finish_asserted = bool(
        VERIFIED_FINISH_ASSERTION_RE.search(text)
    )
    if verified_finish_asserted and not CLOSURE_CONTRACT_SIGNAL_RE.search(text):
        findings.append(
            finding(
                "L17",
                "MATERIAL",
                0,
                "Verified Finish has no explicit resolved closure contract or criteria.",
                "Identify the active CLOSURE_CONTRACT, CLOSURE_CRITERIA or ACCEPTANCE_CONTRACT governing final closure.",
            )
        )

    if strict and SUZGEC_SEQUENCE_TRIGGER_RE.search(text):
        matches = []
        missing = []

        for name, pattern in SUZGEC_SEQUENCE_FIELDS:
            found = pattern.search(text)
            if found is None:
                missing.append(name)
            else:
                matches.append(found.start())

        ordered = (
            not missing
            and matches == sorted(matches)
        )

        if missing or not ordered:
            findings.append(
                finding(
                    "L18",
                    "MATERIAL",
                    0,
                    "Governed decision sequence is incomplete or out of order.",
                    "Restore PRESERVED_VALUE → NECESSARY_DIFFERENCE → "
                    "REUSE_EXECUTION → EVIDENCE → CLOSURE.",
                )
            )

    scoped_states = list(SCOPED_STATE_RE.finditer(text))
    bare_states = list(BARE_STATE_RE.finditer(text))

    material_multi_state = len(verdict_values) > 1

    if strict and material_multi_state and bare_states and not scoped_states:
        findings.append(
            finding(
                "L15",
                "MATERIAL",
                0,
                "Multiple governed judgments are present without explicit judgment scope.",
                "Name each material judgment by object or acceptance scope.",
            )
        )
    malformed = re.findall(
        r"(?m)^\s*(?:[A-Z][A-Z0-9_]*_STATE|STATE|VERDICT)\s*[:=]\s*([A-Z_]+)",
        text,
    )
    for value in malformed:
        if value not in {"PASS", "HOLD", "BLOCKED", "FAIL"}:
            findings.append(
                finding(
                    "L06",
                    "MATERIAL",
                    0,
                    f"Non-canonical verdict value '{value}'.",
                    "Use PASS, HOLD, BLOCKED or FAIL for governed verdict state.",
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
