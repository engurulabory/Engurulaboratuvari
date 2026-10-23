"""A07 G02: actual invoice evidence read and report authorization contract.

All verifier grants below are synthetic test doubles, not canonical owner-issued
grants. Field G02 and external verifier integration remain HOLD.
"""
import json
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.access_gate import BillingAccessDenied
from cores.billing.evidence_store import MemoryEvidenceStore
from cores.billing.invoice_record import InvoiceRecord
from cores.billing.monthly_report import MonthlyReporter
from cores.billing.persistent_store import JsonFileEvidenceStore


class SyntheticVerifier:
    """Local adversarial fixture; no private keys, issuer or production authority."""
    def __init__(self):
        self.blocked = set()
        self.calls = []

    def authorize(self, *, subject, tenant_id, resource_id, action, grant):
        self.calls.append((subject,tenant_id,resource_id,action))
        return bool(
            subject == "actor-" + tenant_id
            and grant == "SYNTHETIC-" + tenant_id
            and action in {"billing.invoice.write","billing.invoice.list","billing.invoice.read"}
            and (tenant_id,resource_id,action) not in self.blocked
        )


def row(tenant_id, suffix):
    return InvoiceRecord(
        order_id="order-" + suffix, product="synthetic", document_no="INT-" + suffix,
        document_id="doc-" + suffix, document_type="E_ARCHIVE_INTERNET",
        amount=Decimal("10"), currency="TRY", issued_at=datetime(2026, 10, 1),
        provider_status="DELIVERED", customer_delivery_id="test",
        accounting_delivery_id="test", tenant_id=tenant_id,
    )


def auth(tenant):
    return {"subject":"actor-"+tenant,"tenant_id":tenant,"grant":"SYNTHETIC-"+tenant}


class G02ActualAccessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.verifier = SyntheticVerifier()
        self.store = JsonFileEvidenceStore(
            Path(self.temp.name)/"invoices.json",grant_verifier=self.verifier)
        self.store.add(row("tenant-a","a"), subject=auth("tenant-a")["subject"],
                       grant=auth("tenant-a")["grant"])
        self.store.add(row("tenant-b","b"), subject=auth("tenant-b")["subject"],
                       grant=auth("tenant-b")["grant"])
        self.start=datetime(2026,10,1)
        self.end=datetime(2026,11,1)

    def test_no_verifier_holds_instead_of_listing(self):
        orphan=JsonFileEvidenceStore(Path(self.temp.name)/"invoices.json")
        with self.assertRaises(BillingAccessDenied):
            orphan.between(self.start,self.end,**auth("tenant-a"))

    def test_blank_grant_holds(self):
        with self.assertRaises(BillingAccessDenied):
            self.store.between(self.start,self.end,subject="actor-tenant-a",
                               tenant_id="tenant-a")

    def test_tenant_a_only_sees_own_invoice(self):
        result=self.store.between(self.start,self.end,**auth("tenant-a"))
        self.assertEqual([x.document_id for x in result],["doc-a"])
        self.assertTrue(any(x[3]=="billing.invoice.read" for x in self.verifier.calls))

    def test_tenant_b_only_sees_own_invoice(self):
        result=self.store.between(self.start,self.end,**auth("tenant-b"))
        self.assertEqual([x.document_id for x in result],["doc-b"])

    def test_cross_tenant_stolen_grant_holds(self):
        with self.assertRaises(BillingAccessDenied):
            self.store.between(self.start,self.end,subject="actor-tenant-a",
                               tenant_id="tenant-b",grant="SYNTHETIC-tenant-a")

    def test_resource_specific_denial_blocks_full_read(self):
        self.verifier.blocked.add(("tenant-a","doc-a","billing.invoice.read"))
        with self.assertRaises(BillingAccessDenied):
            self.store.between(self.start,self.end,**auth("tenant-a"))

    def test_unauthorized_write_holds(self):
        with self.assertRaises(BillingAccessDenied):
            self.store.add(row("tenant-c","c"),subject="actor-tenant-a",
                           grant="SYNTHETIC-tenant-a")

    def test_monthly_report_rejects_legacy_ungated_read(self):
        with self.assertRaises(BillingAccessDenied):
            MonthlyReporter(self.store).build(2026,10)

    def test_monthly_report_is_tenant_scoped(self):
        report=MonthlyReporter(self.store).build(2026,10,**auth("tenant-a"))
        self.assertEqual(report.invoice_count,1)
        self.assertEqual(report.total_amount,Decimal("10"))

    def test_historical_unowned_record_is_invisible_pending_migration(self):
        path=Path(self.temp.name)/"invoices.json"
        payload=json.loads(path.read_text(encoding="utf-8"))
        legacy=dict(payload[0],order_id="legacy-order",document_id="legacy-document")
        legacy.pop("tenant_id",None)
        payload.append(legacy)
        path.write_text(json.dumps(payload),encoding="utf-8")
        result=self.store.between(self.start,self.end,**auth("tenant-a"))
        self.assertEqual([x.document_id for x in result],["doc-a"])

    def test_memory_store_follows_identical_guard(self):
        mem=MemoryEvidenceStore(grant_verifier=self.verifier)
        mem.add(row("tenant-a","memory"),subject="actor-tenant-a",
                grant="SYNTHETIC-tenant-a")
        with self.assertRaises(BillingAccessDenied):
            mem.between(self.start,self.end)
        self.assertEqual(len(mem.between(self.start,self.end,**auth("tenant-a"))),1)

    def test_verifier_unavailable_fails_closed(self):
        class OfflineVerifier:
            def authorize(self,**kwargs):
                raise ConnectionError("injected verifier outage")
        self.store.grant_verifier=OfflineVerifier()
        with self.assertRaises(BillingAccessDenied):
            self.store.between(self.start,self.end,**auth("tenant-a"))

if __name__=="__main__":
    unittest.main()
