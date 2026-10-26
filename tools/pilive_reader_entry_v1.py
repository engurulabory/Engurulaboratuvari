"""Signed app-resource entry: validate every packaged reader byte before imports."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

def verified_read(root, name):
    p=Path(name)
    if p.is_absolute() or '..' in p.parts:raise ValueError('HOLD_READER_PATH')
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for part in p.parts[:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd);os.close(fd);fd=child
        source=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
        try:
            info=os.fstat(source)
            if not stat.S_ISREG(info.st_mode) or info.st_size>2*1024*1024:raise ValueError('HOLD_READER_FILE')
            parts=[];size=0
            while True:
                b=os.read(source,65536)
                if not b:break
                size+=len(b)
                if size>2*1024*1024:raise ValueError('HOLD_READER_SIZE')
                parts.append(b)
            return b''.join(parts)
        finally:os.close(source)
    finally:os.close(fd)

def validate(root, expected):
    raw=verified_read(root,'READER_MANIFEST.json')
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('HOLD_READER_MANIFEST')
    pins=json.loads(raw)
    if not isinstance(pins,dict) or not 1<=len(pins)<=12:raise ValueError('HOLD_READER_SCOPE')
    for name,pin in pins.items():
        if hashlib.sha256(verified_read(root,name)).hexdigest()!=pin:raise ValueError('HOLD_READER_SHA')
    return pins

if __name__=='__main__':
    try:
        root=Path(__file__).parent;validate(root,sys.argv[1]);sys.path.insert(0,str(root))
        from tools.pilive_live_reader_v1 import main
        raise SystemExit(main())
    except (OSError,ValueError,KeyError,IndexError):
        print('{"state":"HOLD_READER_PACKAGE"}');raise SystemExit(2)
