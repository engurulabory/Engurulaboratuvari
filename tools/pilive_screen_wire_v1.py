"""Lossless transport for the existing Core portfolio; no new progress authority."""
import hashlib
import json
from tools.pilive_core_snapshot_adapter_v1 import canonical, Hold

def export_wire(snapshot):
    fields=('sourceRevision','sourcePins','projects','canonicalWrite','productionGrant','verifiedFinish','technicalPassIsOfficial')
    if snapshot.get('schema')!='enguru.pilive.core-portfolio/v1':raise Hold('HOLD_WIRE_SCHEMA')
    content={k:snapshot[k] for k in fields}
    raw=canonical(content)
    if hashlib.sha256(raw).hexdigest()!=snapshot.get('projectionDigest'):raise Hold('HOLD_WIRE_DIGEST')
    return canonical({'schema':'enguru.pilive.screen-wire/v1','snapshot':snapshot,'canonicalProjection':raw.decode('utf-8')})
