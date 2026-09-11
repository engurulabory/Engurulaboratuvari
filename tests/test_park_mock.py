import unittest
from decimal import Decimal

from cores.billing.billing_core import BillingRequest, DocumentType, PaymentProof
from cores.billing.park_mock import MockParkAdapter


class ParkMockTests(unittest.TestCase):
    def test_internet_series_prefix(self):
        adapter = MockParkAdapter()
        request = BillingRequest(
            order_id="builder-1",
            customer_name="Customer",
            customer_email="customer@example.com",
            tax_identifier="11111111111",
            amount=Decimal("120.00"),
            currency="TRY",
            description="ENGURU Builder",
            payment=PaymentProof("provider", "payment-1", True, Decimal("120.00"), "TRY"),
        )
        receipt = adapter.issue(request, DocumentType.E_ARCHIVE_INTERNET)
        self.assertTrue(receipt.document_no.startswith("INT2026"))
        self.assertEqual(receipt.status, "DELIVERED")


if __name__ == "__main__":
    unittest.main()
