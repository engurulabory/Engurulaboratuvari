import hashlib,sqlite3,tempfile,unittest
from pathlib import Path
from pilot_contract import Pilot,manifest,digest
class PilotContractTests(unittest.TestCase):
 def test_real_task_api(self):
  with tempfile.TemporaryDirectory() as tmp:
   db=Path(tmp)/'p.db';p=Pilot(db);s=manifest()[0]['source_sha256']
   self.assertEqual(p.add('T01',1,s),'ACTIVE')
   self.assertEqual(p.add('T02',2,manifest()[1]['source_sha256']),'HOLD_ACTIVE')
   self.assertEqual(p.finish('T01',b'evidence','0'*64),'HOLD_PROOF')
   self.assertEqual(p.finish('T01',b'evidence',digest(b'evidence')),'PASS_TEST_ONLY')
   self.assertEqual(p.finish('T01',b'evidence',digest(b'evidence')),'HOLD_STATE')
   self.assertEqual(p.verify(),'PASS_LEDGER');p.close()
   p=Pilot(db);self.assertEqual(p.verify(),'PASS_LEDGER')
   p.db.execute("UPDATE events SET body='invalid' WHERE seq=1")
   self.assertEqual(p.verify(),'HOLD_LEDGER')
   p.close()
 def test_wrong_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Pilot(Path(tmp)/'p.db')
   self.assertEqual(p.add('T01',1,'0'*64),'HOLD_SOURCE')
   p.close()
if __name__=='__main__':unittest.main(verbosity=2)
