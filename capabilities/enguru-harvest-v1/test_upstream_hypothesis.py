"""Real Hypothesis property tests exercising ENGURU source gates.

The generator and shrinker are external Hypothesis, installed in the GitHub
runner, not a synthetic imitation. Positive acceptance still requires review.
"""
import hashlib
import unittest
from hypothesis import given, settings, strategies as st
from harvest import evaluate, verify_bytes
from skill_kernel import execute

SCALAR=st.one_of(st.none(),st.booleans(),st.integers(),st.text(max_size=32))
UNTRUSTED=st.recursive(
    SCALAR,
    lambda children: st.lists(children,max_size=5) | st.dictionaries(st.text(max_size=20),children,max_size=5),
    max_leaves=20,
)
CFG=settings(max_examples=140, deadline=None, derandomize=True)

class UpstreamHypothesisTests(unittest.TestCase):
    @CFG
    @given(UNTRUSTED)
    def test_never_auto_promote_untrusted_record(self,record):
        result=evaluate(record)
        self.assertIn(result["state"],("CANDIDATE","HOLD"))
        self.assertNotIn(result["state"],("ADOPTED","PROVEN"))
    @CFG
    @given(UNTRUSTED)
    def test_malformed_source_evidence_fails_closed(self,untrusted):
        base={"id":"fixture","library":"skills","source_url":"https://example.org/fixture",
              "source_sha256":hashlib.sha256(b"hello").hexdigest(),"license":"MIT",
              "security_review":"PASS","mandatory_paid_api":0}
        data={**base,"source_sha256":untrusted}
        outcome=verify_bytes(data,b"hello")
        self.assertIn(outcome["state"],("HOLD","CANDIDATE"))
        if outcome["state"]=="CANDIDATE":
            self.assertEqual(untrusted,base["source_sha256"])
    @CFG
    @given(UNTRUSTED)
    def test_arbitrary_catalog_cannot_invent_adoption(self,record):
        result=execute("source-candidate",{"record":record})
        self.assertIn(result["state"],("HOLD","CANDIDATE"))
    @CFG
    @given(st.lists(st.text(max_size=12),max_size=30))
    def test_duplicates_are_conservative(self,ids):
        result=execute("duplicate-check",{"identifiers":ids})
        expected="HOLD" if any(not value for value in ids) or len(ids)!=len(set(ids)) else "UNIQUE"
        self.assertEqual(result["state"],expected)

if __name__=="__main__":
    unittest.main()
