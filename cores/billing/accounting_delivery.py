class AccountingDelivery:
    def send_invoice_copy(self, *, request, result) -> str:
        raise NotImplementedError


class MockAccountingDelivery(AccountingDelivery):
    def __init__(self):
        self.sent = []

    def send_invoice_copy(self, *, request, result) -> str:
        delivery_id = f"acct-{request.order_id}"
        self.sent.append((request.order_id, result.receipt.document_no))
        return delivery_id
