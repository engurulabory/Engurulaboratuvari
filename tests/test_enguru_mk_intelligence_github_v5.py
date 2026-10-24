"""Bounded cross-peer protocol parity; GH actor and immutable evidence defenses."""
import json,tempfile,unittest
from pathlib import Path
from tools import enguru_mk_bridge_v1 as bridge
from tools import enguru_mk_intelligence_v5 as mac
from tools import enguru_mk_intelligence_github_v5 as gh
class GithubParity(unittest.TestCase):
 def sample(self,code,producer):
  return bridge.make_event(producer,1,'a'*40,code=code,observed='2026-10-24T14:00:00Z')
 def test_all_seven_cases_both_directions(self):
  for code in mac.CATALOG:
   for producer in ('MAC_OSI_MK','GITHUB_MK'):
    with self.subTest(code=code,producer=producer):
     e=self.sample(code,producer)
     self.assertEqual(gh.canon(gh.assess(e)),mac.canon(mac.assess(e)))
 def test_immutable_owner_worker(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/gh.ROOT/'streams/mac';p.mkdir(parents=True)
   e=self.sample('PILOT_HELLO','MAC_OSI_MK')
   (p/'MAC-00000001.json').write_bytes(gh.canon(e))
   self.assertEqual(gh.process(t,'owner','owner')['newRecords'],1)
   self.assertEqual(gh.process(t,'owner','owner')['newRecords'],0)
   file=Path(t)/gh.ROOT/'diagnostics/mac/MAC-00000001.json'
   file.write_text('{}')
   with self.assertRaises(gh.Hold):gh.process(t,'owner','owner')
 def test_owner_authority_and_bot_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   for actor in ('intruder','github-actions[bot]',''):
    with self.subTest(actor=actor):
     with self.assertRaises(gh.Hold):gh.process(t,'owner',actor)
 def test_no_remote_command(self):
  r=mac.assess(self.sample('RUNTIME_DRIFT','GITHUB_MK'))
  self.assertEqual(r['authority'],'SUGGESTION_ONLY')
  self.assertEqual(r['rootCause'],'UNCONFIRMED')
  self.assertEqual(r['productWrites'],0)
  self.assertEqual(r['officialAcceptance'],'HOLD')
 def test_event_digest_binding(self):
  e=self.sample('PILOT_HELLO','MAC_OSI_MK');x=gh.assess(e)
  self.assertEqual(x['eventSha256'],mac.digest(e))
  e2=dict(e,sourceCommit='b'*40)
  self.assertNotEqual(x['eventSha256'],mac.assess(e2)['eventSha256'])
 def test_incomplete_data_rejected(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/gh.ROOT/'streams/mac';p.mkdir(parents=True)
   (p/'MAC-00000001.json').write_bytes(gh.canon(dict(self.sample('PILOT_HELLO','MAC_OSI_MK'),code='DELETE_REPO')))
   with self.assertRaises(gh.Hold):gh.process(t,'owner','owner')
 def test_unique_json(self):
  with self.assertRaises(gh.Hold):gh.unique([('a',1),('a',2)])
 def test_stable_order(self):
  e=self.sample('GITHUB_RECEIVED','GITHUB_MK')
  self.assertEqual(gh.canon(gh.assess(e)),gh.canon(gh.assess(e)))
 def test_safeguard_learning_proof(self):
  import sqlite3
  with sqlite3.connect(':memory:') as db:
   mac.candidate(db,'CASE-ABCDEFGH','ACK_RECONCILE','FAIL','1'*64)
   with self.assertRaises(mac.Hold):mac.promote(db,'CASE-ABCDEFGH',None)
   self.assertEqual(mac.trusted_stats(db),{})
 def test_provisional_outcomes_have_zero_learning_authority(self):
  import sqlite3
  with sqlite3.connect(':memory:') as db:
   code='PACKAGE_SHA_AUDIT'
   for i in range(3):
    self.assertEqual(mac.candidate(db,'CASE-PROV%08d'%i,code,'PASS','a'*64),'PROVISIONAL')
   self.assertEqual(mac.trusted_stats(db),{})
   ev=self.sample('PACKAGE_ABSENT','GITHUB_MK')
   report=mac.assess(ev,mac.trusted_stats(db))
   self.assertTrue(all(alt['verifiedCases']==0 for alt in report['alternatives']))
   self.assertEqual(report['rootCause'],'UNCONFIRMED')
 def test_wrong_actor_and_same_proof_never_verify(self):
  import sqlite3
  with sqlite3.connect(':memory:') as db:
   mac.candidate(db,'CASE-CIPROOF00000001','SOURCE_AUDIT','PASS','b'*64)
   with self.assertRaises(mac.Hold):
    mac.promote(db,'CASE-CIPROOF00000001',lambda case,proof:('UNTRUSTED','c'*64))
   with self.assertRaises(mac.Hold):
    mac.promote(db,'CASE-CIPROOF00000001',lambda case,proof:('INDEPENDENT_CI','b'*64))
   self.assertEqual(mac.trusted_stats(db),{})
if __name__=='__main__':unittest.main()
