"""Bound T01 local regression. Claims only scoped read-only caller."""
import unittest
from pathlib import Path
from tools import enguru_suzgec_v23_field_dispatch as f

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'governance/mac-engineer/OPERATOR_ACTION_REGISTRY_V1.json'

class ProductionBindingSourceTests(unittest.TestCase):
    def test_live_registry_and_all_source_pins(self):
        self.assertEqual(f.verify_authority(ROOT, REG)['state'],
                         'PASS_T01_AUTHORITY_AND_SOURCE_VERIFIED')
    def test_unpinned_head_holds(self):
        with self.assertRaisesRegex(ValueError, 'GIT_HEAD_DRIFT'):
            f.verify_authority(ROOT, REG, expected_head='0'*40)
    def test_8_scenario_declarations_preserved(self):
        from tools.enguru_suzgec_v23_forecast import MANDATORY_SCENARIOS
        self.assertEqual(len(MANDATORY_SCENARIOS),8)
    def test_registry_never_grants_remote_mutation_or_human_acceptance(self):
        self.assertFalse(f.ENTRY['remotePush'])
        self.assertEqual(f.ENTRY['humanThreshold'],'HUMAN_ONLY')
        self.assertEqual(f.ENTRY['mutationScope'],'NONE')
    def test_no_canonical_rewrite_claim(self):
        self.assertEqual(f.ACTION,'ENGURU_SUZGEC_V23_T01_BOUND_FIELD')
        self.assertNotIn('P01', f.ACTION)

if __name__ == '__main__': unittest.main()
