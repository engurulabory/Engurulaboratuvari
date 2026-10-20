import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/"tools/plive_p02_g3a_exact_build_provenance_v1.py"
s=importlib.util.spec_from_file_location("provenance",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def make():
    files={key:(key+"-fixture").encode() for key in
           ("source","buildCommand","unsignedBinary","signedBinary","signingReceipt","profileEligibilityEvidence")}
    manifest={"schema":"enguru.p02.g3a.exact-build-provenance/v1",
              "teamId":"DNMRGL53T4","bundleId":"local.enguru.plive.g3a.signer.diagnostic.v1"}
    manifest.update({k+"Sha256":hashlib.sha256(v).hexdigest() for k,v in files.items()})
    raw=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()
    return raw, files, hashlib.sha256(raw).hexdigest()

class ProvenanceTests(unittest.TestCase):
    def test_matching_bytes_never_authorize_issuer(self):
        raw,files,pin=make()
        r=m.check(raw,files,approved_manifest_sha256=pin)
        self.assertEqual(r["state"],"PASS_PINNED_PROVENANCE_BYTES_ONLY")
        self.assertEqual(r["buildProvenance"],"HOLD_PRODUCER_ATTESTATION_REQUIRED")
        self.assertEqual(r["nativeIssuer"],"HOLD")
        self.assertFalse(r["authorizedToWrite"])

    def test_tampered_each_file(self):
        raw,files,pin=make()
        for k in files:
            with self.subTest(k=k):
                bad=dict(files);bad[k]+=b"x"
                self.assertEqual(m.check(raw,bad,approved_manifest_sha256=pin)["state"],"HOLD")

    def test_wrong_pin(self):
        raw,files,pin=make()
        self.assertEqual(m.check(raw,files,approved_manifest_sha256="0"*64)["state"],"HOLD")

    def test_missing_file(self):
        raw,files,pin=make(); del files["unsignedBinary"]
        self.assertEqual(m.check(raw,files,approved_manifest_sha256=pin)["state"],"HOLD")

    def test_untrusted_extra_field(self):
        raw,files,pin=make()
        obj=json.loads(raw);obj["issuerQualified"]=True
        raw=json.dumps(obj).encode()
        r=m.check(raw,files,approved_manifest_sha256=hashlib.sha256(raw).hexdigest())
        self.assertEqual(r["state"],"HOLD")

    def test_duplicate_key(self):
        raw,files,pin=make()
        raw=raw[:-1]+b',"schema":"fake"}'
        self.assertEqual(m.check(raw,files,approved_manifest_sha256=hashlib.sha256(raw).hexdigest())["state"],"HOLD")

if __name__=="__main__":
    unittest.main()
