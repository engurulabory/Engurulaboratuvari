"""HYM2 / Zülfikar V1.2 integration: adversarial original-authority guard."""
import copy
import json
import shutil
import tempfile
import types
import unittest
from pathlib import Path

from tools.arge_hym2_zulfikar_v12_bridge import (
    ROOT, MATRIX, CASES, PROVENANCE, BLOCKS, TASKS, SOURCE_PINS,
    check_advisory, crosswalk, read_zulfikar, review, validate_hym_data
)


class ZulfikarHYM2GuardTests(unittest.TestCase):
    def test_40_original_ids_six_blocks_preserved(self):
        cw=crosswalk()
        self.assertEqual(len(BLOCKS),6)
        self.assertEqual([len(x) for x in BLOCKS],[9,9,7,7,4,4])
        self.assertEqual(len(TASKS),len(cw))
        self.assertEqual(len(set(TASKS)),40)
        self.assertEqual(set(cw),set(TASKS))
        self.assertEqual(set(cw["A04"]["zulfikar_advisory_packages"]),{"K02","K03"})
        self.assertTrue(all(x["real_task_acceptance"]=="HOLD"
                            and x["original_contract_authority"]=="UNCHANGED"
                            for x in cw.values()))

    def test_current_h1_original_18_cases_234_cells_verified_in_source(self):
        b=validate_hym_data(ROOT)
        self.assertEqual(len(b),3)
        m=json.loads(b[MATRIX])
        c=json.loads(b[CASES])
        self.assertEqual(m["official_pass"],"0/9")
        self.assertEqual(len(m["tasks"]),9)
        self.assertEqual(c["baseline"]["rows"],234)
        self.assertEqual(len(c["cases"]),18)

    def make_base(self):
        ctx=tempfile.TemporaryDirectory()
        out=Path(ctx.name)
        for p in (
            MATRIX,CASES,PROVENANCE,
            "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md",
            "governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json",
        ):
            dst=out/p;dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes((ROOT/p).read_bytes())
        return ctx,out

    def test_false_official_A04_or_missing_owner_scope_fails_closed(self):
        for kind in ("fake_a04_acceptance","fake_factory_auth","fake_E5","fake_40"):
            with self.subTest(kind=kind):
                ctx,out=self.make_base()
                try:
                    mpath=out/MATRIX; cpath=out/CASES; ppath=out/PROVENANCE
                    if kind=="fake_a04_acceptance":
                        d=json.loads(mpath.read_text())
                        d["tasks"]["A04"]["official"]="PASS"
                        mpath.write_text(json.dumps(d))
                    elif kind=="fake_factory_auth":
                        d=json.loads(ppath.read_text())
                        d["a04_canonical_scope_boundary"]["status"]="PASS_CANONICAL"
                        ppath.write_text(json.dumps(d))
                    elif kind=="fake_E5":
                        d=json.loads(cpath.read_text())
                        d["baseline"]["all_18_e5_original_status"]="PASS"
                        cpath.write_text(json.dumps(d))
                    else:
                        d=json.loads(ppath.read_text())
                        d["acceptance"]="PASS_40_OF_40"
                        ppath.write_text(json.dumps(d))
                    with self.assertRaises(ValueError):
                        validate_hym_data(out)
                finally:
                    ctx.cleanup()

    def test_missing_v3_source_integrity_fails_closed(self):
        ctx,out=self.make_base()
        try:
            p=out/"governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md"
            p.write_bytes(p.read_bytes()+b"tamper")
            with self.assertRaises(ValueError):
                validate_hym_data(out)
        finally:
            ctx.cleanup()

    def test_mismatched_zulfikar_bytes_refused_without_execution(self):
        self.assertEqual(len(SOURCE_PINS),2)
        def fake_fetch(path):
            return b"malicious bytes"
        with self.assertRaisesRegex(ValueError,"ZULFIKAR_SOURCE_BLOB_MISMATCH"):
            read_zulfikar(fetch=fake_fetch)

    def test_whole_review_with_forged_source_is_hold_and_never_official(self):
        res=review(fetch=lambda path:b"forged bytes")
        self.assertEqual(res["state"],"HOLD")
        self.assertEqual(res["official_total"],"0/40")
        self.assertEqual(res["verified_finish"],"HOLD")
        self.assertEqual(res["mac_osi_handoff"],"HOLD")

    def test_zulfikar_lineage_synthetic_early_pass_not_promoted(self):
        # A mocked upstream oracle trying to skip required incomplete hops
        # must be rejected before official or field acceptance.
        fake=types.SimpleNamespace(
            CHAIN=("INTENT","GOAL","CONTRACT","PLAN","SOURCE","EXECUTION",
                   "TEST","USER_OUTCOME","AUTHORITY"),
            check_event=lambda x:[],
            check_lineage=lambda x:[],
            check_fin=lambda x:[])
        with self.assertRaisesRegex(ValueError,"ZULFIKAR_REAL_CHAIN_MISSING_EVIDENCE"):
            check_advisory(fake,validate_hym_data(ROOT),crosswalk())

    def test_private_factory_payload_absent_from_public_crosswalk(self):
        data=json.dumps(crosswalk(),sort_keys=True)
        for forbidden in ("FACTORY_SECRET","PRIVATE_GITHUB_TOKEN",
                          "CLIENT_KEY","signed_owner_grant_payload"):
            self.assertNotIn(forbidden,data)
        self.assertFalse(any("PASS"==v["real_task_acceptance"]
                             for v in crosswalk().values()))


if __name__=="__main__":
    unittest.main()
