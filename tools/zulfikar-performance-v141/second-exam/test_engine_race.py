"""Deterministic adversarial schedule at the journal commit boundary, real bytes."""
import hashlib,json,os,sys,unittest
from pathlib import Path
DOM=Path(os.environ['DOM_ENGINE_DIR']) if 'DOM_ENGINE_DIR' in os.environ else Path(__file__).resolve().parents[3]/'governance/enguru-suzgeci/zulfikar-v12/v141/dom'
sys.path.insert(0,str(DOM))
import test_engine
from engine import LocalJournal,sha
class CheckpointTruth(unittest.TestCase):
 def setUp(self):
  self.f=test_engine.CycleTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
  self.f.drive();self.f.state['checks']={k:True for k in self.f.goal.criteria}
 def test_replay_has_no_new_task_process(self):
  observed=[]
  def verify(*args):observed.append(args[2]);return self.f.verify(*args)
  r=self.f.drive(independent_verifier=verify)
  self.assertTrue(r['replayedVerifiedCheckpoint'])
  self.assertIs(observed[-1]['processObserved'],False)
  self.assertIsNone(observed[-1]['exitCode'])
  self.assertIs(observed[-1]['replayedProcessProof']['processObserved'],True)
  self.assertIs(r['processObserved'],False)
 def test_mutation_during_journal_publication(self):
  self.f.journal.path.unlink();self.f.journal=LocalJournal(self.f.root)
  append=self.f.journal.append
  def mutate(payload):
   value=append(payload);self.f.record.write_text(json.dumps({k:False for k in self.f.goal.criteria}));return value
  self.f.journal.append=mutate
  r=self.f.drive()
  self.assertNotEqual(r.get('diagnostic'),100)
  self.assertEqual(r['reason'],'ARTIFACT_CHANGED_AT_CHECKPOINT')
 def test_source_probe_after_last_verifier_mutates_artifact(self):
  self.f.journal.path.unlink();self.f.journal=LocalJournal(self.f.root);v=[0]
  def verify(*args):v[0]+=1;return self.f.verify(*args)
  def probe(c):
   if v[0]>=2:self.f.record.write_text('changed after last verifier')
   return self.f.source_probe(c)
  r=self.f.drive(independent_verifier=verify,source_probe=probe)
  self.assertNotEqual(r.get('diagnostic'),100)
 def test_pinned_snapshot_retains_committed_bytes(self):
  e=self.f.journal.events[-1]['payload'];snap=self.f.root/e['artifactSnapshot'];before=snap.read_bytes()
  self.f.record.write_text('later external edit')
  self.assertEqual(hashlib.sha256(before).hexdigest(),e['artifactSha256'])
  self.assertEqual(snap.read_bytes(),before)
  self.assertNotEqual(self.f.drive().get('diagnostic'),100)
 def test_mutated_snapshot_is_rejected_on_replay(self):
  e=self.f.journal.events[-1]['payload'];snap=self.f.root/e['artifactSnapshot'];snap.chmod(0o600);snap.write_text('tampered snapshot')
  self.assertNotEqual(self.f.drive().get('diagnostic'),100)
 def test_missing_historical_process_is_hold(self):
  events=self.f.journal.events;events[-1]['payload'].pop('executionProof',None);prior='0'*64
  for e in events:e['prior']=prior;e['hash']=sha({k:v for k,v in e.items() if k!='hash'});prior=e['hash']
  self.f.journal.path.write_text(''.join(json.dumps(e)+'\n' for e in events));self.f.journal=LocalJournal(self.f.root)
  self.assertEqual(self.f.drive()['reason'],'CHECKPOINT_PROCESS_PROOF_REQUIRED')
if __name__=='__main__':unittest.main()
