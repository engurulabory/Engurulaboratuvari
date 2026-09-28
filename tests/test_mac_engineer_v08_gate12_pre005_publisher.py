from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.mac_engineer_v08_gate12_pre005_publisher import (
    CrashDurablePublisher,
    PublicationHold,
    sha256_bytes,
)


class Gate12Pre005PublisherTests(unittest.TestCase):
    def test_publish_fsyncs_and_reads_back_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt.json"
            result = CrashDurablePublisher().publish_bytes(destination, b"payload\n")
            self.assertEqual(result.state, "PASS")
            self.assertEqual(destination.read_bytes(), b"payload\n")
            self.assertEqual(result.digest, sha256_bytes(b"payload\n"))
            self.assertTrue(CrashDurablePublisher.marker_path(destination).is_file())

    def test_exact_existing_destination_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt"
            publisher = CrashDurablePublisher()
            publisher.publish_bytes(destination, b"same")
            result = publisher.publish_bytes(destination, b"same")
            self.assertTrue(result.idempotent)

    def test_conflicting_destination_holds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt"
            publisher = CrashDurablePublisher()
            publisher.publish_bytes(destination, b"old")
            with self.assertRaisesRegex(PublicationHold, "DESTINATION_CONFLICT"):
                publisher.publish_bytes(destination, b"new")

    def test_fault_before_rename_leaves_recoverable_staging_and_holds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt"
            publisher = CrashDurablePublisher(
                lambda stage: (_ for _ in ()).throw(RuntimeError("TEST_FAULT"))
                if stage == "after_staged_file_fsync"
                else None
            )
            with self.assertRaisesRegex(PublicationHold, "PUBLICATION_IO_FAILURE"):
                publisher.publish_bytes(destination, b"payload")
            self.assertFalse(destination.exists())
            with self.assertRaisesRegex(PublicationHold, "INCOMPLETE_STAGING"):
                CrashDurablePublisher().publish_bytes(destination, b"payload")

    def test_rename_before_parent_fsync_is_ambiguous_on_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt"
            def fault(stage: str) -> None:
                if stage == "after_rename_before_parent_directory_fsync":
                    raise RuntimeError("TEST_FAULT")
            with self.assertRaisesRegex(PublicationHold, "PUBLICATION_IO_FAILURE"):
                CrashDurablePublisher(fault).publish_bytes(destination, b"payload")
            with self.assertRaisesRegex(PublicationHold, "AMBIGUOUS_RECOVERY"):
                CrashDurablePublisher().publish_bytes(destination, b"payload")

    def test_readback_failure_holds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "receipt"
            def fault(stage: str) -> None:
                if stage == "before_readback":
                    raise RuntimeError("TEST_FAULT")
            with self.assertRaisesRegex(PublicationHold, "PUBLICATION_IO_FAILURE"):
                CrashDurablePublisher(fault).publish_bytes(destination, b"payload")


if __name__ == "__main__":
    unittest.main()
