from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Sequence


PASS = "PASS"
HOLD = "HOLD"


@dataclass(frozen=True)
class ControlResult:
    state: str
    reason: str
    evidence: tuple[str, ...] = tuple()


@dataclass(frozen=True)
class CapabilityRequirement:
    name: str
    required_level: str = "SUPPORTED"


class HarnessCapabilityMatrix:
    """Fail-closed capability truth for a concrete execution harness."""

    VALID_LEVELS = {"SUPPORTED", "DEGRADED", "UNSUPPORTED", "HUMAN_THRESHOLD"}

    def assess(
        self,
        required: Sequence[CapabilityRequirement],
        observed: Mapping[str, str],
    ) -> ControlResult:
        evidence: list[str] = []
        for item in required:
            level = observed.get(item.name, "UNSUPPORTED").upper()
            if level not in self.VALID_LEVELS:
                return ControlResult(HOLD, f"invalid_capability_level:{item.name}")
            evidence.append(f"{item.name}={level}")
            if level == "UNSUPPORTED":
                return ControlResult(HOLD, f"unsupported_capability:{item.name}", tuple(evidence))
            if level == "HUMAN_THRESHOLD":
                return ControlResult(HOLD, f"human_threshold:{item.name}", tuple(evidence))
            if item.required_level.upper() == "SUPPORTED" and level != "SUPPORTED":
                return ControlResult(HOLD, f"degraded_capability:{item.name}", tuple(evidence))
        return ControlResult(PASS, "capability_matrix_pass", tuple(evidence))


class PreflightDryRunGate:
    """Requires declared scope, dry-run evidence and Human Threshold where needed."""

    def assess(
        self,
        *,
        scope: tuple[str, ...],
        mutations: tuple[str, ...],
        dry_run_evidence: tuple[str, ...],
        human_threshold_required: bool = False,
        human_approved: bool = False,
    ) -> ControlResult:
        if not scope:
            return ControlResult(HOLD, "missing_scope")
        if mutations and not dry_run_evidence:
            return ControlResult(HOLD, "dry_run_required")
        if human_threshold_required and not human_approved:
            return ControlResult(HOLD, "human_threshold_required", dry_run_evidence)
        return ControlResult(PASS, "preflight_pass", dry_run_evidence)


class EvidenceGatedSkillLearning:
    """Repeated wins may propose a skill; promotion remains evidence and authority gated."""

    def assess(
        self,
        *,
        observation_count: int,
        evidence: tuple[str, ...],
        benchmark_pass: bool,
        human_threshold_required: bool = True,
        human_approved: bool = False,
    ) -> ControlResult:
        if observation_count < 3:
            return ControlResult(HOLD, "insufficient_repeated_observation")
        if not evidence:
            return ControlResult(HOLD, "missing_skill_evidence")
        if not benchmark_pass:
            return ControlResult(HOLD, "benchmark_required", evidence)
        if human_threshold_required and not human_approved:
            return ControlResult(HOLD, "human_threshold_required", evidence)
        return ControlResult(PASS, "skill_promotion_pass", evidence)


class SelfDiagnosticDoctor:
    """Aggregates deterministic subsystem checks without manufacturing PASS."""

    def assess(self, checks: Mapping[str, ControlResult]) -> ControlResult:
        if not checks:
            return ControlResult(HOLD, "no_diagnostic_checks")
        evidence: list[str] = []
        for name in sorted(checks):
            result = checks[name]
            evidence.append(f"{name}:{result.state}:{result.reason}")
            if result.state != PASS:
                return ControlResult(HOLD, f"doctor_hold:{name}", tuple(evidence))
        return ControlResult(PASS, "doctor_pass", tuple(evidence))


@dataclass(frozen=True)
class SurfaceFinding:
    path: str
    code: str
    severity: str
    evidence: str


class AgentSurfaceScanner:
    """Deterministic semantic pre-scan for prompts, hooks, MCP/config and permissions."""

    SENSITIVE_PATH_MARKERS = (
        ".github/",
        "hooks/",
        "mcp",
        "prompt",
        "agent",
        "permission",
        "config",
    )

    PATTERNS = (
        ("PLAINTEXT_SECRET", "CRITICAL", re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*['\"][^'\"]{8,}")),
        ("SHELL_PIPE_REMOTE", "HIGH", re.compile(r"(?i)(curl|wget).{0,120}\|\s*(bash|sh)")),
        ("UNBOUNDED_SHELL", "HIGH", re.compile(r"(?i)(shell\s*=\s*true|subprocess\..*shell\s*=\s*True)")),
        ("PERMISSION_WILDCARD", "HIGH", re.compile(r"(?i)(permissions?|allow)\s*[:=]\s*['\"]?\*")),
        ("PROMPT_AUTHORITY_BYPASS", "HIGH", re.compile(r"(?i)(ignore|bypass).{0,80}(approval|authority|human threshold|security)")),
    )

    def scan(self, artifacts: Mapping[str, str]) -> tuple[SurfaceFinding, ...]:
        findings: list[SurfaceFinding] = []
        for path, text in artifacts.items():
            lower_path = path.lower()
            if not any(marker in lower_path for marker in self.SENSITIVE_PATH_MARKERS):
                continue
            for code, severity, pattern in self.PATTERNS:
                match = pattern.search(text)
                if match:
                    snippet = match.group(0)[:160]
                    findings.append(SurfaceFinding(path, code, severity, snippet))
        return tuple(findings)

    def assess(self, artifacts: Mapping[str, str]) -> ControlResult:
        findings = self.scan(artifacts)
        if findings:
            evidence = tuple(f"{f.path}:{f.code}:{f.severity}" for f in findings)
            return ControlResult(HOLD, "agent_surface_findings_require_review", evidence)
        return ControlResult(PASS, "agent_surface_scan_pass")


def budget_context(
    *,
    latest_instruction: str,
    verified_facts: tuple[str, ...],
    prior_summary: str = "",
    max_chars: int = 1600,
) -> str:
    """Keep verified truth and latest instruction ahead of disposable prior context."""
    latest = latest_instruction.strip()
    facts = tuple(x.strip() for x in verified_facts if x.strip())
    if not latest:
        return ""

    fixed_parts = []
    if facts:
        fixed_parts.append("VERIFIED:" + " | ".join(facts))
    fixed_parts.append("LATEST:" + latest)
    fixed = " || ".join(fixed_parts)
    if len(fixed) >= max_chars:
        return fixed[:max_chars]

    prior = prior_summary.strip()
    if not prior:
        return fixed
    remaining = max_chars - len(fixed) - len(" || PRIOR:")
    if remaining <= 0:
        return fixed
    return fixed + " || PRIOR:" + prior[-remaining:]
