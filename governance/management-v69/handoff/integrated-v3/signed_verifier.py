"""Test-only independent verifier of exact Pilot task/source/artifact binding."""
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from pilot_contract import stable,digest
def signed_payload(task,goal,source,artifact,generation):
 return {"task":task,"goal":goal,"source_sha256":source,"artifact_sha256":digest(artifact),"generation":generation,"scope":"TEST_ONLY_VERIFIER"}
def verify(public_key_bytes,task,goal,source,artifact,generation,receipt,signature):
 expected=signed_payload(task,goal,source,artifact,generation)
 if not isinstance(receipt,dict) or receipt!=expected:return "HOLD_BINDING"
 try:Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature,stable(receipt))
 except (InvalidSignature,ValueError,TypeError):return "HOLD_SIGNATURE"
 return "PASS_TEST_VERIFIER"
