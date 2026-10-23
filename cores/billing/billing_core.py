from dataclasses import dataclass
from hashlib import sha256
import json
from decimal import Decimal
from enum import Enum
from typing import Protocol, Optional, Mapping


class BillingError(RuntimeError):
    pass


class DocumentType(str, Enum):
    E_INVOICE = "E_INVOICE"
    E_ARCHIVE = "E_ARCHIVE"
    E_ARCHIVE_INTERNET = "E_ARCHIVE_INTERNET"


@dataclass(frozen=True)
class PaymentProof:
    provider: str
    payment_id: str
    verified: bool
    amount: Decimal
    currency: str = "TRY"


@dataclass(frozen=True)
class BillingRequest:
    order_id: str
    customer_name: str
    customer_email: str
    tax_identifier: str
    amount: Decimal
    currency: str
    description: str
    payment: PaymentProof
    internet_sale: bool = True
    idempotency_key: Optional[str] = None


@dataclass(frozen=True)
class ProviderReceipt:
    document_id: str
    document_no: str
    status: str
    pdf_bytes: bytes = b""
    xml_bytes: bytes = b""


@dataclass(frozen=True)
class BillingResult:
    state: str
    document_type: DocumentType
    receipt: ProviderReceipt
    mail_message_id: str
    evidence: Mapping[str, str]


class TaxpayerRegistry(Protocol):
    def is_einvoice_taxpayer(self, tax_identifier: str) -> bool: ...


class InvoiceProvider(Protocol):
    def issue(self, request: BillingRequest, document_type: DocumentType) -> ProviderReceipt: ...


class MailDelivery(Protocol):
    def send_invoice(self, *, to: str, customer_name: str, document_no: str,
                     pdf_bytes: bytes, order_id: str) -> str: ...


class IdempotencyStore(Protocol):
    def get(self, key: str) -> Optional[BillingResult]: ...
    def put(self, key: str, value: BillingResult) -> None: ...


class BillingCore:
    ACCEPTED_PROVIDER_STATES = {"ACCEPTED", "DELIVERED", "SUCCESS"}

    def __init__(self, registry, invoice_provider, mail_delivery, idempotency_store):
        self.registry = registry
        self.invoice_provider = invoice_provider
        self.mail_delivery = mail_delivery
        self.idempotency_store = idempotency_store

    def issue_paid_order(self, request: BillingRequest) -> BillingResult:
        self._validate(request)
        key = request.idempotency_key or f"invoice:{request.order_id}"
        request_sha256 = self._request_sha256(request)
        existing = self.idempotency_store.get(key)
        if existing:
            # A key reused for another order/customer/payment must never expose
            # the prior customer receipt. Legacy entries without the digest HOLD.
            if existing.evidence.get("request_sha256") != request_sha256:
                raise BillingError("Idempotency key is bound to another request or unverified legacy record")
            return existing

        is_taxpayer = self.registry.is_einvoice_taxpayer(request.tax_identifier)
        if is_taxpayer:
            document_type = DocumentType.E_INVOICE
        elif request.internet_sale:
            document_type = DocumentType.E_ARCHIVE_INTERNET
        else:
            document_type = DocumentType.E_ARCHIVE

        receipt = self.invoice_provider.issue(request, document_type)
        if receipt.status.upper() not in self.ACCEPTED_PROVIDER_STATES:
            raise BillingError(f"Invoice provider state is not accepted: {receipt.status}")
        if not receipt.document_id or not receipt.document_no:
            raise BillingError("Provider receipt has no canonical document identity")
        if not receipt.pdf_bytes:
            raise BillingError("Official invoice PDF is missing; delivery blocked")

        message_id = self.mail_delivery.send_invoice(
            to=request.customer_email,
            customer_name=request.customer_name,
            document_no=receipt.document_no,
            pdf_bytes=receipt.pdf_bytes,
            order_id=request.order_id,
        )
        if not message_id:
            raise BillingError("Mail delivery evidence is missing")

        result = BillingResult(
            state="PASS",
            document_type=document_type,
            receipt=receipt,
            mail_message_id=message_id,
            evidence={
                "order_id": request.order_id,
                "payment_provider": request.payment.provider,
                "payment_id": request.payment.payment_id,
                "document_id": receipt.document_id,
                "document_no": receipt.document_no,
                "provider_status": receipt.status,
                "mail_message_id": message_id,
                "idempotency_key": key,
                "request_sha256": request_sha256,
            },
        )
        self.idempotency_store.put(key, result)
        return result

    @staticmethod
    def _request_sha256(request: BillingRequest) -> str:
        """Bind the replay key to the exact payment and recipient request.

        A digest is a comparison marker, not an authorization grant. In-flight
        lost acknowledgements still require durable provider reconciliation.
        """
        fingerprint = {
            "order_id": request.order_id,
            "customer_name": request.customer_name,
            "customer_email": request.customer_email,
            "tax_identifier": request.tax_identifier,
            "amount": str(request.amount),
            "currency": request.currency,
            "description": request.description,
            "internet_sale": request.internet_sale,
            "payment_provider": request.payment.provider,
            "payment_id": request.payment.payment_id,
            "payment_amount": str(request.payment.amount),
            "payment_currency": request.payment.currency,
            "payment_verified": request.payment.verified,
        }
        data = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate(request: BillingRequest) -> None:
        if not request.payment.verified:
            raise BillingError("Payment proof is not verified")
        if request.payment.amount != request.amount:
            raise BillingError("Payment amount mismatch")
        if request.payment.currency != request.currency:
            raise BillingError("Payment currency mismatch")
        if request.amount <= 0:
            raise BillingError("Invoice amount must be positive")
        if not request.order_id.strip():
            raise BillingError("order_id is required")
        if "@" not in request.customer_email:
            raise BillingError("Valid customer email is required")
        if not request.tax_identifier.strip():
            raise BillingError("Tax/TCKN identifier is required")


class MemoryIdempotencyStore:
    def __init__(self):
        self._items = {}

    def get(self, key):
        return self._items.get(key)

    def put(self, key, value):
        if key in self._items:
            raise BillingError("Duplicate idempotency key")
        self._items[key] = value
