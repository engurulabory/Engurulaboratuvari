from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

CONTRACT = (
    ROOT
    / "governance"
    / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_CONTRACT_V1.json"
)

PRECEDENCE = (
    ROOT
    / "governance"
    / "chatgpt"
    / "ENGURU_LANGUAGE_GOVERNANCE_AUTHORITY_PRECEDENCE_V1.json"
)


class EnguruSuzgeciContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(
            CONTRACT.read_text(encoding="utf-8")
        )

        self.precedence = json.loads(
            PRECEDENCE.read_text(encoding="utf-8")
        )

    def test_identity(self):
        self.assertEqual(
            self.contract["governanceId"],
            "ENGURU_LANGUAGE_GOVERNANCE",
        )

    def test_execution_states(self):
        self.assertEqual(
            self.contract["executionStates"],
            ["PASS", "HOLD", "BLOCKED", "FAIL"],
        )

    def test_preservation_first_language(self):
        self.assertEqual(
            self.contract["preferredVocabulary"]["bozmadan"],
            "koruyarak",
        )

    def test_capability_order(self):
        self.assertEqual(
            self.contract["capabilityDecisionOrder"],
            ["REUSE", "EXTEND", "ADAPTER", "NEW"],
        )

    def test_claim_classes(self):
        self.assertEqual(
            self.contract["claimClasses"],
            ["OBSERVED", "PROVEN", "INFERRED", "PROPOSED"],
        )

    def test_precedence_layers(self):
        self.assertEqual(
            len(self.precedence["layers"]),
            10,
        )

    def test_intent_cannot_rewrite_fact(self):
        self.assertIn(
            "USER_INTENT_DOES_NOT_CONVERT_TECHNICAL_FAIL_TO_PASS",
            self.precedence["conflictRules"],
        )


if __name__ == "__main__":
    unittest.main()
