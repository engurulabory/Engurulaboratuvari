import tempfile
import unittest
import json
import hashlib
import os
import subprocess
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord
from cores.billing.persistent_store import JsonFileEvidenceStore
from cores.billing.monthly_report import MonthlyReporter
from unittest.mock import patch


class PersistentStoreTests(unittest.TestCase):
    def make_record(self, order_id="o1", document_id="d1"):
        return InvoiceRecord(
            order_id=order_id,
            product="ENGURU Builder",
            document_no="INT1",
            document_id=document_id,
            document_type="E_ARCHIVE_INTERNET",
            amount=Decimal("100"),
            currency="TRY",
            issued_at=datetime(2026, 9, 11, 12, 0, 0),
            provider_status="DELIVERED",
            customer_delivery_id="m1",
            accounting_delivery_id="a1",
        )

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileEvidenceStore(Path(tmp) / "billing.json")
            store.add(self.make_record())
            rows = store.between(datetime(2026, 9, 1), datetime(2026, 10, 1))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].order_id, "o1")

    def test_duplicate_order_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = JsonFileEvidenceStore(Path(tmp) / "billing.json")
            store.add(self.make_record())
            with self.assertRaises(ValueError):
                store.add(self.make_record(document_id="d2"))

    @unittest.skipUnless(os.name == "posix", "Requires POSIX file-size resource limit")
    def test_real_partial_write_failure_preserves_committed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "billing.json"
            store = JsonFileEvidenceStore(path)
            store.add(self.make_record())
            committed = path.read_bytes()
            # A separate OS process hits a real kernel-enforced write limit.
            # This exercises actual disk I/O; the evidence store is not mocked.
            code = '''
import resource, signal, sys
from dataclasses import replace
from cores.billing.persistent_store import JsonFileEvidenceStore
signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
store = JsonFileEvidenceStore(sys.argv[1])
first = store._load()[0]
limit = len(store.path.read_bytes()) + 64
resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
try:
    store.add(replace(first, order_id="o2", document_id="d2", product="X" * 4096))
except OSError:
    print("WRITE_LIMIT_REACHED")
    sys.exit(0)
sys.exit("Expected a real write failure")
'''
            run = subprocess.run([sys.executable, "-B", "-c", code, str(path)],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout.strip(), "WRITE_LIMIT_REACHED")
            self.assertEqual(path.read_bytes(), committed)
            self.assertEqual(list(Path(tmp).iterdir()), [path])
            self.assertEqual(MonthlyReporter(JsonFileEvidenceStore(path)).build(2026, 9).invoice_count, 1)

    def test_failed_publication_preserves_committed_evidence_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "billing.json"
            store = JsonFileEvidenceStore(path)
            store.add(self.make_record())
            committed = path.read_bytes()
            with patch("os.replace", side_effect=OSError("publish failure")):
                with self.assertRaises(OSError):
                    store.add(self.make_record(order_id="o2", document_id="d2"))
            self.assertEqual(path.read_bytes(), committed)
            self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_fresh_process_reopens_and_reports_successful_retry_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "billing.json"
            store = JsonFileEvidenceStore(path)
            store.add(self.make_record())
            code = '''
import json, sys
from dataclasses import replace
from decimal import Decimal
from cores.billing.persistent_store import JsonFileEvidenceStore
from cores.billing.monthly_report import MonthlyReporter
store = JsonFileEvidenceStore(sys.argv[1])
first = store._load()[0]
if len(sys.argv) > 2:
    store.add(replace(first, order_id="o2", document_id="d2", amount=Decimal("50")))
report = MonthlyReporter(store).build(2026, 9)
print(json.dumps({"invoice_count":report.invoice_count, "total_amount":str(report.total_amount),
                  "delivered_count":report.delivered_count, "accounting_count":report.accounting_count},
                 sort_keys=True))
'''
            command = [sys.executable, "-B", "-c", code, str(path)]
            first_run = subprocess.run(command + ["append"], capture_output=True, text=True, timeout=10)
            self.assertEqual(first_run.returncode, 0, first_run.stderr)
            self.assertEqual(json.loads(first_run.stdout), {"invoice_count": 2, "total_amount": "150",
                                                           "delivered_count": 2, "accounting_count": 2})
            reopened = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(reopened.returncode, 0, reopened.stderr)
            self.assertEqual(reopened.stdout, first_run.stdout)
            # Separate stdlib JSON reader checks published bytes without the
            # product reader/report implementation supplying its own oracle.
            raw_records = json.loads(path.read_bytes())
            self.assertEqual([row["order_id"] for row in raw_records], ["o1", "o2"])
            self.assertEqual(sum(Decimal(row["amount"]) for row in raw_records), Decimal("150"))
            print("BILL_08_TEST_RECORDS_REPORT=" + first_run.stdout.strip())
            print("BILL_08_REPORT_SHA256=" + hashlib.sha256(first_run.stdout.encode()).hexdigest())
            with self.assertRaises(ValueError):
                JsonFileEvidenceStore(path).add(self.make_record(order_id="o2", document_id="d2"))

    def test_abrupt_process_exit_before_publication_keeps_last_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "billing.json"
            store = JsonFileEvidenceStore(path)
            store.add(self.make_record())
            committed = path.read_bytes()
            code = '''
import os, sys
from dataclasses import replace
from cores.billing.persistent_store import JsonFileEvidenceStore
store = JsonFileEvidenceStore(sys.argv[1])
first = store._load()[0]
# Actual abrupt process termination at the atomic publication boundary.
# No Python exception/finally cleanup runs; all prior file I/O is real.
os.replace = lambda *args: os._exit(86)
store.add(replace(first, order_id="o2", document_id="d2"))
'''
            run = subprocess.run([sys.executable, "-B", "-c", code, str(path)],
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 86, run.stderr)
            self.assertEqual(path.read_bytes(), committed)
            # The OS may retain the abandoned temp file. It is never read as
            # committed evidence; normal retry starts from the original file.
            reopened = JsonFileEvidenceStore(path)
            reopened.add(self.make_record(order_id="o2", document_id="d2"))
            self.assertEqual(MonthlyReporter(JsonFileEvidenceStore(path)).build(2026, 9).invoice_count, 2)


if __name__ == "__main__":
    unittest.main()
