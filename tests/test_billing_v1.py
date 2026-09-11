import unittest
from datetime import datetime
from decimal import Decimal

from cores.billing.accounting_delivery import MockAccountingDelivery
from cores.billing.evidence_store import MemoryEvidenceStore
from cores.billing.invoice_record import InvoiceRecord
from cores.billing.monthly_report import MonthlyReporter
from cores.billing.refund_state import InvoiceLifecycle, LifecycleState, transition
from cores.billing.retry_policy import RetryPolicy
from cores.billing.ubl_factory import UblFactory
from cores.billing.billing_core import BillingRequest, PaymentProof, DocumentType


class BillingV1Tests(unittest.TestCase):
    def test_evidence_store_blocks_duplicates(self):
        store = MemoryEvidenceStore()
        record = InvoiceRecord(
            order_id="o1", product="Builder", document_no="INT1", document_id="d1",
            document_type="E_ARCHIVE_INTERNET", amount=Decimal("100"), currency="TRY",
            issued_at=datetime(2026, 9, 1), provider_status="DELIVERED",
            customer_delivery_id="m1", accounting_delivery_id="a1"
        )
        store.add(record)
        with self.assertRaises(ValueError):
            store.add(record)

    def test_monthly_report(self):
        store = MemoryEvidenceStore()
        store.add(InvoiceRecord("o1","Builder","INT1","d1","E_ARCHIVE_INTERNET",Decimal("100"),"TRY",datetime(2026,9,1),"DELIVERED","m1","a1"))
        store.add(InvoiceRecord("o2","Builder","INT2","d2","E_ARCHIVE_INTERNET",Decimal("50"),"TRY",datetime(2026,9,2),"DELIVERED","m2","a2"))
        report = MonthlyReporter(store).build(2026, 9)
        self.assertEqual(report.invoice_count, 2)
        self.assertEqual(report.total_amount, Decimal("150"))
        self.assertEqual(report.delivered_count, 2)
        self.assertEqual(report.accounting_count, 2)

    def test_accounting_delivery_contract(self):
        delivery = MockAccountingDelivery()
        request = BillingRequest("o1","Can","can@example.com","11111111111",Decimal("10"),"TRY","Builder",PaymentProof("p","1",True,Decimal("10"),"TRY"))
        class Receipt: document_no = "INT1"
        class Result: receipt = Receipt()
        delivery_id = delivery.send_invoice_copy(request=request, result=Result())
        self.assertEqual(delivery_id, "acct-o1")

    def test_refund_state_machine(self):
        state = LifecycleState("d1", InvoiceLifecycle.ISSUED)
        pending = transition(state, InvoiceLifecycle.REFUND_PENDING)
        done = transition(pending, InvoiceLifecycle.REFUNDED)
        self.assertEqual(done.state, InvoiceLifecycle.REFUNDED)
        with self.assertRaises(ValueError):
            transition(done, InvoiceLifecycle.CANCELLED)

    def test_retry_policy_is_bounded(self):
        calls = {"n": 0}
        def op():
            calls["n"] += 1
            if calls["n"] < 3:
                raise TimeoutError("temporary")
            return "ok"
        result = RetryPolicy(max_attempts=3).run(op, lambda exc: isinstance(exc, TimeoutError))
        self.assertEqual(result, "ok")
        self.assertEqual(calls["n"], 3)

    def test_ubl_factory_series_contract(self):
        request = BillingRequest("o1","Can","can@example.com","11111111111",Decimal("10"),"TRY","Builder",PaymentProof("p","1",True,Decimal("10"),"TRY"))
        doc = UblFactory().build(request=request, document_type=DocumentType.E_ARCHIVE_INTERNET, series="INT")
        self.assertEqual(doc.series, "INT")
        with self.assertRaises(ValueError):
            UblFactory().build(request=request, document_type=DocumentType.E_ARCHIVE_INTERNET, series="XX")


if __name__ == "__main__":
    unittest.main()
