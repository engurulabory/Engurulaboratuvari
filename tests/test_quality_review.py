import unittest

from shared_ai.quality_review import (
    OutsideVoiceReport,
    QualityReviewEngine,
    ReviewFinding,
)


class QualityReviewEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = QualityReviewEngine(min_confidence=0.80)
        self.paths = ("shared_ai/runtime.py",)

    def test_low_confidence_finding_is_suppressed(self):
        result = self.engine.assess(
            [ReviewFinding("maybe", "possible issue", ("diff@abc",), 0.40)],
            changed_paths=self.paths,
            history_evidence=tuple(),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(len(result.accepted), 0)
        self.assertEqual(len(result.suppressed), 1)

    def test_evidence_free_finding_is_suppressed(self):
        result = self.engine.assess(
            [ReviewFinding("noise", "unsupported concern", tuple(), 0.99)],
            changed_paths=self.paths,
            history_evidence=tuple(),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(len(result.suppressed), 1)

    def test_high_confidence_critical_finding_blocks_pass(self):
        result = self.engine.assess(
            [
                ReviewFinding(
                    "authority-bypass",
                    "human threshold removed",
                    ("shared_ai/runtime.py@abc:L10-L20",),
                    0.98,
                    severity="CRITICAL",
                    category="AUTHORITY_CHANGE",
                    history_ref="commit:previous-authority-fix",
                )
            ],
            changed_paths=self.paths,
            history_evidence=("commit:previous-authority-fix",),
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "review_findings_require_resolution")

    def test_history_sensitive_finding_without_history_is_suppressed(self):
        result = self.engine.assess(
            [
                ReviewFinding(
                    "regression",
                    "old failure may return",
                    ("diff@abc",),
                    0.95,
                    category="REGRESSION",
                )
            ],
            changed_paths=self.paths,
            history_evidence=tuple(),
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(len(result.accepted), 0)

    def test_duplicate_findings_keep_highest_confidence(self):
        finding_a = ReviewFinding("dup", "same", ("a",), 0.81)
        finding_b = ReviewFinding("dup", "same", ("b",), 0.95)
        result = self.engine.assess(
            [finding_a, finding_b],
            changed_paths=self.paths,
            history_evidence=tuple(),
        )
        self.assertEqual(len(result.accepted), 1)
        self.assertEqual(result.accepted[0].confidence, 0.95)

    def test_required_outside_voice_must_be_independent(self):
        report = OutsideVoiceReport(
            producer_identity="provider-a/model-x",
            reviewer_identity="provider-a/model-x",
            state="PASS",
            evidence=("review:1",),
        )
        result = self.engine.assess(
            [],
            changed_paths=self.paths,
            history_evidence=tuple(),
            outside_voice=report,
            outside_voice_required=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "outside_voice_not_independent")

    def test_outside_voice_disagreement_holds(self):
        report = OutsideVoiceReport(
            producer_identity="provider-a/model-x",
            reviewer_identity="provider-b/model-y",
            state="HOLD",
            evidence=("review:2",),
            disagreements=("authority interpretation differs",),
        )
        result = self.engine.assess(
            [],
            changed_paths=self.paths,
            history_evidence=tuple(),
            outside_voice=report,
            outside_voice_required=True,
        )
        self.assertEqual(result.state, "HOLD")
        self.assertEqual(result.reason, "outside_voice_disagreement")

    def test_independent_evidence_backed_outside_voice_passes(self):
        report = OutsideVoiceReport(
            producer_identity="provider-a/model-x",
            reviewer_identity="provider-b/model-y",
            state="PASS",
            evidence=("review:3",),
        )
        result = self.engine.assess(
            [],
            changed_paths=self.paths,
            history_evidence=("commit:abc",),
            outside_voice=report,
            outside_voice_required=True,
        )
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.outside_voice_state, "PASS")


if __name__ == "__main__":
    unittest.main()
