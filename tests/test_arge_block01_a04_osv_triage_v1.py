"""HYM2 A04: adversarial full OSV metadata triage without network."""
import copy
import hashlib
import json
import unittest
from tools.arge_block01_a04_osv_triage_v1 import audit, _source_roster, _normalize_record

ALPHA="GHSA-dem0-one-0001"
BETA="GHSA-dem0-two-0002"


def scenario():
    items=[
        {"upstream":"Medusa","name":"axios","version":"1.13.2",
         "purl":"pkg:npm/axios@1.13.2","ecosystem":"npm",
         "precision":"LOCKFILE_EXACT_CANDIDATE",
         "advisories":[{"id":ALPHA},{"id":BETA}]},
        {"upstream":"Saleor","name":"django","version":"5.2.0",
         "purl":"pkg:pypi/django@5.2.0","ecosystem":"PyPI",
         "precision":"LOCKFILE_EXACT_CANDIDATE",
         "advisories":[{"id":ALPHA}]},
        {"upstream":"OpenFGA","name":"github.com/google/uuid","version":"v1.6.0",
         "purl":"pkg:golang/github.com/google/uuid@v1.6.0","ecosystem":"Go",
         "precision":"DIRECT_GO_MOD_DECLARATION_NOT_BUILD_GRAPH",
         "advisories":[]},
    ]
    source={"schema":"enguru.hym2.a04.osv-source-advisory-snapshot/v1",
            "observations":items,
            "source_candidate_sha256":"a"*64}
    raw=json.dumps(source,sort_keys=True,separators=(",",":")).encode()
    receipt={"state":"PASS_OSV_SOURCE_SNAPSHOT_ONLY",
             "source_candidate_sha256":source["source_candidate_sha256"],
             "query_coverage":3,"advisory_matches":3,"affected_package_candidates":2}
    metadata={
        ALPHA:{"id":ALPHA,"database_specific":{"severity":"HIGH"},"severity":[],
               "affected":[
                   {"package":{"name":"axios","ecosystem":"npm"},
                    "ranges":[{"type":"SEMVER","events":[{"introduced":"0"},{"fixed":"1.14.0"}]}]},
                   {"package":{"name":"django","ecosystem":"PyPI"},"ranges":[]}
               ]},
        BETA:{"id":BETA,"severity":[{"type":"CVSS_V3",
                "score":"CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}],
               "affected":[{"package":{"name":"axios","ecosystem":"npm"}}]}
    }
    return source,receipt,raw,metadata


class OSVTriageTests(unittest.TestCase):
    def test_source_bound_priority_with_unrated_cvss_metadata(self):
        source,receipt,raw,meta=scenario()
        calls=[]
        def lookup(identifier):
            calls.append(identifier)
            return meta[identifier]
        output,report=audit(source,receipt,raw,lookup=lookup,workers=2)
        self.assertEqual(output["state"],"PASS_PUBLIC_OSV_METADATA_TRIAGE_ONLY")
        self.assertEqual(output["advisory_ids_total"],2)
        self.assertEqual(output["metadata_records_observed"],2)
        self.assertEqual(output["source_advisory_total"],3)
        self.assertEqual(output["affected_package_total"],2)
        self.assertEqual(output["explicit_severity_distribution"],{"HIGH":2,"UNKNOWN":1})
        self.assertEqual(len(calls),2)
        self.assertEqual(len(report["priority_queue"]),2)
        self.assertEqual(report["priority_queue"][0]["triage_lane"],"REVIEW_HIGH")
        self.assertEqual(report["priority_queue"][0]["recorded_fix_events"][0]["fixed_event"],"1.14.0")
        self.assertEqual(report["priority_queue"][0]["deployment_applicability"],"UNKNOWN_CUSTOMER_RUNTIME")
        self.assertEqual(output["security_clearance"],"HOLD")
        self.assertEqual(output["a04_official"],"HOLD")

    def test_source_count_tamper_prevents_any_metadata_request(self):
        s,r,raw,meta=scenario()
        r["advisory_matches"]=4
        hit=[]
        verdict,_=audit(s,r,raw,lookup=lambda x:hit.append(x))
        self.assertEqual(verdict["state"],"HOLD")
        self.assertFalse(hit)

    def test_source_digest_drift_prevents_any_metadata_request(self):
        s,r,raw,meta=scenario()
        r["source_candidate_sha256"]="b"*64
        verdict,_=audit(s,r,raw,lookup=lambda x:meta[x])
        self.assertEqual(verdict["state"],"HOLD")

    def test_duplicate_advisory_id_per_component_is_rejected(self):
        s,r,raw,meta=scenario()
        s["observations"][0]["advisories"].append({"id":ALPHA})
        r["advisory_matches"]+=1
        verdict,_=audit(s,r,raw,lookup=lambda x:meta[x])
        self.assertEqual(verdict["state"],"HOLD")

    def test_partial_metadata_fails_closed(self):
        s,r,raw,meta=scenario()
        def lookup(x):
            if x==BETA:raise OSError("temporary failure")
            return meta[x]
        verdict,report=audit(s,r,raw,lookup=lookup)
        self.assertEqual(verdict["state"],"HOLD")
        self.assertEqual(verdict["metadata_records_observed"],1)
        self.assertIsNone(report)

    def test_record_id_substitution_fails_closed(self):
        s,r,raw,meta=scenario()
        meta[BETA]["id"]="GHSA-other"
        verdict,report=audit(s,r,raw,lookup=lambda x:meta[x])
        self.assertEqual(verdict["state"],"HOLD")
        self.assertIsNone(report)

    def test_unknown_severity_is_review_required_not_safety_clearance(self):
        s,r,raw,meta=scenario()
        meta[ALPHA]["database_specific"]={}
        verdict,report=audit(s,r,raw,lookup=lambda x:meta[x])
        self.assertEqual(verdict["state"],"PASS_PUBLIC_OSV_METADATA_TRIAGE_ONLY")
        self.assertEqual(verdict["explicit_severity_distribution"],{"UNKNOWN":3})
        self.assertTrue(all(x["triage_lane"]=="REVIEW_UNRATED"
                            for x in report["priority_queue"]))
        self.assertEqual(verdict["security_clearance"],"HOLD")

    def test_missing_package_fix_event_is_not_claimed(self):
        s,r,raw,meta=scenario()
        meta[ALPHA]["affected"][0]["package"]["name"]="other"
        verdict,report=audit(s,r,raw,lookup=lambda x:meta[x])
        self.assertEqual(verdict["state"],"PASS_PUBLIC_OSV_METADATA_TRIAGE_ONLY")
        axios=next(x for x in report["priority_queue"] if x["name"]=="axios")
        self.assertEqual(axios["recorded_fix_events"],[])
        self.assertEqual(axios["fix_version_suitable_for_installed_product"],"UNVERIFIED")

    def test_invalid_worker_budget_rejected(self):
        s,r,raw,meta=scenario()
        verdict,report=audit(s,r,raw,lookup=lambda x:meta[x],workers=20)
        self.assertEqual(verdict["state"],"HOLD")
        self.assertIsNone(report)


if __name__=="__main__":
    unittest.main()
