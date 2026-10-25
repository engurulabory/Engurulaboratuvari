"""Independent arithmetic oracle, hostile inputs and real isolated source capture."""
import copy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from tools import pilive_prepare_v2 as prep
from tools import pilive_osi_source_observer_v2 as obs

ROOT = Path(__file__).resolve().parents[1]


class RehearsalTests(unittest.TestCase):
    def test_full_user_flow_fixture_and_reopen(self):
        original = prep.fixture()
        r = prep.rehearsal(original, 1001)
        self.assertEqual(r["state"], "PASS_MODEL_ONLY")
        self.assertEqual(r["native"]["finish"], "HOLD")
        self.assertEqual(r["technical"]["percent"], 100)
        self.assertEqual(len(r["active"]), 1)
        self.assertEqual(r["drawer"]["head"], obs.BASELINE_HEAD)
        self.assertEqual(prep.rehearsal(prep.parse(prep.canonical(original)), 1001), r)
        self.assertFalse(r["officialPassGranted"])
        self.assertEqual(original, prep.fixture())

    def test_separate_fraction_oracle_across_counter_range(self):
        for total in range(1, 30):
            for done in range(total+1):
                x = prep.fixture(); x["technical"] = {"completed": done, "total": total}
                r = prep.rehearsal(x, 1001)
                self.assertEqual(r["technical"]["percent"], round(float(Fraction(done,total)*100),6))
                self.assertEqual(r["native"]["countedPass"],0)

    def test_all_ten_counterconditions(self):
        rows = prep.adversarial()
        self.assertEqual(len(rows),10)
        self.assertEqual(len({x[0] for x in rows}),10)
        self.assertTrue(all(ok for _,ok in rows),rows)

    def test_malformed_input_is_hold(self):
        for key in ("source", "technical", "native", "active", "workItems"):
            for value in (None, True, 42, "data", [None], {}):
                with self.subTest(key=key,value=value):
                    x=prep.fixture();x[key]=value
                    self.assertEqual(prep.rehearsal(x,1001)["state"],"HOLD")
        self.assertEqual(prep.rehearsal({},True)["state"],"HOLD")

    def test_wrong_percent_bool_and_boundaries(self):
        for data in ({"completed":True,"total":12}, {"completed":0,"total":0},
                     {"completed":13,"total":12}, {"completed":-1,"total":12},
                     {"completed":1,"total":2,"percent":100},
                     {"completed":1,"total":2,"percent":True}):
            x=prep.fixture(); x["technical"]=data
            self.assertEqual(prep.rehearsal(x,1001)["state"],"HOLD")

    def test_future_stale_source_and_five_empty_headings(self):
        x=prep.fixture(); x["workItems"]=[]; x["active"]=[]
        self.assertEqual(list(prep.rehearsal(x,1001)["areas"]),list(prep.AREA_IDS))
        self.assertEqual(prep.rehearsal(x,999)["state"],"HOLD")
        self.assertEqual(prep.rehearsal(x,1400)["freshness"],"SON_DOGRULANMIS_OKUMA")

    def test_grant_cannot_be_self_declared_by_fixture(self):
        x=prep.fixture(); x["native"]={"verified":True,"countedPass":12,"total":12,"finish":"LOCKED"}
        self.assertEqual(prep.rehearsal(x,1001)["state"],"HOLD")
        x["finishEvidence"]={"donechecks":4,"field":7,"human":"ACCEPTED"}
        r=prep.rehearsal(x,1001)
        self.assertEqual(r["state"],"PASS_MODEL_ONLY")
        self.assertEqual(r["native"]["finish"],"LOCKED")
        self.assertFalse(r["officialPassGranted"])

    def test_active_binding_requires_one_registered_item(self):
        for active in (prep.fixture()["active"]*2,[{"workId":"foreign"}], [{}]):
            x=prep.fixture();x["active"]=active
            self.assertEqual(prep.rehearsal(x,1001)["state"],"HOLD")

    def test_duplicate_keys_nonfinite_and_corrupt_json(self):
        for raw in (b'{', b'{"x":1,"x":2}',b'{"x":Infinity}', b'{"x":NaN}'):
            with self.assertRaises(ValueError):prep.parse(raw)

    def test_scope_score_retains_missing_native_weights(self):
        plan=json.loads((ROOT/"governance/pilive-preparation-v2/PLAN.json").read_text())
        report={"repositories":[{"historical_plive_pins":{p:{"sha256":sha} for p,sha in obs.PINS.items()}}]}
        r=prep.evaluate(prep.canonical(report),plan)
        self.assertEqual(r["scores"],{"THEORY":60,"DESIGN":70,"SIM1":80,"SIM2":100,"SIM3":70})
        self.assertEqual(r["GITHUB_PREPARED"],"HOLD")
        self.assertEqual([len(r["controls"][a]) for a in prep.AXES],[10]*5)
        # Caller-provided status/score strings cannot manufacture absent evidence.
        plan["GITHUB_PREPARED"]="PASS";plan["scores"]={a:100 for a in prep.AXES}
        report["nativeVerified"]=True; report["swiftSourceVerified"]=True
        self.assertEqual(prep.evaluate(prep.canonical(report),plan)["GITHUB_PREPARED"],"HOLD")

    def test_historical_reused_bytes_match_manifest(self):
        prov=json.loads((ROOT/"governance/pilive-preparation-v2/REUSE_PROVENANCE.json").read_text())
        for path,expected in prov["files"].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)

    def test_malformed_plan_and_repository_metadata_return_value_error_or_hold(self):
        plan=json.loads((ROOT/"governance/pilive-preparation-v2/PLAN.json").read_text())
        for bad in ([],None,True,"plan"):
            with self.subTest(plan=bad),self.assertRaises(ValueError):
                prep.evaluate(b'{}',bad)
        for repos in (None,[],{},[None],[{"historical_plive_pins":None}]):
            r=prep.evaluate(prep.canonical({"repositories":repos}),plan)
            self.assertEqual(r["GITHUB_PREPARED"],"HOLD")

    def test_plan_dependency_graph_has_exact_ids_and_no_cycles(self):
        plan=json.loads((ROOT/"governance/pilive-preparation-v2/PLAN.json").read_text())
        graph={x["id"]:set(x["requires"]) for x in plan["blocks"]}
        self.assertEqual(set(graph),{f"G{i:02d}" for i in range(10)})
        self.assertTrue(all(v<=graph.keys() for v in graph.values()))
        while graph:
            ready={k for k,v in graph.items() if not(v & graph.keys())}
            self.assertTrue(ready)
            graph={k:v for k,v in graph.items() if k not in ready}


