"""G02 tenant/resource access gate for billing evidence.

This is an adapter contract, never a signer, identity provider, or acceptance grant.
Only a trusted server can inject the independently verified canonical grant verifier.
Missing verifier, grant, identity or any failed authorization -> fail closed.
"""
from typing import Protocol, Any

from cores.billing.billing_core import BillingError


class BillingAccessDenied(BillingError):
    pass


class CanonicalGrantVerifier(Protocol):
    def authorize(self, *, subject: str, tenant_id: str, resource_id: str,
                  action: str, grant: Any) -> bool: ...


def require_grant(verifier, *, subject, tenant_id, resource_id, action, grant):
    if not all(isinstance(x, str) and x.strip() for x in
               (subject, tenant_id, resource_id, action)):
        raise BillingAccessDenied("Missing principal, tenant, resource or action scope")
    if verifier is None or grant is None:
        raise BillingAccessDenied("Canonical verifier and grant are required")
    # Production injects this verifier from a trusted server/authority boundary.
    # An untrusted caller-supplied verifier would invalidate this security model.
    try:
        allowed = verifier.authorize(
            subject=subject, tenant_id=tenant_id,
            resource_id=resource_id, action=action, grant=grant)
    except Exception as exc:
        raise BillingAccessDenied("Canonical authorization check unavailable") from exc
    if allowed is not True:
        raise BillingAccessDenied("Canonical authorization denied")
