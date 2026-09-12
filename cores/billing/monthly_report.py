from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MonthlyBillingReport:
    year: int
    month: int
    invoice_count: int
    total_amount: Decimal
    delivered_count: int
    accounting_count: int


class MonthlyReporter:
    def __init__(self, evidence_store):
        self.evidence_store = evidence_store

    def build(self, year: int, month: int) -> MonthlyBillingReport:
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)
        records = list(self.evidence_store.between(start, end))
        return MonthlyBillingReport(
            year=year,
            month=month,
            invoice_count=len(records),
            total_amount=sum((r.amount for r in records), Decimal("0")),
            delivered_count=sum(1 for r in records if r.customer_delivery_id),
            accounting_count=sum(1 for r in records if r.accounting_delivery_id),
        )
