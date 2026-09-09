#!/usr/bin/env python3
"""ENGÜRÜ IP & MODEL TRUST GATE™ — fail-closed enforcement CLI."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "governance" / "ip-model-trust" / "MODEL_REGISTRY.json"
CLASS_RANK = {f"T{i}": i for i in range(6)}

SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|password|passwd|pwd)\b\s*[:=]\s*[\"']?(?!<SECRET>|REDACTED|CHANGE_ME)[A-Za-z0-9_./+\-=]{12,}"
    ),
}


def load_registry() -> dict:
    with REGISTRY.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def scan_text(text: str) -> list[str]:
    return sorted(name for name, pattern in SECRET_PATTERNS.items() if pattern.search(text))


def decision(provider: str, ip_class: str, text: str = "", human_approved: bool = False) -> dict:
    registry = load_registry()
    now = datetime.now(timezone.utc).isoformat()
    base = {
        "gate": "ENGÜRÜ IP & MODEL TRUST GATE™",
        "schema_version": "1.0",
        "evaluated_at": now,
        "provider": provider,
        "ip_class": ip_class,
        "human_approved": human_approved,
    }

    if ip_class not in CLASS_RANK:
        return {**base, "state": "BLOCKED", "reason": "UNKNOWN_IP_CLASS", "next_action": "Use T0-T5 classification."}

    findings = scan_text(text)
    if findings:
        return {
            **base,
            "state": "BLOCKED",
            "reason": "SECRET_ZERO_RULE",
            "findings": findings,
            "next_action": "Remove or replace secrets with placeholders, then evaluate again.",
        }

    if ip_class == "T5":
        return {
            **base,
            "state": "BLOCKED",
            "reason": "RESTRICTED_CLASS",
            "next_action": "Keep restricted content outside general-purpose model context.",
        }

    profile = registry["providers"].get(provider)
    if profile is None:
        return {
            **base,
            "state": registry["default_policy"]["unknown_provider"],
            "reason": "UNKNOWN_PROVIDER",
            "next_action": "Register and verify the provider before access.",
        }

    max_rank = CLASS_RANK[profile["max_ip_class"]]
    requested_rank = CLASS_RANK[ip_class]
    needs_human = ip_class in profile.get("human_threshold_classes", [])

    if requested_rank > max_rank:
        state = "HOLD" if human_approved and ip_class in {"T3", "T4"} else "BLOCKED"
        return {
            **base,
            "state": state,
            "reason": "IP_CLASS_EXCEEDS_PROVIDER_LIMIT",
            "provider_policy_status": profile["policy_status"],
            "max_ip_class": profile["max_ip_class"],
            "next_action": "Use local-first execution or reduce context through fragmentation and sanitization.",
        }

    if needs_human and not human_approved:
        return {
            **base,
            "state": "HOLD",
            "reason": "HUMAN_THRESHOLD_REQUIRED",
            "provider_policy_status": profile["policy_status"],
            "max_ip_class": profile["max_ip_class"],
            "next_action": "Obtain an explicit Human Threshold™ decision for this asset and scope.",
        }

    return {
        **base,
        "state": "PASS",
        "reason": "WITHIN_VERIFIED_POLICY_LIMIT",
        "provider_policy_status": profile["policy_status"],
        "max_ip_class": profile["max_ip_class"],
        "next_action": "Proceed with minimum necessary context and retain the decision envelope as evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="ENGÜRÜ IP & MODEL TRUST GATE™")
    parser.add_argument("--provider", required=True)
    parser.add_argument("--ip-class", required=True, dest="ip_class")
    parser.add_argument("--text", default="")
    parser.add_argument("--file", type=Path)
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    text = args.text
    if args.file:
        text += "\n" + args.file.read_text(encoding="utf-8", errors="replace")

    envelope = decision(args.provider, args.ip_class, text, args.human_approved)
    rendered = json.dumps(envelope, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return {"PASS": 0, "HOLD": 2, "BLOCKED": 3}[envelope["state"]]


if __name__ == "__main__":
    sys.exit(main())
