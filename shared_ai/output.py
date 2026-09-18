from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_RESPONSE_LENGTHS = {"AUTO", "CONCISE", "STANDARD", "DETAILED"}
VALID_RESPONSE_STRUCTURES = {"PLAIN", "GOVERNED", "STRUCTURED"}


@dataclass(frozen=True)
class OutputProfile:
    language: str = "AUTO"
    length: str = "AUTO"
    structure: str = "PLAIN"
    include_technical_evidence: bool = False


class GovernedFormatter:
    def profile(self, request: Any) -> OutputProfile:
        return OutputProfile(
            language=str(getattr(request, "response_language", "AUTO")).upper(),
            length=str(getattr(request, "response_length", "AUTO")).upper(),
            structure=str(getattr(request, "response_structure", "PLAIN")).upper(),
            include_technical_evidence=bool(
                getattr(request, "include_technical_evidence", False)
            ),
        )

    def instruction(self, request: Any) -> str:
        profile = self.profile(request)
        parts = []
        if profile.language != "AUTO":
            parts.append(f"RESPONSE_LANGUAGE:{profile.language}")
        if profile.length != "AUTO":
            parts.append(f"RESPONSE_LENGTH:{profile.length}")
        if profile.structure != "PLAIN":
            parts.append(f"RESPONSE_STRUCTURE:{profile.structure}")
        return "\n".join(parts)

    @staticmethod
    def _typed_claims(output: Any) -> dict[str, list[Any]]:
        if not isinstance(output, dict):
            return {
                "facts": [],
                "inferences": [],
                "proposals": [],
                "uncertainties": [],
            }
        return {
            "facts": list(output.get("facts", []))
            if isinstance(output.get("facts", []), list)
            else [],
            "inferences": list(output.get("inferences", []))
            if isinstance(output.get("inferences", []), list)
            else [],
            "proposals": list(output.get("proposals", []))
            if isinstance(output.get("proposals", []), list)
            else [],
            "uncertainties": list(output.get("uncertainties", []))
            if isinstance(output.get("uncertainties", []), list)
            else [],
        }

    @staticmethod
    def _answer(output: Any) -> Any:
        if isinstance(output, dict) and "answer" in output:
            return output["answer"]
        return output

    def format(
        self,
        *,
        request: Any,
        output: Any,
        state: str,
        evidence_refs: tuple[str, ...] = tuple(),
        technical_evidence: dict[str, Any] | None = None,
    ) -> Any:
        profile = self.profile(request)

        # Backward-compatible fast path.
        if (
            profile.structure == "PLAIN"
            and profile.language == "AUTO"
            and profile.length == "AUTO"
            and not profile.include_technical_evidence
        ):
            return output

        typed = self._typed_claims(output)
        answer = self._answer(output)

        if profile.structure == "GOVERNED":
            payload: dict[str, Any] = {
                "state": state,
                "claim": answer,
                "evidence": list(evidence_refs),
                "next_action": (
                    output.get("next_action")
                    if isinstance(output, dict)
                    else None
                ),
                "facts": typed["facts"],
                "inferences": typed["inferences"],
                "proposals": typed["proposals"],
                "uncertainties": typed["uncertainties"],
                "language": profile.language,
                "length": profile.length,
            }
        else:
            # STRUCTURED, or PLAIN with explicit output controls.
            payload = {
                "answer": answer,
                "facts": typed["facts"],
                "inferences": typed["inferences"],
                "proposals": typed["proposals"],
                "uncertainties": typed["uncertainties"],
                "language": profile.language,
                "length": profile.length,
                "structure": profile.structure,
            }

        if profile.include_technical_evidence:
            payload["technical_evidence"] = technical_evidence or {}

        return payload
