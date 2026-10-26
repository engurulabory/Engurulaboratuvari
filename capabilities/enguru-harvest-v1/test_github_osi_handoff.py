"""GitHub-only OSi handoff anti-tamper/authority regression tests."""
import io
import json
import unittest
import zipfile
from unittest.mock import patch
from pathlib import Path
from build_github_osi_handoff import build, inspect, SOURCES, MAX_PACKAGE_BYTES

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
    def test_expanded_budget_rejected_before_member_read(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
            for name in [*SOURCES,'HANDOFF_MANIFEST.json']:
                z.writestr(name,b'a'*(MAX_PACKAGE_BYTES//2))
        self.assertLess(len(out.getvalue()),MAX_PACKAGE_BYTES)
        with patch.object(zipfile.ZipFile,'read',side_effect=AssertionError('decompression must not start')):
            self.assertEqual(inspect(out.getvalue())['state'],'HOLD_EXPANDED_PACKAGE_BUDGET')

    def test_manifest_array_controlled_hold(self):
        data=remake(self.data,{'HANDOFF_MANIFEST.json':lambda raw:b'[]'})
        self.assertEqual(inspect(data)['state'],'HOLD_MANIFEST_TYPE')

    def test_source_row_schema_controlled_hold(self):
        def change(raw):
            doc=json.loads(raw);doc['sources'][SOURCES[0]]=[]
            return json.dumps(doc).encode()
        self.assertEqual(inspect(remake(self.data,{'HANDOFF_MANIFEST.json':change}))['state'],'HOLD_SOURCE_ENTRY_SCHEMA')

    def test_boolean_size_rejected(self):
        def change(raw):
            doc=json.loads(raw);doc['sources'][SOURCES[0]]['size']=True
            return json.dumps(doc).encode()
        self.assertEqual(inspect(remake(self.data,{'HANDOFF_MANIFEST.json':change}))['state'],'HOLD_SOURCE_ENTRY_SCHEMA')

    def test_unsupported_compression_controlled_hold(self):
        with patch.object(zipfile.ZipFile,'read',side_effect=NotImplementedError('unsupported compression')):
            self.assertEqual(inspect(self.data)['state'],'HOLD_PACKAGE_PARSE')

    def test_repeat_build_exact_head_same_zip(self):
        repeated=build()
        self.assertEqual(repeated['github_head'],self.receipt['github_head'])
        self.assertEqual(repeated['zip_sha256'],self.receipt['zip_sha256'])
        self.assertEqual(repeated['manifest_sha256'],self.receipt['manifest_sha256'])
if __name__=="__main__":
    unittest.main()
