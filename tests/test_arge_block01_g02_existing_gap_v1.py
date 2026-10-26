"""A07 G02 review-only: characterize real billing access gap and test an isolated guard.

Existing product billing behavior is unchanged. PASS in this suite denotes
correct gap detection and hypothetical guard behavior, NOT G02 field acceptance.
"""
import inspect
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord
from cores.billing.persistent_store import JsonFileEvidenceStore
from cores.billing.evidence_store import MemoryEvidenceStore
from cores.billing.monthly_report import MonthlyReporter
from tools.arge_block01_g02_access_gate_v1 import require_grant, BillingAccessDenied


class TestVerifier:
    def authorize(self, *, subject, tenant_id, resource_id, action, grant):
        return (subject == "synthetic-tenant-a" and tenant_id == "tenant-a"
                and resource_id == "invoice-a" and action == "billing.invoice.read"
                and grant == "SYNTHETIC_ONLY")


def record():
    return InvoiceRecord(
        order_id="o1", product="synthetic", document_no="INT-1", document_id="invoice-a",
        document_type="E_ARCHIVE_INTERNET", amount=Decimal("10"), currency="TRY",
        issued_at=datetime(2026, 10, 1), provider_status="DELIVERED",
        customer_delivery_id="test", accounting_delivery_id="test"
    )


class G02ScopeTests(unittest.TestCase):
    def test_original_invoice_schema_lacks_tenant_scope(self):
        self.assertNotIn("tenant_id", InvoiceRecord.__dataclass_fields__)

    def test_unprotected_read_signature_confirmed(self):
        self.assertEqual(set(inspect.signature(JsonFileEvidenceStore.between).parameters),
                         {"self", "start", "end"})
        self.assertEqual(set(inspect.signature(MemoryEvidenceStore.between).parameters),
                         {"self", "start", "end"})

    def test_existing_product_can_read_without_auth_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileEvidenceStore(Path(tmp) / "invoices.json")
            store.add(record())
            records = store.between(datetime(2026,10,1), datetime(2026,11,1))
            self.assertEqual([r.document_id for r in records], ["invoice-a"])
            report = MonthlyReporter(store).build(2026, 10)
            self.assertEqual(report.invoice_count, 1)

    def test_isolated_guard_denies_missing_verifier_and_fake_grant(self):
        args = dict(subject="synthetic-tenant-a", tenant_id="tenant-a",
                    resource_id="invoice-a", action="billing.invoice.read",
                    grant="SYNTHETIC_ONLY")
        with self.assertRaises(BillingAccessDenied):
            require_grant(None, **args)
        with self.assertRaises(BillingAccessDenied):
            require_grant(TestVerifier(), **dict(args, grant="ATTACKER"))

    def test_isolated_guard_does_not_create_canonical_grant(self):
        result = require_grant(
            TestVerifier(), subject="synthetic-tenant-a", tenant_id="tenant-a",
            resource_id="invoice-a", action="billing.invoice.read",
            grant="SYNTHETIC_ONLY")
        self.assertIsNone(result)

    def test_cross_tenant_isolated_guard_holds(self):
        with self.assertRaises(BillingAccessDenied):
            require_grant(TestVerifier(),subject="synthetic-tenant-a",tenant_id="tenant-b",
                          resource_id="invoice-a",action="billing.invoice.read",
                          grant="SYNTHETIC_ONLY")


if __name__ == "__main__":
    unittest.main()
