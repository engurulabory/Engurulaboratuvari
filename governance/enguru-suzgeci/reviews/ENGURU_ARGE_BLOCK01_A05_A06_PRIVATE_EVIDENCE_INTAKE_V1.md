# ENGÜRÜ BLOK 01 — A05/A06 gerçek kanıt giriş köprüsü V1

**STATE:** `A05_A06_LOCAL_INPUT_READY / FILE_INTEGRITY_CI_PASS / CRYPTO_AUTHORITY_HOLD / OFFICIAL_0_OF_9`

Kanonik görev kapsamı: A05 = 18 müşterinin gerçek kurulu sürüm/edition/dağıtım kanıtı; A06 = 18 bağımsız E5 kararı. Özgün V19 18×13=234 hücreli baz SHA-256 `3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08` korunur.

## 1. Sahadan gerçek teslim

Her **özgün müşteri-vaka** için kaynak sahibi/teknik yetkili tarafından sağlanacak:

1. Kurulu kesin sürüm, edition, gerçek source commit SHA, gerçek müşteri dağıtım manifesti ve SHA-256
2. Kurulu sürüme ait SPDX veya CycloneDX **müşteri SBOM dosyası**, SHA-256 ve bağımlılık/sürüm doğruluğunun ayrıca yetkili denetimi
3. Yetkili müşteri beyanı, imzası ve doğrulanabilir yetkili anahtar kimliği
4. Müşteri ve sağlayıcıdan ayrı, yetkili **bağımsız E5 gözlemcisi**: gerçek kullanım gözlemi, zaman, rapor, imzalı bağımsız beyan ve doğrulanabilir güven kökü

Bağlayıcı güven kökü, geçerli anahtar, imzacı yetkisi ve bağımsız doğrulayıcı kararı mevcut canonical DoneCheck/Human Threshold mekanizmasında doğrulanacaktır. Bu giriş aracı yalnız **yerel dosya bütünlüğü ve şekil denetimi** yapar.

## 2. Giriş sözleşmesi

Dosyaları gerçek Mac OSi sahasında yetkili sahibin seçtiği **özel yerel çalışma alanında** sakla. Kamuya açık GitHub PR/issue içine müşteri belgelerini, kişisel verileri, özel anahtarları veya gizli dağıtım kayıtlarını koymak güvenli teslim yöntemi değildir; GitHub'da yalnız kaynak kapsamı ve redakte durum/kanıt referansları kaydedilir.

Kullanım:

```sh
python3 -B tools/arge_block01_a05_a06_evidence_intake_v1.py \
  --catalog governance/enguru-suzgeci/reviews/ENGURU_ARGE_BLOCK01_18_CASE_RECONCILIATION_V428.json \
  --packet /PRIVATE_EVIDENCE_ROOT/packet.json \
  --artifacts /PRIVATE_EVIDENCE_ROOT/files
```

`packet.json`:

```json
{
  "schema": "enguru.arge.block01.a05-a06-external-evidence/v1",
  "baseline_sha256": "3906f7bd6ae07d26547babc172d1337cfdfeff85244ece95efb76c3cb448df08",
  "cases": [
    {
      "case_id": "01",
      "customer": "Bookshop.org",
      "technology": "Meilisearch",
      "deployment": {
        "release": "REAL_CUSTOMER_RELEASE",
        "edition": "REAL_EDITION",
        "source_commit": "REAL_40_OR_64_HEX_COMMIT",
        "customer_owner_id": "AUTHORIZED_OWNER_REFERENCE",
        "deployed_manifest": "01/manifest.json",
        "manifest_sha256": "REAL_FILE_SHA256",
        "customer_sbom": "01/sbom.json",
        "sbom_sha256": "REAL_FILE_SHA256",
        "customer_assertion": "01/owner.json",
        "customer_assertion_sha256": "REAL_FILE_SHA256",
        "customer_signature": "01/owner.sig",
        "customer_signature_sha256": "REAL_FILE_SHA256"
      },
      "e5": {
        "verifier_identity": "INDEPENDENT_VERIFIER_ID",
        "verifier_organization": "INDEPENDENT_ORGANIZATION",
        "observed_at": "2026-10-23T19:00:00+03:00",
        "report": "01/e5-report.json",
        "report_sha256": "REAL_FILE_SHA256",
        "verifier_assertion": "01/e5.json",
        "verifier_assertion_sha256": "REAL_FILE_SHA256",
        "verifier_signature": "01/e5.sig",
        "verifier_signature_sha256": "REAL_FILE_SHA256"
      }
    }
  ]
}
```

Örnek **yalnız alan yapısını** gösterir; üretim dosyası 01–18 özgün vaka kayıtlarının tamamını taşımalıdır. Müşteri adı, teknoloji, imza ve sürüm alanları gerçek kanıt kaynağından alınır.

## 3. Çıktı ve karar

