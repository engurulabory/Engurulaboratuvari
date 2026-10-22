import sys,unittest,tempfile
from pathlib import Path
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from enguru_five_minute_controller import cycle,select,verifier,key,REPO
G={"state":"ENABLED_BOUNDED_PR","repository":REPO,"max_tasks_per_cycle":1,"max_additional_spend_usd":0,"paid_providers":False,"human_final_authority":"OWNER"}
def t(**kwargs):
    x={"id":"LABORY_PILOT","state":"READY","target_repo":REPO,"action":"verify_file_digest","path":"source.txt","expected_sha256":sha256(b"PASS").hexdigest(),"dependencies":[]}
    x.update(kwargs);return x
class ControllerTests(unittest.TestCase):
    def test_proof(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            r=cycle(root,{"tasks":[t()]},G)
            self.assertEqual(r["state"],"PASS");self.assertEqual(r["verification"]["state"],"PASS")
            self.assertFalse(r["authorized_merge"]);self.assertEqual(r["additional_spend_usd"],0)
    def test_idle(self):self.assertEqual(cycle(Path("."),{"tasks":[t()]},G,{"LABORY_PILOT"})["state"],"PASS_IDLE")
    def test_paid_provider(self):self.assertEqual(cycle(Path("."),{"tasks":[]},{**G,"paid_providers":True})["reason"],"AUTHORITY_OR_ZERO_COST_GATE")
    def test_cost(self):self.assertEqual(cycle(Path("."),{"tasks":[]},{**G,"max_additional_spend_usd":1})["state"],"HOLD_GUVENLI_DUR")
    def test_private(self):self.assertEqual(cycle(Path("."),{"tasks":[t(target_repo="private")]},G)["reason"],"PRIVATE_REPO_GRANT_REQUIRED")
    def test_shell(self):self.assertEqual(cycle(Path("."),{"tasks":[t(action="shell")]},G)["reason"],"ACTION_GRANT_REQUIRED")
    def test_duplicate(self):self.assertEqual(select({"tasks":[t(),t()]},set())[1],"DUPLICATE_TASK_IDS")
    def test_missing_dependency(self):self.assertEqual(select({"tasks":[t(dependencies=["MISSING"])]},set())[1],"DEPENDENCY_AUTHORITY")
    def test_priority(self):
        nexttask=t(id="LABORY_SECOND",dependencies=["LABORY_PILOT"])
        self.assertEqual(select({"tasks":[nexttask,t()]},set())[0]["id"],"LABORY_PILOT")
        self.assertEqual(select({"tasks":[nexttask,t()]},{"LABORY_PILOT"})[0]["id"],"LABORY_SECOND")
    def test_escape(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(cycle(Path(d),{"tasks":[t(path="../secret")]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"FAIL")
            self.assertEqual(cycle(root,{"tasks":[t()]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            self.assertEqual(verifier(t(),{"state":"PASS","evidence":{"sha256":"0"*64,"size":4}},root)["state"],"HOLD_GUVENLI_DUR")
    def test_unknown_recipe(self):self.assertEqual(cycle(Path("."),{"tasks":[t(action="run_unit_test",path="other.py")]},G)["reason"],"TEST_RECIPE_SCOPE")
    def test_fingerprint(self):self.assertNotEqual(key(t()),key(t(path="change.txt")))

    def test_pass_receipt_rechecks_source_sha(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/"source.txt").write_bytes(b"PASS")
            task=t()
            old=key(task,root,"a"*40)
            (root/"source.txt").write_bytes(b"DRIFT")
            self.assertNotEqual(old,key(task,root,"a"*40))
            self.assertNotEqual(old,key(task,root,"b"*40))
    def test_retry_budget_governed(self):
        task=t()
        r=cycle(Path("."),{"tasks":[task]},G,failed={task["id"]:2})
        self.assertEqual(r["reason"],"RETRY_BUDGET_REQUIRES_MANAGEMENT_REVIEW")
        self.assertEqual(r["state"],"AWAITING_MANAGEMENT")
    def test_current_source_verified_finish_separate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"source.txt").write_bytes(b"PASS")
            r=cycle(root,{"tasks":[t()]},G,commit="a"*40)
            self.assertEqual(r["official_verified_finish"],"HOLD_DONECHECK_HUMAN_GATE")

    def test_repair_candidate_second_verification_and_owner_gate(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sub=root/"governance/controller/work";sub.mkdir(parents=True)
            (sub/"fix.txt").write_bytes(b"old\n")
            item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
                   expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
                   replace_from="old",replace_to="new")
            result=cycle(root,{"tasks":[item]},G,commit="a"*40)
            self.assertEqual(result["state"],"PR_PENDING")
            self.assertEqual(result["verification"]["proof"],"REPAIR_INDEPENDENT_RECOMPUTE")
            self.assertFalse(result["authorized_merge"])
            self.assertEqual((sub/"fix.txt").read_bytes(),b"old\n")
            (sub/"fix.txt").write_bytes(b"new\n")
            self.assertEqual(cycle(root,{"tasks":[item]},G,commit="a"*40)["state"],"PASS")
    def test_repair_wrong_digest_holds(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);sub=root/"governance/controller/work";sub.mkdir(parents=True)
            (sub/"fix.txt").write_bytes(b"old\n")
            item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
                   expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256="0"*64,
                   replace_from="old",replace_to="new")
            self.assertEqual(cycle(root,{"tasks":[item]},G)["state"],"HOLD_GUVENLI_DUR")
    def test_repair_scope_is_explicit(self):
        self.assertEqual(cycle(Path("."),{"tasks":[t(action="propose_exact_repair")]},G)["reason"],"REPAIR_PATH_GRANT")
    def test_pending_blocks_repeat_without_unlocking_dependencies(self):
        item=t()
        root=Path(".")
        self.assertEqual(select({"tasks":[item]},set(),{item["id"]})[1],"NO_ELIGIBLE_TASK")
        child=t(id="LABORY_SECOND",dependencies=[item["id"]])
        self.assertEqual(select({"tasks":[item,child]},set(),{item["id"]})[1],"NO_ELIGIBLE_TASK")
    def test_repair_contract_alters_fingerprint(self):
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256="1"*64,desired_sha256="2"*64,replace_from="old",replace_to="new")
        self.assertNotEqual(key(item),key({**item,"replace_to":"different"}))

    def test_pending_human_gate_freezes_next_task(self):
        task=t()
        result=cycle(Path("."),{"tasks":[task]},G,pending={task["id"]})
        self.assertEqual(result["state"],"AWAITING_HUMAN")
        self.assertEqual(result["human_final_authority"],"OWNER_RESERVED")

    def test_repair_pr_remote_provenance_and_draft_boundary(self):
        from unittest.mock import patch
        import base64
        from enguru_five_minute_controller import prepare_repair_pr
        calls=[]
        def fake_github(url,token,body=None,method=None):
            calls.append((url,body,method))
            if "?ref=" in url:
                return {"content":base64.b64encode(b"old\n").decode(),"sha":"blob-old"}
            if url.endswith("/pulls"):
                self.assertTrue(body["draft"])
                self.assertEqual(body["base"],"main")
                return {"html_url":"https://github.com/engurulabory/Engurulaboratuvari/pull/999"}
            return {"ok":True}
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
               replace_from="old",replace_to="new")
        result={"fingerprint":"a"*64,"engineering":{"evidence":{"candidate_base64":base64.b64encode(b"new\n").decode()}}}
        with patch("enguru_five_minute_controller.github",fake_github):
            url=prepare_repair_pr("token",item,result,"b"*40)
        self.assertTrue(url.endswith("999"))
        self.assertTrue(any(method=="PUT" and body["branch"].startswith("enguru/controller-") for _,body,method in calls))
        self.assertFalse(any(url.endswith("/git/refs/heads/main") for url,_,_ in calls))
    def test_repair_pr_remote_drift_rejected(self):
        from unittest.mock import patch
        import base64
        from enguru_five_minute_controller import prepare_repair_pr
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
               replace_from="old",replace_to="new")
        result={"fingerprint":"a"*64,"engineering":{"evidence":{"candidate_base64":base64.b64encode(b"new\n").decode()}}}
        with patch("enguru_five_minute_controller.github",return_value={"content":base64.b64encode(b"drift\n").decode(),"sha":"blob-remote"}):
            with self.assertRaisesRegex(ValueError,"REPAIR_REMOTE_SOURCE_DRIFT"):
                prepare_repair_pr("token",item,result,"b"*40)

    def test_receipt_requires_actual_successful_schedule_run(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import receipts,MARKER
        root=Path("."); task=t()
        commit="a"*40
        entry=MARKER+"PASS:"+task["id"]+":"+key(task,root,commit)+":123:"+commit
        comment={"user":{"login":"github-actions[bot]"},"body":"<!-- "+entry+" -->"}
        def fake(url,token,body=None,method=None):
            if "/comments?" in url:return [comment]
            return {"head_sha":commit,"status":"completed","event":"schedule","conclusion":"success"}
        with patch("enguru_five_minute_controller.github",side_effect=fake):
            done,pending,failed=receipts("token",root,[task],commit)
        self.assertEqual(done,{task["id"]})
        self.assertEqual(pending,set())
        def failed_run(url,token,body=None,method=None):
            if "/comments?" in url:return [comment]
            return {"head_sha":commit,"status":"completed","event":"schedule","conclusion":"failure"}
        with patch("enguru_five_minute_controller.github",side_effect=failed_run):
            done,_,_=receipts("token",root,[task],commit)
        self.assertEqual(done,set())
    def test_receipt_from_wrong_actor_and_old_sha_is_rejected(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import receipts,MARKER
        root=Path("."); task=t();commit="a"*40
        entry=MARKER+"PASS:"+task["id"]+":"+key(task,root,commit)+":123:"+commit
        comments=[{"user":{"login":"other-bot"},"body":"<!-- "+entry+" -->"}]
        with patch("enguru_five_minute_controller.github",return_value=comments):
            done,_,_=receipts("token",root,[task],commit)
        self.assertEqual(done,set())
    def test_malformed_policy_rejects_retry_and_priority(self):
        self.assertEqual(cycle(Path("."),{"tasks":[t(max_attempts=10)]},G)["reason"],"RETRY_POLICY")
        self.assertEqual(cycle(Path("."),{"tasks":[t(priority="high")]},G)["reason"],"PRIORITY_POLICY")

    def test_existing_owner_pr_recovery_checks_exact_source_and_repo(self):
        from unittest.mock import patch
        import base64
        from enguru_five_minute_controller import prepare_repair_pr,REPO
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
               replace_from="old",replace_to="new",existing_pr_number=196)
        result={"fingerprint":"a"*64,"engineering":{"evidence":{"candidate_base64":base64.b64encode(b"new\n").decode()}}}
        def fake(url,token,body=None,method=None):
            if "/pulls/196/files?" in url:
                return [{"filename":"governance/controller/work/fix.txt","status":"modified"}]
            if "/pulls/196" in url:
                return {"state":"open","base":{"ref":"main"},"head":{"ref":"enguru/controller-labory-repair","repo":{"full_name":REPO}},"html_url":"https://github.com/engurulabory/Engurulaboratuvari/pull/196"}
            if "?ref=" in url:return {"content":base64.b64encode(b"new\n").decode()}
            raise AssertionError("UNEXPECTED_REMOTE_MUTATION")
        with patch("enguru_five_minute_controller.github",side_effect=fake):
            self.assertTrue(prepare_repair_pr("token",item,result,"b"*40).endswith("/196"))
    def test_existing_pr_wrong_scope_holds(self):
        from unittest.mock import patch
        import base64
        from enguru_five_minute_controller import prepare_repair_pr
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
               replace_from="old",replace_to="new",existing_pr_number=196)
        result={"fingerprint":"a"*64,"engineering":{"evidence":{"candidate_base64":base64.b64encode(b"new\n").decode()}}}
        with patch("enguru_five_minute_controller.github",return_value={"state":"open","base":{"ref":"other"},"head":{"repo":{"full_name":"other/repo"}}}):
            with self.assertRaisesRegex(ValueError,"PR_REFERENCE_AUTHORITY"):
                prepare_repair_pr("token",item,result,"b"*40)

    def test_owner_pr_additional_file_is_denied(self):
        from unittest.mock import patch
        import base64
        from enguru_five_minute_controller import prepare_repair_pr,REPO
        item=t(id="LABORY_REPAIR",action="propose_exact_repair",path="governance/controller/work/fix.txt",
               expected_sha256=sha256(b"old\n").hexdigest(),desired_sha256=sha256(b"new\n").hexdigest(),
               replace_from="old",replace_to="new",existing_pr_number=196)
        result={"fingerprint":"a"*64,"engineering":{"evidence":{"candidate_base64":base64.b64encode(b"new\n").decode()}}}
        def mock_api(url,token,body=None,method=None):
            if "/pulls/196/files?" in url:
                return [{"filename":item["path"],"status":"modified"},{"filename":"governance/private/secret.txt","status":"modified"}]
            if "/pulls/196" in url:
                return {"state":"open","base":{"ref":"main"},"head":{"ref":"enguru/controller-test","repo":{"full_name":REPO}}}
            raise AssertionError("UNEXPECTED_REMOTE_MUTATION")
        with patch("enguru_five_minute_controller.github",side_effect=mock_api):
            with self.assertRaisesRegex(ValueError,"PR_REFERENCE_DIFF_SCOPE"):
                prepare_repair_pr("token",item,result,"b"*40)

    def test_separate_token_privileges_for_pr_and_worker(self):
        source=Path(__file__).resolve().parents[1]/".github"/"workflows"/"enguru-five-minute-controller.yml"
        policy=source.read_text(encoding="utf8")
        self.assertIn("  verify:\n",policy)
        self.assertIn("  worker:\n",policy)
        self.assertIn("    if: github.event_name != 'schedule'\n",policy)
        verify=policy.split("  verify:\n",1)[1].split("  worker:\n",1)[0]
        worker=policy.split("  worker:\n",1)[1]
        self.assertIn("      contents: read\n",verify)
        self.assertNotIn("issues: write",verify)
        self.assertNotIn("pull-requests: write",verify)
        self.assertIn("      issues: write\n",worker)
        self.assertIn("      pull-requests: write\n",worker)
        self.assertIn("github.event_name != 'pull_request'",worker)

    def test_dependency_cycles_are_governed_holds(self):
        first=t(id="LABORY_FIRST",dependencies=["LABORY_SECOND"])
        second=t(id="LABORY_SECOND",dependencies=["LABORY_FIRST"])
        self.assertEqual(select({"tasks":[first,second]},set())[1],"DEPENDENCY_CYCLE")
        self.assertEqual(cycle(Path("."),{"tasks":[t(dependencies=["LABORY_PILOT"])]},G)["reason"],"DEPENDENCY_CYCLE")

    def test_dependency_schema_requires_string_ids(self):
        task=t(dependencies=[["LABORY_PILOT"]])
        self.assertEqual(select({"tasks":[task]},set())[1],"DEPENDENCY_AUTHORITY")

    def test_successful_push_receipt_is_reusable_on_same_commit(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import receipts,MARKER
        task=t()
        commit="a"*40
        root=Path(".")
        entry=MARKER+"PASS:"+task["id"]+":"+key(task,root,commit)+":123:"+commit
        comment={"user":{"login":"github-actions[bot]"},"body":"<!-- "+entry+" -->"}
        def fake(url,token,body=None,method=None):
            if "/comments?" in url:return [comment]
            return {"head_sha":commit,"status":"completed","event":"push","conclusion":"success"}
        with patch("enguru_five_minute_controller.github",side_effect=fake):
            done,_,_=receipts("token",root,[task],commit)
        self.assertEqual(done,{task["id"]})

    def test_pr_ci_receipt_cannot_count_as_worker_completion(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import receipts,MARKER
        task=t()
        commit="a"*40
        root=Path(".")
        entry=MARKER+"PASS:"+task["id"]+":"+key(task,root,commit)+":123:"+commit
        comment={"user":{"login":"github-actions[bot]"},"body":"<!-- "+entry+" -->"}
        def fake(url,token,body=None,method=None):
            if "/comments?" in url:return [comment]
            return {"head_sha":commit,"status":"completed","event":"pull_request","conclusion":"success"}
        with patch("enguru_five_minute_controller.github",side_effect=fake):
            done,_,_=receipts("token",root,[task],commit)
        self.assertEqual(done,set())

    def test_schedule_cadence_reports_true_gap_and_recovery(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import observe_schedule
        current={"id":333,"event":"schedule","created_at":"2026-10-22T06:05:00Z"}
        older={"id":222,"event":"schedule","created_at":"2026-10-22T05:45:00Z"}
        with patch("enguru_five_minute_controller.github",return_value={"workflow_runs":[current,older]}):
            gap=observe_schedule("token",333)
        self.assertEqual(gap["state"],"HOLD")
        self.assertEqual(gap["reason"],"SCHEDULE_CADENCE_GAP")
        self.assertEqual(gap["missed_slots_lower_bound"],3)
        older["created_at"]="2026-10-22T06:00:00Z"
        with patch("enguru_five_minute_controller.github",return_value={"workflow_runs":[current,older]}):
            good=observe_schedule("token",333)
        self.assertEqual(good["state"],"PASS")
        self.assertEqual(good["gap_seconds"],300)

    def test_schedule_cadence_missing_observation_holds(self):
        from unittest.mock import patch
        from enguru_five_minute_controller import observe_schedule
        with patch("enguru_five_minute_controller.github",return_value={"workflow_runs":[]}):
            self.assertEqual(observe_schedule("token",333)["reason"],"CURRENT_SCHEDULE_NOT_OBSERVED")

    def test_receipt_covers_pr_handoff_and_schedule_observation(self):
        from enguru_five_minute_controller import finalize_receipt
        result={"state":"PR_PENDING","pull_request":"https://github.com/x/y/pull/1"}
        first=finalize_receipt(result)["receipt_sha256"]
        result["schedule_observation"]={"state":"HOLD","gap_seconds":600}
        self.assertNotEqual(first,finalize_receipt(result)["receipt_sha256"])
        result["pull_request"]="https://github.com/x/y/pull/2"
        self.assertNotEqual(first,finalize_receipt(result)["receipt_sha256"])

    def test_workflow_uses_explicit_actions_read_and_supported_checkout(self):
        workflow=(Path(__file__).resolve().parents[1]/".github/workflows/enguru-five-minute-controller.yml").read_text(encoding="utf8")
        self.assertIn("      actions: read\n",workflow)
        self.assertIn("actions/checkout@v5",workflow)
if __name__=="__main__":unittest.main()
