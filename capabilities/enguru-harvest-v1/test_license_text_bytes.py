"""A05 exact-root-license-byte validation: factual integrity, not legal authority."""
import base64
import copy
import hashlib
import json
import unittest
from pathlib import Path
from verify_license_text_bytes import (
    blob_sha, classify_risk, validate_license_bytes, reconcile, fetch_license,
)

HERE=Path(__file__).resolve().parent
PINS=json.loads((HERE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
REG=json.loads((HERE/"root_license_observations.json").read_text(encoding="utf-8"))
FIRST=PINS["sources"][0]
LIC=next(r for r in REG["observations"] if r["repository"]==FIRST["repository"])

class LicenseBytesTests(unittest.TestCase):
    def setUp(self):
        self.pin=copy.deepcopy(FIRST)
        self.license=copy.deepcopy(LIC)
        self.payload=b"MIT License\\n\\nPermission is hereby granted, free of charge\\n"
        self.license["git_blob_sha1"]=blob_sha(self.payload)
        self.response={
            "type":"file","path":self.license["path"],
            "sha":self.license["git_blob_sha1"],
            "size":len(self.payload),"encoding":"base64",
            "content":base64.b64encode(self.payload).decode("ascii"),
        }
    def test_known_git_blob_calculation(self):
        # Git empty blob ID is stable, independent of any repository.
        self.assertEqual(blob_sha(b""),"e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")
    def test_normal_valid_source(self):
        r=validate_license_bytes(self.pin,self.license,self.response)
        self.assertEqual(r["state"],"PASS_LICENSE_BYTES_OBSERVED_ONLY")
        self.assertEqual(r["license_fulltext_sha256"],hashlib.sha256(self.payload).hexdigest())
        self.assertIs(r["legal_reuse_authorized"],False)
    def test_github_multiline_base64(self):
        x=copy.deepcopy(self.response)
        x["content"]=x["content"][:15]+chr(10)+x["content"][15:]
        self.assertEqual(validate_license_bytes(self.pin,self.license,x)["state"],"PASS_LICENSE_BYTES_OBSERVED_ONLY")
    def test_same_metadata_different_bytes_fails(self):
        x=copy.deepcopy(self.response)
        x["content"]=base64.b64encode(self.payload.replace(b"Permission",b"PermissionX")).decode()
        x["size"]=len(self.payload.replace(b"Permission",b"PermissionX"))
        self.assertEqual(validate_license_bytes(self.pin,self.license,x)["state"],"HOLD_LICENSE_BLOB_INTEGRITY")
    def test_malformed_base64_fails(self):
        x=copy.deepcopy(self.response)
        x["content"]="BOGUS%%%%"
        self.assertEqual(validate_license_bytes(self.pin,self.license,x)["state"],"HOLD_LICENSE_BYTES")
    def test_wrong_path_fails(self):
        x=copy.deepcopy(self.response)
        x["path"]="README.md"
        self.assertEqual(validate_license_bytes(self.pin,self.license,x)["state"],"HOLD_GITHUB_METADATA_MISMATCH")
    def test_reuse_promotion_is_rejected(self):
        x=copy.deepcopy(self.license)
        x["redistribution_approval"]="PASS"
        self.assertEqual(validate_license_bytes(self.pin,x,self.response)["state"],"HOLD_SOURCE_OR_RIGHTS")
    def test_source_adoption_promotion_rejected(self):
        x=copy.deepcopy(self.pin)
        x["adoption"]="PASS"
        self.assertEqual(validate_license_bytes(x,self.license,self.response)["state"],"HOLD_SOURCE_OR_RIGHTS")
    def test_rejects_wrong_size(self):
        x=copy.deepcopy(self.response)
        x["size"]+=1
        self.assertEqual(validate_license_bytes(self.pin,self.license,x)["state"],"HOLD_LICENSE_BLOB_INTEGRITY")
    def test_rejects_suspect_host(self):
        x=copy.deepcopy(self.pin)
        x["repository"]="https://evil.example/path"
        with self.assertRaises(ValueError):
            fetch_license(x,self.license,"")
    def test_license_scope_flags_not_clearance(self):
        self.assertEqual(classify_risk("anthropics/claude-code","terms"),"RESTRICTED_VENDOR_COMMERCIAL_TERMS_REVIEW")
        self.assertEqual(classify_risk("meilisearch/meilisearch","BUSL"),"MIXED_BUSL_AND_MIT_COMPONENT_SCOPE_REVIEW")
        self.assertEqual(classify_risk("HypothesisWorks/hypothesis","MPL"),"MPL_FILE_LEVEL_OBLIGATIONS_REVIEW")
    def test_real_30_29_proof_without_license_rights(self):
        # Synthetic byte transport tests only; the GitHub job tests genuine bytes.
        sources=copy.deepcopy(PINS)
        registry=copy.deepcopy(REG)
        for pin in sources["sources"]:
            license_row=next(r for r in registry["observations"] if r["repository"]==pin["repository"])
            if license_row["path"]:
                license_row["git_blob_sha1"]=blob_sha(self.payload)
        def fake_fetch(pin,lic):
            return {"type":"file","path":lic["path"],"sha":lic["git_blob_sha1"],
                    "size":len(self.payload),"encoding":"base64",
                    "content":base64.b64encode(self.payload).decode("ascii")}
        result=reconcile(sources,registry,fake_fetch)
        self.assertEqual(result["state"],"PASS_PINNED_29_LICENSE_FULLTEXT_DIGESTS_OBSERVED_ONLY")
        self.assertEqual((result["root_license_fulltext_sha256_count"],result["legal_reuse_approvals"]),(29,0))
    def test_network_failure_holds(self):
        def failure(pin,license_row):
            raise OSError("github unreachable")
        self.assertEqual(reconcile(PINS,REG,failure)["state"],"HOLD_LICENSE_SOURCE_VERIFICATION")
    def test_forged_license_registry_holds(self):
        registry=copy.deepcopy(REG)
        registry["observations"][0]["repository"]="forged/owner"
        self.assertEqual(reconcile(PINS,registry,lambda pin,license_row:None)["state"],"HOLD_REPOSITORY_SETS")

if __name__=="__main__":
    unittest.main()
