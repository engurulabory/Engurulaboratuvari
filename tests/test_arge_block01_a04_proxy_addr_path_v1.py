"""A04 source-chain regression: counterfeit source, advisory drift, and patch range."""
import copy
import json
import unittest

from tools.arge_block01_a04_proxy_addr_path_v1 import (
    PINS,MEDUSA,MEDUSA_COMMIT,ADVISORY_REPO,ADVISORY_COMMIT,ADVISORY_PATH,
    git_blob,range_allows,verify,
)


def fixture():
    yarn='''"express@npm:^4.21.0":
  version: 4.22.1
  resolution: "express@npm:4.22.1"
  dependencies:
    proxy-addr: ~2.0.7

"proxy-addr@npm:~2.0.7":
  version: 2.0.7
  resolution: "proxy-addr@npm:2.0.7"
  dependencies:
    forwarded: 0.2.0
'''
    advisory={"id":"GHSA-jqcg-44mw-7w3h","aliases":["CVE-2026-90711"],
              "affected":[{"package":{"name":"proxy-addr","ecosystem":"npm"},
                           "ranges":[{"type":"ECOSYSTEM","events":[
                               {"introduced":"1.1.0"},{"fixed":"2.0.8"}]}]}]}
    app={"name":"@medusajs/medusa","dependencies":{"express":"^4.21.0"}}
    framework={"name":"@medusajs/framework","dependencies":{"express":"^4.21.0"}}
    return {
        (MEDUSA,MEDUSA_COMMIT,"yarn.lock"):yarn.encode(),
        (MEDUSA,MEDUSA_COMMIT,"packages/medusa/package.json"):json.dumps(app).encode(),
        (MEDUSA,MEDUSA_COMMIT,"packages/core/framework/package.json"):json.dumps(framework).encode(),
        (ADVISORY_REPO,ADVISORY_COMMIT,ADVISORY_PATH):json.dumps(advisory).encode(),
    }


class SourceFixPath(unittest.TestCase):
    def mock_fetch(self,files):
        return lambda repo,commit,path:files[(repo,commit,path)]

    def test_exact_original_sources_resolve_vulnerable_and_patch_compatible(self):
        data=fixture()
        import tools.arge_block01_a04_proxy_addr_path_v1 as tool
        original=tool.PINS.copy()
        try:
            tool.PINS.clear()
            tool.PINS.update({k:git_blob(v) for k,v in data.items()})
            receipt=verify(fetch=self.mock_fetch(data))
        finally:
            tool.PINS.clear()
            tool.PINS.update(original)
        self.assertEqual(receipt["state"],"PASS_SOURCE_FIX_COMPATIBILITY_ONLY")
        self.assertEqual(receipt["sources_verified"],4)
        self.assertTrue(receipt["patch_in_existing_express_selector"])
        self.assertEqual(receipt["fixed_version"],"2.0.8")
        self.assertEqual(len(receipt["source_paths"]),2)
        for k in ("medusa_installation_proven","application_proxy_trust_config_proven",
                  "real_customer_exposure","regression_for_real_installation",
                  "a04_official","verified_finish"):
            self.assertEqual(receipt[k],"HOLD")

    def test_semver_patch_tilde_boundary(self):
        self.assertTrue(range_allows("~2.0.7","2.0.7"))
        self.assertTrue(range_allows("~2.0.7","2.0.8"))
        self.assertTrue(range_allows("~2.0.7","2.0.99"))
        self.assertFalse(range_allows("~2.0.7","2.0.6"))
        self.assertFalse(range_allows("~2.0.7","2.1.0"))
        with self.assertRaises(ValueError):
            range_allows("^2.0.7","2.0.8")

    def test_changed_upstream_bytes_fail_closed(self):
        data=fixture()
        receipt=verify(fetch=self.mock_fetch(data))
        # Static production pins never match synthetic fixtures.
        self.assertEqual(receipt["state"],"HOLD")
        self.assertLess(receipt["sources_verified"],4)

    def test_broken_express_proxy_edge_fails(self):
        import tools.arge_block01_a04_proxy_addr_path_v1 as tool
        data=fixture()
        key=(MEDUSA,MEDUSA_COMMIT,"yarn.lock")
        data[key]=data[key].replace(b"proxy-addr: ~2.0.7",b"proxy-addr: ~2.0.6")
        saved=tool.PINS.copy()
        try:
            tool.PINS.clear()
            tool.PINS.update({k:git_blob(v) for k,v in data.items()})
            result=verify(fetch=self.mock_fetch(data))
        finally:
            tool.PINS.clear()
            tool.PINS.update(saved)
        self.assertEqual(result["state"],"HOLD")
        self.assertEqual(result["sources_verified"],4)

    def test_advisory_fixed_event_forgery_fails(self):
        import tools.arge_block01_a04_proxy_addr_path_v1 as tool
        data=fixture()
        key=(ADVISORY_REPO,ADVISORY_COMMIT,ADVISORY_PATH)
        a=json.loads(data[key])
        a["affected"][0]["ranges"][0]["events"][1]["fixed"]="2.0.7"
        data[key]=json.dumps(a).encode()
        saved=tool.PINS.copy()
        try:
            tool.PINS.clear()
            tool.PINS.update({k:git_blob(v) for k,v in data.items()})
            result=verify(fetch=self.mock_fetch(data))
        finally:
            tool.PINS.clear()
            tool.PINS.update(saved)
        self.assertEqual(result["state"],"HOLD")

    def test_wrong_package_authority_fails(self):
        import tools.arge_block01_a04_proxy_addr_path_v1 as tool
        data=fixture()
        key=(MEDUSA,MEDUSA_COMMIT,"packages/medusa/package.json")
        record=json.loads(data[key])
        record["dependencies"]["express"]="^5.0.0"
        data[key]=json.dumps(record).encode()
        saved=tool.PINS.copy()
        try:
            tool.PINS.clear()
            tool.PINS.update({k:git_blob(v) for k,v in data.items()})
            result=verify(fetch=self.mock_fetch(data))
        finally:
            tool.PINS.clear()
            tool.PINS.update(saved)
        self.assertEqual(result["state"],"HOLD")

    def test_unreachable_authority_keeps_result_hold(self):
        def denied(repo,commit,path):
            raise OSError("offline")
        receipt=verify(fetch=denied)
        self.assertEqual(receipt["state"],"HOLD")
        self.assertEqual(receipt["a04_official"],"HOLD")
        self.assertEqual(receipt["sources_verified"],0)


if __name__=="__main__":
    unittest.main()
