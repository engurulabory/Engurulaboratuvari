from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools import mac_engineer_v08_gate12_pre005_evidence as producer


def fixture(root: Path) -> Path:
    gates = {"gate12": {"executionStarted": False}}
    for number in range(1, 12):
        key = f"gate{number}Closure" if number in (8, 9, 10) else f"gate{number}"
        path = root / f"gate{number}" / "evidence.json"
        path.parent.mkdir()
        source = {"state": "PASS"}
        if number <= 7:
            source["gate"] = f"V08-{number:02d}"
        elif number <= 10:
            source["gate"] = number
        else:
            source["gate11State"] = "VERIFIED_LOCKED"
        path.write_text(json.dumps(source), encoding="utf-8")
        gate = {"state": "PASS" if number <= 7 else "VERIFIED_LOCKED"}
        if number in (2, 3, 4):
            gate["evidenceRoot"] = str(path.parent)
            gate["operatorReceipt"] = str(root / "historical-hold.json")
        else:
            gate["evidence"] = str(path)
        gates[key] = gate
    session = root / "session.json"
    session.write_text(json.dumps({"currentV08": gates}), encoding="utf-8")
    return session


class Gate12EvidenceTests(unittest.TestCase):
    def test_real_source_bindings_and_donecheck_machine_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = fixture(root)
            result = producer.prepare(session_path=session, output_root=root / "out")
            manifest = json.loads(Path(result["evidenceManifest"]).read_text())
            machine = json.loads(Path(result["verificationResult"]).read_text())
            self.assertEqual(machine["outcome"], "pass")
            self.assertEqual(len(machine["criteria"]), 11)
            producer.verify_source_lineage(manifest, json.loads(session.read_text()))
            self.assertTrue(all(Path(item["path"]).is_file() for item in manifest["evidenceFiles"]))

    def test_gate_source_hold_does_not_promote_historical_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = fixture(root)
            source = root / "gate2" / "evidence.json"
            source.write_text('{"state":"HOLD","gate":"V08-02"}', encoding="utf-8")
            with self.assertRaisesRegex(producer.EvidenceHold, "GATE2_SOURCE_NOT_PASS"):
                producer.prepare(session_path=session, output_root=root / "out")

    def test_source_digest_drift_holds_after_machine_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            session = fixture(root)
            result = producer.prepare(session_path=session, output_root=root / "out")
            manifest = json.loads(Path(result["evidenceManifest"]).read_text())
            (root / "gate4" / "evidence.json").write_text('{"state":"PASS","gate":"V08-04","changed":true}', encoding="utf-8")
            with self.assertRaisesRegex(producer.EvidenceHold, "GATE4_SOURCE_LINEAGE_MISMATCH"):
                producer.verify_source_lineage(manifest, json.loads(session.read_text()))


if __name__ == "__main__":
    unittest.main()
