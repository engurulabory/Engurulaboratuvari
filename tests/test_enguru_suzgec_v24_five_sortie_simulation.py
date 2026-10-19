import unittest
from pathlib import Path
from tools.enguru_suzgec_v24_five_sortie_simulation import simulate, SORTIES

class FiveSortieSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=simulate(Path(__file__).resolve().parents[1])
    def test_five_sorties_and_sequence(self):
        self.assertEqual(tuple(x["sortie"] for x in self.r["sorties"]),SORTIES)
        self.assertIn("8_ASAMA",self.r["goal"])
    def test_source_scope_and_dependency(self):
        self.assertEqual(self.r["source_count"],21)
        self.assertEqual(self.r["source_total"],21)
        self.assertEqual(self.r["static_closure"],"PASS_BOUNDED_STATIC_CLOSURE_ONLY")
    def test_field_stays_hold_for_all(self):
        self.assertTrue(all(x["field"].startswith("HOLD") for x in self.r["sorties"]))
    def test_native_finish_never_self_granted(self):
        self.assertEqual(self.r["verifiedFinish"],"HOLD")
        self.assertEqual(self.r["nativeAuthority"],"HOLD")
        self.assertEqual(self.r["osiRepositoryWrites"],0)
    def test_simulation_only_is_explicit(self):
        self.assertEqual(self.r["state"],"PASS_BOUNDED_FIVE_SORTIE_SIMULATION_ONLY")
        self.assertEqual(self.r["scope"],"GITHUB_CANDIDATE_SIMULATION_ONLY")
if __name__=="__main__":unittest.main()
