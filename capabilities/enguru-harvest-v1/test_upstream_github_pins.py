"""Verify 30 source HEAD-to-README Git blob pair observations without promoting legal rights."""
import copy
import json
import re
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parent
OBS=json.loads((BASE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
REG=json.loads((BASE/"source_candidates.json").read_text(encoding="utf-8"))
HEX40=re.compile(r"^[0-9a-f]{40}$")

def validate(pins,registry):
    if not isinstance(pins,dict) or not isinstance(registry,dict):
        return "HOLD_INPUT"
    records=pins.get("sources")
    candidates=registry.get("candidates")
    if not isinstance(records,list) or not isinstance(candidates,list) or len(records)!=30 or len(candidates)!=30:
        return "HOLD_COUNTS"
    if pins.get("promotion_allowed") is not False or pins.get("verified_count")!=30:
        return "HOLD_ADOPTION_CLAIM"
    for n,(record,candidate) in enumerate(zip(records,candidates),1):
        if not isinstance(record,dict) or not isinstance(candidate,dict):
            return "HOLD_ROW"
        if record.get("id")!="SRC-"+str(n).zfill(2) or record.get("repository")!=candidate.get("repository"):
            return "HOLD_IDENTITY"
        if record.get("readme_path")!="README.md":
            return "HOLD_PATH"
        if HEX40.fullmatch(record.get("commit_sha") if isinstance(record.get("commit_sha"),str) else "") is None:
            return "HOLD_COMMIT"
        blob=record.get("readme_git_blob_sha1")
        if HEX40.fullmatch(blob if isinstance(blob,str) else "") is None or blob!=candidate.get("readme_git_blob_sha1"):
            return "HOLD_BLOB"
        if (record.get("source_archive_sha256") is not None or
                any(record.get(k)!="HOLD" for k in ("legal_approval","security_acceptance","adoption"))):
            return "HOLD_FALSE_ACCEPTANCE"
    if len({r["repository"] for r in records})!=30:
        return "HOLD_DUPLICATES"
    return "PASS_SOURCE_COMMIT_BLOB_OBSERVATION_ONLY"

class UpstreamPinTests(unittest.TestCase):
    def test_real_30_commits(self):
        self.assertEqual(validate(OBS,REG),"PASS_SOURCE_COMMIT_BLOB_OBSERVATION_ONLY")
    def test_forged_license(self):
        x=copy.deepcopy(OBS)
        x["sources"][0]["legal_approval"]="PASS"
        self.assertEqual(validate(x,REG),"HOLD_FALSE_ACCEPTANCE")
    def test_fake_archive_digest(self):
        x=copy.deepcopy(OBS)
        x["sources"][0]["source_archive_sha256"]="a"*64
        self.assertEqual(validate(x,REG),"HOLD_FALSE_ACCEPTANCE")
    def test_wrong_blob(self):
        x=copy.deepcopy(OBS)
        x["sources"][0]["readme_git_blob_sha1"]="b"*40
        self.assertEqual(validate(x,REG),"HOLD_BLOB")
    def test_missing_commit(self):
        x=copy.deepcopy(OBS)
        x["sources"][0]["commit_sha"]=None
        self.assertEqual(validate(x,REG),"HOLD_COMMIT")
    def test_swap_repositories(self):
        x=copy.deepcopy(OBS)
        x["sources"][0],x["sources"][1]=x["sources"][1],x["sources"][0]
        self.assertEqual(validate(x,REG),"HOLD_IDENTITY")
    def test_count(self):
        x=copy.deepcopy(OBS)
        x["sources"].pop()
        self.assertEqual(validate(x,REG),"HOLD_COUNTS")
    def test_no_promote(self):
        x=copy.deepcopy(OBS)
        x["promotion_allowed"]=True
        self.assertEqual(validate(x,REG),"HOLD_ADOPTION_CLAIM")

if __name__=="__main__":
    unittest.main()
