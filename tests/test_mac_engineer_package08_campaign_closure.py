from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import mac_engineer_package08_campaign_closure as closure


class Package08CampaignClosureTests(unittest.TestCase):
    def test_current_campaign_is_aggregate_closure_ready(self) -> None:
        checks, context = closure.evaluate()
        self.assertTrue(all(checks.values()), checks)
        self.assertEqual(len(checks), 14)
        self.assertEqual(len(context["evidenceBindings"]), 19)
        self.assertTrue(all(row["digestValid"] for row in context["evidenceBindings"]))

    def test_canonical_surfaces_bind_verified_closed_receipt(self) -> None:
        documents = closure.load_documents()
        ledger = documents["ledger"]
        session_campaign = documents["session"]["postV08Objective"]
        roadmap_campaign = documents["roadmap"]["current"]["postV08Objective"]
        self.assertEqual(ledger["state"], "VERIFIED_CLOSED")
        self.assertEqual(session_campaign, roadmap_campaign)
        self.assertEqual(session_campaign["state"], "VERIFIED_CLOSED")
        self.assertEqual(session_campaign["nextAction"], closure.FINAL_NEXT_ACTION)
        self.assertTrue(session_campaign["campaignDoneCheckPass"])
        receipt_path = Path(session_campaign["campaignClosureReceipt"])
        donecheck_path = Path(session_campaign["campaignDoneCheck"])
        self.assertEqual(closure.sha256(receipt_path), session_campaign["campaignClosureReceiptSha256"])
        self.assertEqual(closure.sha256(donecheck_path), session_campaign["campaignDoneCheckSha256"])
        self.assertEqual(ledger["campaignClosure"]["receiptSha256"], session_campaign["campaignClosureReceiptSha256"])

    def test_non_field_verified_capability_fails_closed(self) -> None:
        documents = closure.load_documents()
        held = copy.deepcopy(documents)
        held["ledger"]["capabilities"][0]["fieldState"] = "HOLD"
        with patch.object(closure, "load_documents", return_value=held):
            checks, _context = closure.evaluate()
        self.assertFalse(checks["field_ledger_19_of_19"])

    def test_nonzero_zero_tolerance_counter_fails_closed(self) -> None:
        documents = closure.load_documents()
        held = copy.deepcopy(documents)
        held["ledger"]["zeroTolerance"]["CRITICAL_FALSE_PASS"] = 1
        with patch.object(closure, "load_documents", return_value=held):
            checks, _context = closure.evaluate()
        self.assertFalse(checks["zero_tolerance_all_zero"])

    def test_closure_evidence_binds_donecheck_and_all_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "closure"
            result = closure.create_closure_evidence(output)
            receipt_path = Path(result["receiptPath"])
            donecheck_path = Path(result["doneCheckPath"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            donecheck = json.loads(donecheck_path.read_text(encoding="utf-8"))

            self.assertEqual(receipt["state"], "PASS")
            self.assertEqual(receipt["campaignState"], "VERIFIED_CLOSED")
            self.assertEqual(receipt["fieldVerifiedCount"], 19)
            self.assertEqual(len(receipt["capabilities"]), 19)
            self.assertTrue(all(row["digestValid"] for row in receipt["capabilities"]))
            self.assertEqual(receipt["campaignDoneCheck"]["sha256"], closure.sha256(donecheck_path))
            self.assertEqual(donecheck["state"], "PASS")
            self.assertEqual(donecheck["criterionCount"], 14)
            self.assertTrue(all(row["state"] == "PASS" for row in donecheck["criteria"].values()))
            self.assertFalse(receipt["execution"]["remotePush"])
            self.assertFalse(receipt["execution"]["commitCreated"])


if __name__ == "__main__":
    unittest.main()
