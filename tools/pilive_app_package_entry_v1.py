"""Reviewed zipapp bootstrap: authenticate payload, then explicit isolated build/open."""
import hashlib,json,sys,tempfile,zipfile
from pathlib import Path

def main():
    if sys.argv[1:]!=['--build-and-open']:print('STATE=HOLD_EXPLICIT_BUILD_AND_OPEN_REQUIRED');return 2
    if sys.platform!='darwin':print('STATE=HOLD_MAC_REQUIRED');return 2
    with zipfile.ZipFile(sys.argv[0]) as archive,tempfile.TemporaryDirectory(prefix='enguru-pilive-delivery-') as folder:
        root=Path(folder).resolve();raw=archive.read('MANIFEST.json');manifest=json.loads(raw)
        if not isinstance(manifest['files'],dict) or not 1<=len(manifest['files'])<=80:raise ValueError('HOLD_PACKAGE_SCOPE')
        for name,pin in manifest['files'].items():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or not path.parts:raise ValueError('HOLD_PACKAGE_PATH')
            data=archive.read('payload/'+name)
            if len(data)>2*1024*1024 or hashlib.sha256(data).hexdigest()!=pin:raise ValueError('HOLD_PACKAGE_SHA')
            target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        (root/'MANIFEST.json').write_bytes(raw);sys.path.insert(0,str(root))
        from tools.pilive_native_app_handoff_v1 import build_and_open
        return build_and_open(root,Path.home())
if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,zipfile.BadZipFile):print('STATE=HOLD_PACKAGE_VALIDATION');raise SystemExit(2)
