"""Tested strict one-package extraction; no code executes during extraction."""
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import zipfile


def extract_verified(package_bytes, expected_sha, target):
    if len(package_bytes)>15000000 or hashlib.sha256(package_bytes).hexdigest()!=expected_sha:
        raise ValueError('PACKAGE_SHA_HOLD')
    target=Path(target).absolute()
    if '..' in target.parts or any(p.is_symlink() for p in (target,*target.parents)) or target.exists():
        raise ValueError('NEW_NON_SYMLINK_TARGET_REQUIRED')
    with zipfile.ZipFile(io.BytesIO(package_bytes)) as z:
        names=z.namelist()
        if len(names)!=len(set(names)) or len(names)>250:raise ValueError('DUPLICATE_OR_TOO_MANY_MEMBERS')
        if sum(i.file_size for i in z.infolist())>25000000:raise ValueError('ARCHIVE_SIZE_LIMIT')
        for i in z.infolist():
            parts=Path(i.filename).parts
            if not parts or Path(i.filename).is_absolute() or any(x in ('..','.') for x in parts) or '\\' in i.filename:
                raise ValueError('ARCHIVE_PATH')
            if i.is_dir() or stat.S_ISLNK(i.external_attr>>16):raise ValueError('ARCHIVE_FILE_TYPE')
        if z.testzip() is not None:raise ValueError('ARCHIVE_CRC')
        manifest=json.loads(z.read('PACKAGE_MANIFEST.json'))
        if set(manifest['files'])!=set(names)-{'PACKAGE_MANIFEST.json'}:raise ValueError('EXACT_ARCHIVE_MANIFEST')
        for name,sha in manifest['files'].items():
            if hashlib.sha256(z.read(name)).hexdigest()!=sha:raise ValueError('MEMBER_SHA')
        target.mkdir(mode=0o700)
        for name in names:
            p=target/name;p.parent.mkdir(parents=True,exist_ok=True)
            fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,'wb') as f:f.write(z.read(name))
    return target
