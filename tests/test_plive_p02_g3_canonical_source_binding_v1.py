"""Adversarial source-binding checks; these cannot authorize a native write."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

src = Path(__file__).resolve().parents[1] / "tools/plive_p02_g3_scoped_grant_verify_v1.py"
spec = importlib.util.spec_from_file_location("grant", src)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def prepare():
    c = {"schema": "enguru.work-contract/v1", "workId": m.PROJECT,
         "progressBinding": {"projectId": m.PROJECT, "state": m.P02_STATE_PATH,
                             "worklist": m.P02_WORKLIST_PATH}}
    packages = [{"id": f"P02.S0{i}", "items": [f"P02.S0{i}.0{j}" for j in range(1,4)]}
                for i in range(1,5)]
    w = {"schema": "enguru.plive.p02.worklist/v1", "projectId": m.PROJECT,
         "packages": packages}
    s = {"schema": "enguru.plive.p02.state/v1", "projectId": m.PROJECT,
         "activeItem": m.ITEM, "packages": {"P02.S01": {"items": {
             m.ITEM: {"state": "ACTIVE", "head": None}}}}}
    src = {k: json.dumps(v, sort_keys=True).encode()
           for k, v in {"contract": c, "state": s, "worklist": w}.items()}
    pins = {k: hashlib.sha256(v).hexdigest() for k, v in src.items()}
    return src, pins

class SourceBinding(unittest.TestCase):
    def check(self, src, pins):
        return m.inspect_p02_canonical_source_binding(
            contract_raw=src["contract"], state_raw=src["state"],
            worklist_raw=src["worklist"], approved_source_sha256=pins)

    def test_positive_source_binding_is_not_native_authority(self):
        src, pins = prepare()
        outcome = self.check(src, pins)
        self.assertEqual(outcome["state"], "PASS_SOURCE_BINDING_ONLY")
        self.assertFalse(outcome["authorizedToWrite"])

    def test_missing_or_tampered_pin_fails_closed(self):
        src, pins = prepare()
        self.assertEqual(self.check(src, {})["state"], "HOLD")
        src["state"] = src["state"] + b" "
        self.assertEqual(self.check(src, pins)["state"], "HOLD")

    def test_wrong_project_with_matching_attacker_pins(self):
        src, pins = prepare()
        for name, target in [("contract", b'"workId": "EVIL"'),
                             ("state", b'"projectId": "EVIL"'),
                             ("worklist", b'"projectId": "EVIL"')]:
            with self.subTest(name=name):
                copy = dict(src)
                copy[name] = copy[name].replace(
                    (b'"workId": "' + m.PROJECT.encode() + b'"') if name == "contract"
                    else (b'"projectId": "' + m.PROJECT.encode() + b'"'), target)
                keys = dict(pins)
                keys[name] = hashlib.sha256(copy[name]).hexdigest()
                self.assertEqual(self.check(copy, keys)["state"], "HOLD")

    def test_duplicate_key_rejected(self):
        src, pins = prepare()
        src["contract"] = src["contract"].replace(b'{', b'{"workId":"EVIL",', 1)
        pins["contract"] = hashlib.sha256(src["contract"]).hexdigest()
        self.assertEqual(self.check(src, pins)["state"], "HOLD")

if __name__ == "__main__":
    unittest.main()
