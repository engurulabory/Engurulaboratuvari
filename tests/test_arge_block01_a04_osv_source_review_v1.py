"""HYM2 A04 OSV adapter: adversarial offline tests, no network or product PASS."""
import copy
import hashlib
import json
import unittest

from tools.arge_block01_a04_osv_source_review_v1 import (
    assessment, read_cdxbom, query_all,
)


def sample():
    packages=[
        ("actix-web","4.1.0","cargo","Meilisearch","LOCKFILE_EXACT_CANDIDATE"),
        ("django","5.1.0","pypi","Saleor","LOCKFILE_EXACT_CANDIDATE"),
        ("@adobe/css-tools","4.4.4","npm","Medusa","LOCKFILE_EXACT_CANDIDATE"),
        ("github.com/google/uuid","v1.6.0","golang","Temporal",
         "DIRECT_GO_MOD_DECLARATION_NOT_BUILD_GRAPH"),
    ]
    components=[]
    for name,version,eco,upstream,precision in packages:
        purl="pkg:"+eco+"/"+name.replace("@","%40")+"@"+version
        components.append({
            "type":"library","name":name,"version":version,
            "purl":purl,"bom-ref":purl,
            "properties":[
                {"name":"enguru:a04:source","value":upstream},
                {"name":"enguru:a04:precision","value":precision},
            ]
        })
    bom={"bomFormat":"CycloneDX","specVersion":"1.5","version":1,
         "components":components}
    raw=json.dumps(bom,sort_keys=True,separators=(",",":")).encode("utf-8")
    receipt={"state":"PASS_SOURCE_SCOPED_COMPONENT_CANDIDATES_ONLY",
             "source_count_verified":7,"candidate_components_with_version":len(components),
             "candidate_sbom_sha256":hashlib.sha256(raw).hexdigest(),
             "unresolved_declarations":[{"requirement":"foo>=1.0"}]}
    return bom,receipt,raw


class OSVSourceReviewTests(unittest.TestCase):
    def test_real_source_candidate_mapping_and_purls(self):
        b,r,raw=sample()
        c=read_cdxbom(b,r,raw)
        self.assertEqual([x["ecosystem"] for x in c],
                         ["crates.io","PyPI","npm","Go"])
        self.assertEqual(c[2]["name"],"@adobe/css-tools")

    def test_negative_query_results_are_not_security_clearance(self):
        b,r,raw=sample()
        def no_reports(queries):
            return {"results":[{} for q in queries]}
        result,report=assessment(b,r,raw,send=no_reports,batch_size=2)
        self.assertEqual(result["state"],"PASS_OSV_SOURCE_SNAPSHOT_ONLY")
        self.assertEqual(result["query_coverage"],4)
        self.assertEqual(result["affected_package_candidates"],0)
        self.assertEqual(result["known_vulns_absent"],"UNDETERMINED")
        self.assertEqual(result["cve_security_clearance"],"HOLD")
        self.assertEqual(result["a04_official"],"HOLD")
        self.assertEqual(len(report["observations"]),4)

    def test_positive_finding_and_batch_pagination_keep_alignment(self):
        b,r,raw=sample()
        requests=[]
        def send(queries):
            requests.append(copy.deepcopy(queries))
            if len(requests)==1:
                self.assertEqual(len(queries),3)
                return {"results":[
                    {"vulns":[{"id":"GHSA-demo-one","modified":"2025-01-01T00:00:00Z"}],
                     "next_page_token":"p2"},
                    {},
                    {"vulns":[{"id":"OSV-demo-two"}]},
                ]}
            if len(requests)==2:
                self.assertEqual(len(queries),1)
                self.assertEqual(queries[0]["page_token"],"p2")
                return {"results":[{"vulns":[{"id":"GHSA-demo-three"}]}]}
            self.assertEqual(len(queries),1)
            return {"results":[{}]}
        result,report=assessment(b,r,raw,send=send,batch_size=3)
        self.assertEqual(result["state"],"PASS_OSV_SOURCE_SNAPSHOT_ONLY")
        self.assertEqual(result["query_coverage"],4)
        self.assertEqual(result["affected_package_candidates"],2)
        self.assertEqual(result["advisory_matches"],3)
        self.assertEqual(len(report["observations"][0]["advisories"]),2)
        self.assertEqual(report["observations"][1]["advisories"],[])
        self.assertEqual(len(report["observations"][2]["advisories"]),1)
        self.assertEqual(result["batch_requests_with_pagination"],3)

    def test_source_bytes_sha_drift_fails_closed_without_api(self):
        b,r,raw=sample()
        called=[]
        def send(queries):
            called.append(1)
            return {"results":[]}
        result,report=assessment(b,r,raw+b"x",send=send)
        self.assertEqual(result["state"],"HOLD")
        self.assertEqual(report,None)
        self.assertEqual(called,[])

    def test_unsupported_unresolved_range_fails_closed(self):
        b,r,raw=sample()
        b["components"][0]["properties"][1]["value"]="UNRESOLVED_ROOT_PACKAGE_RANGE"
        raw=json.dumps(b,sort_keys=True,separators=(",",":")).encode()
        r["candidate_sbom_sha256"]=hashlib.sha256(raw).hexdigest()
        result,report=assessment(b,r,raw,send=lambda q:None)
        self.assertEqual(result["state"],"HOLD")
        self.assertIsNone(report)

    def test_wrong_response_length_fails_closed(self):
        b,r,raw=sample()
        result,report=assessment(b,r,raw,send=lambda q:{"results":[]},batch_size=2)
        self.assertEqual(result["state"],"HOLD")
        self.assertEqual(result["query_coverage"],0)
        self.assertIsNone(report)

    def test_false_osv_vuln_and_bad_id_fail_closed(self):
        b,r,raw=sample()
        for result in ({"results":[{"vulns":"not-list"}]*4},
                       {"results":[{"vulns":[{"modified":"no-id"}]}]*4}):
            res,details=assessment(b,r,raw,send=lambda q:result,batch_size=4)
            self.assertEqual(res["state"],"HOLD")
            self.assertIsNone(details)

    def test_pagination_loop_fail_closed(self):
        b,r,raw=sample()
        res,details=assessment(b,r,raw,
            send=lambda q:{"results":[{"next_page_token":"same"} for _ in q]},
            batch_size=4)
        self.assertEqual(res["state"],"HOLD")
        self.assertIsNone(details)

    def test_invalid_batch_size_fails_closed(self):
        b,r,raw=sample()
        res,details=assessment(b,r,raw,send=lambda q:None,batch_size=501)
        self.assertEqual(res["state"],"HOLD")
        self.assertIsNone(details)


if __name__=="__main__":
    unittest.main()
