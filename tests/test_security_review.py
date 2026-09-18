import unittest

from shared_ai.security_review import (
    SecurityFinding,
    SecurityReviewEngine,
    ThreatAssessment,
    ThreatModelContext,
)


def full_assessments():
    items = [
        ThreatAssessment(category, "PASS", (f"evidence:{category}",))
        for category in ("S", "T", "R", "I", "D", "E")
    ]
    items.extend(
        ThreatAssessment(f"OWASP:{control}", "PASS", (f"evidence:{control}",))
        for control in (
            "AUTHENTICATION",
            "AUTHORIZATION",
            "INPUT_VALIDATION",
            "INJECTION",
            "SECRETS",
            "DATA_EXPOSURE",
            "LOGGING",
        )
    )
    return tuple(items)


def context(**overrides):
    values = {
        "source_trusted": True,
        "changed_paths": ("shared_ai/runtime.py",),
        "trust_boundaries": ("caller -> shared-ai",),
    }
    values.update(overrides)
    return ThreatModelContext(**values)


class SecurityReviewEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = SecurityReviewEngine()

    def test_untrusted_source_holds(self):
        result = self.engine.assess(
            context(source_trusted=False),
            threat_assessments=full_assessments(),
            findings=(),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "untrusted_review_source")

    def test_missing_trust_boundary_holds(self):
        result = self.engine.assess(
            context(trust_boundaries=tuple()),
            threat_assessments=full_assessments(),
            findings=(),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "missing_trust_boundary")

    def test_incomplete_stride_coverage_holds(self):
        assessments = tuple(x for x in full_assessments() if x.category != "E")
        result = self.engine.assess(
            context(),
            threat_assessments=assessments,
            findings=(),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "incomplete_stride_coverage")

    def test_incomplete_owasp_coverage_holds(self):
        assessments = tuple(
            x for x in full_assessments() if x.category != "OWASP:AUTHORIZATION"
        )
        result = self.engine.assess(
            context(),
            threat_assessments=assessments,
            findings=(),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "incomplete_owasp_coverage")

    def test_complete_threat_model_passes(self):
        result = self.engine.assess(
            context(),
            threat_assessments=full_assessments(),
            findings=(),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(set(result.stride_coverage), {"S", "T", "R", "I", "D", "E"})

    def test_evidence_free_semantic_finding_is_suppressed(self):
        result = self.engine.assess(
            context(),
            threat_assessments=full_assessments(),
            findings=(
                SecurityFinding(
                    "maybe",
                    "possible issue",
                    tuple(),
                    0.99,
                    severity="HIGH",
                ),
            ),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(len(result.suppressed_findings), 1)

    def test_high_unmitigated_semantic_finding_holds(self):
        result = self.engine.assess(
            context(),
            threat_assessments=full_assessments(),
            findings=(
                SecurityFinding(
                    "authz-bypass",
                    "caller can cross tenant boundary",
                    ("runtime.py@abc:L1-L20",),
                    0.99,
                    severity="CRITICAL",
                    mitigated=False,
                    framework="OWASP",
                    control="AUTHORIZATION",
                ),
            ),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "security_findings_require_resolution")

    def test_mitigated_high_finding_can_pass(self):
        result = self.engine.assess(
            context(),
            threat_assessments=full_assessments(),
            findings=(
                SecurityFinding(
                    "authz-guard",
                    "cross tenant path is bounded",
                    ("runtime.py@abc:L1-L20",),
                    0.99,
                    severity="HIGH",
                    mitigated=True,
                    framework="OWASP",
                    control="AUTHORIZATION",
                ),
            ),
        )
        self.assertEqual(result.state, "PASS")


if __name__ == "__main__":
    unittest.main()
