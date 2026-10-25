"""A03 advisory preflight adversarial tests: reject false positive readiness."""
import unittest
from tools.arge_a03_preflight_v419 import assess_a03, GATES


def fixture():
    x = {
        "task_id": "A03", "source_commit": "1" * 40,
        "artifact_sha256": "a" * 64,
        "producer_id": "producer", "reviewer_id": "different-reviewer",
    }
    for k in GATES:
        x[k] = True
        x[k + "_evidence_ref"] = (
            "https://github.com/engurulabory/donecheck/blob/"
            + ("2" * 40) + "/docs/" + k + ".json#sha256=" + ("b" * 64)
        )
    return x


class A03PreflightTests(unittest.TestCase):
    def assert_external_hold(self, record):
        result = assess_a03(record)
        self.assertEqual(result["state"], "HOLD")
        self.assertIn("EXTERNAL_AUTHORITY_VERIFICATION_REQUIRED", result["blockers"])
        self.assertFalse(result["official_acceptance"])
        self.assertFalse(result["verified_finish"])
        return result

    def test_valid_syntactic_metadata_is_always_advisory_only(self):
        result = self.assert_external_hold(fixture())
        self.assertEqual(result["structural_preflight"], "PASS_FORMAT_ONLY")
        self.assertEqual(result["blockers"], ["EXTERNAL_AUTHORITY_VERIFICATION_REQUIRED"])

    def test_missing_reviewer_holds(self):
        for blank in (None, "", "   "):
            with self.subTest(blank=blank):
                case = fixture()
                case["reviewer_id"] = blank
                result = self.assert_external_hold(case)
                self.assertIn("REVIEWER_ID_MISSING", result["blockers"])
                self.assertEqual(result["structural_preflight"], "HOLD_INVALID_INPUT")

    def test_missing_producer_holds(self):
        case = fixture()
        case["producer_id"] = " "
        self.assertIn("PRODUCER_ID_MISSING", self.assert_external_hold(case)["blockers"])

    def test_same_reviewer_holds_even_with_whitespace(self):
        case = fixture()
        case["reviewer_id"] = " producer "
        self.assertIn("REVIEWER_NOT_INDEPENDENT", self.assert_external_hold(case)["blockers"])

    def test_placeholder_references_holds_for_every_gate(self):
        for k in GATES:
            with self.subTest(gate=k):
                case = fixture()
                case[k + "_evidence_ref"] = "evidence://placeholder"
                result = self.assert_external_hold(case)
                self.assertIn(k.upper() + "_EVIDENCE_REF_INVALID", result["blockers"])

    def test_malformed_or_unpinned_references_hold(self):
        for ref in ("", None, "https://github.com/owner/repo/blob/main/path",
                    "https://github.com/owner/repo/commit/" + ("3" * 40),
                    "file:///tmp/proof.json", "https://example.com/evidence",
                    "evidence://trusted", "sha256:" + ("f" * 64)):
            with self.subTest(ref=ref):
                case = fixture()
                case[GATES[0] + "_evidence_ref"] = ref
                self.assertIn(GATES[0].upper() + "_EVIDENCE_REF_INVALID",
                              self.assert_external_hold(case)["blockers"])

    def test_each_missing_assertion_holds(self):
        for k in GATES:
            with self.subTest(gate=k):
                case = fixture()
                case[k] = False
                self.assertIn(k.upper(), self.assert_external_hold(case)["blockers"])

    def test_string_true_is_not_authority(self):
        case = fixture()
        case[GATES[1]] = "true"
        self.assertIn(GATES[1].upper(), self.assert_external_hold(case)["blockers"])

    def test_invalid_source_and_artifact_holds(self):
        for name,bad,blocker in (
            ("source_commit", "bad", "SOURCE_COMMIT_FORMAT"),
            ("artifact_sha256", "bad", "ARTIFACT_DIGEST_FORMAT"),
            ("artifact_sha256", 123, "ARTIFACT_DIGEST_FORMAT"),
        ):
            with self.subTest(field=name):
                case = fixture()
                case[name] = bad
                self.assertIn(blocker, self.assert_external_hold(case)["blockers"])

    def test_plausible_hashes_alone_are_not_source_authentication(self):
        case = fixture()
        case["source_commit"] = "f" * 40
        case["artifact_sha256"] = "e" * 64
        result = self.assert_external_hold(case)
        self.assertEqual(result["structural_preflight"], "PASS_FORMAT_ONLY")
        self.assertIn("EXTERNAL_AUTHORITY_VERIFICATION_REQUIRED", result["blockers"])

    def test_cross_task_record_holds(self):
        case = fixture()
        case["task_id"] = "A04"
        self.assertIn("TASK_SCOPE", self.assert_external_hold(case)["blockers"])

    def test_invalid_record_fails_closed(self):
        result = self.assert_external_hold(None)
        self.assertIn("INVALID_RECORD", result["blockers"])

    def test_forged_authority_claims_never_issue_receipt(self):
        case = fixture()
        case.update({"official_acceptance": True,
                     "verified_finish": True, "signed_by": "OWNER",
                     "independent_verifier_passed": True})
        self.assert_external_hold(case)

    def test_local_pinned_reference_only_passes_format_gate(self):
        case = fixture()
        case[GATES[2] + "_evidence_ref"] = (
            "file:///Users/owner/AudiV13/reviewer-proof.json#sha256=" + ("c" * 64)
        )
        self.assertEqual(self.assert_external_hold(case)["structural_preflight"],
                         "PASS_FORMAT_ONLY")


if __name__ == "__main__":
    unittest.main()
