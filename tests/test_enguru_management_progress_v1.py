"""Read-only management projection regression and fail-closed tests."""

import unittest

from tools.enguru_management_progress_v1 import HandoffError, project


def base():
    return {
        "schema": "enguru.management.handoff/v1",
        "source": {"report": "V9", "sha256": "a" * 64},
        "goals": {
            "H1": {"passed": 0, "total": 4},
            "H2": {"passed": 0, "total": 4},
            "H3": {"passed": 0, "total": 4},
            "native": "HOLD",
            "verifiedFinish": "HOLD",
        },
        "blockers": [{"id": f"F{i:02d}", "status": "HOLD_EVIDENCE"} for i in range(1, 7)],
    }


class ManagementProgressTests(unittest.TestCase):
    def test_v9_baseline_is_zero_and_single_primary(self):
        result = project(base())
        self.assertEqual(result["officialAccepted"]["percent"], 0)
        self.assertEqual(result["blockers"]["closedPercent"], 0)
        self.assertEqual(result["nextWork"]["primary"], "F01")
        self.assertEqual(result["nextWork"]["independentSupport"], "F05_SCOPE_AND_SOURCE_PREPARATION")
        self.assertEqual(result["state"], "PROJECTION_ONLY_NOT_AUTHORITY")
        self.assertEqual(result["terminalProjection"], "HOLD_PENDING_AUTHORIZED_ACCEPTANCE")

    def test_partial_official_acceptance_is_not_a_finished_goal(self):
        record = base()
        record["goals"]["H1"]["passed"] = 1
        result = project(record)
        self.assertEqual(result["officialAccepted"]["percent"], 8.33)
        self.assertNotEqual(result["terminalProjection"], "READY_FOR_INDEPENDENT_FINAL_ACCEPTANCE")

    def test_real_receipt_is_required_for_closed_blocker(self):
        record = base()
        record["blockers"][0]["status"] = "PASS_CLOSED"
        with self.assertRaises(HandoffError):
            project(record)
        record["blockers"][0]["acceptanceReceipt"] = "receipt:scoped"
        result = project(record)
        self.assertEqual(result["blockers"]["closedPercent"], 16.67)
        self.assertEqual(result["nextWork"]["primary"], "F02")

    def test_h1_gate_must_be_four_before_signer_blocker_closes(self):
        record = base()
        record["blockers"][1].update(status="PASS_CLOSED", acceptanceReceipt="h1")
        with self.assertRaises(HandoffError):
            project(record)

    def test_native_owner_evidence_needed_before_f05_closes(self):
        record = base()
        record["blockers"][4].update(status="PASS_CLOSED", acceptanceReceipt="native")
        with self.assertRaises(HandoffError):
            project(record)

    def test_verified_finish_requires_every_accepted_gate(self):
        record = base()
        record["blockers"][5].update(status="PASS_CLOSED", acceptanceReceipt="finish")
        with self.assertRaises(HandoffError):
            project(record)

    def test_duplicate_blocker_fails_closed(self):
        record = base()
        record["blockers"][1]["id"] = "F01"
        with self.assertRaises(HandoffError):
            project(record)

    def test_bool_is_not_integer_pass(self):
        record = base()
        record["goals"]["H1"]["passed"] = True
        with self.assertRaises(HandoffError):
            project(record)

    def test_v10_native_identity_is_preserved_without_claiming_acceptance(self):
        import json
        from pathlib import Path
        fixture = Path(__file__).resolve().parents[1] / "governance" / "mac-engineer" / "examples" / "ENGURU_MANAGEMENT_V10_PROJECTION_INPUT.json"
        report = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(report["scope"]["activeProduct"], "ENGURU_MAC_ENGINEER")
        self.assertEqual(report["scope"]["nativeProductIdentity"], "PASS_TWO_CANONICAL_CONTRACTS")
        self.assertEqual(report["scope"]["nextProduct"], "PLIVE")
        self.assertFalse(report["scope"]["buildExecuted"])
        view = project(report)
        self.assertEqual(view["officialAccepted"]["sum"], 0)
        self.assertEqual(view["blockers"]["closed"], 0)
        self.assertEqual(view["nextWork"], {"primary": "F01", "independentSupport": "F05_SCOPE_AND_SOURCE_PREPARATION"})
        self.assertEqual(view["terminalProjection"], "HOLD_PENDING_AUTHORIZED_ACCEPTANCE")

    def test_v12_real_compiler_failure_stays_hold_and_proposals_unapproved(self):
        import json
        from pathlib import Path
        fixture = (Path(__file__).resolve().parents[1] / "governance"
                   / "mac-engineer" / "examples"
                   / "ENGURU_MANAGEMENT_V12_PROJECTION_INPUT.json")
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertTrue(raw["scope"]["swiftBuild"]["attempted"])
        self.assertEqual(raw["scope"]["swiftBuild"]["returnCode"], 1)
        self.assertEqual(raw["scope"]["swiftBuild"]["errorsReceiptField"], "F05.build.build_errors")
        self.assertEqual(raw["scope"]["swiftBuild"]["cause"], "NEDEN_BEKLIYOR")
        self.assertEqual(raw["scope"]["f01"]["proposedCriteria"], 12)
        self.assertEqual(raw["scope"]["f01"]["approvedCriteria"], 0)
        self.assertEqual(raw["scope"]["f01"]["proposalState"], "UNAPPROVED_ENGINEERING_PROPOSAL")
        self.assertEqual(raw["scope"]["nextProduct"], "PILIVE")
        view = project(raw)
        self.assertEqual(view["officialAccepted"]["sum"], 0)
        self.assertEqual(view["blockers"]["closed"], 0)
        self.assertEqual(view["terminalProjection"], "HOLD_PENDING_AUTHORIZED_ACCEPTANCE")
        self.assertEqual(view["nextWork"]["primary"], "F01")
        self.assertEqual(view["nextWork"]["independentSupport"], "F05_SCOPE_AND_SOURCE_PREPARATION")

    def test_v13_sdk_repair_is_technical_pass_not_official_finish(self):
        import json
        from pathlib import Path
        fixture = (Path(__file__).resolve().parents[1] / "governance"
                   / "mac-engineer" / "examples"
                   / "ENGURU_MANAGEMENT_V13_PROJECTION_INPUT.json")
        source = json.loads(fixture.read_text(encoding="utf-8"))
        self.assertEqual(source["scope"]["isolatedBuild"], "PASS")
        self.assertEqual(source["scope"]["compilerRC"], 0)
        self.assertEqual(len(source["scope"]["buildBinarySha256"]), 64)
        self.assertEqual(source["scope"]["sourceBuildIntegration"], "HOLD")
        self.assertEqual(source["scope"]["criteriaApproved"], 0)
        self.assertEqual(source["scope"]["criteriaProposed"], 12)
        self.assertEqual(source["scope"]["criteriaStatus"], "UNAPPROVED_ENGINEERING_PROPOSAL")
        self.assertEqual(source["scope"]["nextProduct"], "PILIVE")
        view = project(source)
        self.assertEqual(view["officialAccepted"]["sum"], 0)
        self.assertEqual(view["blockers"]["closed"], 0)
        self.assertEqual(view["nextWork"]["primary"], "F01")
        self.assertEqual(view["terminalProjection"], "HOLD_PENDING_AUTHORIZED_ACCEPTANCE")

    def test_full_chain_still_projection_not_authority(self):
        record = base()
        for goal in ("H1", "H2", "H3"):
            record["goals"][goal]["passed"] = 4
        record["goals"]["native"] = record["goals"]["verifiedFinish"] = "PASS"
        for item in record["blockers"]:
            item.update(status="PASS_CLOSED", acceptanceReceipt=f"receipt:{item['id']}")
        result = project(record)
        self.assertEqual(result["terminalProjection"], "READY_FOR_INDEPENDENT_FINAL_ACCEPTANCE")
        self.assertEqual(result["state"], "PROJECTION_ONLY_NOT_AUTHORITY")
        self.assertEqual(result["blockers"]["closedPercent"], 100)


if __name__ == "__main__":
    unittest.main()
