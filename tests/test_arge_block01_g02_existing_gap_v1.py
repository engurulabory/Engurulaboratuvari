"""A07 G02: adversarial characterization of the existing billing evidence API.

A passing test here documents a missing authorization boundary, NOT G02 PASS.
Do not expose this API to untrusted callers without a canonical grant check.
"""
import inspect
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord
from cores.billing.persistent_store import JsonFileEvidenceStore


class G02ExistingGapTests(unittest.TestCase):
    def test_legacy_schema_has_no_tenant_or_principal(self):
        names = set(InvoiceRecord.__dataclass_fields__)
        self.assertFalse({"tenant_id", "principal_id", "owner_subject"} & names)

    def test_existing_evidence_listing_has_no_grant_parameter(self):
        params = set(inspect.signature(JsonFileEvidenceStore.between).parameters)
        self.assertEqual(params, {"self", "start", "end"})

    def test_legacy_read_exposes_invoice_without_identity_context(self):
        with tempfile.TemporaryDirectory() as d:
            store = JsonFileEvidenceStore(Path(d) / "invoices.json")
            record = InvoiceRecord(
                order_id="order-1", product="synthetic",
                document_no="INT-001", document_id="invoice-1",
                document_type="E_ARCHIVE_INTERNET", amount=Decimal("10"),
                currency="TRY", issued_at=datetime(2026, 10, 1),
                provider_status="DELIVERED", customer_delivery_id="test1",
                accounting_delivery_id="test2"
            )
            store.add(record)
            # This call has no principal / tenant / authorized resource scope.
            rows = store.between(datetime(2026, 10, 1), datetime(2026, 11, 1))
            self.assertEqual([x.document_id for x in rows], ["invoice-1"])

if __name__ == "__main__":
    unittest.main()
