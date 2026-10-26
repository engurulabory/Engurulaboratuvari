import unittest
from tools import pilive_learning_adapter_v1 as p
from tools.enguru_muhendislik_kasi import IntakeHold

class ProjectSetTests(unittest.TestCase):
    def test_equal_sets_ignore_order_without_acceptance(self):
        r=p.project_set_evidence(['P01','P02'],['P02','P01'])
        self.assertEqual(r['state'],'PASS_SUPPLIED_PROJECT_SET_EQUALITY_ONLY')
        self.assertEqual(r['productAcceptance'],'HOLD')
    def test_missing_dynamic_p02_is_hold(self):
        r=p.project_set_evidence(['P01','ENGURU_PLIVE_P02_USER_SCREEN'],['P01'])
        self.assertEqual(r['missingProjectIds'],['ENGURU_PLIVE_P02_USER_SCREEN'])
        self.assertEqual(r['state'],'HOLD_PROJECT_SET')
    def test_extra_or_placeholder_is_hold(self):
        r=p.project_set_evidence(['P02'],['P02','PLANNED'])
        self.assertEqual(r['extraProjectIds'],['PLANNED'])
        self.assertEqual(r['state'],'HOLD_PROJECT_SET')
    def test_duplicates_on_either_side_are_hold(self):
        for core,ui in [(['P02','P02'],['P02']),(['P02'],['P02','P02'])]:
            r=p.project_set_evidence(core,ui)
            self.assertTrue(r['duplicateIdentity']);self.assertEqual(r['state'],'HOLD_PROJECT_SET')
    def test_empty_core_never_proves_parity(self):
        self.assertEqual(p.project_set_evidence([],[])['state'],'HOLD_PROJECT_SET')
    def test_invalid_shapes(self):
        for value in [None,{},'P02',True,['P02']*5001]:
            with self.subTest(value=type(value)),self.assertRaises(IntakeHold):p.project_set_evidence(value,[])
    def test_invalid_and_private_identity(self):
        for value in [True,1,'','/Users/private','a'*129]:
            with self.subTest(value=value),self.assertRaises(IntakeHold):p.project_set_evidence(['P02'],[value])
    def test_missing_id_output_is_deterministic(self):
        self.assertEqual(p.project_set_evidence(['C','B','A'],['B']),
                         p.project_set_evidence(['A','C','B'],['B']))

if __name__=='__main__':unittest.main()
