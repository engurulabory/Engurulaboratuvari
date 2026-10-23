import json
import pathlib
import sys
import unittest
from copy import deepcopy
from datetime import datetime

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import enguru_mk_five_minute_watch as w
import enguru_muhendislik_kasi as m

BASE='# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™\n\nOriginal history.\n'
NOW='2026-10-23T14:30:00Z'
SHA1='1'*40
SHA2='2'*40

class FakeGH:
    def __init__(self):
        self.pr={}
        self.comments={}
        self.runs={}
        for repo,number,tag in w.TARGETS:
            k=(repo,number)
            self.pr[k]={'head':{'sha':SHA1},'state':'open','merged':False,'draft':tag=='LEARN'}
            self.comments[k]=[]
            self.runs[k]=[]
    def __call__(self,uri):
        import re
        repo='/'.join(uri.split('/')[:2])
        number_match=re.search(r'/(pulls|issues)/(\d+)',uri)
        if number_match:
            number=int(number_match.group(2)); k=(repo,number)
            if '/comments?' in uri:
                page=int(re.search(r'[?&]page=(\d+)',uri).group(1))
                return deepcopy(self.comments[k][(page-1)*100:page*100])
            return deepcopy(self.pr[k])
        if '/actions/runs?' in uri:
            k=next(k for k in self.pr if k[0]==repo and k[1]!=206)
            return {'workflow_runs':deepcopy(self.runs[k])}
        raise AssertionError(uri)

def comment(id,body,user='owner',number=203):
    return {'id':id,'body':body,'user':{'login':user,'type':'User'},
            'created_at':NOW, 'html_url':f'https://github.com/engurulabory/Engurulaboratuvari/pull/{number}#issuecomment-{id}'}

