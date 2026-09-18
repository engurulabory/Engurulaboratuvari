from __future__ import annotations

from collections.abc import Iterable


CAPABILITY_ALIASES = {
    "image": "vision",
    "images": "vision",
    "visual": "vision",
    "document": "file",
    "documents": "file",
    "files": "file",
    "speech": "audio",
    "voice": "audio",
}

CANONICAL_CAPABILITIES = frozenset({
    "text",
    "vision",
    "file",
    "audio",
    "tool_calling",
    "structured_output",
    "reasoning",
    "streaming",
    "long_context",
})


def normalize_capabilities(values: Iterable[str]) -> frozenset[str]:
    normalized = []
    for value in values:
        raw = str(value).strip().lower()
        normalized.append(CAPABILITY_ALIASES.get(raw, raw))
    return frozenset(normalized)
