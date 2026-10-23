from cores.billing.access_gate import require_grant

class MemoryEvidenceStore:
    def __init__(self, *, grant_verifier=None):
        self.items = []
        self.grant_verifier = grant_verifier

    def add(self, record, *, subject=None, grant=None):
        require_grant(self.grant_verifier, subject=subject, tenant_id=record.tenant_id,
                      resource_id=record.document_id, action="billing.invoice.write", grant=grant)
        if any(item.order_id == record.order_id for item in self.items):
            raise ValueError("duplicate order")
        if any(item.document_id == record.document_id for item in self.items):
            raise ValueError("duplicate document")
        self.items.append(record)

    def between(self, start, end, *, subject=None, tenant_id=None, grant=None):
        require_grant(self.grant_verifier, subject=subject, tenant_id=tenant_id,
                      resource_id=tenant_id, action="billing.invoice.list", grant=grant)
        found = []
        for row in self.items:
            if row.tenant_id != tenant_id or not (start <= row.issued_at < end):
                continue
            require_grant(self.grant_verifier, subject=subject, tenant_id=tenant_id,
                          resource_id=row.document_id, action="billing.invoice.read", grant=grant)
            found.append(row)
        return found
