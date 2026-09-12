from cores.billing.billing_core import DocumentType, ProviderReceipt


class MockParkAdapter:
    def __init__(self, taxpayer=False, status="DELIVERED"):
        self.taxpayer = taxpayer
        self.status = status
        self.calls = 0

    def is_einvoice_taxpayer(self, tax_identifier: str) -> bool:
        return self.taxpayer

    def issue(self, request, document_type: DocumentType) -> ProviderReceipt:
        self.calls += 1
        prefix = {
            DocumentType.E_INVOICE: "ENG",
            DocumentType.E_ARCHIVE: "EGR",
            DocumentType.E_ARCHIVE_INTERNET: "INT",
        }[document_type]
        return ProviderReceipt(
            document_id=f"mock-{request.order_id}",
            document_no=f"{prefix}2026000000001",
            status=self.status,
            pdf_bytes=b"%PDF-mock",
            xml_bytes=b"<Invoice>mock</Invoice>",
        )
