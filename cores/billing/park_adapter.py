from dataclasses import dataclass
from typing import Protocol

from cores.billing.billing_core import BillingError, BillingRequest, DocumentType, ProviderReceipt


class ParkSoapTransport(Protocol):
    def call(self, service: str, action: str, fields: dict) -> dict: ...


@dataclass(frozen=True)
class ParkEndpointTruth:
    efatura_service: str
    earchive_service: str


class ParkAdapter:
    """PARK e-Fatura/e-Arsiv adapter over an authenticated SOAP transport."""

    def __init__(self, transport: ParkSoapTransport, endpoints: ParkEndpointTruth):
        self.transport = transport
        self.endpoints = endpoints

    def authenticate(self) -> str:
        result = self.transport.call("efatura", "Login", {})
        session_id = result.get("session_id")
        if not session_id:
            raise BillingError("PARK Login did not return a session identifier")
        return session_id

    def account_identity(self) -> str:
        result = self.transport.call("efatura", "AccountIdentity", {})
        identity = result.get("legal_name")
        if not identity:
            raise BillingError("PARK account identity proof is inconclusive")
        return identity

    def is_einvoice_taxpayer(self, tax_identifier: str) -> bool:
        if not tax_identifier.strip():
            raise BillingError("Tax identifier is required")
        result = self.transport.call("efatura", "CheckUser", {"tax_identifier": tax_identifier})
        return bool(result.get("registered"))

    def issue(self, request: BillingRequest, document_type: DocumentType) -> ProviderReceipt:
        if document_type is DocumentType.E_INVOICE:
            result = self.transport.call("efatura", "SendInvoice", self._fields(request, document_type))
        else:
            result = self.transport.call("earchive", "WriteToArchiveExtended", self._fields(request, document_type))
        return self._receipt(result)

    def get_status(self, document_id: str, document_type: DocumentType) -> str:
        if document_type is DocumentType.E_INVOICE:
            result = self.transport.call("efatura", "GetInvoiceStatus", {"document_id": document_id})
        else:
            result = self.transport.call("earchive", "GetEArchiveInvoiceStatus", {"document_id": document_id})
        status = result.get("status")
        if not status:
            raise BillingError("PARK status response is inconclusive")
        return str(status)

    def download(self, document_id: str, document_type: DocumentType, output_type: str) -> bytes:
        if document_type is DocumentType.E_INVOICE:
            result = self.transport.call(
                "efatura", "GetInvoiceWithType",
                {"document_id": document_id, "output_type": output_type.upper()},
            )
        else:
            result = self.transport.call(
                "earchive", "ReadFromArchive",
                {"document_id": document_id, "output_type": output_type.upper()},
            )
        content = result.get("content")
        if not isinstance(content, bytes) or not content:
            raise BillingError("PARK document download has no binary content")
        return content

    @staticmethod
    def _fields(request: BillingRequest, document_type: DocumentType) -> dict:
        series = {
            DocumentType.E_INVOICE: "ENG",
            DocumentType.E_ARCHIVE: "EGR",
            DocumentType.E_ARCHIVE_INTERNET: "INT",
        }[document_type]
        return {
            "order_id": request.order_id,
            "idempotency_key": request.idempotency_key or f"invoice:{request.order_id}",
            "series": series,
            "customer_name": request.customer_name,
            "customer_email": request.customer_email,
            "tax_identifier": request.tax_identifier,
            "amount": str(request.amount),
            "currency": request.currency,
            "description": request.description,
        }

    @staticmethod
    def _receipt(result: dict) -> ProviderReceipt:
        document_id = result.get("document_id")
        document_no = result.get("document_no")
        status = result.get("status")
        if not document_id or not document_no or not status:
            raise BillingError("PARK issue response has no canonical document identity/state")
        return ProviderReceipt(
            document_id=str(document_id),
            document_no=str(document_no),
            status=str(status),
            pdf_bytes=result.get("pdf_bytes", b""),
            xml_bytes=result.get("xml_bytes", b""),
        )