- A05/A06 için `FILES_HASH_MATCH_REQUIRE_EXTERNAL_SIGNATURE_AUTHORITY` = dosya baytları girilmiş SHA-256 ile eşleşen, ancak imzacı yetkisi ve bağımsızlığı henüz dış kaynakta doğrulanan **aday**.
- Eksik vaka, tekrar kimliği, dosya dışına çıkış/symlink, değiştirilmiş SHA, geçersiz SBOM, beyan ve imza alanı eksikliği → vaka bazlı `HOLD`.
- Giriş aracının CLI çıkış kodu her durumda nonzero kalır; otomatik PASS/Verified Finish makbuzu üretmez.
- Resmî A05=HOLD, A06=HOLD, A01–A09=0/9, tüm iş=0/40. Kanıtı doğrulanmış owner, bağımsız reviewer, canonical grant ve DoneCheck/Human Threshold yetkisi ayrı bir resmî kapıdır.

## 4. Ek teknik sınırlar

İmza dosyasının SHA-256'sı imzanın **kriptografik geçerliliğini** göstermez. Aynı şekilde kendini bağımsız diye tanıtan üçüncü kişi bir doğrulayıcı kararı oluşturmaz. Gerçek bağımsız E5 için kanonik güven kayıtlarında sürümlü trust root, public key, scope-bound issuer grant, revocation/freshness ve reviewer yetki doğrulaması gerekir.

`tools/arge_block01_a05_a06_evidence_intake_v1.py` dosyasının testleri özgün 18 vakanın tamamını, dört vaka eksikliği, yinelenen kimlik, belge değiştirme, geçersiz SBOM, sahte bağımsızlık, symlink ve dosya yolundan dışarı çıkış senaryolarını kapsar.

**NEXT:** Gerçek yetkili customer/owner ve independent E5 belgeleri sahada temin edilince dosya bütünlüğünü bu read-only araçla denetle; ardından ayrı canonical kriptografik güven doğrulayıcısına ve bağımsız insan kabulüne geçir. `main`, ürün kaynakları ve yetkiler korunur.

## 5. Aynı dağıtım bağının zorunlu alanları

SHA-256 bütünlüğü doğrulandıktan sonra araç aşağıdaki **JSON beyan alanlarını** da birbirine bağlar:

- `deployed_manifest`: `case_id`, `customer`, `technology`, `release`, `edition`, `source_commit`. Alanlar packet içindeki aynı müşteri ve gerçek release bilgileriyle birebir eşleşir.
- `customer_assertion`: `case_id`, `customer`, `owner_id`, `manifest_sha256`. İmza referansının alındığı müşteri beyanı aynı manifest SHA-256 kimliğini içerir.
- `e5.report`: `case_id`, `customer`, `technology`, `observed_manifest_sha256`, `verifier_identity`. E5 gözlemi aynı kurulu manifesti işaret eder.
- `e5.verifier_assertion`: `case_id`, `report_sha256`, `verifier_identity`. Bağımsız denetim beyanı birebir rapor hashine bağlanır.

Dış müşteri belgelerinin kaynağı PDF ya da farklı yapıdaysa canonical sahibi tarafından yetkili, kanıt dosyasına imzalı ve kaynak byte hashleriyle bağlı JSON projeksiyonu sağlanır. Bu projeksiyonun varlığı gerçek imzanın geçerlilik hükmü değildir; ayrı canonical doğrulayıcı kapısı sürer.

**Karşıt kanıt:** Farklı müşterinin manifesti, başka manifesti gösteren owner beyanı, başka manifesti gösteren E5 raporu ve A05 HOLD iken A06 aday durumunun yükselmesi testlerde güvenli HOLD verir. `tests/test_arge_block01_a05_a06_evidence_intake_v1.py` kapsamı **16 adversarial test**. Kanıt dönüştürme kapsamında kişisel veriler ve özel anahtarlar özel yerel delil alanında korunur.


## 6. Tek okumalı dosya bütünlüğü / TOCTOU sınırı

- Kanıt dosyaları POSIX `O_NOFOLLOW` ve dizin dosya tanıtıcıları (`dir_fd`) kullanılarak açılır; son dosya `fstat` ile düzenli dosya olarak doğrulanır. FIFO, sembolik bağlantı ve kapsam dışı yollar güvenli HOLD üretir.
- Dosya SHA-256 kontrolü ve JSON alan/beyan bağları **aynı bellekte tutulan dosya baytları üzerinden** değerlendirilir. Doğrulama sonrası aynı belgeyi yeniden okuma yolu kaldırılmıştır.
- Boyut üst sınırı okuma sırasında da uygulanır (25 MiB/artifact). Sağlayıcı imzası ile güven kökü için yetkili Ed25519/issuer değerlendirmesi yine canonical ayrı doğrulayıcıda yapılır.
- `tests/test_arge_block01_a05_a06_evidence_intake_v1.py` içinde **19 test**; tek-okuma regresyonu, dizin symlink ve FIFO saldırıları dâhildir. Test PASS, gerçek müşteri imzası veya E5 yetkili kabulü anlamına gelmez.

**Kanıt:** PR #207 review-only; exact HEAD `050e56e5beb0dde44a72283858a6063bbd7964ed`, 4/4 GitHub Actions PASS, Labory Final Gate run `40004468046`, ilgili A05–A06 test adımı PASS. `main` ve üretim kaynakları korunur. Resmî A05/A06 HOLD.
