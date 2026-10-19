import importlib.util
from pathlib import Path
import unittest

file = Path(__file__).resolve().parents[1] / "tools/plive_p02_six_gate_dependency_matrix_v1.py"
spec = importlib.util.spec_from_file_location("dependency", file)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture(value=True):
    return {g: {key: value for key in checks} for g, checks in m.REQUIRED_CHECKS.items()}

class SixGateMatrixTests(unittest.TestCase):
    def test_all_true_still_no_native_authority(self):
        r=m.reconcile(fixture())
        self.assertEqual(r["state"], "PASS_ENGINEERING_MATRIX_OFFICIAL_HOLD")
        self.assertFalse(r["authorizedToWrite"])
        self.assertEqual(r["verifiedFinish"], "HOLD")
        self.assertEqual(len(r["gates"]),6)
        self.assertTrue(all(not g["fieldAccepted"] for g in r["gates"]))

    def test_all_false_exhaustive_blockers(self):
        r=m.reconcile(fixture(False))
        self.assertEqual(len(r["blockingChecks"]),sum(map(len,m.REQUIRED_CHECKS.values())))
        self.assertEqual(r["officialP02"],"HOLD")

    def test_each_gate_missing_has_exact_blocker(self):
        for gate, checks in m.REQUIRED_CHECKS.items():
            for check in checks:
                f=fixture()
                f[gate][check]=False
                with self.subTest(gate=gate,check=check):
                    r=m.reconcile(f)
                    self.assertEqual(r["blockingChecks"],[gate+":"+check])
                    self.assertFalse(r["gates"][m.GATES.index(gate)]["engineeringReady"])

    def test_rejects_injected_native(self):
        f=fixture()
        f["verifiedFinish"]="PASS"
        self.assertEqual(m.reconcile(f)["state"],"HOLD")
        f=fixture()
        f[m.GATES[0]]["fieldAccepted"]=True
        self.assertEqual(m.reconcile(f)["state"],"HOLD_INVALID_EVIDENCE")

    def test_rejects_non_boolean(self):
        for v in [1,"PASS",None,[],{}]:
            f=fixture()
            f[m.GATES[0]]["sourceBinaryBinding"]=v
            with self.subTest(v=v):
                self.assertEqual(m.reconcile(f)["state"],"HOLD_INVALID_EVIDENCE")

    def test_dependency_graph(self):
        self.assertEqual(m.PREREQUISITES[m.GATES[3]],m.GATES[:3])
        self.assertEqual(m.PREREQUISITES[m.GATES[-1]],(m.GATES[-2],))

if __name__ == "__main__":
    unittest.main()
