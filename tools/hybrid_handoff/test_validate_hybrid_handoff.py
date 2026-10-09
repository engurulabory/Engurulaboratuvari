"""Adversarial checks for the GitHub-only hybrid contract preflight."""
import copy
import json
import unittest
from pathlib import Path
from validate_hybrid_handoff import validate

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "governance/mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_HANDOFF_TEMPLATE_V1.json"


class HybridValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_template_is_valid(self):
        self.assertEqual(validate(self.base), [])

    def test_wrong_schema_fails(self):
        x = copy.deepcopy(self.base)
        x["schema"] = "other"
        self.assertIn("SCHEMA_MISMATCH", validate(x))

    def test_premature_lock_fails(self):
        x = copy.deepcopy(self.base)
        x["verifiedFinish"] = "LOCKED"
        self.assertIn("GITHUB_CANNOT_LOCK_OSI_VERIFIED_FINISH", validate(x))

    def test_missing_suzgec_fails(self):
        x = copy.deepcopy(self.base)
        x.pop("suzgec")
        self.assertIn("SUZGEC_DECISION_SEQUENCE_MISSING", validate(x))

    def test_unsupported_pass_fails(self):
        x = copy.deepcopy(self.base)
        x["suzgec"]["judgment"] = "PASS"
        self.assertIn("UNSUPPORTED_PASS", validate(x))

    def test_missing_project_identity_fails(self):
        self.assertIn("PROJECT_IDENTITY_MISSING", validate(self.base, mode="handoff"))

    def test_invalid_mode_fails(self):
        x = self._handoff()
        x["executionMode"] = "MAGIC"
        self.assertIn("EXECUTION_MODE_INVALID", validate(x, mode="handoff"))

    def test_invalid_digest_fails(self):
        x = self._handoff()
        x["artifactDigest"] = "not-a-digest"
        self.assertIn("ARTIFACT_DIGEST_INVALID", validate(x, mode="handoff"))

    def test_github_cannot_attest_osi_field(self):
        x = self._handoff()
        x["fieldReceipt"]["osiFieldState"] = "PASS"
        self.assertIn("GITHUB_FIELD_ATTESTATION_FORBIDDEN", validate(x, mode="handoff"))

    def test_scoped_handoff_is_valid_but_not_locked(self):
        self.assertEqual(validate(self._handoff(), mode="handoff"), [])

    def _handoff(self):
        x = copy.deepcopy(self.base)
        x.update(projectId="sample", subproduct="sample", executionMode="HYBRID",
                 canonicalRepo="owner/repo", sourceRef="refs/heads/main",
                 sourceCommit="a" * 40, artifactDigest="b" * 64)
        return x


if __name__ == "__main__":
    unittest.main()
