"""HYM2 A04: adversarial source-scoped CycloneDX candidate evidence tests."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

from tools.arge_block01_a04_sbom_candidates_v1 import assemble, parse_locked, parse_declared
from tools.arge_block01_a04_dependency_seeds_v1 import blob_sha1

ROOT=Path(__file__).resolve().parents[1]/"governance/enguru-suzgeci/reviews"
M=json.loads((ROOT/"ENGURU_ARGE_A04_DEPENDENCY_SEEDS_V1.json").read_text())
U=json.loads((ROOT/"ENGURU_ARGE_BLOCK01_A04_UPSTREAM_LICENSE_PINS_V1.json").read_text())
PAYLOAD={
    "Meilisearch":b'version=4\n[[package]]\nname="actix-web"\nversion="4.1.0"\nsource="registry+https://example.com"\n',
    "Medusa":b'__metadata:\n  version: 6\n"@adobe/css-tools@npm:^4.0.0":\n  version: 4.4.4\n  resolution: "@adobe/css-tools@npm:4.4.4"\n  linkType: hard\n',
    "Saleor":b'version=1\n[[package]]\nname="django"\nversion="5.1.0"\nsource={registry="https://pypi.org/simple"}\n',
    "Supabase":b'{"name":"supabase","dependencies":{"react":"^19.0.0"}}',
    "Temporal":b'module go.temporal.io/server\nrequire (\n  github.com/google/uuid v1.6.0\n)\n',
    "OpenFGA":b'module github.com/openfga/openfga\nrequire github.com/google/uuid v1.5.0\n',
    "LangGraph":b'[project]\nname="langgraph"\nversion="1.2.16"\ndependencies=["pydantic>=2.7"]\n',
}


def synthetic():
    m=copy.deepcopy(M)
    payload={}
    for source in m["sources"]:
        tech=source["technology"]
        body=PAYLOAD[tech]
        key=(source["repository"],source["source_commit_sha"],
             source["dependency_path"])
        payload[key]=body
        source["dependency_git_blob_sha1"]=blob_sha1(body)
    return m,copy.deepcopy(U),payload


def fetching(payload):
    def run(url,timeout):
        p=urlparse(url)
        parts=p.path.lstrip("/").split("/",3)
        key=("/".join(parts[:2]),parts[2],parts[3])
        return payload[key],url
    return run


class SourceBoundCandidates(unittest.TestCase):
    def test_locked_sources_have_literal_resolved_versions(self):
        for tech in ("Meilisearch","Saleor","Medusa"):
            data=parse_locked(tech,PAYLOAD[tech])
            self.assertEqual(len(data),1)
            self.assertIn(data[0]["version"],("4.1.0","5.1.0","4.4.4"))
            self.assertEqual(data[0]["properties"][1]["value"],
                             "LOCKFILE_EXACT_CANDIDATE")

    def test_go_require_is_not_claimed_as_deployed_binary(self):
        for tech in ("Temporal","OpenFGA"):
            data=parse_declared(tech,PAYLOAD[tech])
            self.assertEqual(len(data),1)
            self.assertEqual(data[0]["properties"][1]["value"],
                             "DIRECT_GO_MOD_DECLARATION_NOT_BUILD_GRAPH")

    def test_range_only_inputs_remain_unresolved(self):
        for tech in ("Supabase","LangGraph"):
            data=parse_declared(tech,PAYLOAD[tech])
            self.assertEqual(len(data),1)
            self.assertIn("UNRESOLVED",data[0]["precision"])

    def test_seven_source_components_but_never_official_sbom_or_cve(self):
        m,u,p=synthetic()
        receipt,bom=assemble(m,u,fetch=fetching(p))
        self.assertEqual(receipt["state"],"PASS_SOURCE_SCOPED_COMPONENT_CANDIDATES_ONLY")
        self.assertEqual(receipt["source_count_verified"],7)
        self.assertEqual(len(bom["components"]),5)
        self.assertEqual(len(receipt["unresolved_declarations"]),2)
        self.assertEqual(bom["specVersion"],"1.5")
        self.assertEqual(receipt["candidate_components_with_version"],5)
        for key in ("complete_sbom","customer_installation_sbom","cve_advisory_review",
                    "legal_license_clearance","a04_official","verified_finish"):
            self.assertEqual(receipt[key],"HOLD")
        actual=hashlib.sha256(json.dumps(
            bom,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
        self.assertEqual(receipt["candidate_sbom_sha256"],actual)

    def test_tampered_bytes_fail_without_sbom(self):
        m,u,p=synthetic()
        k=next(iter(p))
        p[k]+=b"TAMPERED"
        receipt,bom=assemble(m,u,fetch=fetching(p))
        self.assertEqual(receipt["state"],"HOLD")
        self.assertEqual(receipt["source_count_verified"],6)
        self.assertIsNone(bom)

    def test_missing_ref_and_untrusted_redirect_fail(self):
        m,u,p=synthetic()
        for fetch in (
            lambda uri,timeout: (_ for _ in ()).throw(OSError("offline")),
            lambda uri,timeout: (b"payload","https://evil.invalid/redir"),
        ):
            receipt,bom=assemble(m,u,fetch=fetch)
            self.assertEqual(receipt["state"],"HOLD")
            self.assertIsNone(bom)

    def test_false_complete_claim_cannot_override_verdict(self):
        m,u,p=synthetic()
        m["acceptance_boundary"]["sbom_generated_and_verified"]="PASS"
        receipt,bom=assemble(m,u,fetch=fetching(p))
        self.assertEqual(receipt["complete_sbom"],"HOLD")
        self.assertEqual(receipt["cve_advisory_review"],"HOLD")
        self.assertEqual(receipt["a04_official"],"HOLD")

    def test_manifest_source_and_roster_tamper_block(self):
        for mutation in ("missing","repo","sha","source","duplicate"):
            with self.subTest(mutation=mutation):
                m,u,p=synthetic()
                if mutation=="missing":m["sources"].pop()
                if mutation=="repo":m["sources"][0]["repository"]="wrong/repo"
                if mutation=="sha":m["sources"][0]["source_commit_sha"]="f"*40
                if mutation=="source":m["sources"][0]["dependency_path"]="../../evil"
                if mutation=="duplicate":m["sources"][1]=copy.deepcopy(m["sources"][0])
                receipt,bom=assemble(m,u,fetch=fetching(p))
                self.assertEqual(receipt["state"],"HOLD")
                self.assertIsNone(bom)


if __name__=="__main__":
    unittest.main()
