from dataclasses import dataclass
from enum import Enum


class InvoiceLifecycle(str, Enum):
    ISSUED = "ISSUED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    CANCEL_PENDING = "CANCEL_PENDING"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class LifecycleState:
    document_id: str
    state: InvoiceLifecycle


def transition(current: LifecycleState, target: InvoiceLifecycle) -> LifecycleState:
    allowed = {
        InvoiceLifecycle.ISSUED: {InvoiceLifecycle.REFUND_PENDING, InvoiceLifecycle.CANCEL_PENDING},
        InvoiceLifecycle.REFUND_PENDING: {InvoiceLifecycle.REFUNDED},
        InvoiceLifecycle.CANCEL_PENDING: {InvoiceLifecycle.CANCELLED},
    }
    if target not in allowed.get(current.state, set()):
        raise ValueError(f"invalid transition: {current.state} -> {target}")
    return LifecycleState(current.document_id, target)
