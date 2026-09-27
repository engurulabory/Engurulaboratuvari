from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARD = ROOT / "tools/mac_engineer_v11_jev_guard.py"

ACCEPTANCE = (
    ROOT
    / "governance/mac-engineer/"
      "V11_JEV_PROVIDER_QUALIFICATION_ACCEPTANCE_V1.json"
)


def run_guard(path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(GUARD),
            "--acceptance",
            str(path),
        ],
        capture_output=True,
        text=True,
    )

    return result.returncode, json.loads(result.stdout)


class V11JevGuardTests(unittest.TestCase):
    def test_current_acceptance_is_fail_closed(self):
        rc, payload = run_guard(ACCEPTANCE)

        self.assertEqual(rc, 2)
        self.assertEqual(payload["state"], "HOLD")
        self.assertEqual(
            payload["claim"],
            "JEV_PROVIDER_QUALIFICATION_EVIDENCE_PENDING",
        )
        self.assertTrue(payload["accessExpected"])
        self.assertFalse(payload["v13MandatoryDependency"])

    def test_contract_thresholds_are_locked(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        thresholds = data["thresholds"]

        self.assertEqual(
            thresholds["canonicalAgreementMin"],
            0.95,
        )
        self.assertEqual(
            thresholds["criticalFalsePassMax"],
            0,
        )
        self.assertEqual(
            thresholds["humanThresholdMissMax"],
            0,
        )
        self.assertEqual(
            thresholds["latencyImprovementFactorTarget"],
            0.75,
        )
        self.assertEqual(
            thresholds["costImprovementFactorTarget"],
            0.75,
        )
        self.assertLessEqual(
            thresholds["maxRetryAttempts"],
            2,
        )

    def test_all_live_evidence_allows_pass(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        candidate = deepcopy(data)

        candidate["currentProviderEvidenceState"] = (
            "LIVE_EVIDENCE_COMPLETE"
        )

        for name, criterion in candidate["criteria"].items():
            criterion["state"] = "PASS"
            criterion["evidence"] = (
                f"evidence/jev/live/{name}.json"
            )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "acceptance.json"
            path.write_text(
                json.dumps(
                    candidate,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            rc, payload = run_guard(path)

        self.assertEqual(rc, 0)
        self.assertEqual(payload["state"], "PASS")
        self.assertEqual(
            payload["claim"],
            "JEV_PROVIDER_QUALIFICATION_PASS",
        )

    def test_pass_without_evidence_remains_hold(self):
        data = json.loads(
            ACCEPTANCE.read_text(encoding="utf-8")
        )

        candidate = deepcopy(data)

        for criterion in candidate["criteria"].values():
            criterion["state"] = "PASS"
            criterion["evidence"] = "evidence/jev/live/pass.json"

        candidate["criteria"][
            "LIVE_TRANSPORT_VERIFIED"
        ]["evidence"] = None

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "acceptance.json"
            path.write_text(
                json.dumps(
                    candidate,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            rc, payload = run_guard(path)

        self.assertEqual(rc, 2)
        self.assertEqual(payload["state"], "HOLD")
        self.assertIn(
            "EVIDENCE_REQUIRED:LIVE_TRANSPORT_VERIFIED",
            payload["issues"],
        )


if __name__ == "__main__":
    unittest.main()
