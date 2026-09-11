import unittest
from decimal import Decimal

from cores.billing.monthly_maya_mail import MonthlyMayaMailRenderer, MockManagementMailDelivery
from cores.billing.monthly_report import MonthlyBillingReport


class MonthlyMayaMailTests(unittest.TestCase):
    def test_clean_report(self):
        report = MonthlyBillingReport(2026, 9, 2, Decimal("150"), 2, 2)
        mail = MonthlyMayaMailRenderer().render(report)
        self.assertIn("Toplam fatura: 2", mail.body)
        self.assertNotIn("ATTENTION", mail.body)
        delivery = MockManagementMailDelivery()
        self.assertTrue(delivery.send(to="management@example.com", mail=mail))

    def test_gap_is_visible(self):
        report = MonthlyBillingReport(2026, 9, 2, Decimal("150"), 2, 1)
        mail = MonthlyMayaMailRenderer().render(report)
        self.assertIn("ATTENTION", mail.body)
        self.assertIn("Muhasebe teslim eksik: 1", mail.body)


if __name__ == "__main__":
    unittest.main()
