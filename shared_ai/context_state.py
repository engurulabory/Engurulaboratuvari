from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextEnvelope:
    context_id: str
    revision: int
    summary: str
    latest_instruction: str
    verified_facts: tuple[str, ...] = tuple()


def compact_context(
    messages: list[str],
    *,
    max_chars: int = 1200,
    verified_facts: tuple[str, ...] = tuple(),
) -> str:
    cleaned = [str(m).strip() for m in messages if str(m).strip()]
    if not cleaned:
        return ""
    latest = cleaned[-1]
    previous = " | ".join(cleaned[:-1])
    fact_text = " | ".join(verified_facts)
    compacted = " || ".join(
        part
        for part in [
            f"VERIFIED:{fact_text}" if fact_text else "",
            f"PRIOR:{previous}" if previous else "",
            f"LATEST:{latest}",
        ]
        if part
    )
    if len(compacted) <= max_chars:
        return compacted
    keep = max(0, max_chars - len(f"LATEST:{latest}") - 5)
    prior = previous[-keep:] if keep else ""
    compacted = " || ".join(
        part
        for part in [
            f"PRIOR:{prior}" if prior else "",
            f"LATEST:{latest}",
        ]
        if part
    )
    return compacted[-max_chars:]


def apply_steering(
    envelope: ContextEnvelope,
    steering_instruction: str,
) -> ContextEnvelope:
    steering = steering_instruction.strip()
    if not steering:
        return envelope
    return ContextEnvelope(
        context_id=envelope.context_id,
        revision=envelope.revision + 1,
        summary=envelope.summary,
        latest_instruction=steering,
        verified_facts=envelope.verified_facts,
    )
