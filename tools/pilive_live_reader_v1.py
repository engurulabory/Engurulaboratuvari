"""Existing pinned Core collector -> authenticated wire; read-only runtime seam."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
from tools import pilive_portfolio_probe_v1 as collector
from tools.pilive_screen_wire_v1 import export_wire

def packet(observation):
    if observation.get('state')!='PASS_NATIVE_PORTFOLIO_CAPTURE_ONLY':raise ValueError('HOLD_NATIVE_SOURCE')
    s=observation['snapshot'];wire=export_wire(s)
    return {'wire':base64.b64encode(wire).decode(),'identity':{'revision':s['sourceRevision'],'pins':s['sourcePins'],'digest':s['projectionDigest'],'wireSha256':hashlib.sha256(wire).hexdigest()},'observation':observation}

def main():
    try:
        with tempfile.TemporaryDirectory(prefix='enguru-pilive-read-') as temp:
            observation=collector.portfolio_read(Path.home(),Path(temp).resolve())
            if observation.get('state')!='PASS_NATIVE_PORTFOLIO_CAPTURE_ONLY':
                print(json.dumps({'state':'HOLD_READER_SOURCE','observation':observation}));return 2
            result=packet(observation)
        raw=json.dumps(result,ensure_ascii=False,allow_nan=False).encode()
        if len(raw)>4*1024*1024:raise ValueError('HOLD_OUTPUT_LIMIT')
        sys.stdout.buffer.write(raw);return 0
    except Exception:
        print('{"state":"HOLD_READER_SOURCE"}');return 2
if __name__=='__main__':raise SystemExit(main())
