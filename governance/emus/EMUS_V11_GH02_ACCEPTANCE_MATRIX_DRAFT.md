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

## 2026-10-23 — Gerçek CI kapsam ayrımı
- `dccdd9705aeab4a493e66150d5390b5ec9ddc60a` commit'ine bağlı GitHub workflow sonuçları: PARK Adapter CI `39985686137` success; IP Model Trust Fleet `39985686186` success; ENGURU Labory Final Gate `39985686480` success; IP Model Trust Gate `39985686182` success.
- `.github/workflows/labory-final-gate.yml` (blob `376b791dcdf0f9596fbdc2ddfadb43745960a423`) mevcut WorkingMemory birim testlerini çalıştırır; `test_emus_task_identity_probe.py` çağrısı içermez. Bu dört yeşil workflow EMÜS üçlü kimlik entegrasyon testinin PASS kanıtı değildir.
- `TASK_ID_BINDING=HOLD_TEST`; kaynak pin düzeltmesi GitHub dosya geri-okuması PASS. Sıradaki dar ihtiyaç: özel Mac Engineer runtime'ın sabit sürümü için yetkili ve tekrar üretilebilir koşu, test çıktısı ve bağımsız kontrol. Geçerli grant ve owner kabulü ayrı HOLD.

## 2026-10-23 — EMÜS CI sözdizimi gerçek çalışma kanıtı
- Commit `92daa4e538b3fa31e0f59a52cd18647dd1df202d`, GitHub `ENGURU Labory Final Gate` run `39991208795`, job `120543122620`: `EMUS task identity probe syntax (integration execution remains gated)` adımı GitHub API üzerinden `completed/success` doğrulandı.
- Aynı commit'te PARK Adapter CI `39991208529`, IP Model Trust Fleet `39991208536`, IP Model Trust Gate `39991208553` completed/success. Kapsam yalnız ilgili workflow adımlarıdır.
- Karar `EMUS_TEST_SYNTAX_CI=PASS`; `EMUS_TASK_ID_INTEGRATION=HOLD_TEST`; `EMUS_AUTHORITY=HOLD`. Başarılı sözdizimi adımı gerçek özel runtime entegrasyon testi değildir.

## 2026-10-23 — Güncel CI ve DoneCheck verifyTask giriş sınırı
- Commit `21db054067be4d3df38382e3bfd96a2bd9ab4ace`: ENGURU Labory Final Gate run `39991715950`, job `120544847391`, EMUS sözdizimi adımı `completed/success`. Aynı commit PARK Adapter `39991715667`, IP Model Trust Fleet `39991715710`, IP Model Trust Gate `39991715741` `completed/success`.
- DoneCheck `src/domain/donecheck/verification-engine.ts` blob `e7c8d97f8adaec07742e1f9cd1c9e9fc026cc73e` `verifyTask` girdileri: `task`, `criteria`, `aiOutput`, `evidence`, `resultId`, `verifiedAt`, opsiyonel `policy`. Kaynakta `trustedProducerIds` allowlist'inin kriptografik kimlik doğrulaması olmadığı açıkça belirtilir.
- Mevcut Python EMUS probe `DoneCheck TaskId` için string eşitliği kontrol eder; TypeScript `verifyTask` çağırmaz. Doğru sonraki fark, iki ürünün source-pinned ortamında gerçek `verifyTask` fixture çalıştırılması ve sonuç/evidence kimliklerini karşılaştırmaktır; reviewer imzası ve issuer/owner yetkisi ayrı HOLD.
- Hüküm: `EMUS_SYNTAX_CI=PASS`, `EMUS_VERIFYTASK_EXECUTION=HOLD_TEST`, `EMUS_OWNER_REVIEWER_ISSUER=HOLD`, `GH01/GH02/GH03=PARTIAL`, `GH04/OSI_READY=HOLD`.

## GH-03 güvenli duruş CI kanıtı — 2026-10-23
- Commit `e34bd9aedf07f968518458d2b01c82752ced4906`; Final Gate run `39993766974`, job `120551868991`: EMÜS sözdizimi step 9 ve `SOURCE_HOLD` negatif testi step 10, her ikisi `completed/success`.
- Karar: `SOURCE_MISSING_FAIL_CLOSED=PASS_CI`. Özel runtime görev kimliği entegrasyonu, DoneCheck verifyTask ve resmî owner/reviewer/issuer yetkisi ayrı `HOLD`.

## GH-03 — Kaynak kayması negatif test CI kanıtı (2026-10-23)
- Commit `a318c3013c6264b5412ed896738fcf447be3c973`; Labory Final Gate run `39994167178`, job `120553255924`: EMÜS sözdizimi step 9, eksik özel runtime güvenli duruş step 10, farklı SHA kaynak yüklemeden duruş step 11; üçü de `completed/success`.
- Aynı commit'in genel CI koşuları: PARK `39994167063`, IP Model Trust Fleet `39994167246`, IP Model Trust Gate `39994167137` `completed/success`.
- Kesin hüküm: `EMUS_SOURCE_MISSING_FAIL_CLOSED=PASS_CI`; `EMUS_SOURCE_DRIFT_FAIL_CLOSED=PASS_CI`; `EMUS_REAL_TASK_ID_BINDING=HOLD_TEST`; `EMUS_DONECHECK_VERIFYTASK=HOLD_TEST`; `EMUS_AUTHORITY=HOLD`. Test sonucu emniyet kontrollerine aittir, ürün Verified Finish değildir.

