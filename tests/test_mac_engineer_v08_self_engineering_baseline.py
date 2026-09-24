from __future__ import annotations

import importlib.util
from pathlib import Path
import plistlib
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "mac_engineer_v08_self_engineering_baseline.py"
SPEC = importlib.util.spec_from_file_location(
    "mac_engineer_v08_self_engineering_baseline",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
baseline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(baseline)


class V08SelfEngineeringBaselineTests(unittest.TestCase):
    def test_donecheck_v12_authority_is_exact(self) -> None:
        self.assertEqual(baseline.DONECHECK_VERSION, "1.2.0")
        self.assertEqual(
            baseline.DONECHECK_EXACT_MAIN,
            "8b90a8fc93453dd8a84994195d28d14b15e261cb",
        )

    def test_evidence_root_is_v08_scoped(self) -> None:
        self.assertIn(
            "MacEngineer/v0.8/self-engineering-baseline",
            str(baseline.EVIDENCE_ROOT),
        )

    def test_plist_version_reads_short_and_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Info.plist"
            with path.open("wb") as handle:
                plistlib.dump(
                    {
                        "CFBundleShortVersionString": "0.8",
                        "CFBundleVersion": "80",
                    },
                    handle,
                )

            value = baseline.plist_version(path)

        self.assertEqual(value["short"], "0.8")
        self.assertEqual(value["build"], "80")


if __name__ == "__main__":
    unittest.main()
