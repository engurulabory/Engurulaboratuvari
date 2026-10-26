"""V1.4.1 HYM method source/authority/scope three adversarial simulations."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from tools import arge_hym_v141_crosswalk_v1 as m

ROOT=Path(__file__).resolve().parents[1]

def fixtures():
    h=json.loads((ROOT/m.HANDOFF).read_text(encoding="utf8"))
    c=json.loads((ROOT/m.CASES).read_text(encoding="utf8"))
    arch={
      "id":"ENGURU_ZULFIKAR_V1_4_1",
      "gates":[{"id":v,"acceptance":"ACC_"+v,
                "requiredOutputs":["one","two","three","four","five"]}
               for v in m.STAGES],
      "transitionRule":"ONLY_CURRENT_GATE_EVIDENCED_100_PASS_ALLOWS_NEXT_GATE",
      "userGoalContract":{"id":"ZF.V141.PREGH.2026-10-26"}}
    dom={"id":"ENGURU_DOM_V1_0",
         "scope":"PRE_GITHUB_PREPARATION_AND_DISPOSABLE_TESTS_ONLY",
         "fiveEqualWeightEngineeringRequirements":[{"weight":20} for _ in range(5)]}
    raw={k:json.dumps(v,sort_keys=True).encode()
         for k,v in zip(m.PINS,(arch,dom))}
    pins={k:hashlib.sha256(v).hexdigest() for k,v in raw.items()}
    return h,c,raw,pins

_MISSING=object()
def evaluate(h=_MISSING,c=_MISSING,raw=None,pins=None):
    baseh,basec,braw,bpins=fixtures()
    return m.assess(baseh if h is _MISSING else h,
                    basec if c is _MISSING else c,
                    fetcher=lambda name:(braw if raw is None else raw)[name],
                    pins=bpins if pins is None else pins)

class V141SourceCrosswalkTests(unittest.TestCase):
    def test_positive_source_method_only_never_stage_or_official_pass(self):
        out=evaluate()
        self.assertEqual(out["crosswalkScore"],100)
        self.assertEqual(out["state"],"PASS_METHOD_SOURCE_CROSSWALK_ONLY")
        self.assertEqual(list(out["stageAcceptance"]),list(m.STAGES))
        self.assertEqual(out["namespace"]["methodA03"],"ZF.V141.A03")
        self.assertEqual(out["namespace"]["originalA03"],"HYM.A03")
        self.assertTrue(all(v.startswith("HOLD_") for v in out["stageAcceptance"].values()))
        self.assertEqual(out["official"],"0/40")
        self.assertEqual(out["verifiedFinish"],"HOLD")

    def test_sim1_true_bytes_and_stage_identity(self):
        h,c,raw,pins=fixtures()
        for name,mutation in (
          ("source_substitution",lambda r:r.__setitem__(next(iter(r)),b"FAKE")),
          ("source_json_wrong_gate",lambda r:r.__setitem__(
              next(iter(r)),r[next(iter(r))].replace(b'"T01"',b'"T99"'))),
          ("fake_extra_file",lambda r:r.__setitem__("rogue",b'{}')),
        ):
            with self.subTest(name=name):
                alt=dict(raw)
                mutation(alt)
                result=evaluate(h,c,raw=alt,pins=pins)
                if name=="fake_extra_file":
                    self.assertEqual(result["state"],"PASS_METHOD_SOURCE_CROSSWALK_ONLY")
                    self.assertEqual(len(result["passed"]),10)
                else:
                    self.assertEqual(result["state"],"HOLD")
                    self.assertIn("SOURCE_SHA256_MISMATCH",result["reason"])

    def test_sim2_preserved_40_18_and_original_id(self):
        h,c,raw,pins=fixtures()
        changes=[
          lambda d:d["single_active_execution_queue"][0]["scope"].pop(),
          lambda d:d["preserved_scope"].update(cells=233),
          lambda d:d["single_active_execution_queue"][0]["scope"].append("A03"),
        ]
        for i,change in enumerate(changes):
            with self.subTest(case=i):
                hd=copy.deepcopy(h);change(hd)
                out=evaluate(h=hd,c=c,raw=raw,pins=pins)
                self.assertEqual(out["state"],"HOLD")
                self.assertLess(out["crosswalkScore"],100)

    def test_sim3_solo_owner_and_false_external_acceptance(self):
        h,c,raw,pins=fixtures()
        changes=[
          lambda d:d["solo_owner_github_preparation_v2"].update(approved_owner="fake"),
          lambda d:d["A03"].update(decision="PASS_UNVERIFIED"),
          lambda d:d["A05_A06"].update(independent_e5="18/18"),
          lambda d:d["current_counters"].update(overall_official="40/40"),
        ]
        for i,change in enumerate(changes):
            with self.subTest(case=i):
                hd=copy.deepcopy(h);change(hd)
                out=evaluate(h=hd,c=c,raw=raw,pins=pins)
                self.assertEqual(out["state"],"HOLD")
                self.assertEqual(out["verifiedFinish"],"HOLD")

    def test_external_source_unavailable_is_hold(self):
        h,c,raw,pins=fixtures()
        def fail(name):raise OSError("unavailable")
        result=m.assess(h,c,fetcher=fail,pins=pins)
        self.assertEqual(result["state"],"HOLD")
        self.assertEqual(result["official"],"0/40")

    def test_malformed_inputs_fail_closed(self):
        _,c,raw,pins=fixtures()
        for bad in (None,{},[],False):
            with self.subTest(type=type(bad).__name__):
                self.assertEqual(evaluate(h=bad,c=c,raw=raw,pins=pins)["state"],"HOLD")

if __name__=="__main__":unittest.main()
