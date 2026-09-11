import unittest
from decimal import Decimal
from cores.billing.billing_core import BillingCore, BillingError, BillingRequest, PaymentProof, ProviderReceipt, DocumentType, MemoryIdempotencyStore


class Registry:
    def __init__(self, taxpayer=False): self.taxpayer = taxpayer
    def is_einvoice_taxpayer(self, tax_identifier): return self.taxpayer


class Provider:
    def __init__(self, status="DELIVERED"):
        self.status = status
        self.calls = 0
        self.last_type = None
    def issue(self, request, document_type):
        self.calls += 1
        self.last_type = document_type
        return ProviderReceipt("ettn-1", "INT2026000000001", self.status, b"%PDF-test", b"<Invoice/>")


class Mail:
    def __init__(self): self.calls = 0
    def send_invoice(self, **kwargs):
        self.calls += 1
        return "mail-1"


def req(**changes):
    data = dict(
        order_id="order-1",
        customer_name="Musteri",
        customer_email="musteri@example.com",
        tax_identifier="11111111111",
        amount=Decimal("120.00"),
        currency="TRY",
        description="ENGURU product",
        payment=PaymentProof("payment-provider", "pay-1", True, Decimal("120.00"), "TRY"),
        internet_sale=True,
    )
    data.update(changes)
    return BillingRequest(**data)


class BillingCoreTests(unittest.TestCase):
    def build(self, taxpayer=False, provider_status="DELIVERED"):
        self.provider = Provider(provider_status)
        self.mail = Mail()
        return BillingCore(Registry(taxpayer), self.provider, self.mail, MemoryIdempotencyStore())

    def test_taxpayer_routes_to_einvoice(self):
        result = self.build(taxpayer=True).issue_paid_order(req())
        self.assertEqual(result.state, "PASS")
        self.assertEqual(result.document_type, DocumentType.E_INVOICE)

    def test_internet_non_taxpayer_routes_to_earchive_internet(self):
        result = self.build().issue_paid_order(req())
        self.assertEqual(result.document_type, DocumentType.E_ARCHIVE_INTERNET)

    def test_unverified_payment_blocks(self):
        core = self.build()
        bad = req(payment=PaymentProof("payment-provider", "pay-1", False, Decimal("120.00"), "TRY"))
        with self.assertRaises(BillingError):
            core.issue_paid_order(bad)
        self.assertEqual(self.provider.calls, 0)

    def test_provider_failure_blocks_mail(self):
        core = self.build(provider_status="FAILED")
        with self.assertRaises(BillingError):
            core.issue_paid_order(req())
        self.assertEqual(self.mail.calls, 0)

    def test_idempotency_prevents_duplicate_invoice_and_mail(self):
        core = self.build()
        a = core.issue_paid_order(req())
        b = core.issue_paid_order(req())
        self.assertEqual(a, b)
        self.assertEqual(self.provider.calls, 1)
        self.assertEqual(self.mail.calls, 1)

    def test_payment_amount_mismatch_blocks(self):
        core = self.build()
        bad = req(payment=PaymentProof("payment-provider", "pay-1", True, Decimal("119.99"), "TRY"))
        with self.assertRaises(BillingError):
            core.issue_paid_order(bad)


if __name__ == "__main__":
    unittest.main()
