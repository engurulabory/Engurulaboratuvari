"""HYM2 Hedef 1 / A04: live GitHub byte provenance, adversarial unit oracle.

All fixtures are synthetic and never attest customer deployments, CVEs, or E5.
The CI live-fetch step independently checks the actual upstream commit bytes.
"""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

from tools.arge_block01_a04_live_verify_v1 import _blob_sha1, _entries, verify_upstream

MANIFEST = (Path(__file__).resolve().parents[1] / "governance" /
            "enguru-suzgeci" / "reviews" /
            "ENGURU_ARGE_BLOCK01_A04_UPSTREAM_LICENSE_PINS_V1.json")


def controlled_fixture():
    record = json.loads(MANIFEST.read_text(encoding="utf-8"))
    payloads = {}
    for item in record["tech"]:
        files = [(item, "license_path", "license_git_blob_sha")]
        files.extend((x, "path", "git_blob_sha") for x in item["additional_license_files"])
        if "security_policy" in item:
            files.append((item["security_policy"], "path", "git_blob_sha"))
        for target, key, digest_key in files:
            path = target[key]
            content = f"synthetic:{item['repository']}:{item['source_commit_sha']}:{path}".encode()
            target[digest_key] = _blob_sha1(content)
            payloads[(item["repository"], item["source_commit_sha"], path)] = content
    return record, payloads


def fake_fetch(payloads):
    def fetch(url, timeout):
        info = urlparse(url)
        segments = info.path.lstrip("/").split("/", 3)
        repo = segments[0] + "/" + segments[1]
        raw = payloads[(repo, segments[2], segments[3])]
        return raw, url
    return fetch


class A04RemoteSourceTests(unittest.TestCase):
    def test_real_manifest_contains_13_immutable_source_pins(self):
        raw = json.loads(MANIFEST.read_text(encoding="utf-8"))
        entries = _entries(raw)
        self.assertEqual(len(entries), 13)
        self.assertEqual(sum(e["kind"] == "LICENSE" for e in entries), 7)
        self.assertEqual(sum(e["kind"] == "EXTRA_LICENSE" for e in entries), 3)
        self.assertEqual(sum(e["kind"] == "SECURITY_POLICY" for e in entries), 3)

    def test_synthetic_13_sources_only_prove_public_byte_identity(self):
        fixture, payloads = controlled_fixture()
        result = verify_upstream(fixture, fetch=fake_fetch(payloads))
        self.assertEqual(result["state"], "PASS_PINNED_PUBLIC_BYTES_ONLY")
        self.assertEqual(result["matched"], 13)
        self.assertTrue(all(x["bytes_sha256"] == hashlib.sha256(
            payloads[(x["repository"], x["commit"], x["path"])]).hexdigest()
            for x in result["files"]))
        for key in ("legal_clearance", "cve", "sbom", "a04_official", "verified_finish"):
            self.assertEqual(result[key], "HOLD")
        self.assertEqual(result["independent_e5"], "HOLD_0_OF_18")

    def test_remote_bytes_mutation_fails_closed(self):
        fixture, payloads = controlled_fixture()
        first = next(iter(payloads))
        payloads[first] += b"tampered"
        result = verify_upstream(fixture, fetch=fake_fetch(payloads))
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["matched"], 12)
        self.assertIn("HOLD_BLOB_MISMATCH", [x["state"] for x in result["files"]])

    def test_unavailable_source_fails_closed(self):
        fixture, payloads = controlled_fixture()
        def unavailable(url, timeout):
            raise OSError("network")
        result = verify_upstream(fixture, fetch=unavailable)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["matched"], 0)
        self.assertEqual(result["checked"], 13)

    def test_untrusted_redirect_fails_closed(self):
        fixture, payloads = controlled_fixture()
        def redirect(url, timeout):
            return b"other", "https://evil.example/blob"
        result = verify_upstream(fixture, fetch=redirect)
        self.assertEqual(result["state"], "HOLD")
        self.assertEqual(result["matched"], 0)

    def test_roster_and_license_pin_requirements(self):
        original, payloads = controlled_fixture()
        for mutation in ("scope", "missing", "duplicate", "bad_ref", "bad_sha", "security"):
            with self.subTest(mutation=mutation):
                copy_manifest = copy.deepcopy(original)
                if mutation == "scope":
                    copy_manifest["scope"] = "WRONG_SCOPE"
                elif mutation == "missing":
                    copy_manifest["tech"][0]["case_ids"].pop()
                elif mutation == "duplicate":
                    copy_manifest["tech"][0]["additional_license_files"].append(
                        copy.deepcopy(copy_manifest["tech"][0]["additional_license_files"][0]))
                elif mutation == "bad_ref":
                    copy_manifest["tech"][0]["repository"] = "example/../evil"
                elif mutation == "bad_sha":
                    copy_manifest["tech"][0]["license_git_blob_sha"] = "1" * 38
                elif mutation == "security":
                    copy_manifest["tech"][0].pop("security_policy")
                verdict = verify_upstream(copy_manifest, fetch=fake_fetch(payloads))
                self.assertEqual(verdict["state"], "HOLD")
                self.assertEqual(verdict["checked"], 0)

    def test_non_dict_records_fail_closed(self):
        fixture, payloads = controlled_fixture()
        fixture["tech"][2] = None
        self.assertEqual(verify_upstream(fixture, fetch=fake_fetch(payloads))["state"], "HOLD")


if __name__ == "__main__":
    unittest.main()
