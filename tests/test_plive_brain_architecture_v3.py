"""ENGÜRÜ PLive brain V3: contract + adversarial model tests (no OSi writes)."""
import copy
import json
import unittest

from tools.plive_brain_v3_simulator import (
    STAGES, AREA_IDS, FACETS, REQUIRED_FINISH, contract, coverage,
    ready_items, read_projection, lab_to_factory_handoff,
    privileged_decision, simulated_finish,
)


def snapshot(items=None, *, counted=0, total=12, finish="HOLD",
             valid=True, verified=True, read_at=1000, p01=None):
    return {
        "source": {"valid": valid, "head": "pinned-osi-head", "readAt": read_at},
        "native": {"verified": verified, "countedPass": counted,
                   "total": total, "finish": finish},
        "workItems": items if items is not None else [],
        "p01": p01 if p01 is not None else
               {"bindingValid": True, "nativeVerified": True, "countedPass": 2, "total": 2},
    }


def tasks():
    return [
        {"workId": "M03", "dependsOn": ["M02"], "priority": 1},
        {"workId": "M02", "dependsOn": ["M01"], "priority": 2},
        {"workId": "M01", "dependsOn": [], "priority": 3},
        {"workId": "M04", "dependsOn": [], "priority": 1},
        {"workId": "M05", "dependsOn": [], "priority": 1},
    ]


def handoff():
    return {
        "source_project_id": "lab:proto-1", "source_head": "abc123",
        "evidence_sha256": "e" * 64, "scope": "web-product",
        "qualification_receipt": "sha:test", "sourceFacet": "LABORATUVAR",
        "targetFacet": "ANA_FABRIKA",
    }


def auth():
    req = {"ownerExplicit": True, "projectId": "P02", "workId": "P02.S01.01",
           "action": "P02_ITEM_PASS", "sourceHead": "abc"}
    grant = {"issuerVerified": True, "signatureVerified": True, "nonce": "n01",
             "nonceConsumed": False, "expiresAt": 2000,
             "projectId": "P02", "workId": "P02.S01.01", "action": "P02_ITEM_PASS",
             "sourceHead": "abc"}
    return req, grant, {"accepted": True}


class ContractCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = contract()

    def test_json_schema_and_design_scope(self):
        self.assertEqual(self.doc["schema"], "enguru.plive.brain-architecture/v3")
        self.assertIn("SIMULATION_CANDIDATE", self.doc["kind"])
        self.assertTrue(self.doc["acceptance"]["noAutomaticFieldPromotion"])
        self.assertEqual(self.doc["acceptance"]["fieldScore"], "UNMEASURED__REQUIRES_OSI")

    def test_design_ten_gates_100(self):
        self.assertEqual(coverage(self.doc), 100)
        self.assertEqual(sum(g["points"] for g in self.doc["acceptance"]["designGates"]), 100)

    def test_prior_78_baseline_is_not_erased_or_mixed_with_field(self):
        rows = self.doc["acceptance"]["baseline78Crosswalk"]
        self.assertEqual(len(rows), 10)
        self.assertEqual(sum(x["previousScore"] for x in rows), 78)
        self.assertTrue(all(x["designGoal"] == 10 for x in rows))
        self.assertEqual(self.doc["acceptance"]["fieldScore"], "UNMEASURED__REQUIRES_OSI")
        self.assertEqual(self.doc["acceptance"]["p02Counted"], "0_OF_12_HOLD")

    def test_audit_all_design_gates_are_unique(self):
        gates = self.doc["acceptance"]["designGates"]
        self.assertEqual(len(gates), 10)
        self.assertEqual([g["id"] for g in gates], [f"A{i:02d}" for i in range(1, 11)])

    def test_coverage_declines_when_requirement_disappears(self):
        for gate in self.doc["acceptance"]["designGates"]:
            c = copy.deepcopy(self.doc)
            path = gate["requires"][0].split(".")
            node = c
            for piece in path[:-1]:
                node = node[piece]
            del node[path[-1]]
            with self.subTest(gate=gate["id"]):
                self.assertLess(coverage(c), 100)

    def test_false_show_five_must_not_score_full(self):
        c = copy.deepcopy(self.doc)
        c["screen"]["alwaysShowFive"] = False
        self.assertLess(coverage(c), 100)

    def test_method_is_eight_stage_and_existing(self):
        self.assertEqual(self.doc["method"]["stages"], list(STAGES))
        self.assertTrue(self.doc["method"]["noNewCore"])
        self.assertTrue(self.doc["method"]["noNinthStage"])
        self.assertTrue(self.doc["method"]["noParallelProgress"])

    def test_five_categories_exact_order(self):
        self.assertEqual([x["id"] for x in self.doc["screen"]["categories"]], list(AREA_IDS))
        self.assertEqual([x["label"] for x in self.doc["screen"]["categories"]],
                         ["Motor", "Çekirdek", "Web Yapımı", "Uygulama / App Yapımı", "Agent"])

    def test_five_categories_are_not_factory_and_lab(self):
        self.assertEqual(self.doc["production"]["facet"], list(FACETS))
        self.assertTrue(self.doc["production"]["categoryOrthogonalToFacet"])
        self.assertTrue(self.doc["screen"]["noSixthCategory"])

    def test_separate_read_and_privileged_paths(self):
        p = self.doc["execution"]
        self.assertEqual(p["readOnlyPath"][0], "VERIFY_SOURCE_BINDING")
        self.assertEqual(p["privilegedPath"][0], "EXPLICIT_OWNER_APPROVAL")
        self.assertTrue(self.doc["screen"]["readOnlyWithoutGrant"])
        self.assertTrue(self.doc["userAuthority"]["noImplicitReuseBetweenProjects"])

    def test_p01_p02_p06_boundaries(self):
        a = self.doc["userAuthority"]
        self.assertIn("PRESERVE", a["p01"])
        self.assertIn("0_OF_12", a["p02"])
        self.assertEqual(a["p06"], "SEPARATE_AUTHORITY")
        self.assertEqual(a["canonicalWrites"], "NONE_IN_THIS_GITHUB_CANDIDATE")

    def test_p02_all_final_gates(self):
        self.assertEqual(self.doc["acceptance"]["p02FinishNeeds"], list(REQUIRED_FINISH))
        self.assertEqual(self.doc["acceptance"]["formalStatus"], "HOLD_UNTIL_OSI")

    def test_no_repackaging_as_osi_claim(self):
        self.assertTrue(self.doc["readiness"]["githubModelSimulationOnly"])
        self.assertEqual(self.doc["readiness"]["productionImplementation"], "NOT_CLAIMED")
        self.assertEqual(self.doc["acceptance"]["p02Counted"], "0_OF_12_HOLD")


