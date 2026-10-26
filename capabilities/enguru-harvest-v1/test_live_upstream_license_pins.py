"""A05: exact source revision license observations, anti-forgery tests."""
import copy
import json
import unittest
from pathlib import Path
from verify_live_upstream_license_pins import verify_all, inspect_response, fetch_root

BASE=Path(__file__).resolve().parent
PINS=json.loads((BASE/"UPSTREAM_GITHUB_PINS_30.json").read_text(encoding="utf-8"))
LICENSES=json.loads((BASE/"root_license_observations.json").read_text(encoding="utf-8"))
LIC={license_entry["repository"]:license_entry for license_entry in LICENSES["observations"]}

def fixture_root(pin):
    lic=LIC[pin["repository"]]
    entries=[{"name":"README.md","type":"file","sha":pin["readme_git_blob_sha1"]}]
    if lic["path"]:
        entries.append({"name":lic["path"],"type":"file","sha":lic["git_blob_sha1"]})
    return entries

class GitHubExactCommitLicenseTests(unittest.TestCase):
    def test_thirty_same_commit_roots(self):
        result=verify_all(PINS,LICENSES,fixture_root)
        self.assertEqual(result["state"],"PASS_GITHUB_PINNED_SOURCE_AND_LICENSE_BYTES_OBSERVED_ONLY")
        self.assertEqual((result["readme_blob_matches"],result["root_license_matches"],result["root_license_absent"]),(30,29,1))
        self.assertEqual(result["authorized_redistribution"],0)
    def test_tampered_upstream_license_rejected(self):
        def corrupt(pin):
            root=fixture_root(pin)
            if pin["repository"]=="openai/codex":
                root[1]["sha"]="f"*40
            return root
        self.assertEqual(verify_all(PINS,LICENSES,corrupt)["state"],"HOLD")
    def test_wrong_readme_rejected(self):
        def corrupt(pin):
            root=fixture_root(pin)
            if pin["repository"]=="openai/codex":
                root[0]["sha"]="0"*40
            return root
        self.assertEqual(verify_all(PINS,LICENSES,corrupt)["state"],"HOLD")
    def test_unauthorized_reuse_rejected(self):
        license_claim=copy.deepcopy(LICENSES)
        license_claim["observations"][0]["redistribution_approval"]="PASS"
        self.assertEqual(verify_all(PINS,license_claim,fixture_root)["state"],"HOLD")
    def test_missing_root_license_at_expected_commit(self):
        def corrupt(pin):
            data=fixture_root(pin)
            if pin["repository"]=="openai/codex":
                data=data[:1]
            return data
        self.assertEqual(verify_all(PINS,LICENSES,corrupt)["state"],"HOLD")
    def test_fake_new_root_license_at_missing_repo(self):
        def corrupt(pin):
            data=fixture_root(pin)
            if pin["repository"]=="anthropics/skills":
                data.append({"name":"LICENSE","sha":"f"*40,"type":"file"})
            return data
        self.assertEqual(verify_all(PINS,LICENSES,corrupt)["state"],"HOLD")
    def test_wrong_commit_rejected(self):
        x=copy.deepcopy(PINS["sources"][0])
        x["commit_sha"]="invalid-ref"
        self.assertEqual(inspect_response(x,LIC[x["repository"]],fixture_root(x))["state"],"HOLD")
    def test_root_symlink_rejected(self):
        x=PINS["sources"][0]
        rows=fixture_root(x)
        rows[1]["type"]="symlink"
        self.assertEqual(inspect_response(x,LIC[x["repository"]],rows)["state"],"HOLD")
    def test_external_untrusted_url_rejected(self):
        x=copy.deepcopy(PINS["sources"][0])
        x["repository"]="https://other-host.invalid/repo"
        with self.assertRaises(ValueError):
            fetch_root(x,"")
    def test_network_failure_must_hold(self):
        def fail(_):
            raise OSError("temporary network outage")
        self.assertEqual(verify_all(PINS,LICENSES,fail)["state"],"HOLD")
    def test_duplicate_manifest_rejected(self):
        x=copy.deepcopy(LICENSES)
        x["observations"][1]["repository"]=x["observations"][0]["repository"]
        self.assertEqual(verify_all(PINS,x,fixture_root)["state"],"HOLD")
    def test_source_release_is_not_legal_authority(self):
        outcome=verify_all(PINS,LICENSES,fixture_root)
        self.assertFalse(any(x.get("redistribution_authorized",False) for x in outcome["results"]))
        self.assertEqual(outcome["independently_proven_skills"],0)

if __name__=="__main__":
    unittest.main()
