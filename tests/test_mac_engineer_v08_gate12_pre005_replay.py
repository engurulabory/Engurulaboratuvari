from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.mac_engineer_v08_gate12_pre005_replay import (
    PersistentReplayAuthority,
    ReplayStoreHold,
    SCHEMA,
)


def record(*, decision: str = "ACCEPT", suffix: str = "a") -> dict[str, str]:
    return {
        "decisionId": "g12-ht-sha256:" + suffix * 64,
        "terminalCandidateId": "g12-candidate-sha256:" + ("b" if suffix == "a" else "c") * 64,
        "payloadDigest": "sha256:" + "1" * 64,
        "envelopeDigest": "sha256:" + "2" * 64,
        "decision": decision,
    }


class Gate12Pre005ReplayTests(unittest.TestCase):
    def test_new_record_persists_and_reopen_preserves_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.json"
            first = PersistentReplayAuthority(path)
            self.assertEqual(first.remember(record()), "NEW")
            reopened = PersistentReplayAuthority(path)
            self.assertEqual(reopened.get_decision(record()["decisionId"]), record())
            self.assertEqual(reopened.get_terminal_candidate(record()["terminalCandidateId"]), record())
            self.assertEqual(first.remember(record()), "IDEMPOTENT")

    def test_changed_id_content_and_terminal_accept_conflict_hold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.json"
            store = PersistentReplayAuthority(path)
            original = record()
            store.remember(original)
            changed = dict(original, envelopeDigest="sha256:" + "3" * 64)
            with self.assertRaisesRegex(ReplayStoreHold, "ID_CONTENT_CONFLICT"):
                store.remember(changed)
            conflict = record(decision="HOLD", suffix="d")
            conflict["terminalCandidateId"] = original["terminalCandidateId"]
            with self.assertRaisesRegex(ReplayStoreHold, "TERMINAL_CANDIDATE_ALREADY_ACCEPTED"):
                store.remember(conflict)

    def test_corrupt_truncated_unknown_and_duplicate_records_hold(self) -> None:
        cases = [
            b"{\"schema\": \"" + SCHEMA.encode() + b"\", \"records\":[",
            b"not-json",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for index, payload in enumerate(cases):
                path = Path(directory) / f"replay-{index}.json"
                path.write_bytes(payload)
                with self.assertRaises(ReplayStoreHold):
                    PersistentReplayAuthority(path).get_decision("missing")

            path = Path(directory) / "unknown.json"
            path.write_text('{"schema":"' + SCHEMA + '","records":[],"unknown":true}')
            with self.assertRaisesRegex(ReplayStoreHold, "ROOT_INVALID"):
                PersistentReplayAuthority(path).get_decision("missing")

    def test_incomplete_staging_does_not_fall_back_to_empty(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replay.json"
            staging = path.parent / f".{path.name}.staging-test"
            staging.mkdir()
            with self.assertRaisesRegex(ReplayStoreHold, "INCOMPLETE_STAGING"):
                PersistentReplayAuthority(path).get_decision("missing")


if __name__ == "__main__":
    unittest.main()