class DeterministicDependencyTests(unittest.TestCase):
    def test_selected_ready_order_is_stable(self):
        a = ready_items(tasks(), [])
        b = ready_items(list(reversed(tasks())), [])
        self.assertEqual(a, b)
        self.assertEqual(a["ready"], ["M04", "M05", "M01"])

    def test_dependency_progression(self):
        self.assertEqual(ready_items(tasks(), ["M01"])["ready"], ["M04", "M05", "M02"])
        self.assertEqual(ready_items(tasks(), ["M01", "M02"])["ready"], ["M03", "M04", "M05"])

    def test_unknown_dep_blocks(self):
        t = tasks()
        t[0]["dependsOn"] = ["UNREGISTERED"]
        self.assertEqual(ready_items(t, [])["reason"], "UNKNOWN_DEPENDENCY")

    def test_self_cycle_blocks(self):
        t = tasks()
        t[0]["dependsOn"] = ["M03"]
        self.assertEqual(ready_items(t, [])["reason"], "DEPENDENCY_CYCLE")

    def test_multinode_cycle_blocks(self):
        t = tasks()
        t[2]["dependsOn"] = ["M03"]
        self.assertEqual(ready_items(t, [])["reason"], "DEPENDENCY_CYCLE")

    def test_duplicate_id_blocks(self):
        t = tasks() + [copy.deepcopy(tasks()[0])]
        self.assertEqual(ready_items(t, [])["reason"], "DUPLICATE_OR_INVALID_WORK_ID")

    def test_invalid_priority_blocks(self):
        t = tasks()
        t[0]["priority"] = "1"
        self.assertEqual(ready_items(t, [])["reason"], "BAD_PRIORITY_OR_DEPENDENCY")

    def test_unregistered_accepted_blocks(self):
        self.assertEqual(ready_items(tasks(), ["FAKE"])["reason"], "UNREGISTERED_ACCEPTED_ITEM")

    def test_same_input_same_output_and_immutable(self):
        t = tasks()
        old = copy.deepcopy(t)
        self.assertEqual(ready_items(t, []), ready_items(t, []))
        self.assertEqual(t, old)


