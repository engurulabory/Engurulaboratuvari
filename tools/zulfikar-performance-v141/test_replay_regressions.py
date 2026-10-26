"""Direct counterexamples found during five-task campaign; existing engine only."""
import sys,unittest
from pathlib import Path
import run_campaign
sys.path.insert(0,str(run_campaign.DOM))
import test_engine
from engine import LocalJournal
class ReplayRegression(unittest.TestCase):
 def setUp(self):
  self.fx=test_engine.CycleTests();self.fx.setUp();self.addCleanup(self.fx.doCleanups)
  self.fx.drive();self.fx.state['checks']={k:True for k in self.fx.goal.criteria}
 def test_output_changed_after_checkpoint(self):
  self.fx.record.write_text('{"A":false}')
  self.assertEqual(self.fx.drive()['reason'],'REPLAY_ARTIFACT_OR_CRITERIA_CHANGED')
 def test_current_semantics_no_longer_complete(self):
  r=self.fx.drive(evaluator=lambda *_:{k:False for k in self.fx.goal.criteria})
  self.assertEqual(r['reason'],'REPLAY_ARTIFACT_OR_CRITERIA_CHANGED')
 def test_source_changed_by_replay_verifier(self):
  def verifier(*args):self.fx.source.write_text('changed');return True
  r=self.fx.drive(independent_verifier=verifier)
  self.assertEqual(r['reason'],'SOURCE_CHANGED_DURING_REPLAY_VERIFY')
 def test_journal_changed_by_replay_verifier(self):
  def verifier(*args):
   self.fx.journal.path.write_text(self.fx.journal.path.read_text().replace('"afterDiagnostic":100','"afterDiagnostic":99'));return True
  self.assertNotEqual(self.fx.drive(independent_verifier=verifier).get('diagnostic'),100)
 def test_replay_does_not_execute_or_repair(self):
  def forbidden(*_):raise AssertionError('duplicate work')
  old=self.fx.record.read_bytes();n=len(LocalJournal(self.fx.root).events)
  r=self.fx.drive(repairer=forbidden,real_tester=forbidden)
  self.assertTrue(r['replayedVerifiedCheckpoint']);self.assertEqual(self.fx.record.read_bytes(),old)
  self.assertEqual(len(LocalJournal(self.fx.root).events),n)
 def test_no_new_authority_from_replay(self):
  r=self.fx.drive();self.assertIsNone(r['acceptedScore']);self.assertFalse(r['stagePassIssued'])
  self.assertEqual(r['productVerifiedFinish'],'NOT_ISSUED')
if __name__=='__main__':unittest.main()
