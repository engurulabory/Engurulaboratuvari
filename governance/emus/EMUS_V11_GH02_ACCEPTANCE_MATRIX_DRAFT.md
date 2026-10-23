# EMÜS V1.1 — GH-02 Kabul Matrisi ve Mühendislik Fark Sözleşmesi
Tarih: 2026-10-23
STATE: DRAFT_CONTRACT / GH02_PARTIAL / GH01_HOLD

## Amaç
Mevcut ENGÜRÜ Yönetim, İcra, Mac Engineer™, Süzgeç™ ve DoneCheck™ kaynaklarını koruyarak EMÜS'ün yerel/ücretsiz gerçek görev kabul şartlarını makine testine çevrilebilir olarak tanımlamak.

## Gerçek kaynağa dayalı kritik düzeltme
- Ana depodaki `shared_ai/working_memory.py`: file-backed JSON + atomik `os.replace` + `fsync`.
- Mac Engineer v0.7 kabul matrisi: A01 1000 geçiş, A02 üç kesinti sınıfı x 10, A03 100 replay, A04 16 eşzamanlı contender, A05–A12 kaynak/kanıt/yetki eşikleri.
- A03/A04 mühendislik kanıt kaydı test beyanı ve CI kimlikleri içeriyor; EMÜS'e kendiliğinden aktarılmaz.
- SQLite yalnız seçilecek motorun gerçek kabul açığını kapattığı bağımsız testle gösterilirse yerel görev defteri backend adayıdır; mevcut güvenilir mekanizma korunur.

## Her özgün işin kabul alanları
`CONTROL_ID | TASK_ID | SOURCE_REPO | SOURCE_COMMIT | ACCEPTANCE_VERSION | REQUIRED_EVIDENCE | INDEPENDENT_VERIFIER | OWNER_AUTHORITY | EXECUTION_STATE | EVIDENCE_STATE | AUTHORITY_STATE | NEXT_ACTION`.
Her özgün şart bir kez sayılır. `DESIGN_PASS`, `EXECUTION_PASS`, `EVIDENCE_PASS`, `AUTHORITY_PASS` birbirine dönüşmez.

## GH-02 kabul kapıları (tasarım)
| ID | Koşul | Kabul kanıtı | Beklenen negatif sınama |
|---|---|---|---|
| G01 | Görev girişi ve yerel kapasite ölçümü | versioned task JSON + model/araç availability | bilinmeyen görev -> HOLD_CAPABILITY |
| G02 | Tek gerçek backend üzerinde durability | checkpoint+restart+duplicate ledger | crash üç sınırda; çift yan etki yok |
| G03 | Tek motor ve kaynak bütçesi | model lock + RSS/disk/süre raporu | kaynak taşması -> HOLD_RESOURCE |
| G04 | Tamamlanma doğrulama | output digest + test oracle + independent reviewer | kanıtsız PASS reddi |
| G05 | İnsan/yetki | authority snapshot + redacted audit | yetkisiz yan etki -> HOLD_AUTHORITY |
| G06 | Hafıza/köken | canonical provenance ve retention | çelişik kaynak -> HOLD_SOURCE |
| G07 | Gerçek görev benchmark | önceden SHA kilitli sabit test kümesi | sonradan test ayıklama reddi |
| G08 | Yerel kurulum | macOS preflight + rollback + lisans manifest | ücretli API zorunluluğu -> HOLD_COST |
| G09 | Upgrade | runtime/skill/model pin, LKG geri dönüş | farklı digest -> HOLD_VERSION |
| G10 | GitHub→OSi kabul kapısı | GH04 bağımsız CI + yetkili karar | eksik reviewer -> HOLD_REVIEW |

