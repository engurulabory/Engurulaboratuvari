from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


HISTORY_SENSITIVE = {"REGRESSION", "BEHAVIOR_CHANGE", "AUTHORITY_CHANGE"}


@dataclass(frozen=True)
class ReviewFinding:
    code: str
    claim: str
    evidence: tuple[str, ...]
    confidence: float
    severity: str = "MEDIUM"
    category: str = "GENERAL"
    history_ref: str | None = None


@dataclass(frozen=True)
class OutsideVoiceReport:
    producer_identity: str
    reviewer_identity: str
    state: str
    evidence: tuple[str, ...] = tuple()
    disagreements: tuple[str, ...] = tuple()


@dataclass(frozen=True)
class QualityReviewResult:
    state: str
    reason: str
    accepted: tuple[ReviewFinding, ...]
    suppressed: tuple[ReviewFinding, ...]
    outside_voice_state: str


class QualityReviewEngine:
    """Evidence-bound PR review contract for Quality & Red Team."""

    def __init__(self, *, min_confidence: float = 0.80) -> None:
        self.min_confidence = min_confidence

    @staticmethod
    def _dedupe(findings: Iterable[ReviewFinding]) -> tuple[ReviewFinding, ...]:
        best: dict[tuple[str, str], ReviewFinding] = {}
        for finding in findings:
            key = (finding.code, finding.claim.strip())
            current = best.get(key)
            if current is None or finding.confidence > current.confidence:
                best[key] = finding
        return tuple(best.values())

    @staticmethod
    def _outside_voice_state(report: OutsideVoiceReport | None, required: bool) -> tuple[str, str | None]:
        if report is None:
            return ("MISSING", "outside_voice_required") if required else ("NOT_REQUIRED", None)
        if not report.reviewer_identity.strip() or report.reviewer_identity == report.producer_identity:
            return "INVALID", "outside_voice_not_independent"
        if report.state not in {"PASS", "HOLD"}:
            return "INVALID", "outside_voice_invalid_state"
        if report.state == "HOLD" or report.disagreements:
            return "HOLD", "outside_voice_disagreement"
        if not report.evidence:
            return "HOLD", "outside_voice_missing_evidence"
        return "PASS", None

    def assess(
        self,
        findings: Iterable[ReviewFinding],
        *,
        changed_paths: tuple[str, ...],
        history_evidence: tuple[str, ...],
        outside_voice: OutsideVoiceReport | None = None,
        outside_voice_required: bool = False,
    ) -> QualityReviewResult:
        if not changed_paths:
            return QualityReviewResult("HOLD", "missing_diff_scope", tuple(), tuple(), "NOT_RUN")

        ov_state, ov_reason = self._outside_voice_state(outside_voice, outside_voice_required)
        if ov_reason is not None:
            return QualityReviewResult("HOLD", ov_reason, tuple(), tuple(), ov_state)

        accepted: list[ReviewFinding] = []
        suppressed: list[ReviewFinding] = []

        for finding in self._dedupe(findings):
            has_evidence = bool(finding.evidence)
            confidence_ok = 0.0 <= finding.confidence <= 1.0 and finding.confidence >= self.min_confidence
            history_ok = (
                finding.category.upper() not in HISTORY_SENSITIVE
                or bool(finding.history_ref)
                or bool(history_evidence)
            )
            if not has_evidence or not confidence_ok or not history_ok:
                suppressed.append(finding)
                continue
            accepted.append(finding)

        blockers = tuple(
            finding for finding in accepted if finding.severity.upper() in {"HIGH", "CRITICAL"}
        )
        if blockers:
            return QualityReviewResult(
                "HOLD",
                "review_findings_require_resolution",
                tuple(accepted),
                tuple(suppressed),
                ov_state,
            )

        return QualityReviewResult(
            "PASS",
            "quality_review_pass",
            tuple(accepted),
            tuple(suppressed),
            ov_state,
        )
