import tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pilot_contract import Pilot,manifest,digest,stable
from signed_verifier import signed_payload,verify
class SignedVerifierTests(unittest.TestCase):
 def test_adversarial_evidence(self):
  with tempfile.TemporaryDirectory() as td:
   key=Ed25519PrivateKey.generate();foreign=Ed25519PrivateKey.generate()
   pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
   task="T01";goal=1;source=manifest()[0]["source_sha256"];raw=b"actual bytes"
   r=signed_payload(task,goal,source,raw,1);sig=key.sign(stable(r))
   self.assertEqual(verify(pub,task,goal,source,raw,1,r,sig),"PASS_TEST_VERIFIER")
   self.assertEqual(verify(pub,task,goal,source,raw+b"x",1,r,sig),"HOLD_BINDING")
   self.assertEqual(verify(pub,task,goal,source,raw,2,r,sig),"HOLD_BINDING")
   self.assertEqual(verify(pub,"T02",goal,source,raw,1,r,sig),"HOLD_BINDING")
   self.assertEqual(verify(pub,task,goal,source,raw,1,r,foreign.sign(stable(r))),"HOLD_SIGNATURE")
   self.assertEqual(verify(pub,task,goal,source,raw,1,{**r,"scope":"OWNER_APPROVED"},sig),"HOLD_BINDING")
   p=Pilot(Path(td)/"p.db")
   self.assertEqual(p.add(task,goal,source),"ACTIVE")
   self.assertEqual(verify(pub,task,goal,source,raw,1,r,sig),"PASS_TEST_VERIFIER")
   self.assertEqual(p.finish(task,raw,digest(raw)),"PASS_TEST_ONLY")
   self.assertEqual(p.verify(),"PASS_LEDGER")
   p.close()
if __name__=="__main__":unittest.main(verbosity=2)
