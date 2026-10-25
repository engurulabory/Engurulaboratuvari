# PiLive — gerçek runtime bağımlılıklarının salt-okunur devri

Amaç: bulunan bundle kaynaklarının gerçekten kullanılan LiveProgress/v4 dosyalarıyla eşliğini incelemek. Yerel modül çalıştırılmaz; mevcut SHA sabitli Work paketinin yalnız güvenli okuyucusu kullanılır. Kaynakların SHA ve içerikleri yeni özel makbuza alınır. Mevcut dosyalar değiştirilmez; yalnız yeni AudiV13 orijinali ve Desktop kopyası yazılır. Bu yakalama atomik çoklu dosya snapshot veya ürün kabulü değildir.

Terminal'e bütünüyle yapıştırın; oluşan ORIGINAL JSON'u incelemeye aktarın. Ham içerik GitHub'a yayımlanmaz.

```bash
python3 -B -I - <<'PY'
import hashlib, sys, platform
from pathlib import Path
from datetime import datetime, timezone
if platform.system() != 'Darwin':
    raise SystemExit('HOLD_MAC_REQUIRED')
package = Path.home() / 'Downloads/ENGURU_PILIVE_RUNTIME_KOKEN_V1.pyz'
if package.is_symlink() or not package.is_file():
    raise SystemExit('HOLD_PACKAGE_PATH')
if hashlib.sha256(package.read_bytes()).hexdigest() != '455aa3b109a903bc62be00953fb1640dfd08cae726b0441cce1bcbe2a225c6aa':
    raise SystemExit('HOLD_PACKAGE_SHA256')
sys.path.insert(0, str(package))
from tools import pilive_native_learning_probe_v1 as safe
home = Path.home()
repo = home / 'Enguru/Projects/Engurulaboratuvari'
before = safe.core_pin_check(repo)
sources = []
scopes = [
    (home / 'Library/Application Support/ENGURU/LiveProgress/v4',
     ['projection_v6.py', 'snapshot_v52.py', 'snapshot.py']),
    (Path('/Applications/ENGURU-PLive-V31.app/Contents/Resources'),
     ['plive_v3_projection.py', 'plive_v3_base_projection.py'])
]
for root, names in scopes:
    for name in names:
        row = {'path': str(root / name)}
        try:
            raw = safe.read_file(root, name)
            row.update(state='CAPTURED_ONLY', sha256=safe.digest(raw),
                       bytes=len(raw), contentUtf8=raw.decode('utf-8'))
        except (OSError, ValueError, UnicodeError) as exc:
            row.update(state='HOLD_EXACT_SOURCE_READ', reason=type(exc).__name__)
        sources.append(row)
after = safe.core_pin_check(repo)
pairs = []
for name, pin in safe.RECEIPT_PINS.items():
    row = {'name': name, 'expectedSha256': pin}
    for label, relative in [('original', 'AudiV13/' + name), ('desktopCopy', name)]:
        try:
            actual = safe.digest(safe.read_file(home / 'Desktop', relative, 20*1024*1024))
            row[label] = {'sha256': actual, 'match': actual == pin}
        except (OSError, ValueError) as exc:
            row[label] = {'state': 'HOLD_EXACT_PATH', 'reason': type(exc).__name__}
    pairs.append(row)
receipt = dict(schema='enguru.pilive.runtime-dependency-observation/v1',
    observedAtUtc=datetime.now(timezone.utc).isoformat(),
    parentReceiptSha256='d91557b11abe20363f1a8ff89fb55267ec0549376c3c76839e2f80ea278349fa',
    state='SOURCE_CAPTURE_ONLY_REQUIRES_REVIEW', sources=sources,
    corePinsBefore=before, corePinsAfter=after, corePinsStable=before == after,
    priorReceiptLocations=pairs, canonicalWrites=0, nativeMuscleWrites=0,
    sqliteConnections=0, networkRequests=0, keychainReads=0, appLaunches=0,
    nativeCodeExecution=0, verifiedFinish='HOLD',
    atomicity='PER_FILE_FSTAT_ONLY; MULTI_FILE_CAPTURE_NOT_ATOMIC')
safe.save(home, receipt)
print('STATE=' + receipt['state'])
print('CANONICAL_WRITES=0; NATIVE_MUSCLE_WRITES=0; NATIVE_CODE_EXECUTION=0')
PY
```

Sınır: geçmiş üç makbuz yalnız önceki exact konumlarında aranır; taşınma/silinme varsayılmaz, yerine yeni orijinal oluşturulmaz. Kaynak okuma boşlukları HOLD kalır. Paket ve kurulum değişimi yok; gerçek Core çalıştırması veya native test tekrarı yapılmaz. Bu kaynak yakalaması, sonradan içerik/pin/mahremiyet incelemesi ve proje kümesi eşliği sınamasının girdisidir.
