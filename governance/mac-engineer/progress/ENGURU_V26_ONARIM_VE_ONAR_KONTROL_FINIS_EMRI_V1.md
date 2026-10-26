# ENGÜRÜ YÖNETİM → İCRA V26 | Finişe bağlı onar kontrol kapanış emri

**Tarih:** 21.10.2026. **Kaynak:** V25 R1 tam mühendislik devir raporu + GitHub V25 commit kanıtları + 100 özgün ID ledger. **Hüküm:** `PASS_REVIEW_SOURCE_PUBLISHED / HOLD_OWNER_AUTHORIZED_ACCEPTANCE`.

## 1. Finiş hiyerarşisi (P0 → P1 → P2)

**P0 — Kalıcı sabit hedef:** ENGÜRÜ Mac Engineer™ yerel Product Engineering Operator ürününü güvenli, tekrarlanabilir, yetkili ve kanıtlanabilir **Verified Finish → `BITTI_DUR`** noktasına taşı.

**P1 — Bağımlı resmî kabul sırası:** H1 Secure Enclave P-256 4/4 → H2 canonical atomic writer 4/4 → H3 GitHub↔OSi 4/4 → Native Mac Engineer OSi gerçek saha → Mandatory DoneCheck JSON / DoneCheck v1.2 `verifyTask` → Ed25519 HumanReview → yetkili `recordVerifiedFinish()` → `BITTI_DUR`. F01–F06 bütünü ve PLive™ sonraki ayrı ürün sırası korunur.

**P2 — V26 tek ana ve bağımsız destek:** F01 canonical owner/reviewer/12-kriter/DoneCheck bağı; F05 Native 0.8 kaynak onarımı, yetkili source review, ikon/sürüm ve canlı kabul. Diğer F02–F04/F06 bağımlılıklarının hazırlanabilir güvenli işlemleri tek planın parçasıdır.

## 2. ENGÜRÜ Süzgeci™ ve pozitif dil evreni

**Canonical sekiz aşama:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet.

**Bağlayıcı çalışma dili:** ENGÜRÜ pozitif, doğru, yapıcı mühendislik söylemi; `mevcut hakikat + gerekli fark`; `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT`. Olumsuz durumları `HOLD`/`GÜVENLİ_DUR` olarak gerçek kanıtla sınıflandır. Eylemleri doğru ileri hareketle tarif et: “mevcut kaynağı koru”, “yetkili karar al”, “bağımsız doğrula”, “kabul kapısını tamamla”. `PASS` gerçek scope+yetki+test+receipt birleşiminden doğar. ENGÜRÜ 100/100 Yönetim/İCRA tasarım standardı ve gerçek saha kapasite sonucu ayrı tutulur. Aynı Süzgeç, aynı canonical otorite, aynı 100 özgün ID; ek core, dokuzuncu aşama veya paralel kabul kapısı oluşturulmaz.

## 3. Kanıtlı V25 kaynak durumu

- F01 gerçek karar dosyası: `governance/mac-engineer/review/F01_TEK_YETKILI_HUMAN_THRESHOLD_KARARI_V23.md`, Yönetim PR #191 V25 commit `ef0483e1af033e782e1c4513be5442b84e19060e`; blob `c4fc992543d3e6282e31f36818e3f0ba3b005651`; gerçek dosya SHA-256 `b928713a9117168ab93051f3dd1fecb8467a38c3f284ba8427668fbbe477da97`. Published review material PASS; owner/Ed25519/criteria authority HOLD.
- F05 gerçek patch: `execution_prep/native_app/review/F05_V23_PR14_TO_V08_LAUNCH_RETRY_FIX.patch`, Engineer PR #14 V25 commit `dbf34e055672ba4c93afddbac80662f288c37d3e`; blob `8b4da8ddba9ce030cea9dc6676192433116ac540`; gerçek dosya SHA-256 `947693553748463068011b1fed994c5e37d0b95c7cdedf632982813ba959b55f`. Published review material PASS; gerçek Swift/Info.plist code diff, owner review ve canlı kabul HOLD.
- V25 iki GitHub PR exact-head CI olumlu olsa da **review dosyasına ait HEAD** içindir. Korunmuş yerel 185 commit, kullanıcı dirty yollar, çalışan Native 0.8 ve tarihsel v0.6 provenance esastır.
- Yönetim 100 kontrol: **22 PASS_EVIDENCE / 78 HOLD**; H1/H2/H3 **0/12**, F01–F06 tam kapanış **0/6**, Native/DoneCheck/Verified Finish HOLD.

