import unittest
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import tempfile
from dataclasses import replace
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

    def test_only_boolean_true_is_verified_even_on_replay(self):
        core = self.build()
        valid = req()
        for flag in (False, None, 0, 1, "false", "true", [], {"verified": True}):
            bad = replace(valid, payment=replace(valid.payment, verified=flag))
            for _ in range(2):
                with self.subTest(flag=flag), self.assertRaises(BillingError):
                    core.issue_paid_order(bad)
        self.assertEqual((self.provider.calls, self.mail.calls), (0, 0))
        result = core.issue_paid_order(valid)
        # A cached success must not bypass validation of a later bad proof.
        with self.assertRaises(BillingError):
            core.issue_paid_order(replace(valid, payment=replace(valid.payment, verified="false")))
        self.assertEqual(core.issue_paid_order(valid), result)
        self.assertEqual((self.provider.calls, self.mail.calls), (1, 1))

    def test_nonfinite_nonpositive_and_untyped_amounts_block_before_dispatch(self):
        core = self.build()
        valid = req()
        for value in (Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN"),
                      Decimal("sNaN"), Decimal("0"), Decimal("-1"), 120, 120.0,
                      "120", True, None):
            for invoice_amount, payment_amount in ((value, value), (valid.amount, value),
                                                   (value, valid.payment.amount)):
                with self.subTest(value=repr(value)), self.assertRaises(BillingError):
                    core.issue_paid_order(replace(valid, amount=invoice_amount,
                        payment=replace(valid.payment, amount=payment_amount)))
        self.assertEqual((self.provider.calls, self.mail.calls), (0, 0))

    def test_payment_identity_currency_and_shape_are_required(self):
        core = self.build()
        valid = req()
        for field in ("provider", "payment_id", "currency"):
            for value in ("", "  ", None, 123):
                with self.subTest(field=field, value=value), self.assertRaises(BillingError):
                    core.issue_paid_order(replace(valid, payment=replace(valid.payment, **{field: value})))
        for value in ("", " ", None, 123):
            with self.assertRaises(BillingError):
                core.issue_paid_order(replace(valid, currency=value))
        for proof in (None, {}, {"verified": True}):
            with self.assertRaises(BillingError):
                core.issue_paid_order(replace(valid, payment=proof))
        with self.assertRaises(BillingError):
            core.issue_paid_order(replace(valid, payment=replace(valid.payment, currency="EUR")))
        self.assertEqual((self.provider.calls, self.mail.calls), (0, 0))

    @unittest.skipUnless(os.name == "posix", "Requires SIGKILL")
    def test_rejected_payment_process_interruption_then_valid_retry(self):
        # Local sandbox side effects are independently observed in a JSON-lines
        # journal. No payment, fiscal, network or mail provider is contacted.
        code = '''
import json, sys
from pathlib import Path
from dataclasses import replace
sys.path.insert(0, "tests")
from test_billing_core import *
path = Path(sys.argv[1])
def record(event):
    with path.open("a") as handle:
        handle.write(json.dumps(event) + "\\n")
        handle.flush()
        os.fsync(handle.fileno())
class SandboxProvider(Provider):
    def issue(self, request, document_type):
        record({"event": "issue", "order": request.order_id})
        return super().issue(request, document_type)
class SandboxMail(Mail):
    def send_invoice(self, **kwargs):
        record({"event": "mail", "order": kwargs["order_id"]})
        return super().send_invoice(**kwargs)
core = BillingCore(Registry(), SandboxProvider(), SandboxMail(), MemoryIdempotencyStore())
valid = req()
if sys.argv[2] == "reject":
    try:
        core.issue_paid_order(replace(valid, payment=replace(valid.payment, verified="false")))
    except BillingError:
        print("REJECTED_BEFORE_DISPATCH", flush=True)
        sys.stdin.read()
    else:
        sys.exit("Invalid payment was accepted")
else:
    first = core.issue_paid_order(valid)
    assert core.issue_paid_order(valid) == first
    print("VALID_RETRY_AND_REPLAY_PASS", flush=True)
'''
        with tempfile.TemporaryDirectory() as tmp:
            journal = Path(tmp) / "sandbox.jsonl"
            command = [sys.executable, "-B", "-c", code, str(journal)]
            child = subprocess.Popen(command + ["reject"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(child.stdout, selectors.EVENT_READ)
                    self.assertTrue(selector.select(timeout=10), "Sandbox startup timeout")
                self.assertEqual(child.stdout.readline().strip(), "REJECTED_BEFORE_DISPATCH")
                self.assertFalse(journal.exists(), "Rejected proof caused a side effect")
                child.kill()
                child.communicate(timeout=10)
                self.assertEqual(child.returncode, -9)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.communicate(timeout=10)
            run = subprocess.run(command + ["valid"], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout.strip(), "VALID_RETRY_AND_REPLAY_PASS")
            self.assertEqual([json.loads(line) for line in journal.read_text().splitlines()],
                [{"event": "issue", "order": "order-1"}, {"event": "mail", "order": "order-1"}])
            print("COMMERCE_SANDBOX: INVALID=BLOCKED; PRE_DISPATCH_SIGKILL=PASS; "
                  "FRESH_PROCESS_VALID_RETRY=PASS; SAME_PROCESS_REPLAY=ONCE")


if __name__ == "__main__":
    unittest.main()
