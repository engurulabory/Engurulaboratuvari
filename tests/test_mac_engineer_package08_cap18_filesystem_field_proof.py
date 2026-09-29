from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import mac_engineer_package08_cap18_filesystem_macos_automation_field_proof as cap18
from tools import mac_engineer_operator as operator


ROOT = Path(__file__).resolve().parents[1]


class Capability18FieldProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.technical = json.loads(cap18.TECHNICAL_PATH.read_text(encoding="utf-8"))
        cls.threshold = json.loads(cap18.HUMAN_THRESHOLD_PATH.read_text(encoding="utf-8"))

    def write(self, root: Path, name: str, payload: dict) -> Path:
        path = root / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def verify(self, technical: dict | None = None, threshold: dict | None = None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            technical_path = self.write(root, "technical.json", technical or self.technical)
            threshold_path = self.write(root, "threshold.json", threshold or self.threshold)
            seal = root / "seal.json"
            return cap18.verify_and_seal(
                technical_path=technical_path,
                technical_digest=cap18.sha256(technical_path),
                human_threshold_path=threshold_path,
                human_threshold_digest=cap18.sha256(threshold_path),
                seal_path=seal,
            )

    def test_exact_accepted_evidence_passes(self) -> None:
        payload = self.verify()
        self.assertEqual(payload["state"], "PASS")
        self.assertFalse(payload["execution"]["technicalFieldTaskReexecuted"])
        self.assertFalse(payload["execution"]["humanThresholdRegenerated"])
        self.assertFalse(payload["execution"]["technicalFilesystemMutationPerformed"])
        self.assertTrue(payload["execution"]["evidenceSealWritten"])

    def test_wrong_technical_sha_holds(self) -> None:
        with self.assertRaisesRegex(cap18.VerificationHold, "TECHNICAL_CANDIDATE_SHA256_MISMATCH"):
            cap18.read_exact(cap18.TECHNICAL_PATH, "0" * 64, "TECHNICAL_CANDIDATE")

    def test_wrong_human_threshold_sha_holds(self) -> None:
        with self.assertRaisesRegex(cap18.VerificationHold, "HUMAN_THRESHOLD_RECEIPT_SHA256_MISMATCH"):
            cap18.read_exact(cap18.HUMAN_THRESHOLD_PATH, "0" * 64, "HUMAN_THRESHOLD_RECEIPT")

    def test_missing_accept_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["decision"] = "HOLD"
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_ACCEPT_REQUIRED"):
            self.verify(threshold=payload)

    def test_unconsumed_human_threshold_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["humanThresholdConsumed"] = False
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_CONSUMED_REQUIRED"):
            self.verify(threshold=payload)

    def test_capability_mismatch_holds(self) -> None:
        payload = copy.deepcopy(self.technical)
        payload["capabilityId"] = "TERMINAL_EXECUTION"
        with self.assertRaisesRegex(cap18.VerificationHold, "TECHNICAL_CAPABILITY_ID_MISMATCH"):
            self.verify(technical=payload)

    def test_scope_broadening_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["authorizedScope"]["mutationScope"] = "UNSCOPED"
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_SCOPE_MISMATCH"):
            self.verify(threshold=payload)

    def test_network_authority_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["authorizedScope"]["networkPolicy"] = "NETWORK_ALLOWED"
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_SCOPE_MISMATCH"):
            self.verify(threshold=payload)

    def test_remote_push_authority_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["authorizedScope"]["remotePush"] = True
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_SCOPE_MISMATCH"):
            self.verify(threshold=payload)

    def test_finder_gui_authority_holds(self) -> None:
        payload = copy.deepcopy(self.threshold)
        payload["authorizedScope"]["finderGuiAuthority"] = True
        with self.assertRaisesRegex(cap18.VerificationHold, "HT_SCOPE_MISMATCH"):
            self.verify(threshold=payload)

    def test_command_surface_is_invocable_without_field_reexecution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            seal = Path(directory) / "seal.json"
            env = {**os.environ, "ENGURU_CAP18_SEAL_PATH": str(seal), "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(
                ["zsh", str(ROOT / "governance/mac-engineer/PACKAGE08_CAP18_FILESYSTEM_MACOS_AUTOMATION_FIELD_PROOF.command")],
                cwd=ROOT,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("CAPABILITY_REEXECUTED=false", result.stdout)
            self.assertTrue(seal.is_file())

    def test_operator_callable_is_invocable(self) -> None:
        output = "STATE=PASS\nCAP18_FILESYSTEM_MACOS_AUTOMATION=PASS\nEVIDENCE=/tmp/seal.json\n"
        with patch.object(
            operator,
            "run",
            return_value={"code": 0, "stdout": output, "stderr": ""},
        ):
            result = operator.run_package08_cap18_filesystem_macos_automation_field_proof()
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["fields"]["CAP18_FILESYSTEM_MACOS_AUTOMATION"], "PASS")
        self.assertEqual(result["evidence"], "/tmp/seal.json")

    def test_canonical_registered_action_and_promotion_readback(self) -> None:
        gov = ROOT / "governance/mac-engineer"
        action_registry = json.loads((gov / "OPERATOR_ACTION_REGISTRY_V1.json").read_text())
        binding_doc = json.loads((gov / "CAPABILITY_EXECUTION_BINDING_V1.json").read_text())
        registry = json.loads((gov / "CAPABILITY_REGISTRY_V1.json").read_text())
        ledger = json.loads((gov / "CAPABILITY_FIELD_VERIFICATION_LEDGER_V1.json").read_text())

        action = action_registry["actions"][cap18.ACTION]
        binding = next(row for row in binding_doc["bindings"] if row["CAPABILITY_ID"] == cap18.CAPABILITY_ID)
        capability = next(row for row in registry["capabilities"] if row["CAPABILITY_ID"] == cap18.CAPABILITY_ID)
        ledger_rows = {row["index"]: row for row in ledger["capabilities"]}

        self.assertEqual(action["handler"], cap18.ACTION)
        self.assertEqual(action["authority"], cap18.AUTHORITY)
        self.assertFalse(action["networkRequired"])
        self.assertFalse(action["remotePush"])
        self.assertEqual(binding["BINDING_TYPE"], "REGISTERED_ACTION")
        self.assertEqual(binding["OPERATOR_CALLABLE"], cap18.OPERATOR_CALLABLE)
        self.assertEqual(capability["STATE"], "VERIFIED")
        self.assertEqual(ledger["fieldVerifiedCount"], 18)
        self.assertEqual(ledger_rows[17]["fieldState"], "FIELD_VERIFIED")
        self.assertEqual(ledger_rows[18]["fieldState"], "FIELD_VERIFIED")
        self.assertTrue(ledger_rows[18]["acceptance"]["humanThresholdPass"])
        self.assertTrue(ledger_rows[18]["acceptance"]["recoveryOrRollbackPass"])
        self.assertEqual(ledger_rows[19]["fieldState"], "PENDING")
        evidence = ledger_rows[18]["evidence"]
        evidence_path = Path(evidence["path"])
        self.assertTrue(evidence_path.is_file())
        self.assertEqual(cap18.sha256(evidence_path), evidence["sha256"])
        seal = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(seal["state"], "PASS")
        self.assertFalse(seal["execution"]["technicalFieldTaskReexecuted"])
        self.assertTrue(seal["execution"]["evidenceSealWritten"])


if __name__ == "__main__":
    unittest.main()
