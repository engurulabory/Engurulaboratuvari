import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord
from cores.billing.persistent_store import JsonFileEvidenceStore


class PersistentStoreTests(unittest.TestCase):
    def make_record(self, order_id="o1", document_id="d1"):
        return InvoiceRecord(
            order_id=order_id,
            product="ENGURU Builder",
            document_no="INT1",
            document_id=document_id,
            document_type="E_ARCHIVE_INTERNET",
            amount=Decimal("100"),
            currency="TRY",
            issued_at=datetime(2026, 9, 11, 12, 0, 0),
            provider_status="DELIVERED",
            customer_delivery_id="m1",
            accounting_delivery_id="a1",
        )

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileEvidenceStore(Path(tmp) / "billing.json")
            store.add(self.make_record())
            rows = store.between(datetime(2026, 9, 1), datetime(2026, 10, 1))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].order_id, "o1")

    def test_duplicate_order_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileEvidenceStore(Path(tmp) / "billing.json")
            store.add(self.make_record())
            with self.assertRaises(ValueError):
                store.add(self.make_record(document_id="d2"))


if __name__ == "__main__":
    unittest.main()