## Ölçüm ve kabul
- `TASK_SUCCESS` = önceden kilitli gerçek görev örneklerinde bağımsız doğrulanmış başarı / başlangıçta belirlenen toplam; HOLD güvenli sonuçtur, başarı değildir.
- `DURABILITY` = önceden kilitli kesinti/recovery/idempotency denemelerinde kabul / toplam.
- `SIMPLICITY` = tek varsayılan yürütme, açık bağımlılık, yeniden kurulabilirlik ve geri alma kabul seti / toplam.
- `RELIABILITY` = yetki, kaynak, çıktı/evidence ve idempotency kabul seti / toplam.
- `LOCAL_ZERO_PAID_API`: Mac OSi temel zorunlu görev kümesi ücretli API çağrısı olmadan çalışır; model lisansı ve model ağırlığı kaynağı kanıtlanır.
- 100/100 yalnız sabit kabul setinin tamamı, bağımsız doğrulama ve yetkili insan eşiği mevcutsa gerçek kabul değeridir.

## GH-02 → GH-03 kapısı
Bu sözleşme ADAY'dır. GH-01 tam kaynak eşleştirmesi, gerçek owner ve bağımsız reviewer, görev şeması, tehdit modeli, seçili runtime ve fixture/benchmark kaynağı kapanınca GH-02 PASS verilebilir. GH-03 kod farkı ancak bu kanıtla daralır.

## Sonuç
`GH02=PARTIAL_CONTRACT_DRAFT`; `GH01=HOLD`; `GH03=HOLD`; `GH04=HOLD`; `OSI_READY=HOLD`. Salt belge gerçek test, CI veya resmî DoneCheck yerine geçmez.

## 2026-10-23 — Kaynakla doğrulanmış dar kapsamlı uzlaştırma
- Özel ürün deposu `engurulabory/enguru-mac-engineer`, gözlenen `main` commit: `5432b9b135499cea18273c0e003877b864af92c6`. Bu commit'in yerel Mac OSi runtime ile tam eşitliği HOLD.
- `runtime/reliability.py` blob `ee0f53e4a1fb899aecd637f059ce840979bb02d4`: QUEUED/RUNNING/CHECKPOINTED/VERIFYING/COMPLETE/HOLD/FAILED/RECOVERY_REQUIRED/ROLLBACK_REQUIRED/BLOCKED durumları, belirli geçişler, retry_limit=2/max_attempts=3, `atomic_json` ve `WriterBusy` mevcut. Bu statik kaynak doğrulamasıdır; EMÜS test PASS değildir.
- `PROVENANCE.json` blob `302bd21f337e70396271421a40a42a91c1dcba74`: tarihi ürün kaynak kimlikleri ve SHA-256 kayıtları var. Dosyanın tarihsel değeri korunur; güncel Mac OSi durumuyla eşitlik kanıtı olarak kullanılmaz.
- Ana depo `governance/controller/ACTIVATION.json` blob `96b33c31197b0e70b64e21529b6fb069aad62ba7`: tek aktif görev, ilave ücret 0, insan nihai otoritesi OWNER. Bu kontrolün EMÜS'e otomatik resmî grant verdiği iddiası yoktur.
- G02 kesin uygulama seçimi: mevcut Mac Engineer reliability bileşeni ana aday; mevcut JSON görev hafızası ile görev kimliği/yan etki uygunluğu ölçülecek. Kanıtlanan açık dışında ikinci defter veya SQLite zorunluluğu tanımlanmaz.
- G05/G10: GitHub owner hesabı/rolleri ile gerçek DoneCheck issuer, reviewer ve imza grant ayrı düzeylerdir. EMÜS adına resmî signer/issuer yetkisi henüz HOLD.
- Kaynakların Git blob SHA-1 değerleri SHA-256 kilidi yerine geçmez. V3 talimatının GitHub'dan alınan UTF-8 içeriği SHA-256 ile yeniden hesaplandı ve kilitle eşleşti (`11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`); Mac OSi yerel kaynak eşitliği ayrı HOLD.
- GH-01 eksik: yönetim/İcra güncel canonical kaynak tam envanteri; V3 kilidi GitHub UTF-8 içeriği üzerinden PASS; owner/issuer/reviewer yetkisi ve gerçek cihaz runtime eşleştirmesi HOLD.

**Son kontrol kuralı:** Belge revizyonu sonrası yeniden fetch edilip yalnız bu ek bölümün bulunduğu, önceki G01–G10 ve GH-02→GH-03 HOLD kapılarının korunduğu doğrulanır.

