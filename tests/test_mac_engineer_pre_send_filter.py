import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "tools/mac_engineer_pre_send_filter.py"

SPEC = importlib.util.spec_from_file_location(
    "pre_send",
    PATH,
)
assert SPEC and SPEC.loader

pre_send = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pre_send)

GOOD = """#!/bin/zsh
# ENGURU_PRE_SEND_PACKAGE_V1
# ACTIVE_OBJECTIVE=V08_EXISTING_PRODUCT_CHANGE_SCENARIO
# NECESSARY_DIFFERENCE=BOUND_OPERATOR_BINDING
# LANGUAGE=POSITIVE_CONSTRUCTIVE_TRUTHFUL
# SECOND_LOOK=REQUIRED
# EXPECTED_SCOPE=ONE_FILE
# RECOVERY=GIT_RESTORE
# DONECHECK=V1.2_REQUIRED
printf 'STATE=PASS\\n'
printf 'CLAIM=PASS\\n'
printf 'NEXT_ACTION=DONE\\n'
"""


class PreSendFilterTests(unittest.TestCase):

    def test_good_contract_passes(self):
        checks = pre_send.check_text(GOOD)
        self.assertTrue(all(checks.values()))

    def test_missing_governance_marker_holds(self):
        source = GOOD.replace(
            "# SECOND_LOOK=REQUIRED\n",
            "",
        )
        checks = pre_send.check_text(source)
        self.assertFalse(
            checks["canonicalMarkers"]
        )

    def test_python_heredoc_syntax_is_checked(self):
        source = (
            GOOD
            + "\npython3 - <<'PY'\n"
            + "if True print('x')\n"
            + "PY\n"
        )
        checks = pre_send.check_text(source)
        self.assertFalse(
            checks["pythonHeredocSyntax"]
        )

    def test_material_authority_is_explicit(self):
        source = GOOD + "\ngit push origin main\n"
        checks = pre_send.check_text(source)
        self.assertFalse(
            checks["authorityBoundary"]
        )

        source += (
            "# HUMAN_THRESHOLD=REQUIRED\n"
        )
        checks = pre_send.check_text(source)
        self.assertTrue(
            checks["authorityBoundary"]
        )


if __name__ == "__main__":
    unittest.main()
