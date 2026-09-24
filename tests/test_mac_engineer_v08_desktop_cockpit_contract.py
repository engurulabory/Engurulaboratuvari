from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "governance"
    / "mac-engineer"
    / "V08_UX_AESTHETIC_PRODUCT_CONTRACT_V1.md"
)


class V08DesktopCockpitContractTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = CONTRACT.read_text(encoding="utf-8")

    def test_desktop_only_target(self):
        self.assertIn("DESKTOP MAC ONLY", self.text)

    def test_ready_heading(self):
        self.assertIn("Her şey yolunda.", self.text)

    def test_system_health_contract(self):
        self.assertIn("SYSTEM HEALTH CONTRACT", self.text)
        self.assertIn("Sistem Sağlığı — İyi", self.text)

    def test_mini_report_contract(self):
        self.assertIn("MINI REPORT CONTRACT", self.text)
        self.assertIn("Mini rapor ver.", self.text)

    def test_secondary_controls(self):
        for item in (
            "Projects",
            "Mini Rapor",
            "Kontrol",
            "Teknik Ayrıntılar",
            "Geçmiş",
        ):
            self.assertIn(item, self.text)

    def test_multimodal_input_target(self):
        for item in (
            "TEXT",
            "VOICE",
            "FILE",
            "IMAGE / PHOTO",
        ):
            self.assertIn(item, self.text)

    def test_local_first_analysis(self):
        self.assertIn(
            "user input → local intake → validation → local analysis / extraction → governed task context → Mac engineering execution",
            self.text,
        )

    def test_missing_capabilities_remain_truthful(self):
        for item in (
            "user-facing file-picker UI: HOLD",
            "microphone UI: HOLD",
            "image-analysis protocol: HOLD",
            "audio-transcription protocol: HOLD",
        ):
            self.assertIn(item, self.text)

    def test_drag_drop_not_manufactured_pass(self):
        self.assertIn(
            "not treated as independent capability PASS",
            self.text,
        )

    def test_human_artistic_authority_remains_open(self):
        self.assertIn(
            "Final Human Artistic Authority™ remains open",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
