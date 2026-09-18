from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VerificationReport:
    state: str
    reason: str
    unsupported_claims: tuple[str, ...] = tuple()
    contradictions: tuple[str, ...] = tuple()
    citations: tuple[str, ...] = tuple()


class IndependentVerifier:
    """Deterministic verifier kept separate from generation/provider routing."""

    @staticmethod
    def _claims(output: Any) -> tuple[str, ...]:
        if isinstance(output, dict):
            claims = output.get("claims", ())
            if isinstance(claims, list):
                return tuple(str(x) for x in claims)
        return tuple()

    @staticmethod
    def _citations(output: Any) -> tuple[str, ...]:
        if isinstance(output, dict):
            citations = output.get("citations", ())
            if isinstance(citations, list):
                return tuple(str(x) for x in citations)
        return tuple()

    def verify(
        self,
        *,
        output: Any,
        verification_profile: str,
        provenance: tuple[str, ...],
        known_truths: tuple[str, ...] = tuple(),
    ) -> VerificationReport:
        if output is None or (isinstance(output, str) and not output.strip()):
            return VerificationReport("HOLD", "empty_output")

        profile = verification_profile.upper()
        claims = self._claims(output)
        citations = self._citations(output)

        if profile == "STRUCTURED" and not isinstance(output, (dict, list)):
            return VerificationReport("HOLD", "structured_output_required")

        if profile == "GROUNDED":
            if not provenance:
                return VerificationReport("HOLD", "missing_provenance")
            if claims:
                unsupported = tuple(
                    claim for claim in claims if claim not in set(known_truths)
                )
                if unsupported:
                    return VerificationReport(
                        "HOLD",
                        "unsupported_claim",
                        unsupported_claims=unsupported,
                        citations=citations,
                    )
            if citations and any(c not in set(provenance) for c in citations):
                return VerificationReport(
                    "HOLD",
                    "unknown_citation",
                    citations=citations,
                )

        if isinstance(output, dict):
            contradictions = output.get("contradictions", ())
            if isinstance(contradictions, list) and contradictions:
                return VerificationReport(
                    "HOLD",
                    "contradiction_detected",
                    contradictions=tuple(str(x) for x in contradictions),
                    citations=citations,
                )

        return VerificationReport(
            "PASS",
            "verification_pass",
            citations=citations or provenance,
        )