class SourceCaptureTests(unittest.TestCase):
    def test_real_git_read_only_capture_preserves_dirty_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            subprocess.run(["git","init","-q",str(root)],check=True)
            for name in obs.PINS:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("{}\n")
            subprocess.run(["git","-C",str(root),"add","."],check=True)
            subprocess.run(["git","-C",str(root),"-c","user.name=Fixture","-c","user.email=fixture@example.invalid",
                            "commit","-qm","fixture"],check=True)
            first=next(iter(obs.PINS));(root/first).write_text('{"changed":true}\n')
            before={p:p.read_bytes() for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}
            r=obs.observe(root)
            after={p:p.read_bytes() for p in before}
            self.assertEqual(before,after)
            self.assertTrue(r["stableBracket"])
            self.assertEqual(r["before"],r["after"])
            self.assertEqual(r["state"],"HOLD_SOURCE_REQUALIFICATION")
            self.assertEqual(len(r["sources"]),7)
            self.assertEqual(r["canonicalWrites"],0)
            self.assertEqual(r["nativeProgressVerification"],"NOT_EXECUTED")

    def test_component_symlink_escape_fifo_and_large_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/"ok").write_text("data")
            self.assertEqual(obs.bounded_read(root,"ok"),b"data")
            (root/"link").symlink_to(root/"ok")
            (root/"alias").symlink_to(root,target_is_directory=True)
            os.mkfifo(root/"fifo")
            with (root/"large").open("wb") as f:f.truncate(obs.LIMIT+1)
            for relative in ("../ok","/etc/passwd","link","alias/ok","fifo","large"):
                with self.subTest(path=relative),self.assertRaises((OSError,ValueError)):
                    obs.bounded_read(root,relative)

    def test_non_mac_cli_stops_before_git_or_source_read(self):
        with patch.object(obs.platform,"system",return_value="Linux"),patch.object(obs,"observe") as run,patch("sys.argv",["observer"]):
            self.assertEqual(obs.main(),2)
            run.assert_not_called()


if __name__=="__main__":unittest.main()
