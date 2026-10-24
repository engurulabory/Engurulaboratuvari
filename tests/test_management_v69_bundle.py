import unittest,sys,io,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from management_v69_bundle import bundle,verify
I={"source":"SYNTHETIC","arch":"arm64","inventory_id":"demo"}
class TestBundle(unittest.TestCase):
 def test_repeatability(self):
  for _ in range(3):
   self.assertEqual(bundle(b"product",I),bundle(b"product",I))
   self.assertEqual(verify(bundle(b"product",I),I),"PASS_REVIEW_BUNDLE")
 def test_drift(self):self.assertEqual(verify(bundle(b"product",I),dict(I,arch="x86_64")),"HOLD_DRIFT")
 def test_empty_payload(self):
  with self.assertRaises(ValueError):bundle(b"",I)
 def test_bad_inventory(self):
  with self.assertRaises(ValueError):bundle(b"product",dict(I,source="UNVERIFIED"))
 def test_payload_tamper(self):
  src=bundle(b"product",I);out=io.BytesIO()
  with zipfile.ZipFile(io.BytesIO(src)) as z:
   manifest=z.read("manifest.json")
  with zipfile.ZipFile(out,"w") as z:
   z.writestr("manifest.json",manifest);z.writestr("product.bin",b"tampered")
  self.assertEqual(verify(out.getvalue(),I),"HOLD_SHA")
if __name__=="__main__":unittest.main()
