import json
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from cores.billing.invoice_record import InvoiceRecord
from cores.billing.access_gate import BillingAccessDenied, require_grant


class JsonFileEvidenceStore:
    """Local persistent evidence store for non-production tests and small deployments.

    Production may replace this with D1/Postgres/S3-backed storage without changing
    the Billing Core contract.
    """

    def __init__(self, path, *, grant_verifier=None):
        self.grant_verifier = grant_verifier
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
                    tenant_id=item.get("tenant_id", ""),
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

    def add(self, record, *, subject=None, grant=None):
        require_grant(self.grant_verifier, subject=subject, tenant_id=record.tenant_id,
                      resource_id=record.document_id, action="billing.invoice.write", grant=grant)
        items = self._load()
        if any(x.order_id == record.order_id for x in items):
            raise ValueError("duplicate order")
        if any(x.document_id == record.document_id for x in items):
            raise ValueError("duplicate document")
        items.append(record)
        self._save(items)

    def between(self, start, end, *, subject=None, tenant_id=None, grant=None):
        require_grant(self.grant_verifier, subject=subject, tenant_id=tenant_id,
                      resource_id=tenant_id, action="billing.invoice.list", grant=grant)
        found = []
        for row in self._load():
            if row.tenant_id != tenant_id or not (start <= row.issued_at < end):
                continue
            require_grant(self.grant_verifier, subject=subject, tenant_id=tenant_id,
                          resource_id=row.document_id, action="billing.invoice.read", grant=grant)
            found.append(row)
        return found
