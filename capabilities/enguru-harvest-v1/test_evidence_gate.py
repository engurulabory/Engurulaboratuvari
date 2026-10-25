import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from evidence_gate import validate, safe_local_assets

def sha(x):
    return hashlib.sha256(x).hexdigest()
SOURCE=b"sample source"
RECEIPT=json.dumps({"result":"PASS","source_sha256":sha(SOURCE)}).encode()
ASSETS={"source.txt":SOURCE,"test.json":RECEIPT,"task.json":RECEIPT,"review.json":RECEIPT}
MANIFEST={key:{"path":path,"sha256":sha(ASSETS[path])} for key,path in zip(("source","test","real_task","review"),ASSETS)}
class EvidenceTests(unittest.TestCase):
    def test_complete_stays_candidate(self):
        self.assertEqual(validate(MANIFEST,ASSETS)["state"],"EVIDENCE_CANDIDATE")
    def test_missing(self):
        self.assertEqual(validate({},ASSETS)["state"],"HOLD")
    def test_tamper(self):
        self.assertEqual(validate(MANIFEST,{**ASSETS,"test.json":b"changed"})["state"],"HOLD")
    def test_forged_result(self):
        bad=b'{"result":"FAIL"}'
        m={**MANIFEST,"review":{"path":"review.json","sha256":sha(bad)}}
        self.assertEqual(validate(m,{**ASSETS,"review.json":bad})["state"],"HOLD")
    def test_missing_bytes(self):
        self.assertEqual(validate(MANIFEST,{"source.txt":SOURCE})["state"],"HOLD")
    def test_traversal_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"source.txt").write_bytes(SOURCE)
            (root/"linked").symlink_to(root/"source.txt")
            m={"a":{"path":"../source.txt"},"b":{"path":"linked"},"c":{"path":"source.txt"}}
            self.assertEqual(safe_local_assets(d,m),{"source.txt":SOURCE})
if __name__=="__main__":
    unittest.main()
