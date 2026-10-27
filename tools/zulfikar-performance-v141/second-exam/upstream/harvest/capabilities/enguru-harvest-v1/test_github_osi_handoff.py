"""GitHub-only OSi handoff anti-tamper/authority regression tests."""
import io
import json
import unittest
import zipfile
from pathlib import Path
from build_github_osi_handoff import build, inspect

ROOT=Path(__file__).resolve().parent

def remake(packet,alter):
    source=zipfile.ZipFile(io.BytesIO(packet),"r")
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_STORED) as target:
        for name in source.namelist():
            data=source.read(name)
            if name in alter:
                data=alter[name](data)
            target.writestr(source.getinfo(name),data)
    source.close()
    return out.getvalue()

class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=build()
        cls.data=(ROOT/cls.receipt["package_filename"]).read_bytes()

    def test_real_github_archive(self):
        self.assertEqual(inspect(self.data)["state"],"PASS_GITHUB_PACKAGE_INTEGRITY_ONLY")
        self.assertEqual(self.receipt["file_count"],9)
        self.assertEqual(self.receipt["osi_execution_count"],0)
        self.assertEqual(self.receipt["authorized_field_action"],"HOLD")
    def test_byte_tamper_rejected(self):
        path="capabilities/enguru-harvest-v1/goal.json"
        corrupted=remake(self.data,{path:lambda raw: raw+b"tamper"})
        self.assertEqual(inspect(corrupted)["state"],"HOLD_SOURCE_DIGEST")
    def test_claimed_owner_approval_rejected(self):
        def mutate(raw):
            x=json.loads(raw)
            x["owner_field_authority"]="PASS"
            return json.dumps(x).encode()
        corrupted=remake(self.data,{"HANDOFF_MANIFEST.json":mutate})
        self.assertEqual(inspect(corrupted)["state"],"HOLD_AUTHORITY")
    def test_false_mac_field_execution_rejected(self):
        def mutate(raw):
            x=json.loads(raw)
            x["osi_execution_count"]=1
            return json.dumps(x).encode()
        corrupted=remake(self.data,{"HANDOFF_MANIFEST.json":mutate})
        self.assertEqual(inspect(corrupted)["state"],"HOLD_AUTHORITY")
    def test_bad_zip_rejected(self):
        self.assertEqual(inspect(b"not-a-valid-archive")["state"],"HOLD_PACKAGE_PARSE")
    def test_oversize_rejected(self):
        self.assertEqual(inspect(b"a"*2_000_001)["state"],"HOLD_PACKAGE_BYTES")
    def test_metadata_canonical_sources_present(self):
        with zipfile.ZipFile(io.BytesIO(self.data)) as arc:
            m=json.loads(arc.read("HANDOFF_MANIFEST.json"))
            self.assertEqual(m["official_github_verified_finish"],"HOLD")
            self.assertEqual(m["mac_field_acceptance"],"HOLD")
            self.assertTrue(m["github_head"])
            self.assertIn("AGENTS.md",m["sources"])
if __name__=="__main__":
    unittest.main()