## 2026-10-23 — İcra bağlantısı ve yetki hükmü
- Ürün deposu `engurulabory/enguru-mac-engineer` gözlenen main SHA: `5432b9b135499cea18273c0e003877b864af92c6`; `runtime/app.py` Git blob `e9f65981ee8b7b7daff0126f34d5fab778265f4c`. Yerel HTTP runtime, CockpitStore, RepoControl, `field_reliability`, `provider` ve yerel test bileşenlerine bağlıdır. Gerçek EMÜS görev doğrulaması yapılmadı.
- Ana depodaki `governance/mac-engineer/CAPABILITY_EXECUTION_BINDING_V1.json` Git blob `419bff0005109644938aae08b8e0b4421af8098b`: mevcut kayıtlı action'lar ve sınırlandırılmış izinler görünür; bu belge EMÜS'e yürütme yetkisi veya owner/issuer grant üretmez.
- EMÜS için kaynak kullanılabilirlik kararı: `SOURCE_CANDIDATE_CONFIRMED`, `CANONICAL_ACTIVE_RUNTIME_EQUIVALENCE=HOLD`, `EMUS_AUTHORITY_GRANT=HOLD`.
- Mühendislik kuralı: Mevcut mac-engineer görev akışı ve güvenilirlik bileşeni denenmeden yeni orkestrasyon, yeni kayıt motoru veya veritabanı kurulmaz. Dar kapsamlı kod farkı gerçek başarısız test kanıtı ile belirlenir.
- `GH01=PARTIAL`, `GH02=PARTIAL`, `GH03/04=HOLD`, `OSI_READY=HOLD`.

## 2026-10-23 — Görev kimliği ve DoneCheck yetki kapsamı
- DoneCheck `src/domain/donecheck/ids.ts` (blob `286d23c8977665d1dc7d29c83f80e62d92044788`) `TaskId` ve `VerificationResultId` için string sözleşmesi kullanır. Tek başına ürün adı/kimliği veya yetki grant'i tanımlamaz.
- DoneCheck `src/domain/donecheck/human-review.ts` (blob `2b106bf1cde33850ec1b3a130fe9e446857d5e5e`) `HumanReview` içinde `taskId`, `verificationResultId`, `decision`, `reviewerId`, `reviewedAt`, `reason` ve kayıt ID'sini bağlar.
- Minimum gerekli bağ: EMÜS'in yetkili görev ID'si → aynı `taskId` ile gerçek `VerificationResult` PASS → aynı `verificationResultId`'ye bağlı imzalı `HumanReview` → yetkili reviewer public key/grant → DoneCheck ledger ve Verified Finish receipt. Görev kimliği üretiminden önce mevcut canonical görev ID kaynağı uzlaştırılacaktır.
- EMÜS adına aktif canonical görev ID, imzalı reviewer grant/receipt ve OSi runtime denkliği bu incelemede doğrulanmadı. `TASK_ID_AUTHORITY=HOLD`, `REVIEWER_GRANT=HOLD`, `OSI_RUNTIME_EQUIVALENCE=HOLD`.
- Bu belge yalnız sözleşme ve kaynak eşleştirmesidir; gerçek görev yaratımı, imza, runtime kod değişimi, yetki devri veya bağımsız test gerçekleştirildiği iddiası yoktur.

## Kaynak incelemesi — görev kimliği sürekliliği (2026-10-23)
- Mac Engineer `runtime/tests/test_reliability.py` blob `5754324423a688a0c6d5a5ae8e512f238f510e71`: `test_persistent_idempotency` aynı idempotency anahtarını yeni `ReliabilityManager` örneğinde tekrar kullanıp aynı `task_id` bekler; `test_checkpoint_restart_resume` yeni manager ile checkpoint'ten devamı kontrol eder.
- Bu mevcut birim testleri EMÜS→WorkingMemory→DoneCheck bütünleşik görev kimliği eşitliğini tek başına kanıtlamaz.
- Kabul edilecek küçük test farkı: gerçek kaynak üzerinde tek görev kimliği ile tekrar/yeniden başlama ve DoneCheck TaskId eşitliği; kanıt yokken `TASK_ID_BINDING=HOLD_TEST`.
