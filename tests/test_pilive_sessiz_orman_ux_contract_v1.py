"""Contract-only UX guard. Synthetic/static design fixture, not native UI acceptance."""
import json
import re
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
UX=ROOT/'governance/plive/SESSIZ_ORMAN_COCKPIT_UX_CONTRACT_V1.md'
FIXTURE=ROOT/'governance/plive/SESSIZ_ORMAN_SCREEN_FIXTURE_V1.json'

def contrast(fg,bg):
    def lum(code):
        values=[int(code[i:i+2],16)/255 for i in (1,3,5)]
        linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
        return linear[0]*.2126+linear[1]*.7152+linear[2]*.0722
    a,b=sorted((lum(fg),lum(bg)), reverse=True)
    return (a+.05)/(b+.05)

class UXContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f=json.loads(FIXTURE.read_text(encoding='utf8'))
        cls.doc=UX.read_text(encoding='utf8')
    def test_real_project_count_and_partial_coverage_distinct(self):
        d=self.f['discovery'];self.assertEqual((d['projects'],d['qualifiedCounters'],d['sourceBoundObservations']),(15,14,15))
    def test_p02_zero_is_official_hold(self):
        d=self.f['p02'];self.assertEqual((d['done'],d['total'],d['percent'],d['officialAcceptance']),(0,12,0,'HOLD'))
    def test_progress_core_technical_100_not_finish(self):
        d=self.f['progressCore'];self.assertEqual((d['done'],d['total'],d['percent'],d['finish']),(44,44,100,'HOLD'))
    def test_visual_cockpit_unproven_has_no_progress(self):
        d=self.f['visualCockpit'];self.assertEqual(d['declared']-d['evidenced'],d['unverified'])
        self.assertIsNone(d['done']);self.assertIsNone(d['total']);self.assertIsNone(d['percent'])
    def test_truth_digest_source_evidence(self):
        self.assertRegex(self.f['projectionDigest'],r'^[0-9a-f]{64}$')
        self.assertRegex(self.f['nativeReceiptSha256'],r'^[0-9a-f]{64}$')
        self.assertEqual((self.f['discovery']['sourcePins'],self.f['discovery']['sourceFiles']),(8,48))
    def test_category_is_source_bound_without_forged_mapping(self):
        self.assertEqual(self.f['categoryLabels'],['Motor','Çekirdek','Web','App','Agent'])
        self.assertEqual(self.f['commerceClassification'],'SOURCE_BOUND_FACET_ONLY')
        self.assertTrue(self.f['projectAreaAssignments'].startswith('N_A'))
    def test_unknown_global_focus_and_ui_times(self):
        self.assertTrue(self.f['globalActiveFocus'].startswith('HOLD'))
        self.assertTrue(all(v is None for v in self.f['timeSources'].values()))
    def test_binary_signature_hold(self):
        self.assertEqual(self.f['historicalBinarySignature'],{'codesignStrictReturnCode':1,'verdict':'HOLD'})
    def test_u_acceptance_not_generated_by_artifact(self):
        self.assertEqual(self.f['ownerAestheticAcceptance'],'HOLD')
        self.assertEqual(self.f['macUserAcceptance'],'HOLD')
        self.assertEqual(self.f['uiPublication'],'NOT_EXECUTED')
        self.assertFalse(self.f['duplicateCounterEngineAllowed'])
        self.assertEqual(self.f['requirements'],[f'U{i:02d}' for i in range(1,13)])
    def test_contract_names_required_views_states_and_gates(self):
        for item in ['Genel Durum','Şimdi','Projeler','Kanıt çekmecesi',
                     'OFFLINE','STALE','GLOBAL_DRIFT','P02.S01.01','Progress Core','Visual Cockpit',
                     'Human Threshold','OWNER_AESTHETIC_ACCEPTANCE_HOLD']:
            with self.subTest(item=item):self.assertIn(item,self.doc)
    def test_text_palette_baseline_contrast(self):
        for fg,bg in [('#EEF4EE','#14241F'),('#A6B7AC','#14241F'),
                      ('#91D4AD','#14241F'),('#E9C78A','#14241F')]:
            with self.subTest(fg=fg):self.assertGreaterEqual(contrast(fg,bg),4.5)
    def test_design_does_not_claim_field_or_official_acceptance(self):
        self.assertIn('G1.D04 kullanıcı estetik kabulü HOLD',self.doc)
        self.assertIn('G1.D02_DESIGN_REVIEW_CANDIDATE',self.doc)
        self.assertIn('resmî kapı',self.doc)

if __name__=='__main__':unittest.main()
