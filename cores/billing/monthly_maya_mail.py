from dataclasses import dataclass


@dataclass(frozen=True)
class MonthlyMail:
    subject: str
    body: str


class MonthlyMayaMailRenderer:
    def render(self, report) -> MonthlyMail:
        subject = f"ENGÜRÜ Maya — {report.year}-{report.month:02d} Fatura Özeti"
        attention = ""
        if report.invoice_count != report.delivered_count or report.invoice_count != report.accounting_count:
            attention = (
                "\nATTENTION\n"
                f"Müşteri teslim eksik: {report.invoice_count - report.delivered_count}\n"
                f"Muhasebe teslim eksik: {report.invoice_count - report.accounting_count}\n"
            )
        body = (
            f"Toplam fatura: {report.invoice_count}\n"
            f"Toplam tutar: {report.total_amount}\n"
            f"Müşteriye teslim: {report.delivered_count}\n"
            f"Muhasebeye aktarım: {report.accounting_count}\n"
            f"{attention}"
        )
        return MonthlyMail(subject=subject, body=body)


class ManagementMailDelivery:
    def send(self, *, to: str, mail: MonthlyMail) -> str:
        raise NotImplementedError


class MockManagementMailDelivery(ManagementMailDelivery):
    def __init__(self):
        self.sent = []

    def send(self, *, to: str, mail: MonthlyMail) -> str:
        message_id = f"monthly-{len(self.sent)+1}"
        self.sent.append((to, mail.subject, mail.body))
        return message_id