## 4. On kontrol turu — adım adım kabul

**V26 saha kapasite hedefi:** 22→**32/100**, yalnız önceden HOLD olan **10 farklı özgün `Bxx-yy`** kabul şartıyla. Sonraki Yönetim eşikleri `32→42→52→62→72→82→92→100` (son +8). Kaynak yetkisiyle erişilebilen bütün uygun işleri tur içinde tamamla; 32 hedefi bitiş kotası değildir. Yetki engelinde gerçek N, `32−N` farkı ve en kısa kesin karar sunulur.

**Öncelikli 10 kanıt adayı (garantisiz):**
- Salt-okuma kaynak/koruma hattı: `B05-03` iki yerel remote ve repo kimliği; `B10-03` resmî v0.6 lock, immutable local yedek ve SHA; `B05-04` yetkili branch/base/ancestry.
- Kaynak-owner mutabakatı: `B01-09` aktif sürüm/owner; `B01-10` F01–F06 tek authoritative snapshot.
- Native yetkili source: `B06-07` accepted local HEAD↔stage SHA; `B06-08` canonical build entrypoint; `B06-09` Native 0.8 sürüm kabulü.
- F01 yetki: `B02-03` canonical owner kimliği; `B02-04` reviewer Ed25519 key authorization.

Bu 10 ID bir **öncelik sırası**dır. Exact kaynak ve yetki şartı başka HOLD ID'sinde daha erken tamamlanırsa ona geç; yeni ID üretme, mevcut PASS'i yeniden sayma. Gerçek kanıt adayı ayrı raporlanır; Yönetim ledger'ı bağımsız inceleme ile günceller.

## 5. F01–F06 ana kapanış işleri

**F01 (birincil):** Mevcut canonical 12-kriter yetki kaynağını, owner ID/scope, reviewer Ed25519 public-key authorization, `CRITERIA_SET_SHA` ve exact branch/commit/blob ile A yolunda kanıtla. Kaynakta yetki boşluğu kanıtlanırsa mevcut dar kapsam B grant adayı için **tek Human Threshold™ kararı** ve durable receipt iste. Yetki çıktısı sonrasında Mac runtime → Progress Core™ → Mandatory DoneCheck JSON → DoneCheck `verifyTask` adapter/validator bağını gerçek pozitif/negatif testle tamamla. H1 P-256 ve Ed25519 reviewer ayrı yetkilerdir.

**F05 (bağımsız):** V25'in yayımlanmış `.patch` kaynak diff'ini gerçek Swift `EnguruMacEngineerApp.swift` ve `Info.plist` üzerinde **izinli izole review/feature çalışma dalı** adayı olarak hazırla. Özellikle V23 `launchInFlight` düzeltmesini, retry/restart/concurrency/shutdown korumalarını, gerçek 0.8 kaynak sürümünü ve v0.6 kilitli tarihi koru. Değişiklikten sonra source SHA, before/after, exact-head macOS CI ve negatif regresyon al. Source owner reviewer inceleme kararıyla kabul sağlar; ikonun lisans/hak sahibi/Git blob izini gerçek kayda bağla. Signing/install/live GUI/status/doctor/real-task/persistency ayrı yetkili saha kapısında gerçekleşir. V25 kullanıcısının yayın yetkisi **yalnız review dosyası** içindir; gerçek Native source mutation için mevcut yetki belgesini ayrıca kontrol et.

