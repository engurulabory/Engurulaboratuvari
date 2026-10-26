"""A05 real repository task quality, negative cases and authority scopes."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from run_a05_real_github_tasks import (
    source_bytes, task_catalog, task_git_pins, task_license,
    task_quarantine, task_handoff, TASKS,
)
from build_github_osi_handoff import inspect

BASE=Path(__file__).resolve().parent
def read(name):
    return (BASE/name).read_bytes()

class A05RealTaskTests(unittest.TestCase):
    def test_five_distinct_real_operations(self):
        self.assertEqual(len(TASKS),5)
        self.assertEqual(len(set(row[1] for row in TASKS)),5)
    def test_real_catalog_and_pins(self):
        catalog=source_bytes("source_candidates.json")
        pins=source_bytes("UPSTREAM_GITHUB_PINS_30.json")
        self.assertEqual(task_catalog(catalog)["catalog_count"],30)
        self.assertEqual(task_git_pins(pins,catalog)["source_commit_count"],30)
    def test_real_license_and_quarantine(self):
        catalog=read("source_candidates.json")
        licenses=read("root_license_observations.json")
        self.assertEqual(task_license(catalog,licenses)["approved_for_reuse"],0)
        self.assertEqual(task_quarantine(catalog,licenses)["adopted"],0)
    def test_catalog_illegal_promotion_rejected(self):
        source=json.loads(read("source_candidates.json"))
        source["candidates"][0]["license"]="VERIFIED"
        with self.assertRaises(ValueError):
            task_catalog(json.dumps(source).encode())
    def test_pin_swap_rejected(self):
        pins=json.loads(read("UPSTREAM_GITHUB_PINS_30.json"))
        pins["sources"][0]["readme_git_blob_sha1"]="0"*40
        with self.assertRaises(ValueError):
            task_git_pins(json.dumps(pins).encode(),read("source_candidates.json"))
    def test_review_forgery_rejected(self):
        license_notes=json.loads(read("root_license_observations.json"))
        license_notes["observations"][0]["redistribution_approval"]="PASS"
        with self.assertRaises(ValueError):
            task_license(read("source_candidates.json"),json.dumps(license_notes).encode())
        with self.assertRaises(ValueError):
            task_quarantine(read("source_candidates.json"),json.dumps(license_notes).encode())
    def test_github_handoff_remains_field_hold(self):
        result=task_handoff(read("OSI_HANDOFF_PREPARATION.md"))
        self.assertIs(result["field_authorized"],False)
        self.assertEqual(result["mac_execution"],0)
        self.assertEqual(result["handoff_guide_sha256"],hashlib.sha256(read("OSI_HANDOFF_PREPARATION.md")).hexdigest())
    def test_invalid_archive_rejected(self):
        self.assertEqual(inspect(b"bad ZIP")["state"],"HOLD_PACKAGE_PARSE")

if __name__=="__main__":
    unittest.main()
