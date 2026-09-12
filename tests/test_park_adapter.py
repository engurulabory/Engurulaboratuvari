import unittest
from decimal import Decimal

from cores.billing.billing_core import BillingError, BillingRequest, DocumentType, PaymentProof
from cores.billing.park_adapter import ParkAdapter, ParkEndpointTruth


class FakeTransport:
    def __init__(self):
        self.calls = []

    def call(self, service, action, fields):
        self.calls.append((service, action, fields))
        if action == "Login":
            return {"session_id": "session-1"}
        if action == "WhoAmI":
            return {"legal_name": "ENGURU MAYA"}
        if action == "CheckUser":
            return {"registered": True}
        if action in {"SendInvoice", "WriteToArchiveExtended"}:
            return {
                "document_id": "doc-1",
                "document_no": "INT2026000000001" if action == "WriteToArchiveExtended" else "ENG2026000000001",
                "status": "DELIVERED",
                "pdf_bytes": b"%PDF",
                "xml_bytes": b"<Invoice/>",
            }
        if action in {"GetInvoiceStatus", "GetEArchiveInvoiceStatus"}:
            return {"status": "DELIVERED"}
        if action in {"GetInvoiceWithType", "ReadFromArchive"}:
            return {"content": b"artifact"}
        return {}


def request():
    return BillingRequest(
        order_id="order-1",
        customer_name="Test Customer",
        customer_email="test@example.com",
        tax_identifier="1234567890",
        amount=Decimal("10.00"),
        currency="TRY",
        description="Test",
        payment=PaymentProof(provider="test", payment_id="pay-1", verified=True, amount=Decimal("10.00")),
        internet_sale=True,
        idempotency_key="idem-1",
    )


class ParkAdapterTests(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.adapter = ParkAdapter(
            self.transport,
            ParkEndpointTruth("efatura", "earchive", account_identity_action="WhoAmI"),
        )

    def test_login_requires_session(self):
        self.assertEqual(self.adapter.authenticate(), "session-1")

    def test_account_identity_uses_provider_confirmed_action(self):
        self.assertEqual(self.adapter.account_identity(), "ENGURU MAYA")
        self.assertIn(("efatura", "WhoAmI", {}), self.transport.calls)

    def test_missing_identity_action_fails_closed(self):
        adapter = ParkAdapter(self.transport, ParkEndpointTruth("efatura", "earchive"))
        with self.assertRaises(BillingError):
            adapter.account_identity()

    def test_taxpayer_lookup(self):
        self.assertTrue(self.adapter.is_einvoice_taxpayer("1234567890"))

    def test_einvoice_issue(self):
        receipt = self.adapter.issue(request(), DocumentType.E_INVOICE)
        self.assertEqual(receipt.document_no[:3], "ENG")

    def test_internet_earchive_uses_int_series(self):
        self.adapter.issue(request(), DocumentType.E_ARCHIVE_INTERNET)
        service, action, fields = self.transport.calls[-1]
        self.assertEqual(service, "earchive")
        self.assertEqual(action, "WriteToArchiveExtended")
        self.assertEqual(fields["series"], "INT")

    def test_status_and_download(self):
        status = self.adapter.get_status("doc-1", DocumentType.E_ARCHIVE_INTERNET)
        artifact = self.adapter.download("doc-1", DocumentType.E_ARCHIVE_INTERNET, "PDF")
        self.assertEqual(status, "DELIVERED")
        self.assertEqual(artifact, b"artifact")

    def test_missing_download_content_fails_closed(self):
        class EmptyTransport(FakeTransport):
            def call(self, service, action, fields):
                return {}
        adapter = ParkAdapter(
            EmptyTransport(),
            ParkEndpointTruth("efatura", "earchive", account_identity_action="WhoAmI"),
        )
        with self.assertRaises(BillingError):
            adapter.download("doc-1", DocumentType.E_INVOICE, "PDF")


if __name__ == "__main__":
    unittest.main()
