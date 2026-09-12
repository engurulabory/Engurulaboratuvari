import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord


class JsonFileEvidenceStore:
    """Local persistent evidence store for non-production tests and small deployments.

    Production may replace this with D1/Postgres/S3-backed storage without changing
    the Billing Core contract.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load(self):
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        items = []
        for item in raw:
            items.append(
                InvoiceRecord(
                    order_id=item["order_id"],
                    product=item["product"],
                    document_no=item["document_no"],
                    document_id=item["document_id"],
                    document_type=item["document_type"],
                    amount=Decimal(item["amount"]),
                    currency=item["currency"],
                    issued_at=datetime.fromisoformat(item["issued_at"]),
                    provider_status=item["provider_status"],
                    customer_delivery_id=item["customer_delivery_id"],
                    accounting_delivery_id=item["accounting_delivery_id"],
                )
            )
        return items

    def _save(self, items):
        payload = []
        for item in items:
            row = asdict(item)
            row["amount"] = str(item.amount)
            row["issued_at"] = item.issued_at.isoformat()
            payload.append(row)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, record):
        items = self._load()
        if any(x.order_id == record.order_id for x in items):
            raise ValueError("duplicate order")
        if any(x.document_id == record.document_id for x in items):
            raise ValueError("duplicate document")
        items.append(record)
        self._save(items)

    def between(self, start, end):
        return [x for x in self._load() if start <= x.issued_at < end]