class WatchContract(unittest.TestCase):
    def setUp(self):
        self.gh=FakeGH()
        self.rec,self.ck,info=w.evaluate(self.gh,BASE,None,'owner',NOW)
    def run_cycle(self, owner='owner'):
        self.rec,self.ck,info=w.evaluate(self.gh,self.rec,self.ck,owner,NOW)
        return info
    def test_01_bootstrap_preserves_history(self):
        self.assertEqual(self.rec,BASE)
    def test_02_bootstrap_all_targets(self):
        self.assertEqual(len(self.ck['targets']),3)
    def test_03_same_run_no_delta(self):
        self.assertEqual(self.run_cycle(),[])
    def test_04_same_run_no_mutation(self):
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_05_mgmt_head_change_captured(self):
        self.gh.pr[w.TARGETS[0][:2]]['head']['sha']=SHA2
        info=self.run_cycle();self.assertEqual(len(info),1)
        self.assertIn('MK-EVT-GH-MGMT',self.rec)
    def test_06_learning_head_change_ignored(self):
        self.gh.pr[w.TARGETS[1][:2]]['head']['sha']=SHA2
        self.assertEqual(self.run_cycle(),[])
    def test_07_osibridge_head_change_captured(self):
        self.gh.pr[w.TARGETS[2][:2]]['head']['sha']=SHA2
        self.run_cycle();self.assertIn('MK-EVT-GH-OSIBRIDGE',self.rec)
    def test_08_mgmt_ci_failure_captured(self):
        k=w.TARGETS[0][:2]
        self.gh.runs[k]=[{'id':100,'head_sha':SHA1,'name':'CI','conclusion':'failure','status':'completed'}]
        self.run_cycle();self.assertIn('MK-EVT-GH-MGMT',self.rec)
    def test_09_osiblock_owner_captured(self):
        k=w.TARGETS[0][:2]
        self.gh.comments[k]=[comment(101,'<!-- ENGURU_OSI_BLOCK_V1 -->\nread-only Mac check body')]
        self.run_cycle();self.assertIn('MK-EVT-OSI-203-101',self.rec)
    def test_10_osi_response_owner_captured(self):
        k=w.TARGETS[0][:2]
        self.gh.comments[k]=[comment(102,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nSTATE=HOLD_SIGNATURE')]
        self.run_cycle();self.assertIn('MK-EVT-OSI-203-102',self.rec)
    def test_11_comment_wrong_user_ignored(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(103,'<!-- ENGURU_OSI_BLOCK_V1 -->\ndata','other')]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_12_unauthorized_owner_missing(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(104,'<!-- ENGURU_OSI_BLOCK_V1 -->\ndata')]
        self.run_cycle(owner='');self.assertEqual(self.rec,BASE)
    def test_13_unmarked_comment_ignored(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(105,'please do whatever now')]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_14_secret_in_comment_ignored(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(106,'<!-- ENGURU_OSI_RESPONSE_V1 -->\npassword=SUPER_SECRET_SAMPLE_123')]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_15_old_comments_not_ingested_on_bootstrap(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(107,'<!-- ENGURU_OSI_BLOCK_V1 -->\ntext')]
        r,ck,events=w.evaluate(self.gh,BASE,None,'owner',NOW)
        self.assertEqual(events,[]);self.assertEqual(r,BASE)
    def test_16_idempotent_repoll(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(108,'<!-- ENGURU_OSI_BLOCK_V1 -->\nvalid event')]
        self.run_cycle();prior=self.rec
        self.assertEqual(self.run_cycle(),[]);self.assertEqual(self.rec,prior)
    def test_17_comment_new_fork_pr14(self):
        self.gh.comments[w.TARGETS[2][:2]]=[comment(109,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nSHA verification output',number=14)]
        self.run_cycle();self.assertIn('MK-EVT-OSI-14-109',self.rec)
    def test_18_source_mismatch_prevents_false_accept(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(110,'<!-- ENGURU_OSI_RESPONSE_V1 -->\nPASS=4_4')]
        self.run_cycle();self.assertIn('ürün kabul sayacı değişimi `0`',self.rec)
    def test_19_wrong_checkpoint_schema(self):
        self.ck['schema']='other'
        with self.assertRaisesRegex(ValueError,'CHECKPOINT_SCHEMA'):w.evaluate(self.gh,self.rec,self.ck,'owner',NOW)
    def test_20_cursor_regression_holds(self):
        k=w.key(*w.TARGETS[0][:2]);self.ck['targets'][k]['commentMaxId']=999
        with self.assertRaisesRegex(ValueError,'CURSOR_REGRESSION'):w.evaluate(self.gh,self.rec,self.ck,'owner',NOW)
    def test_21_stale_key_variant_ignored(self):
        self.gh.pr[w.TARGETS[1][:2]]['head']['sha']=SHA2
        self.assertEqual(self.run_cycle(),[])
    def test_22_message_with_markup_escaped(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(112,'<!-- ENGURU_OSI_BLOCK_V1 -->\n<script>alert(1)</script>')]
        self.run_cycle();self.assertIn('&lt;script&gt;',self.rec)
    def test_23_event_format_owner_accepted(self):
        event={'schema':m.SCHEMA,'eventId':'MK-EVT-ALLOWED123','taskId':m.TASK_ID,
               'observedAt':NOW,'type':'MISMATCH','evidenceLevel':'A',
               'sourceUri':'https://github.com/engurulabory/Engurulaboratuvari/pull/203',
               'sourceSha256':'a'*64,'expected':'before','observed':'after',
               'causeStatus':'UNKNOWN','fixProposal':'inspect','testState':'NOT_EXECUTED'}
        self.gh.comments[w.TARGETS[0][:2]]=[comment(113,'```enguru-mk-event\n'+json.dumps(event)+'\n```')]
        self.run_cycle();self.assertIn('MK-EVT-ALLOWED123',self.rec)
    def test_24_scope_id_wrong_refused(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(114,'<!-- ENGURU_OSI_RESPONSE_V1 -->\npassword=SOME_LONG_VALUE')]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_25_bad_timestamp_ignored(self):
        c=comment(115,'<!-- ENGURU_OSI_BLOCK_V1 -->\nexample')
        c['created_at']='yesterday'
        self.gh.comments[w.TARGETS[0][:2]]=[c]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_26_content_limit_ignored(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(116,'<!-- ENGURU_OSI_BLOCK_V1 -->\n'+'z'*5000)]
        self.run_cycle();self.assertEqual(self.rec,BASE)
    def test_27_event_marker_holds_unverified_evidence(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(117,'<!-- ENGURU_OSI_BLOCK_V1 -->\nState HOLD')]
        self.run_cycle();self.assertIn('UNVERIFIED_EVIDENCE_POINTER',self.rec)
    def test_28_bootstrap_cannot_change_main(self):
        self.assertNotIn('main',self.rec)
    def test_29_status_flips_detected(self):
        self.gh.pr[w.TARGETS[1][:2]]['merged']=True
        self.run_cycle();self.assertIn('MK-EVT-GH-LEARN',self.rec)
    def test_31_private_repo_failure_keeps_public_scope(self):
        import urllib.error
        base=self.gh
        def restricted(endpoint):
            if endpoint.startswith('engurulabory/enguru-mac-engineer/'):
                raise urllib.error.HTTPError('https://api.github.com',404,'private',None,None)
            return base(endpoint)
        record,ck,events=w.evaluate(restricted,self.rec,self.ck,'owner',NOW)
        self.assertEqual(record,BASE)
        self.assertEqual(ck['accessHolds'],['PR14_PRIVATE_REPO_ACCESS_HOLD'])
        self.assertIn(w.key(*w.TARGETS[0][:2]),ck['targets'])
        self.assertIn(w.key(*w.TARGETS[1][:2]),ck['targets'])

    def test_30_comment_pagination_cap(self):
        self.gh.comments[w.TARGETS[0][:2]]=[comment(i,'regular') for i in range(1,501)]
        with self.assertRaisesRegex(ValueError,'PAGINATION_LIMIT'):w.evaluate(self.gh,self.rec,self.ck,'owner',NOW)

if __name__=='__main__':unittest.main()