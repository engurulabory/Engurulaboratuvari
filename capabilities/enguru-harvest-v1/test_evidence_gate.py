import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from evidence_gate import validate, safe_local_assets

def sha(x):
    return hashlib.sha256(x).hexdigest()
SOURCE=b"sample source"
def receipt(stage):
    return json.dumps({"stage":stage,"result":"PASS","source_sha256":sha(SOURCE)},sort_keys=True).encode()
ASSETS={"source.txt":SOURCE,"test.json":receipt("test"),"task.json":receipt("real_task"),"review.json":receipt("review")}
MANIFEST={key:{"path":path,"sha256":sha(ASSETS[path])} for key,path in zip(("source","test","real_task","review"),ASSETS)}
class EvidenceTests(unittest.TestCase):
    def test_complete_stays_candidate(self):
        self.assertEqual(validate(MANIFEST,ASSETS)["state"],"EVIDENCE_CANDIDATE")
    def test_missing(self):
        self.assertEqual(validate({},ASSETS)["state"],"HOLD")
    def test_tamper(self):
        self.assertEqual(validate(MANIFEST,{**ASSETS,"test.json":b"changed"})["state"],"HOLD")
    def test_forged_result(self):
        bad=b'{"stage":"review","result":"FAIL"}'
        m={**MANIFEST,"review":{"path":"review.json","sha256":sha(bad)}}
        self.assertEqual(validate(m,{**ASSETS,"review.json":bad})["state"],"HOLD")
    def test_wrong_stage(self):
        bad=receipt("test")
        m={**MANIFEST,"review":{"path":"review.json","sha256":sha(bad)}}
        self.assertEqual(validate(m,{**ASSETS,"review.json":bad})["state"],"HOLD")
    def test_missing_bytes(self):
        self.assertEqual(validate(MANIFEST,{"source.txt":SOURCE})["state"],"HOLD")
    def test_unhashable_path(self):
        m={**MANIFEST,"test":{"path":[],"sha256":"a"*64}}
        self.assertEqual(validate(m,ASSETS)["state"],"HOLD")
    def test_duplicate_path(self):
        m={**MANIFEST,"test":{"path":"source.txt","sha256":sha(SOURCE)}}
        self.assertEqual(validate(m,ASSETS)["state"],"HOLD")
    def test_traversal_symlink_and_plain(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"source.txt").write_bytes(SOURCE)
            (root/"linked").symlink_to(root/"source.txt")
            m={"a":{"path":"../source.txt"},"b":{"path":"linked"},"c":{"path":"source.txt"},"d":{"path":[]}}
            self.assertEqual(safe_local_assets(d,m),{"source.txt":SOURCE})
    def test_invalid_manifest(self):
        self.assertEqual(safe_local_assets(".",[]),{})
        self.assertEqual(validate([],[] )["state"],"HOLD")
if __name__=="__main__":
    unittest.main()