class ReadOnlyProjectionTests(unittest.TestCase):
    def test_all_five_are_visible_even_when_empty(self):
        r = read_projection(snapshot(), now=1001)
        self.assertEqual(r["state"], "PASS_MODEL_ONLY")
        self.assertEqual(list(r["areas"]), list(AREA_IDS))
        self.assertTrue(all(not r["areas"][x] for x in AREA_IDS))
        self.assertEqual(r["native"]["countedPass"], 0)

    def test_order_and_one_owner_no_double_count(self):
        items = [{"workId": "b", "primaryArea": "web", "facet": "LABORATUVAR",
                  "crossAreas": ["motor", "agent"]},
                 {"workId": "a", "primaryArea": "web", "facet": "ANA_FABRIKA"}]
        r = read_projection(snapshot(items), now=1001)
        self.assertEqual([x["workId"] for x in r["areas"]["web"]], ["a", "b"])
        self.assertEqual(sum(len(x) for x in r["areas"].values()), 2)

    def test_unknown_stays_visible_but_not_sixth_category(self):
        item = [{"workId": "lost", "primaryArea": "unknown"}]
        r = read_projection(snapshot(item), now=1002)
        self.assertEqual(r["unknown"][0]["workId"], "lost")
        self.assertEqual(len(r["areas"]), 5)

    def test_unknown_facet_is_not_invented(self):
        item = [{"workId": "w", "primaryArea": "web"}]
        self.assertEqual(read_projection(snapshot(item), now=1001)["areas"]["web"][0]["facet"],
                         "KAYNAK_BEKLIYOR")

    def test_invalid_facet_is_rejected(self):
        item = [{"workId": "w", "primaryArea": "web", "facet": "THIRD_FACTORY"}]
        self.assertEqual(read_projection(snapshot(item), now=1001)["reason"], "INVALID_FACET")

    def test_duplicate_id_rejects(self):
        item = [{"workId": "w", "primaryArea": "web"},
                {"workId": "w", "primaryArea": "motor"}]
        self.assertEqual(read_projection(snapshot(item), now=1001)["reason"], "DUPLICATE_WORK_ID")

    def test_unverified_source_and_native_rejected(self):
        self.assertEqual(read_projection(snapshot(valid=False), now=1001)["reason"],
                         "UNVERIFIED_SOURCE")
        self.assertEqual(read_projection(snapshot(verified=False), now=1001)["reason"],
                         "NATIVE_PROGRESS_NOT_VERIFIED")

    def test_stale_and_live_explicit_timestamp(self):
        old = read_projection(snapshot(read_at=1000), now=1301)
        new = read_projection(snapshot(read_at=1000), now=1300)
        self.assertEqual(old["freshness"], "SON_DOGRULANMIS_OKUMA")
        self.assertEqual(new["freshness"], "CANLI_DOGRULANMIS_KAYNAK")
        self.assertEqual(old["readAt"], 1000)

    def test_future_timestamp_rejected(self):
        self.assertEqual(read_projection(snapshot(read_at=1500), now=1000)["reason"],
                         "BAD_SOURCE_TIME")

    def test_bad_counters_are_rejected(self):
        for counted, total in ((-1, 12), (13, 12), (1, 0), (1.5, 12), (True, 12)):
            with self.subTest(counted=counted, total=total):
                self.assertEqual(read_projection(snapshot(counted=counted, total=total), 1001)["reason"],
                                 "INVALID_NATIVE_COUNTER")

    def test_done_total_finish_hold_is_not_verified(self):
        r = read_projection(snapshot(counted=12, total=12, finish="HOLD"), 1001)
        self.assertEqual(r["native"]["finish"], "HOLD")
        self.assertNotIn("officialPass", r)

    def test_finish_count_contradiction_rejected(self):
        self.assertEqual(read_projection(snapshot(counted=0, finish="VERIFIED"), 1001)["reason"],
                         "FINISH_COUNT_CONTRADICTION")

    def test_p01_binding_mismatch_requires_reconciliation(self):
        p01 = {"bindingValid": False, "nativeVerified": True, "countedPass": 2, "total": 2}
        self.assertEqual(read_projection(snapshot(p01=p01), 1001)["p01"], "DURUM_DOGRULANIYOR")
        self.assertEqual(read_projection(snapshot(), 1001)["p01"], "DOGRULANDI_KILITLI")

    def test_snapshot_not_modified(self):
        s = snapshot([{"workId": "a", "primaryArea": "web"}])
        old = copy.deepcopy(s)
        self.assertEqual(read_projection(s, 1001), read_projection(s, 1001))
        self.assertEqual(s, old)


