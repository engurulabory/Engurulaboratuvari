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

import datetime, platform, subprocess, sys
if platform.system() != 'Darwin' or platform.machine() != 'arm64':
    sys.exit('STATE=HOLD — Gerçek arm64 Mac ortamı gerekli.')
if sys.version_info < (3, 9):
    sys.exit('STATE=HOLD — Mevcut Python 3.9 veya üzeri gerekli; indirme yapılmadı.')
EXPECTED = '88129529a2920e1d217752c3c38f51ffff84420aa095755b4906c3125ec46697'
def safe_read(path):
    if any(p.is_symlink() for p in path.parents):
        raise RuntimeError('SYMLINK_PARENT_HOLD')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as f:
        s = os.fstat(f.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or s.st_uid != os.getuid():
            raise RuntimeError('REGULAR_OWNED_FILE_REQUIRED')
        b = f.read(15000001)
        if len(b) > 15000000: raise RuntimeError('FILE_SIZE_HOLD')
        return b
home = Path.home()
selected = None
for candidate in sorted((home / 'Downloads').glob('ENGURU_OSI_UCLU_YEREL_ZEKA_V015_FINAL*.zip')):
    if candidate.is_symlink() or not candidate.is_file(): continue
    data = safe_read(candidate)
    if hashlib.sha256(data).hexdigest() == EXPECTED:
        selected = data; break
if selected is None:
    sys.exit('STATE=HOLD — İndirilen V015 dosyası veya SHA eşliği doğrulanamadı.')
print('PACKAGE_SHA=PASS', flush=True)
base = home / 'Desktop' / 'AudiV13'
if any(p.is_symlink() for p in (base, *base.parents)):
    sys.exit('STATE=HOLD — AudiV13 gerçek dizin olmalı.')
base.mkdir(mode=0o700, parents=True, exist_ok=True)
if base.stat().st_uid != os.getuid() or base.stat().st_mode & 0o022:
    sys.exit('STATE=HOLD — AudiV13 sahipliği/izinleri doğrulanmalı.')
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
root = extract_verified(selected, EXPECTED, base / ('ENGURU_V015_' + stamp))
print('ISOLATED_ROOT=' + str(root), flush=True)
run = subprocess.run([sys.executable, '-I', '-B', str(root / 'tools/mac_install.py'), '--owner-start-isolated'])
subprocess.run([sys.executable, '-I', '-B', str(root / 'tools/mac_evidence.py')], check=True)
evidence = safe_read(root / 'MAC_EVIDENCE_V015.zip')
target = home / 'Desktop' / ('ENGURU_V015_MAC_KANIT_' + stamp + '.zip')
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, 'wb') as f: f.write(evidence); f.flush(); os.fsync(f.fileno())
assert hashlib.sha256(safe_read(target)).digest() == hashlib.sha256(evidence).digest()
print('MAC_FLOW_EXIT=' + str(run.returncode))
print('EVIDENCE_ZIP_SHA256=' + hashlib.sha256(evidence).hexdigest())
print('MASAUSTU_DOSYASI=' + str(target))
print('PRODUCT_VERIFIED_FINISH=HOLD_RECEIPT_REVIEW_REQUIRED')
subprocess.run(['/usr/bin/open', '-R', str(target)], check=True)
sys.exit(run.returncode)
