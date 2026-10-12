import hashlib
import unittest
from decimal import Decimal

from cores.billing.vakifpays_adapter import (
    VakifPaySAdapter,
    VakifPaySConfig,
    VakifPaySError,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, fields):
        self.calls.append((url, dict(fields)))
        if not self.responses:
            raise AssertionError("unexpected transport call")
        return self.responses.pop(0)


class VakifPaySAdapterTests(unittest.TestCase):
    def config(self):
        return VakifPaySConfig(
            merchant="merchant-1",
            merchant_user="user-1",
            merchant_password="pass-1",
            secret_key="secret-1",
            mode="TEST",
        )

    def test_hpp_session_keeps_card_data_outside_enguru(self):
        transport = FakeTransport([
            {"responseCode": "00", "responseMsg": "Approved", "sessionToken": "TOK123"}
        ])
        adapter = VakifPaySAdapter(self.config(), transport)

        session = adapter.create_hpp_session(
            merchant_payment_id="order-1",
            amount=Decimal("12.50"),
            currency="EUR",
            return_url="https://example.test/payment/return",
            customer_id="customer-1",
        )

        self.assertEqual(session.payment_url, "https://testpos.vakifpays.com.tr/merchant/payment/TOK123")
        _, fields = transport.calls[0]
        self.assertEqual(fields["ACTION"], "SESSIONTOKEN")
        self.assertEqual(fields["AMOUNT"], "12.50")
        self.assertEqual(fields["CURRENCY"], "EUR")
        self.assertNotIn("CARDPAN", fields)
        self.assertNotIn("CVV", fields)

    def test_callback_hash_is_integrity_only(self):
        adapter = VakifPaySAdapter(self.config(), FakeTransport([]))
        callback = {
            "merchantPaymentId": "order-1",
            "customerId": "customer-1",
            "sessionToken": "TOK123",
            "responseCode": "00",
            "random": "rnd",
        }
        material = "order-1|customer-1|TOK123|00|rnd|secret-1"
        callback["sdSha512"] = hashlib.sha512(material.encode("utf-8")).hexdigest()

        self.assertTrue(adapter.verify_return_callback(callback))
        callback["responseCode"] = "99"
        self.assertFalse(adapter.verify_return_callback(callback))

    def test_payment_proof_requires_querytransaction_and_exact_identity(self):
        transport = FakeTransport([
            {
                "responseCode": "00",
                "responseMsg": "Approved",
                "transaction": {
                    "merchantPaymentId": "order-1",
                    "pgTranId": "txn-42",
                    "amount": "19.90",
                    "currency": "USD",
                },
            }
        ])
        adapter = VakifPaySAdapter(self.config(), transport)

        proof = adapter.verify_payment(
            merchant_payment_id="order-1",
            expected_amount=Decimal("19.90"),
            expected_currency="USD",
        )

        self.assertTrue(proof.verified)
        self.assertEqual(proof.provider, "VAKIFPAYS")
        self.assertEqual(proof.payment_id, "txn-42")
        self.assertEqual(proof.amount, Decimal("19.90"))
        self.assertEqual(proof.currency, "USD")
        _, fields = transport.calls[0]
        self.assertEqual(fields["ACTION"], "QUERYTRANSACTION")

    def test_amount_mismatch_fails_closed(self):
        transport = FakeTransport([
            {
                "responseCode": "00",
                "transaction": {"pgTranId": "txn-1", "amount": "20.00", "currency": "TRY"},
            }
        ])
        adapter = VakifPaySAdapter(self.config(), transport)
        with self.assertRaises(VakifPaySError):
            adapter.verify_payment(
                merchant_payment_id="order-1",
                expected_amount=Decimal("19.90"),
                expected_currency="TRY",
            )

    def test_provider_rejection_fails_closed(self):
        transport = FakeTransport([
            {"responseCode": "99", "responseMsg": "Declined"}
        ])
        adapter = VakifPaySAdapter(self.config(), transport)
        with self.assertRaises(VakifPaySError):
            adapter.verify_payment(
                merchant_payment_id="order-1",
                expected_amount=Decimal("10.00"),
                expected_currency="TRY",
            )

    def test_extra_fields_cannot_override_authoritative_payment_fields(self):
        adapter = VakifPaySAdapter(
            self.config(),
            FakeTransport([{"responseCode": "00", "sessionToken": "TOK"}]),
        )
        with self.assertRaises(VakifPaySError):
            adapter.create_hpp_session(
                merchant_payment_id="order-1",
                amount=Decimal("10.00"),
                currency="TRY",
                return_url="https://example.test/return",
                customer_id="customer-1",
                extra_fields={"AMOUNT": "1.00"},
            )

    def test_refund_uses_provider_transaction_id(self):
        transport = FakeTransport([
            {"responseCode": "00", "responseMsg": "Approved", "refundType": "FULL"}
        ])
        adapter = VakifPaySAdapter(self.config(), transport)
        result = adapter.refund(
            pg_tran_id="txn-1",
            amount=Decimal("9.99"),
            currency="TRY",
        )
        self.assertEqual(result["refundType"], "FULL")
        _, fields = transport.calls[0]
        self.assertEqual(fields["ACTION"], "REFUND")
        self.assertEqual(fields["PGTRANID"], "txn-1")


if __name__ == "__main__":
    unittest.main()
