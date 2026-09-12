class MemoryEvidenceStore:
    def __init__(self):
        self.items = []

    def add(self, record):
        if any(item.order_id == record.order_id for item in self.items):
            raise ValueError("duplicate order")
        if any(item.document_id == record.document_id for item in self.items):
            raise ValueError("duplicate document")
        self.items.append(record)

    def between(self, start, end):
        return [item for item in self.items if start <= item.issued_at < end]