## GH-03 — Son negatif test düzeltmesinin CI kabulü (2026-10-23)
- Commit `fbad5b0483a3405460be4597679d5c20eaa9578b`; ENGURU Labory Final Gate run `39994481444`, job `120554326429`: syntax step 9, missing-private-runtime step 10, source-drift-before-import step 11, her üçü `completed/success`.
- Diğer workflow'lar PARK `39994481593`, IP Model Trust Fleet `39994481423`, IP Model Trust Gate `39994481600` `completed/success`.
- Product CI `engurulabory/enguru-mac-engineer/.github/workflows/product-ci.yml` bağımsız özel ürün test yüzeyidir; Labory CI içine özel ürün kaynağı getiren mevcut yetkili grant bu incelemede doğrulanmadı.
- Son hüküm: `NEGATIVE_GUARDS=PASS_CI`; `REAL_TASK_ID_RESTART=HOLD_TEST`; `DONECHECK_VERIFYTASK=HOLD_TEST`; `AUTHORITY=HOLD`. Sıradaki kabul, yetkili özel runtime çalışma kanıtıdır.

## GH-03 — Doğrudan yükleyici güvenliği gerçek CI kanıtı
- Commit `6b8007928551a93ef2325ec22eddb0e11fa417ec`; Final Gate run `40000254150`, job `120574187904`, EMÜS step 9 (syntax), step 10 (SOURCE_HOLD), step 11 (SOURCE_DRIFT + loader never called): üçü `completed/success`.
- Aynı commit PARK `40000254047`, IP Model Trust Fleet `40000253991`, IP Model Trust Gate `40000254356` completed/success.
- `GH03_NEGATIVE_GUARDS=PASS_CI`; gerçek özel Mac Engineer runtime ile `test_task_id_survives_two_stores_and_restart` bu CI'da çalıştırılmadı. `EMUS_TASK_ID_INTEGRATION=HOLD_TEST`, `DONECHECK_VERIFYTASK=HOLD_TEST`, `GH04=HOLD`. 19 ana işin kabul sayacı kanıtlı bağımsız tamamlanma kararı olmadan yükseltilmez.

## 2026-10-23 — Gerçek P1→DoneCheck verifyTask birleşik CI kanıtı
- Özel Mac Engineer PR #17 commit `72856598e97f3d8c76aaa5b3ecbccd9376f07e6b`: GitHub Product CI run `40008569258`, job `120602706459`, `completed/success`.
- Aynı job içinde pinned Labory checkout, gerçek iki-depo TaskId/checkpoint/restart testi, pinned DoneCheck checkout, gerçek P1 artifact'iyle `verifyTask` testi ve artifact yayın adımları `success`.
- Artifact: `emus-p1-task-identity`, artifact ID `12525586560`, `expired=false` (sınırlı saklama süresi); DoneCheck testinde PASS/FAIL/inconclusive karşıt sınamalar çalışır.
- Kesin kapsam: `P1_REAL_TWO_STORE_CI=PASS`; `P1_TO_DONECHECK_VERIFYTASK_TEST=PASS_CI`. Bunlar test verisiyle makine doğrulamasıdır; yetkili human review/owner/issuer/ledger ve GH-04 resmî kabul `HOLD`.

## Blok 3 — G04/G09 ilk 24 gerçek karşıt test (2026-10-23)
- Mac Engineer özel PR #17 commit `75230a82dd2f609c8bfaa5cd969691033c9202f5`; CI run `40010446918`, job `120609147504`.
- `EMUS G04 G09 24 adversarial P1 artifact integrity tests` adımı `completed/success`: gerçek P1 görev kimliği artifact'i üzerinde 24 ayrı alan/kimlik/checkpoint/commit/otorite bozma mutasyonu.
- Aynı run P1 pinned iki-defter restart testi `completed/success`; workflow'un bütününün nihai kararı bu kayıt anında `in_progress`.
- Kapsam yalnız `G04_EVIDENCE_INTEGRITY` ve `G09_SOURCE_PIN_INTEGRITY` alt testleridir. Yerel model yeteneği (G01/G03), macOS Skill (G08/G09), güven ve insan eşikleri (G05), gerçek benchmark (G07), diğer G01–G10 fonksiyonel ve bütün ürün kapsamındaki özgün #15 karşıt senaryolar `HOLD`.
- Kanıtlı test kapsamı ile özgün #14/#15 ana işlerin resmî kabulü ayrı tutulur; `GITHUB_19_ACCEPTED=0` değişmez.
