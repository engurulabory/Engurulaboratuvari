"""HYM2 A04 seven upstream dependency seeds: offline adversarial format checks."""
import copy
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse
from tools.arge_block01_a04_dependency_seeds_v1 import blob_sha1, entries, verify

ROOT = Path(__file__).resolve().parents[1] / "governance/enguru-suzgeci/reviews"
MANIFEST = ROOT / "ENGURU_ARGE_A04_DEPENDENCY_SEEDS_V1.json"
UPSTREAM = ROOT / "ENGURU_ARGE_BLOCK01_A04_UPSTREAM_LICENSE_PINS_V1.json"


def fixture():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    u = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    payloads = {}
    for x in m["sources"]:
        key = (x["repository"], x["source_commit_sha"], x["dependency_path"])
        payloads[key] = ("synthetic source: " + "|".join(key)).encode("utf-8")
        x["dependency_git_blob_sha1"] = blob_sha1(payloads[key])
    return m, u, payloads


def fake_fetch(payloads):
    def fetch(url, timeout):
        p = urlparse(url)
        bits = p.path.lstrip("/").split("/", 3)
        return payloads[(bits[0]+"/"+bits[1], bits[2], bits[3])], url
    return fetch


class A04SeedsTests(unittest.TestCase):
    def test_seven_real_manifest_pins_have_original_upstream_commit(self):
        m, u, _ = fixture()
        self.assertEqual(len(entries(m, u)), 7)

    def test_valid_seed_bytes_are_not_sbom_cve_or_official(self):
        m, u, data = fixture()
        receipt = verify(m, u, fetch=fake_fetch(data))
        self.assertEqual(receipt["state"], "PASS_7_PINNED_DEPENDENCY_SEEDS_ONLY")
        self.assertEqual(receipt["matched"], 7)
        self.assertEqual(receipt["checked"], 7)
        for k in ("complete_sbom","exact_version_cve_review","legal_clearance",
                  "a04_official","verified_finish"):
            self.assertEqual(receipt[k], "HOLD")
        self.assertEqual(receipt["independent_e5"], "HOLD_0_OF_18")

    def test_content_tamper_fails_closed(self):
        m,u,data=fixture()
        data[next(iter(data))] += b"mutation"
        result=verify(m,u,fetch=fake_fetch(data))
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["matched"], 6)

    def test_missing_or_redirected_source_holds(self):
        m,u,_=fixture()
        self.assertEqual(verify(m,u,fetch=lambda uri,t: (_ for _ in ()).throw(
            OSError("unavailable")))["matched"],0)
        self.assertEqual(verify(m,u,fetch=lambda uri,t: (b"other",
            "https://untrusted.example/file"))["matched"],0)

    def test_tampered_source_commits_and_roster_fail_without_fetch(self):
        m,u,payloads=fixture()
        corruptions=[
            lambda x: x["sources"].pop(),
            lambda x: x["sources"][0].update(source_commit_sha="f"*40),
            lambda x: x["sources"][0].update(dependency_path="../../evil"),
            lambda x: x["sources"][0].update(coverage="COMPLETE_SBOM"),
            lambda x: x["sources"][0].update(security_policy_status="SOURCE_PINNED_SECURITY_POLICY_BUT_UNKNOWN"),
            lambda x: x["expected"].update(root_or_module_lockfiles=7),
        ]
        for mutate in corruptions:
            with self.subTest(mutate=repr(mutate)):
                x=copy.deepcopy(m)
                mutate(x)
                res=verify(x,u,fetch=fake_fetch(payloads))
                self.assertEqual(res["state"], "HOLD")
                self.assertEqual(res["checked"],0)

    def test_cannot_forge_security_policy_confirmation(self):
        m,u,data=fixture()
        e=next(x for x in m["sources"] if x["technology"]=="Supabase")
        e["security_policy_status"]="SOURCE_PINNED_SECURITY_POLICY"
        receipt=verify(m,u,fetch=fake_fetch(data))
        self.assertEqual(receipt["state"],"HOLD")
        self.assertEqual(receipt["checked"],0)


if __name__ == "__main__":
    unittest.main()
