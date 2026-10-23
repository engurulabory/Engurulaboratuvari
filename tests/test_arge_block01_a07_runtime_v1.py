"""A07 G01: actual BillingCore side effects and identity replay oracle.

The G01 lost-ack test intentionally documents an observed unsatisfied guarantee.
CI success means the regression finder worked; it is NOT G01 field PASS.
"""
import unittest
from threading import Event, Thread
from decimal import Decimal

from cores.billing.billing_core import (
    BillingCore, BillingError, BillingRequest, BillingResult, BillingPending, DocumentType,
    MemoryIdempotencyStore, PaymentProof, ProviderReceipt
)

class Registry:
    def is_einvoice_taxpayer(self, tax_identifier):
        return False

class Provider:
    def __init__(self):
        self.calls = 0
    def issue(self, request, document_type):
        self.calls += 1
        return ProviderReceipt("provider-doc-%s" % self.calls, "DOC-%s" % self.calls,
                               "DELIVERED", b"%PDF-dummy", b"")

class Mail:
    def __init__(self, failures=0):
        self.calls = 0
        self.failures = failures
    def send_invoice(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("injected mail acknowledgement loss")
        return "mail-%s" % self.calls

def request(**changes):
    payment = PaymentProof("payment-provider", "payment-01", True, Decimal("100"), "TRY")
    data = dict(
        order_id="order-01", customer_name="Customer A",
        customer_email="a@example.org", tax_identifier="12345678901",
        amount=Decimal("100"), currency="TRY", description="Product",
        payment=payment, idempotency_key="shared-key-01"
    )
    data.update(changes)
    return BillingRequest(**data)

class A07RealBillingTests(unittest.TestCase):
    def setUp(self):
        self.provider = Provider()
        self.mail = Mail()
        self.store = MemoryIdempotencyStore()
        self.core = BillingCore(Registry(), self.provider, self.mail, self.store)

    def test_g01_concurrent_retry_holds_during_provider_call(self):
        started, release = Event(), Event()
        class BlockingProvider(Provider):
            def issue(inner_self, request, document_type):
                started.set()
                if not release.wait(timeout=5):
                    raise RuntimeError("test provider release timeout")
                return super(BlockingProvider, inner_self).issue(request, document_type)
        self.provider = BlockingProvider()
        self.core = BillingCore(Registry(), self.provider, self.mail, self.store)
        errors = []
        def first_call():
            try:
                self.core.issue_paid_order(request())
            except Exception as exc:
                errors.append(type(exc).__name__)
        thread = Thread(target=first_call)
        thread.start()
        try:
            self.assertTrue(started.wait(timeout=5))
            with self.assertRaises(BillingError):
                self.core.issue_paid_order(request())
        finally:
            release.set()
            thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(self.provider.calls, 1)

    def test_g01_memory_store_restart_durability_limit(self):
        self.core.issue_paid_order(request())
        # A new process has a fresh MemoryStore, so a real provider could be
        # called again after restart. Production requires durable reservations.
        self.assertIsNone(MemoryIdempotencyStore().get("shared-key-01"))

    def test_g01_same_request_replay_has_one_effect(self):
        a = self.core.issue_paid_order(request())
        b = self.core.issue_paid_order(request())
        self.assertEqual(a, b)
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.mail.calls, 1)

    def test_g01_cross_customer_same_key_holds_before_new_effect(self):
        self.core.issue_paid_order(request())
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request(customer_email="other@example.org"))
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.mail.calls, 1)

    def test_g01_changed_payment_same_key_holds(self):
        self.core.issue_paid_order(request())
        other = PaymentProof("payment-provider", "payment-02", True, Decimal("100"), "TRY")
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request(payment=other))
        self.assertEqual(self.provider.calls, 1)

    def test_g01_same_key_concurrent_pending_holds(self):
        # Simulate an earlier in-flight reservation by the actual store.
        self.assertIsNone(self.store.reserve("shared-key-01", "fingerprint-one"))
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 0)

    def test_g01_legacy_entry_without_request_binding_holds(self):
        self.store.put("shared-key-01", BillingResult(
            "PASS", DocumentType.E_ARCHIVE_INTERNET,
            ProviderReceipt("legacy-doc", "LEGACY-1", "DELIVERED", b"%PDF"),
            "mail-legacy", {"order_id": "order-01"}
        ))
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 0)

    def test_g01_lost_ack_requires_reconciliation_before_retry(self):
        """A provider issue followed by mail failure leaves a guarded pending state."""
        self.mail = Mail(failures=1)
        self.core = BillingCore(Registry(), self.provider, self.mail, self.store)
        with self.assertRaises(RuntimeError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 1)
        self.assertIsInstance(self.store.get("shared-key-01"), BillingPending)
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 1)
        # This test exercises only an in-memory store. A restart-safe provider
        # reconciliation/durable ledger is still required for G01 acceptance.

if __name__ == "__main__":
    unittest.main()
