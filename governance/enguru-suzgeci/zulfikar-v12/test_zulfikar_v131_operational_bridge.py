"""Zulfikar v1.3.1 mission handoff guard: real registry and negative proof."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SCRIPT=HERE/'zulfikar_v131_operational_bridge.py'
spec=importlib.util.spec_from_file_location('bridge',SCRIPT)
bridge=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


def mission(cap="TEST_REGRESSION", action="PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF"):
    return {
      "schema":bridge.SCHEMA, "missionId":"ZV131.TRIAL.001",
      "projectId":"ENGURU_PILIVE_P02_USER_SCREEN", "workId":"P02.S01.01",
      "capabilityId":cap, "actionId":action, "writerId":"single-owner",
      "ownerId":"engurulabory", "issuer":"EXISTING_CANONICAL_ONLY",
      "sourceHead":bridge.head_sha(bridge.ROOT),
      "dependencies":[], "singleWriter":True, "writerCount":1,
      "networkRequested":False, "remotePushRequested":False, "dryRunOnly":True,
      "humanThreshold":"HOLD", "officialFinish":"HOLD", "checkpointState":"NEW"
    }


class OperationalBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actions, cls.action_sha=bridge.source_read(bridge.ROOT,bridge.ACTION_PATH)
        cls.bindings, cls.bind_sha=bridge.source_read(bridge.ROOT,bridge.BINDING_PATH)
        cls.head=bridge.head_sha(bridge.ROOT)
    def audit(self,m):
        return bridge.assess(m,self.bindings,self.actions,self.head,{
            bridge.BINDING_PATH:self.bind_sha,bridge.ACTION_PATH:self.action_sha})
    def hold(self, mut, marker):
        x=mission();mut(x);out=self.audit(x)
        self.assertEqual(out["decision"],"HOLD")
        self.assertIn(marker,out["holds"])
        self.assertIs(out["realTaskExecuted"],False)
        self.assertEqual(out["officialVerifiedFinish"],"HOLD")

    def test_three_real_registered_capabilities_are_readable(self):
        pairs=[
          ("TEST_REGRESSION","PACKAGE08_CAP08_TEST_REGRESSION_FIELD_PROOF"),
          ("BUILD","PACKAGE08_CAP07_BUILD_FIELD_PROOF"),
          ("OPERATOR_CONTINUE_DISPATCH","MAC_NATIVE_RESTART_RECOVERY_CONTINUITY_PROOF")
        ]
        for cap,action in pairs:
            with self.subTest(capability=cap):
                x=mission(cap,action);out=self.audit(x)
                self.assertEqual(out["decision"],"PREFLIGHT_READY_EXISTING_OPERATOR_ONLY")
                self.assertFalse(out["realTaskExecuted"])
                self.assertFalse(out["newCoreCreated"])
                self.assertEqual(out["officialVerifiedFinish"],"HOLD")
    def test_registry_bytes_match_checkout_head(self):
        self.assertEqual(len(self.bind_sha),64)
        self.assertEqual(len(self.action_sha),64)
    def test_one_writer_proven_by_contract_only(self):
        out=self.audit(mission())
        self.assertEqual(out["sourceHead"],self.head)
        self.assertEqual(out["sourceWrites"],0)
    def test_bad_goal_schema(self):
        self.hold(lambda x:x.update(schema="bad"),"HOLD_SCHEMA")
    def test_owner_forgery(self):
        self.hold(lambda x:x.update(ownerId="someone-else"),"HOLD_OWNER_ISSUER")
    def test_issuer_forgery(self):
        self.hold(lambda x:x.update(issuer="NEW_ISSUER"),"HOLD_OWNER_ISSUER")
    def test_head_drift(self):
        self.hold(lambda x:x.update(sourceHead="0"*40),"HOLD_EXACT_HEAD")
    def test_duplicate_writer(self):
        self.hold(lambda x:x.update(writerCount=2),"HOLD_SINGLE_WRITER")
    def test_bool_writer_count_attack(self):
        self.hold(lambda x:x.update(writerCount=True),"HOLD_SINGLE_WRITER")
    def test_remote_push_deny(self):
        self.hold(lambda x:x.update(remotePushRequested=True),"HOLD_REMOTE_PUSH")
    def test_live_mutation_deny(self):
        self.hold(lambda x:x.update(dryRunOnly=False),"HOLD_REQUIRES_DRY_RUN")
    def test_premature_finish_deny(self):
        self.hold(lambda x:x.update(officialFinish="PASS"),"HOLD_PREMATURE_AUTHORITY")
    def test_checkpoint_resume_not_faked(self):
        self.hold(lambda x:x.update(checkpointState="RESUME_PROPOSED"),"HOLD_RESUME_PROOF_REQUIRED")
    def test_missing_dependency_proof(self):
        self.hold(lambda x:x.update(dependencies=[{"workId":"OTHER","state":"PASS"}]),"HOLD_DEPENDENCY_EVIDENCE")
    def test_dependency_collision(self):
        def bad(x):
            a={"workId":"C1","state":"PASS_EVIDENCED","receiptSha256":"1"*64}
            x["dependencies"]=[a,copy.deepcopy(a)]
        self.hold(bad,"HOLD_DEPENDENCY_COLLISION")
    def test_self_dependency(self):
        self.hold(lambda x:x.update(dependencies=[{"workId":"P02.S01.01","state":"PASS_EVIDENCED","receiptSha256":"1"*64}]),"HOLD_DEPENDENCY_COLLISION")
    def test_missing_action(self):
        self.hold(lambda x:x.update(actionId="UNKNOWN_ACTION"),"HOLD_UNBOUND_OR_MISMATCHED_ACTION")
    def test_wrong_action(self):
        self.hold(lambda x:x.update(actionId="PACKAGE08_CAP07_BUILD_FIELD_PROOF"),"HOLD_UNBOUND_OR_MISMATCHED_ACTION")
    def test_unregistered_capability(self):
        self.hold(lambda x:x.update(capabilityId="UNKNOWN_CAPABILITY"),"HOLD_CAPABILITY_IDENTITY")
    def test_new_network_authority_deny(self):
        self.hold(lambda x:x.update(networkRequested=True),"HOLD_NETWORK_SCOPE")
    def test_bounded_human_threshold_action_deny(self):
        x=mission("RELEASE_LIFECYCLE","PACKAGE08_CAP13_RELEASE_LIFECYCLE_FIELD_PROOF")
        self.assertIn("HOLD_ACTION_REQUIRES_HUMAN_THRESHOLD",self.audit(x)["holds"])
    def test_malformed_registry_action_and_unhashable_attack(self):
        x=mission();x["actionId"]=[]
        out=self.audit(x)
        self.assertEqual(out["decision"],"HOLD")
    def test_same_input_same_decision(self):
        a=self.audit(mission());b=self.audit(mission())
        self.assertEqual(a,b)
        self.assertRegex(a["missionHash"],r"^[0-9a-f]{64}$")
    def test_no_new_execution_authority_for_any_output(self):
        for x in (mission(),mission("BUILD","PACKAGE08_CAP07_BUILD_FIELD_PROOF")):
            o=self.audit(x)
            self.assertFalse(o["newIssuerCreated"])
            self.assertFalse(o["newActionCreated"])
            self.assertEqual(o["osiRuntime"],"HOLD_NOT_OBSERVED")
    def test_real_cli_on_current_checkout_with_temp_input(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"mission.json"
            path.write_text(json.dumps(mission()),encoding="utf-8")
            run=subprocess.run([sys.executable,"-B",str(SCRIPT),"preflight","--input",str(path)],
                               capture_output=True,text=True,timeout=20)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(json.loads(run.stdout)["decision"],"PREFLIGHT_READY_EXISTING_OPERATOR_ONLY")
    def test_cli_deny_bad_json(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"mission.json";path.write_text("{bad")
            run=subprocess.run([sys.executable,"-B",str(SCRIPT),"preflight","--input",str(path)],
                               capture_output=True,text=True,timeout=20)
            self.assertEqual(run.returncode,2)
            self.assertEqual(json.loads(run.stdout)["decision"],"HOLD")
    def test_tampered_registry_read_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);rel="registries/b.json"
            (root/"registries").mkdir()
            (root/rel).write_text('{"actions":{}}')
            with self.assertRaises(ValueError):
                bridge.source_read(root,rel)

    def test_no_symlink_parent_directory_in_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"real").mkdir()
            (root/"real"/"data.json").write_text('{"ok":true}',encoding="utf-8")
            (root/"alias").symlink_to(root/"real",target_is_directory=True)
            with self.assertRaises((OSError,ValueError)):
                bridge.read_no_symlink(root,"alias/data.json",1000)

    def test_no_symlink_leaf_in_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"source").write_text("private",encoding="utf-8")
            (root/"alias").symlink_to(root/"source")
            with self.assertRaises((OSError,ValueError)):
                bridge.read_no_symlink(root,"alias",1000)

    def test_path_escape_is_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for relative in ("../secret","sub/../../secret","/etc/passwd"):
                with self.subTest(relative=relative), self.assertRaises((OSError,ValueError)):
                    bridge.read_no_symlink(root,relative,1000)

    def test_no_fifo_as_registry_source(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            os.mkfifo(root/"pipe")
            with self.assertRaises((OSError,ValueError)):
                bridge.read_no_symlink(root,"pipe",1000)

    def test_bounded_source_size(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"oversize").write_bytes(b"0"*1025)
            with self.assertRaises((OSError,ValueError)):
                bridge.read_no_symlink(root,"oversize",1024)

    def test_no_direct_operator_or_owner_authentication_in_preflight(self):
        result=self.audit(mission())
        self.assertIs(result["ownerIdentityAuthenticated"],False)
        self.assertIs(result["singleWriterLockObserved"],False)
        self.assertIs(result["actualHandlerInvoked"],False)
        self.assertEqual(result["realWorkIdExistsInCanonicalSource"],"NOT_CHECKED")
        self.assertIs(result["manifestClaimsAreNotAuthorization"],True)

    def test_one_bounded_regular_file(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            payload=b'{"known":"bytes"}'
            (root/"valid").write_bytes(payload)
            self.assertEqual(bridge.read_no_symlink(root,"valid",1024),payload)

    def test_fake_source_revision_never_ready(self):
        self.hold(lambda x:x.update(sourceHead="f"*40),"HOLD_EXACT_HEAD")


if __name__=="__main__":
    unittest.main(verbosity=2)
