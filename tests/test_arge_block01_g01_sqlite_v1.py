"""A07 G01 adversarial SQLite durability: real BillingCore invocation and restart."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

from tools.arge_block01_g01_billing_core_prototype_v1 import BillingCore, BillingError, BillingPending, BillingRequest, PaymentProof, ProviderReceipt
from tools.arge_block01_g01_sqlite_reservation_v1 import SqliteReservationStore


def digest(ch="a"):
    return ch * 64


class Provider:
    def __init__(self):
        self.calls = 0

    def issue(self, request, document_type):
        self.calls += 1
        return ProviderReceipt("d1", "f1", "DELIVERED", b"PDF")


class Registry:
    def is_einvoice_taxpayer(self, identifier):
        return False


class Mail:
    def __init__(self, broken=False):
        self.broken = broken

    def send_invoice(self, **kwargs):
        if self.broken:
            raise RuntimeError("injected mail acknowledgement loss")
        return "mail1"


def req(**kw):
    data = dict(
        order_id="order1", customer_name="User One", customer_email="user@example.org",
        tax_identifier="12345678901", amount=Decimal("2"), currency="TRY",
        description="Synthetic", payment=PaymentProof("provider", "p1", True, Decimal("2"), "TRY"),
        idempotency_key="k1"
    )
    data.update(kw)
    return BillingRequest(**data)


class SqliteG01Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "reservation.db"
        self.store = SqliteReservationStore(self.path)
        self.provider = Provider()

    def core(self, store=None, broken=False):
        return BillingCore(Registry(), self.provider, Mail(broken), store or self.store)

    def test_initial_reservation_then_restart_stays_pending(self):
        self.assertIsNone(self.store.reserve("k1", digest()))
        recovered = SqliteReservationStore(self.path)
        self.assertIsInstance(recovered.get("k1"), BillingPending)
        self.assertEqual(recovered.reserve("k1", digest()).request_sha256, digest())

    def test_cross_payment_digest_blocks_after_restart(self):
        self.assertIsNone(self.store.reserve("k1", digest()))
        recovered = SqliteReservationStore(self.path)
        self.assertEqual(recovered.reserve("k1", digest("b")).request_sha256, digest())
        with self.assertRaises(BillingError):
            self.core(recovered).issue_paid_order(req())
        self.assertEqual(self.provider.calls, 0)

    def test_mail_lost_ack_restart_blocks_double_issue(self):
        with self.assertRaises(RuntimeError):
            self.core(broken=True).issue_paid_order(req())
        self.assertEqual(self.provider.calls, 1)
        restarted = SqliteReservationStore(self.path)
        with self.assertRaises(BillingError):
            self.core(restarted).issue_paid_order(req())
        self.assertEqual(self.provider.calls, 1)

    def test_completed_row_restart_requires_authorized_reconciliation(self):
        initial = self.core().issue_paid_order(req())
        self.assertEqual(initial.state, "PASS")
        self.assertEqual(self.provider.calls, 1)
        reopened = SqliteReservationStore(self.path)
        with self.assertRaises(BillingError):
            self.core(reopened).issue_paid_order(req())
        self.assertEqual(self.provider.calls, 1)

    def test_competing_reservations_allow_one_winner(self):
        def worker(_):
            store = SqliteReservationStore(self.path)
            return store.reserve("new", digest())
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(worker, range(5)))
        self.assertEqual(results.count(None), 1)
        self.assertEqual(sum(isinstance(x, BillingPending) for x in results), 4)

    def test_commit_without_matching_reservation_holds(self):
        result = self.core().issue_paid_order(req())
        with self.assertRaises(BillingError):
            self.store.commit("k2", result)
        with self.assertRaises(BillingError):
            self.store.commit("k1", result)

    def test_missing_parent_directory_holds(self):
        with self.assertRaises(BillingError):
            SqliteReservationStore(Path(self.tmp.name) / "missing" / "res.db")

    def test_db_symlink_holds(self):
        symlink = Path(self.tmp.name) / "link.db"
        symlink.symlink_to(self.path)
        with self.assertRaises(BillingError):
            SqliteReservationStore(symlink)

    def test_source_is_not_an_official_provider_receipt(self):
        # The persistent ledger intentionally stores no PDF, tax identifier, email
        # or self-awarded acceptance receipt.
        self.core().issue_paid_order(req())
        raw = self.path.read_bytes()
        self.assertNotIn(b"user@example.org", raw)
        self.assertNotIn(b"12345678901", raw)
        self.assertNotIn(b"PDF", raw)

if __name__ == "__main__":
    unittest.main()