class LabFactoryTests(unittest.TestCase):
    def test_explicit_handoff_is_candidate_not_promotion(self):
        r = lab_to_factory_handoff(handoff(), True)
        self.assertEqual(r["state"], "QUALIFIED_HANDOFF_CANDIDATE_ONLY")
        self.assertEqual(r["canonicalWrites"], 0)

    def test_no_owner_approval_blocks(self):
        self.assertEqual(lab_to_factory_handoff(handoff(), False)["state"], "HOLD")

    def test_missing_provenance_blocks(self):
        h = handoff()
        del h["source_head"]
        self.assertEqual(lab_to_factory_handoff(h, True)["reason"], "INCOMPLETE_PROVENANCE")

    def test_reverse_or_unknown_facet_blocks(self):
        h = handoff()
        h["targetFacet"] = "LABORATUVAR"
        self.assertEqual(lab_to_factory_handoff(h, True)["reason"], "INCORRECT_FACET_TRANSITION")

    def test_no_auto_work_duplication(self):
        h = handoff()
        h["newWorkId"] = "copy"
        self.assertEqual(lab_to_factory_handoff(h, True)["reason"], "IMPLICIT_CANONICAL_PROMOTION")


class AuthorityTests(unittest.TestCase):
    def test_scoped_grant_candidate_never_writes(self):
        req, grant, writer = auth()
        out = privileged_decision(req, grant, writer, now=1000)
        self.assertEqual(out["state"], "READY_FOR_AUTHORIZED_OSI_FIELD_REVIEW_ONLY")
        self.assertEqual(out["canonicalWrites"], 0)
        self.assertFalse(out["grantIssued"])

    def test_missing_owner_grant_issuer_signature_writer(self):
        for target, field in (("req", "ownerExplicit"), ("grant", "issuerVerified"),
                              ("grant", "signatureVerified"), ("writer", "accepted")):
            req, grant, writer = auth()
            {"req": req, "grant": grant, "writer": writer}[target][field] = False
            with self.subTest(field=field):
                self.assertEqual(privileged_decision(req, grant, writer, 1000)["state"], "HOLD")

    def test_cross_project_and_item_action_head_rejected(self):
        for name in ("projectId", "workId", "action", "sourceHead"):
            req, grant, writer = auth()
            req[name] += "-OTHER"
            with self.subTest(field=name):
                self.assertEqual(privileged_decision(req, grant, writer, 1000)["reason"],
                                 "SCOPE_MISMATCH")

    def test_expiry_and_replay_rejected(self):
        req, grant, writer = auth()
        self.assertEqual(privileged_decision(req, grant, writer, 2000)["reason"], "EXPIRED_GRANT")
        grant["expiresAt"] = 4000
        grant["nonceConsumed"] = True
        self.assertEqual(privileged_decision(req, grant, writer, 2000)["reason"],
                         "REPLAY_OR_MISSING_NONCE")

    def test_no_signature_is_not_owner_grant(self):
        req, grant, writer = auth()
        grant["signatureVerified"] = False
        self.assertEqual(privileged_decision(req, grant, writer, 1000)["state"], "HOLD")

    def test_no_crypto_or_producer_write_in_pure_model(self):
        import inspect
        import tools.plive_brain_v3_simulator as sim
        src = inspect.getsource(sim)
        for forbidden in ("subprocess.run(", "os.system(", "write_text(", "write_bytes(",
                          "requests.post(", "keychain.add(", "codesign --force"):
            self.assertNotIn(forbidden, src)

    def test_authority_does_not_modify_fixture(self):
        req, grant, writer = auth()
        old = copy.deepcopy((req, grant, writer))
        privileged_decision(req, grant, writer, 1000)
        self.assertEqual((req, grant, writer), old)


class FinishSemanticsTests(unittest.TestCase):
    def test_full_gate_fixture_is_model_only(self):
        r = simulated_finish(12, 4, 7, "ACCEPTED", "VERIFIED")
        self.assertEqual(r["state"], "MODEL_FINISH_CONDITIONS_MET_ONLY")
        self.assertFalse(r["officialPassGranted"])
        self.assertEqual(r["nativeWrites"], 0)

    def test_each_missing_gate_holds(self):
        for args in ((11, 4, 7, "ACCEPTED", "VERIFIED"),
                     (12, 3, 7, "ACCEPTED", "VERIFIED"),
                     (12, 4, 6, "ACCEPTED", "VERIFIED"),
                     (12, 4, 7, "PENDING", "VERIFIED"),
                     (12, 4, 7, "ACCEPTED", "HOLD")):
            with self.subTest(args=args):
                self.assertEqual(simulated_finish(*args)["state"], "HOLD")
                self.assertFalse(simulated_finish(*args)["officialPassGranted"])

    def test_bogus_percent_or_boolean_count_cannot_finish(self):
        self.assertEqual(simulated_finish(True, 4, 7, "ACCEPTED", "VERIFIED")["state"], "HOLD")
        self.assertEqual(simulated_finish(100, 4, 7, "ACCEPTED", "VERIFIED")["state"], "HOLD")


if __name__ == "__main__":
    unittest.main()
