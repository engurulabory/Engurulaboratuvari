"""Adversarial source-binding checks; these cannot authorize a native write."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

src = Path(__file__).resolve().parents[1] / "tools/plive_p02_g3_scoped_grant_verify_v1.py"
spec = importlib.util.spec_from_file_location("grant", src)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def prepare():
    c = {"schema": "enguru.work-contract/v1", "workId": m.PROJECT,
         "progressBinding": {"projectId": m.PROJECT, "state": m.P02_STATE_PATH,
                             "worklist": m.P02_WORKLIST_PATH}}
    packages = [{"id": f"P02.S0{i}", "items": [f"P02.S0{i}.0{j}" for j in range(1, 4)]}
                for i in range(1, 5)]
    w = {"schema": "enguru.plive.p02.worklist/v1", "projectId": m.PROJECT,
         "packages": packages}
    state_packages = {}
    for i, p in enumerate(packages):
        state_packages[p["id"]] = {
            "state": "ACTIVE" if i == 0 else "PENDING",
            "doneCheck": "PENDING",
            "items": {item: {"state": "ACTIVE" if item == m.ITEM else "PENDING",
                             "head": None} for item in p["items"]}}
    s = {"schema": "enguru.plive.p02.state/v1", "projectId": m.PROJECT,
         "activeItem": m.ITEM, "activePackage": "P02.S01",
         "verifiedFinish": "HOLD", "humanAcceptance": "PENDING",
         "packages": state_packages}
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

    def test_repinning_partial_or_preaccepted_state_is_rejected(self):
        src, pins = prepare()
        for change in (
            lambda x: x["packages"].pop("P02.S04"),
            lambda x: x["packages"]["P02.S01"]["items"].pop("P02.S01.02"),
            lambda x: x["packages"]["P02.S01"]["items"][m.ITEM].update(state="PASS"),
            lambda x: x.update(verifiedFinish="VERIFIED"),
            lambda x: x.update(activePackage="P02.S03"),
        ):
            with self.subTest(change=repr(change)):
                changed = dict(src)
                obj = json.loads(src["state"])
                change(obj)
                changed["state"] = json.dumps(obj, sort_keys=True).encode()
                changed_pins = dict(pins)
                changed_pins["state"] = hashlib.sha256(changed["state"]).hexdigest()
                self.assertEqual(self.check(changed, changed_pins)["state"], "HOLD")

    def test_repinning_changed_worklist_does_not_pass(self):
        src, pins = prepare()
        for change in (
            lambda x: x["packages"][3]["items"].pop(),
            lambda x: x["packages"].reverse(),
            lambda x: x["packages"][0]["items"].append("P02.S01.04"),
        ):
            changed = dict(src)
            obj = json.loads(src["worklist"])
            change(obj)
            changed["worklist"] = json.dumps(obj, sort_keys=True).encode()
            changed_pins = dict(pins)
            changed_pins["worklist"] = hashlib.sha256(changed["worklist"]).hexdigest()
            self.assertEqual(self.check(changed, changed_pins)["state"], "HOLD")


    def test_bound_grant_preimage_matches_exact_native_bytes(self):
        src, pins = prepare()
        real_preimage = hashlib.sha256(src["state"]).hexdigest()
        grant = m.canonical({"preimageSha256": real_preimage})
        params = {
            "contract_raw": src["contract"],
            "state_raw": src["state"],
            "worklist_raw": src["worklist"],
            "approved_source_sha256": pins,
            "trust_record_raw": b"independent-trust-fixture",
            "approved_trust_sha256": "a" * 64,
            "expected_head": "b" * 40,
            "expected_evidence_sha256": "c" * 64,
            "expected_approval_sha256": "d" * 64,
            "observed_at": "2026-10-20T12:00:00Z",
            "consumed_nonces": frozenset(),
        }
        with mock.patch.object(m, "verify_with_pinned_trust",
                               return_value={"state": "CRYPTO_AND_SCOPE_VALID_ONLY",
                                             "authorizedToWrite": False}) as verifier:
            result = m.verify_bound_p02_scoped_grant(grant, "sig", **params)
            self.assertEqual(result["state"], "CRYPTO_AND_SCOPE_VALID_ONLY")
            self.assertFalse(result["authorizedToWrite"])
            self.assertEqual(verifier.call_args.kwargs["expected"]["preimageSha256"],
                             real_preimage)

            forged = m.canonical({"preimageSha256": "0" * 64})
            self.assertEqual(m.verify_bound_p02_scoped_grant(
                forged, "sig", **params)["state"], "HOLD")
            self.assertEqual(verifier.call_count, 1)

            altered = dict(params, state_raw=src["state"] + b" ")
            self.assertEqual(m.verify_bound_p02_scoped_grant(
                grant, "sig", **altered)["state"], "HOLD")
            self.assertEqual(verifier.call_count, 1)

            wrong_head = dict(params, expected_head="unapproved")
            self.assertEqual(m.verify_bound_p02_scoped_grant(
                grant, "sig", **wrong_head)["state"], "HOLD")
            self.assertEqual(verifier.call_count, 1)

    def test_duplicate_key_rejected(self):
        src, pins = prepare()
        src["contract"] = src["contract"].replace(b'{', b'{"workId":"EVIL",', 1)
        pins["contract"] = hashlib.sha256(src["contract"]).hexdigest()
        self.assertEqual(self.check(src, pins)["state"], "HOLD")

if __name__ == "__main__":
    unittest.main()
