"""A07 G01 experimental restart-safe SQLite guard; REVIEW ONLY."""
"""G01 guarded SQLite idempotency reservations for GitHub engineering review.

This is a **non-production** prototype: does not store or replay fiscal documents,
and does not automatically clear pending outcomes. Authorised provider reconciliation,
identity/grants, backup and production storage approval are separate gates.
"""
import re
import sqlite3
from pathlib import Path

from tools.arge_block01_g01_billing_core_prototype_v1 import BillingError, BillingPending, BillingResult

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class SqliteReservationStore:
    """Durable reservation/commit barrier; recovered outcomes always require review."""

    def __init__(self, path):
        self.path = Path(path)
        if self.path.is_symlink() or not self.path.parent.is_dir():
            raise BillingError("A real existing directory and non-symlink DB path are required")
        self.path = self.path.absolute()
        with self._connection() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS billing_reservations ("
                "idem_key TEXT PRIMARY KEY NOT NULL,"
                "request_sha256 TEXT NOT NULL,"
                "state TEXT NOT NULL CHECK(state IN ('PENDING','COMPLETED')))"
            )

    def _connection(self):
        try:
            db = sqlite3.connect(str(self.path), timeout=5, isolation_level=None)
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA busy_timeout=5000")
            return db
        except sqlite3.Error as exc:
            raise BillingError("Reservation storage unavailable") from exc

    @staticmethod
    def _validate(key, digest):
        if not isinstance(key, str) or not key or not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise BillingError("Idempotency key or exact request digest is invalid")

    def _lookup(self, key):
        with self._connection() as db:
            return db.execute(
                "SELECT request_sha256,state FROM billing_reservations WHERE idem_key=?",
                (key,),
            ).fetchone()

    def get(self, key):
        if not isinstance(key, str) or not key:
            raise BillingError("Idempotency key invalid")
        try:
            found = self._lookup(key)
        except sqlite3.Error as exc:
            raise BillingError("Reservation read unavailable") from exc
        if found is None:
            return None
        if found[1] not in ("PENDING", "COMPLETED") or not _DIGEST.fullmatch(found[0]):
            raise BillingError("Reservation state corrupted")
        # Even committed rows cannot replay an invoice without verified receipt
        # and approved provider reconciliation.
        return BillingPending(found[0])

    def reserve(self, key, request_sha256):
        self._validate(key, request_sha256)
        try:
            with self._connection() as db:
                db.execute("BEGIN IMMEDIATE")
                found = db.execute(
                    "SELECT request_sha256,state FROM billing_reservations WHERE idem_key=?",
                    (key,),
                ).fetchone()
                if found is not None:
                    if found[1] not in ("PENDING", "COMPLETED") or not _DIGEST.fullmatch(found[0]):
                        raise BillingError("Reservation state corrupted")
                    db.execute("COMMIT")
                    return BillingPending(found[0])
                db.execute(
                    "INSERT INTO billing_reservations(idem_key,request_sha256,state) VALUES (?,?,?)",
                    (key, request_sha256, "PENDING"),
                )
                db.execute("COMMIT")
                return None
        except sqlite3.Error as exc:
            raise BillingError("Atomic billing reservation unavailable") from exc

    def commit(self, key, value):
        if not isinstance(value, BillingResult):
            raise BillingError("Only a complete billing result may be committed")
        digest = value.evidence.get("request_sha256")
        self._validate(key, digest)
        if value.state != "PASS" or value.evidence.get("idempotency_key") != key:
            raise BillingError("Billing completion evidence mismatched")
        try:
            with self._connection() as db:
                db.execute("BEGIN IMMEDIATE")
                updated = db.execute(
                    "UPDATE billing_reservations SET state='COMPLETED'"
                    " WHERE idem_key=? AND request_sha256=? AND state='PENDING'",
                    (key, digest),
                )
                if updated.rowcount != 1:
                    raise BillingError("No exact pending reservation to commit")
                db.execute("COMMIT")
        except sqlite3.Error as exc:
            raise BillingError("Billing completion evidence could not be committed") from exc
