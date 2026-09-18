from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


STRIDE = {"S", "T", "R", "I", "D", "E"}


@dataclass(frozen=True)
class ThreatAssessment:
    category: str
    state: str
    evidence: tuple[str, ...]
    note: str = ""


@dataclass(frozen=True)
class SecurityFinding:
    code: str
    claim: str
    evidence: tuple[str, ...]
    confidence: float
    severity: str = "MEDIUM"
    mitigated: bool = False
    framework: str = "SEMANTIC"
    control: str | None = None


@dataclass(frozen=True)
class ThreatModelContext:
    source_trusted: bool
    changed_paths: tuple[str, ...]
    trust_boundaries: tuple[str, ...]
    stride_required: tuple[str, ...] = ("S", "T", "R", "I", "D", "E")
    owasp_required: tuple[str, ...] = (
        "AUTHENTICATION",
        "AUTHORIZATION",
        "INPUT_VALIDATION",
        "INJECTION",
        "SECRETS",
        "DATA_EXPOSURE",
        "LOGGING",
    )


@dataclass(frozen=True)
class SecurityReviewResult:
    state: str
    reason: str
    accepted_findings: tuple[SecurityFinding, ...]
    suppressed_findings: tuple[SecurityFinding, ...]
    stride_coverage: tuple[str, ...]
    owasp_coverage: tuple[str, ...]


class SecurityReviewEngine:
    """Semantic security review contract for Security & Authority."""

    def __init__(self, *, min_confidence: float = 0.80) -> None:
        self.min_confidence = min_confidence

    def assess(
        self,
        context: ThreatModelContext,
        *,
        threat_assessments: Iterable[ThreatAssessment],
        findings: Iterable[SecurityFinding],
    ) -> SecurityReviewResult:
        if not context.source_trusted:
            return SecurityReviewResult(
                "HOLD", "untrusted_review_source", tuple(), tuple(), tuple(), tuple()
            )
        if not context.changed_paths:
            return SecurityReviewResult(
                "HOLD", "missing_diff_scope", tuple(), tuple(), tuple(), tuple()
            )
        if (context.stride_required or context.owasp_required) and not context.trust_boundaries:
            return SecurityReviewResult(
                "HOLD", "missing_trust_boundary", tuple(), tuple(), tuple(), tuple()
            )

        assessments = tuple(threat_assessments)
        stride_coverage: set[str] = set()
        owasp_coverage: set[str] = set()

        for item in assessments:
            category = item.category.upper()
            if category in STRIDE and item.state == "PASS" and item.evidence:
                stride_coverage.add(category)
            if category.startswith("OWASP:") and item.state == "PASS" and item.evidence:
                owasp_coverage.add(category.split(":", 1)[1])
            if item.state == "HOLD":
                return SecurityReviewResult(
                    "HOLD",
                    "threat_assessment_hold",
                    tuple(),
                    tuple(),
                    tuple(sorted(stride_coverage)),
                    tuple(sorted(owasp_coverage)),
                )

        required_stride = {x.upper() for x in context.stride_required}
        missing_stride = required_stride - stride_coverage
        if missing_stride:
            return SecurityReviewResult(
                "HOLD",
                "incomplete_stride_coverage",
                tuple(),
                tuple(),
                tuple(sorted(stride_coverage)),
                tuple(sorted(owasp_coverage)),
            )

        required_owasp = {x.upper() for x in context.owasp_required}
        missing_owasp = required_owasp - owasp_coverage
        if missing_owasp:
            return SecurityReviewResult(
                "HOLD",
                "incomplete_owasp_coverage",
                tuple(),
                tuple(),
                tuple(sorted(stride_coverage)),
                tuple(sorted(owasp_coverage)),
            )

        accepted: list[SecurityFinding] = []
        suppressed: list[SecurityFinding] = []
        for finding in findings:
            evidence_ok = bool(finding.evidence)
            confidence_ok = 0.0 <= finding.confidence <= 1.0 and finding.confidence >= self.min_confidence
            if not evidence_ok or not confidence_ok:
                suppressed.append(finding)
                continue
            accepted.append(finding)

        blockers = tuple(
            item
            for item in accepted
            if item.severity.upper() in {"HIGH", "CRITICAL"} and not item.mitigated
        )
        if blockers:
            return SecurityReviewResult(
                "HOLD",
                "security_findings_require_resolution",
                tuple(accepted),
                tuple(suppressed),
                tuple(sorted(stride_coverage)),
                tuple(sorted(owasp_coverage)),
            )

        return SecurityReviewResult(
            "PASS",
            "security_review_pass",
            tuple(accepted),
            tuple(suppressed),
            tuple(sorted(stride_coverage)),
            tuple(sorted(owasp_coverage)),
        )
