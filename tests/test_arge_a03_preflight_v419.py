"""A03 advisory preflight adversarial tests: reject false positive readiness."""
import unittest
import copy
import json
from pathlib import Path
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


class SoloOwnerGitHubScopeTests(unittest.TestCase):
    """Owner-only GitHub CI is a preparation policy, not a forged external grant."""

    @classmethod
    def setUpClass(cls):
        path=(Path(__file__).resolve().parents[1]/
              "governance/enguru-suzgeci/reviews/"
              "ENGURU_ARGE_B01_M01_A03_A04_MANAGEMENT_DECISION_HANDOFF_V1.json")
        cls.record=json.loads(path.read_text(encoding="utf8"))

    @staticmethod
    def valid(record):
        policy=record["solo_owner_github_preparation_v2"]
        ids=[value for package in record["single_active_execution_queue"]
             for value in package["scope"]]
        original=record["preserved_scope"]
        return (
            policy["approved_owner"]=="engurulabory"
            and policy["mode"]=="SOLO_OWNER_GITHUB_AUTOMATED_CI"
            and policy["decision_scope"]=="GITHUB_RESEARCH_AND_TECHNICAL_PREPARATION_ONLY"
            and policy["second_human_github_reviewer_required"] is False
            and policy["official_donecheck_issuer"]=="EXISTING_CANONICAL_ONLY"
            and policy["signed_issuer_grant"]=="REQUIRES_REAL_EXISTING_SOURCE_AND_SCOPE"
            and policy["outside_customer_e5"]=="REQUIRES_GENUINE_INDEPENDENT_CUSTOMER_USE_EVIDENCE"
            and policy["product_field"]=="HOLD"
            and policy["ready_to_automatically_merge"] is False
            and record["A03"]["real_owner_grant_ref"] is None
            and record["A03"]["decision"]=="HOLD_REAL_A03_OWNER_ISSUER_REVIEWER_AUTHORITY"
            and record["A04"]["canonical_runtime_source"] is None
            and record["A04"]["decision"]=="HOLD_OWNER_CANONICAL_SCOPE"
            and record["current_counters"]["overall_official"]=="0/40"
            and record["current_counters"].get("independent_e5","0/18")=="0/18"
            and record["current_counters"].get("customer_deployments","0/18")=="0/18"
            and record["A05_A06"]["customer_deployment"]=="0/18"
            and record["A05_A06"]["independent_e5"]=="0/18"
            and len(ids)==original["original_tasks"]==40
            and len(set(ids))==40
            and len(original["block01"])==9
            and original["blocks"]==6
            and original["cases"]==18
            and original["cells"]==234
        )

    def test_current_single_owner_github_scope_passes_with_real_gates_hold(self):
        self.assertTrue(self.valid(self.record))
        self.assertEqual(self.record["preserved_scope"]["active_package"],"B01-M01")
        self.assertEqual(self.record["preserved_scope"]["chosen"],
                         ["A03","A04","A05","A06"])

    def test_fake_acceptance_or_signer_drift_fails(self):
        mutations=[
            lambda r:r["solo_owner_github_preparation_v2"].update(decision_scope="OFFICIAL_VERIFIED_FINISH"),
            lambda r:r["solo_owner_github_preparation_v2"].update(approved_owner="invented_reviewer"),
            lambda r:r["solo_owner_github_preparation_v2"].update(second_human_github_reviewer_required=0),
            lambda r:r["solo_owner_github_preparation_v2"].update(official_donecheck_issuer="SELF_ISSUED"),
            lambda r:r["solo_owner_github_preparation_v2"].update(ready_to_automatically_merge=True),
            lambda r:r["A03"].update(real_owner_grant_ref="invented-grant"),
            lambda r:r["A04"].update(decision="PASS_UNPROVEN"),
            lambda r:r["current_counters"].update(overall_official="40/40"),
            lambda r:r["current_counters"].update(independent_e5="18/18"),
            lambda r:r["single_active_execution_queue"][1]["scope"].append("A03"),
        ]
        for i,mutate in enumerate(mutations):
            with self.subTest(case=i):
                altered=copy.deepcopy(self.record)
                mutate(altered)
                self.assertFalse(self.valid(altered))


if __name__ == "__main__":
    unittest.main()
