"""Zulfikar V1.3 V2 scores: declarative target != product acceptance."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCORES=ROOT/'governance/plive/SESSIZ_ORMAN_ZULFIKAR_V13_SCORECARD_V2.json'
DESIGN=ROOT/'governance/plive/SESSIZ_ORMAN_ZULFIKAR_V13_V2_DESIGN_REVIEW.md'
class ScorecardTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card=json.loads(SCORES.read_text(encoding='utf-8'))
        cls.md=DESIGN.read_text(encoding='utf-8')
    def test_all_11_dimensions_preserved(self):
        self.assertEqual(len(self.card['dimensions']),11)
        self.assertEqual(len({d['id'] for d in self.card['dimensions']}),11)
    def test_100_is_target_not_current_pass(self):
        self.assertTrue(all(d['target100']==100 for d in self.card['dimensions']))
        self.assertEqual(self.card['productAcceptance'],'HOLD')
        self.assertEqual(self.card['humanThreshold'],'HOLD')
    def test_three_new_scores_exist(self):
        for id_ in ('PROCESS_SIMPLE','SURFACE_SIMPLE','USABILITY'):
            self.assertIn(id_,{x['id'] for x in self.card['dimensions']})
    def test_prior_values_preserved(self):
        m={d['id']:d for d in self.card['dimensions']}
        self.assertEqual((m['AESTHETIC']['baseline']['V1Preview'],m['AESTHETIC']['baseline']['V1WrittenContract']),(73,86))
        self.assertEqual((m['ACCESSIBILITY']['baseline']['V1Preview'],m['ACCESSIBILITY']['baseline']['V1WrittenContract']),(52,82))
        self.assertEqual((m['GENERAL']['baseline']['V1Preview'],m['GENERAL']['baseline']['V1WrittenContract']),(62,87))
    def test_11_by_10_are_specified_not_passed(self):
        m=self.card['dimensions']
        self.assertTrue(all(len(x['conditionsToActuallyAttain100'])==10 for x in m))
        self.assertEqual(sum(len(x['conditionsToActuallyAttain100']) for x in m),110)
        self.assertEqual(self.card['designConditionsDefined'],110)
        self.assertIn('not achieved quality',self.card['strictMeaning'])
    def test_service_is_not_fabricated(self):
        service=next(x for x in self.card['dimensions'] if x['id']=='SERVICE')
        self.assertEqual(service['v2PrototypeProvisional'],0)
        self.assertEqual(service['status'],'HOLD_REAL_SERVICE')
    def test_three_round_scope_and_five_widths(self):
        p=self.card['prototypeV2']
        self.assertEqual(p['viewportWidths'],[320,390,690,1024,1440])
        self.assertEqual(p['testCycles'],3)
        self.assertEqual(p['passingViewportRuns'],15)
        self.assertEqual(p['realNativeUi'],'NOT_EXECUTED')
    def test_artifact_digest_shape(self):
        import re
        self.assertRegex(self.card['prototypeV2']['sha256'],r'^[a-f0-9]{64}$')
        self.assertIn('NOT_GITHUB_FILE',self.card['prototypeV2']['githubContentStatus'])
    def test_osi_pilive_official_boundaries(self):
        st=self.card['stages']
        self.assertEqual(st['OSI_UNIFIED_V1'],'PARKED_HOLD_IN_PR244')
        self.assertEqual(st['G1D04'],'HOLD_OWNER_AESTHETIC')
        self.assertEqual(st['officialP02'],'HOLD')
    def test_work_report_last(self):
        self.assertIn('son bölümde',self.md)
        self.assertIn('G1.D03-V',self.md)
if __name__=='__main__':unittest.main()
