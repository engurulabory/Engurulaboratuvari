"""A07 G01: actual BillingCore side effects and identity replay oracle.

The G01 lost-ack test intentionally documents an observed unsatisfied guarantee.
CI success means the regression finder worked; it is NOT G01 field PASS.
"""
import unittest
from decimal import Decimal

from cores.billing.billing_core import (
    BillingCore, BillingError, BillingRequest, BillingResult, DocumentType,
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

    def test_g01_legacy_entry_without_request_binding_holds(self):
        self.store.put("shared-key-01", BillingResult(
            "PASS", DocumentType.E_ARCHIVE_INTERNET,
            ProviderReceipt("legacy-doc", "LEGACY-1", "DELIVERED", b"%PDF"),
            "mail-legacy", {"order_id": "order-01"}
        ))
        with self.assertRaises(BillingError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 0)

    def test_g01_lost_ack_exposes_unreconciled_duplicate_effect(self):
        """A known gap: mail failure follows provider issue before store commit."""
        self.mail = Mail(failures=1)
        self.core = BillingCore(Registry(), self.provider, self.mail, self.store)
        with self.assertRaises(RuntimeError):
            self.core.issue_paid_order(request())
        self.assertEqual(self.provider.calls, 1)
        self.assertIsNone(self.store.get("shared-key-01"))
        self.core.issue_paid_order(request())
        # This documents the remaining G01 risk; external provider/durable
        # in-flight ledger reconciliation is mandatory before G01 acceptance.
        self.assertEqual(self.provider.calls, 2)

if __name__ == "__main__":
    unittest.main()
