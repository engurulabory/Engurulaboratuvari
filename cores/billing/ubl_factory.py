from dataclasses import dataclass


@dataclass(frozen=True)
class UblDocument:
    xml: str
    profile: str
    document_type: str
    series: str


class UblFactory:
    def build(self, *, request, document_type, series: str) -> UblDocument:
        if not series or len(series) != 3:
            raise ValueError("series must be exactly 3 characters")
        profile = "EARSIVFATURA" if "ARCHIVE" in document_type.value else "TEMELFATURA"
        xml = (
            "<Invoice>"
            f"<ID>{request.order_id}</ID>"
            f"<ProfileID>{profile}</ProfileID>"
            f"<DocumentType>{document_type.value}</DocumentType>"
            f"<Series>{series}</Series>"
            "</Invoice>"
        )
        return UblDocument(xml=xml, profile=profile, document_type=document_type.value, series=series)
