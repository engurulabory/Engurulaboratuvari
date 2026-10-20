import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import unittest

p=Path(__file__).resolve().parents[1]/"tools/plive_p02_existing_writer_signer_discovery_v1.py"
spec=importlib.util.spec_from_file_location("discovery",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class ReadOnlyDiscoveryTests(unittest.TestCase):
    def test_missing_root_hold(self):
        with TemporaryDirectory() as d:
            self.assertEqual(m.inspect(Path(d)/"absent")["state"],"HOLD_INVALID_ROOT")

    def test_discovers_both_and_no_authority(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            (root/"writer.py").write_text("P02.S01.01\ncanonical writer commit",encoding="utf-8")
            (root/"signer.swift").write_text("SecKeyCreateRandomKey",encoding="utf-8")
            r=m.inspect(root)
            self.assertEqual(r["scanned"],2)
            self.assertEqual(len(r["candidates"]),2)
            self.assertEqual(r["nativeAuthority"],"HOLD")
            self.assertEqual(r["canonicalWrites"],0)
            self.assertEqual(r["keychainOperations"],0)
            self.assertEqual(r["signingOperations"],0)
            for entry in r["candidates"]:
                self.assertEqual(len(entry["sha256"]),64)

    def test_skips_links_and_disallowed(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            (root/"real.py").write_text("SecKeyCreateRandomKey",encoding="utf-8")
            (root/"hidden.bin").write_text("P02.S01.01",encoding="utf-8")
            (root/"linked.py").symlink_to(root/"real.py")
            r=m.inspect(root)
            self.assertEqual([x["path"] for x in r["candidates"]],["real.py"])
            self.assertEqual(r["skipped"],1)

    def test_no_matches_no_auth(self):
        with TemporaryDirectory() as d:
            (Path(d)/"empty.py").write_text("x = 1",encoding="utf-8")
            r=m.inspect(Path(d))
            self.assertEqual(r["candidates"],[])
            self.assertEqual(r["writerAuthority"],"HOLD_NOT_PROVEN")
            self.assertEqual(r["signerAuthority"],"HOLD_NOT_PROVEN")

if __name__=="__main__": unittest.main()