**F02 / H1:** Secure Enclave P-256 gerçek owner/grant/issuer ve taze challenge; sign, independent verification, anti-replay, expiry/audit, 4/4 resmî receipt.

**F03 / H2:** H1 resmî 4/4 ardından writer entrypoint, target-scoped grant, atomic/idempotent/conflict/recovery ve owner audit; H2 resmî 4/4.

**F04 / H3:** H2 resmî 4/4 ardından origin/head/dirty preservation, exact parity, independent review, exact CI, authorized remote transaction/receipt ve H3 4/4.

**F06:** Native saha ve 12/12 yetkili evidence sonrası Mandatory JSON, `verifyTask`, Ed25519 HumanReview ve `recordVerifiedFinish()` durable receipt; kaynak→kanıt audit, tarihsel v0.6, tam ürün kabulü.

## 6. Gerçek mühendislik icrası ve kanıt

İCRA mimari/kaynak araştırması, doğrulanmış kök neden, bütünsel bağımlılık planı, tasarım, kod/onarımlar, izole gerçek patch, güvenli entegrasyon, Swift/Mac build, unit/integration, adversarial ve canlı yetkili davranış testleri, Git/CI, provenance/lisans, canonical DoneCheck/human gate, exact SHA ve kalıcı delil üretimini **tek kapsamlı turda** sahiplenir. Her tamamlanan alt iş sonrası sonraki izinli bağımlılıklara ilerler. Yalnız gözleme dayanarak kabul PASS ilanı yerine gerçek onay/receipt ile teslim eder.

**Yürütme kapısı:** gerçek yetkili owner/reviewer/grant ve kaynak-write kapsamı varsa `İLERLE`. İhtiyaç duyulan korumalı karar varsa diğer bağımsız güvenli işleri bitirerek `GÜVENLİ_DUR`; açık soruyu bir gerçek karar nesnesi ve sahibine indir.

## 7. Zorunlu tam V26 devir raporu

**En üstte altı satır:** `STATE`; `SAYAÇ=22/100→N/100; HEDEF=32/100; FARK=32−N`; `YENİ_PASS=gerçek ID + kanıt`; `F01`; `F05`; `RESMÎ=H1/H2/H3, F01–F06, Native, DoneCheck, Verified Finish; RAPOR_SHA256; SONRAKİ`.

**Tam AudiV13 JSON ve Markdown raporu:**
1. Gerçek yapılan görev, onarım, kod farkı, yürütme ve test matrisleri; source/commit/blob/hash.
2. 100 özgün ID için **22 PASS / 78 HOLD** başlangıcından güncel satır bazlı hakikat, her yeni ID'nin full koşul/kanıt/owner/negatif/karar kapısı.
3. F01–F06 için **tüm kalan işler**, teknik ihtiyaçlar, kaynak sahibi, en kısa uygulanabilir kalıcı çözüm, önkoşul, yetkili insan kararı, kabul receipt.
4. Kanıtlanmış kök nedenler ile ayrıca incelenecek hipotezler ayrı; kaynak koruma before/after ve gerçek Native 0.8/v0.6 durumu.
5. H1 x/4, H2 x/4, H3 x/4, Native, DoneCheck, Verified Finish ve BITTI_DUR bitiş matrisi, sonraki 10-kontrol turunun net en uygun sırası.
6. Review-only dosya yayını ile source promotion ve canlı owner acceptance kararı ayrı; tamamlanmış kanıtın SHA ve AudiV13 arşiv yolu.

**Teslim sunumu:** Dosya gerekiyorsa gerçek doğrulanmış ZIP indirme bağlantısı; tek hazır ve korunmuş `zsh` Terminal kod bloğu; altı satır özeti ve kalan engel/çözüm matrisi. Yetki kapısında tek kesin insan kararı.

**Son hüküm:** `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT` ve ENGÜRÜ Süzgeci™ sekiz aşamasıyla finişe doğru gerçek kontrollü ilerleme.
