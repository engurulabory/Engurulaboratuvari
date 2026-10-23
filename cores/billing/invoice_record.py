from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class InvoiceRecord:
    order_id: str
    product: str
    document_no: str
    document_id: str
    document_type: str
    amount: Decimal
    currency: str
    issued_at: datetime
    provider_status: str
    customer_delivery_id: str
    accounting_delivery_id: str
