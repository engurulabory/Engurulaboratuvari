# ENGÜRÜ Yönetim V6.9 — Kanıtlı Bütünleşik Bloklar V1.1

**23.10.2026 · ENGÜRÜ Süzgeci™ sekiz aşama · pozitif dil · tek ana hedef**

`ENGURU_MANAGEMENT_V69_PR_203 → VERIFIED_FINISH → BITTI_DUR`

Bu dosya, mevcut **G1–G6 ana iş listesinin uygulanabilir bloklara bağlanmış icra kaydıdır**. Canonical DoneCheck™ v1.2, owner/issuer, Human Threshold™ ve mevcut V3 SHA-256 kilidi aynı yetkiyle korunur. Yeni gate, issuer veya resmî ürün sayacı oluşmaz.

## Kabul edilmiş V1.2 çalışma yöntemi — Planla, puanla, terminali önceden sınayarak ilerle

**OWNER KARARI:** 23.10.2026 · Yönetim V6.9 için kullanıcı kabulü · sekiz aşamalı ENGÜRÜ Süzgeci™ içinde uygulanacak **icra öncesi alt yöntem**. Evrensel V3, sabit G1–G6 kabul şartları, mevcut DoneCheck™ ve Human Threshold™ yetkileri korunur. Planın kodla okunabilir sözleşmesi [plan.json](plan.json) içindeki `pre_execution_quality_loop` alanıdır.

**Bütünleşik tek döngü:**

1. **PLANLA:** Önümüzdeki gerçek işleri, özgün kontrol ID'lerini, bağımlılıkları, mevcut SHA ile kanıt durumunu ve yetkili kabul şartlarını birlikte belirle.
2. **PUANLA-1:** İlk planı 100 puanlık ölçekte somut gerekçe/kanıtla değerlendir: teknik doğruluk **20**, gerçek uygulanabilirlik **20**, güvenlik ve yetki **20**, sadelik **15**, dayanıklılık/toparlanma **10**, uçtan uca bitirme kapasitesi **15**.
3. **TERMİNAL GİBİ SİMÜLE ET:** Komut argümanları, mevcut dosya yolları, SHA, owner izinleri, OS koşulları, dönüş kodları, eksik dosya, sahte yetki, yanlış kapsam, zaman aşımı, tekrar çalıştırma, kısmi kayıt, toparlanma ve final makbuzunu gerçek uygulama öncesi karşıt sınamaya tabi tut. Bu aşamadaki dosya değişimleri **izole simülasyon** kapsamındadır.
4. **GÖR–TAMAMLA–DÜZELT:** Eksikleri, hataları, ihtiyaçları ve gereksinimleri sınıflandır; doğrulanmış kök nedenleri esas al; düzeltmeyi aynı plan ve kod içinde entegre et; önceki başarılı kanıtı koru.
5. **PUANLA-2 → SİMÜLASYON-2/3:** Düzeltmeleri gerekçeli olarak yeniden puanla, karşıt testleri tekrarla. Azami **3 puanlı simülasyon turu** vardır. Her tur sonunda `PLAN_SCORE`, `SIMULATION_SCORE`, `CRITICAL_BLOCKERS`, `NEXT_ACTION` ayrı raporlanır.
6. **GERÇEK İCRA → KANITLI KABUL:** Kritik iç hata çözülmüş, ilgili simülasyon doğrulayıcısı PASS olmuş ve saha yetkisi mevcutsa gerçek OSi/GitHub icrasına geç. Sahada `REAL_EXECUTION`, `INDEPENDENT_VERIFICATION`, `OWNER_AUTHORITY`, `DONECHECK` ve `VERIFIED_FINISH` ayrı kanıtlanır.

**Mühendislik sınırı 1 — Teori / simülasyon / saha ayrı:** `PLAN_SCORE=100/100` ve `SIMULATION_SCORE=100/100` yalnız sınanmış tasarım kapsamındaki hedeflerdir. Gerçek Mac izinleri, imzalı owner kabulü, canlı audit ledger, yetkili merge ve resmî `VERIFIED_FINISH` kendi doğrulayıcısından PASS aldıktan sonra kabul edilir. Sayaca simülasyondan resmî ilerleme aktarılmaz. Puanın 100 olması, çözülmemiş kritik yetki açığını telafi etmez.

**Mühendislik sınırı 2 — Sonlu düzeltme:** Simülasyon **en fazla 3 tur** sürer. Kritik **dış yetki/erişim bağımlılığı** daha erken ortaya çıkarsa `GUVENLI_DUR_EXTERNAL_AUTHORITY`; üçüncü tur sonrasında teknik eksik sürerse `HOLD_SIMULATION_LIMIT_REACHED`. Her iki durumda yalnız `EXACT_BLOCKER + REUSED_EVIDENCE + SINGLE_NEXT_AUTHORIZED_ACTION` verilir. Tekrar eden Mac kabul töreni ve anahtar üretimi ancak gerçek kaynak veya kapsam değişimiyle gerekçelendirilir.

**G2'de somut uygulama:** İki aşamalı bağımsız ROOT ve scoped-grant Ed25519 kriptografisi **PASS** (Mac raporu SHA `02c65bb7724e59d69f93be9bd0328392ed22dce85bd169b06e2b2647a13fb8d6`). Resmî G2 `HOLD_CANONICAL_ROOT_ADMISSION`: tek sonraki yetkili hareket mevcut canonical owner trust kaynağında sürümlü ROOT admission ve bağımsız yetki makbuzudur. Mühendislik Kası™ V3 öğrenme kaydı olayı `MK-EVT-G2-ROOT-ADMISSION-20261023` mevcut; danışman süreçtir ve G2 kabul otoritesi değildir.

**100/100 hedef kuralı:** Tasarım puanı, simülasyon puanı ve gerçek Verified Finish ayrı gösterilir. Kullanıcının onayladığı çalışma yöntemi tasarım sözleşmesine işlendi; 100/100 gerçek simülasyon veya canlı saha PASS iddiası, yalnız ölçülen sonuçlarla yazılır.

## Ana iş listesi — özgün altı kapı

| Kontrol | Yapılacak gerçek iş | Mevcut kanıtlı sonuç |
|---|---|---|
| **G1** | `ENGURU_MANAGEMENT_V69_PR_203` exact PR HEAD, GitHub bağımsız `verifyTask` 4/4 CI/kaynak/operasyon/sınır | **PASS_TECHNICAL_ONLY**; review run `39852715540`; HEAD `63fe22e7c1ce73adf94b0cbdd40924511e8211cd` |
| **G2** | Mac OSi'de mevcut Ed25519 signer özel anahtar kontrolü ve aynı `TASK_ID + VERIFICATION_RESULT_ID` için canonical kriptografik owner grant | **HOLD_REAL_OWNER_SCOPE_PROOF**; salt-okunur Mac source raporu `PASS`, owner grant/imza ayrıca gerekli |
| **G3** | Owner'ın gerçek `HumanReview.accepted` kararı, canonical Ed25519 detached attestation ve mevcut OSi DoneCheck köprüsü | **HOLD_REAL_SIGNED_HUMAN_REVIEW**; PR #14 gerçek macOS CI adaptör testleri 20/20 PASS, gerçek owner imzası bekliyor |
| **G4** | Mevcut DoneCheck `recordVerifiedFinish` receipt ve hash-zincirli audit ledger, pre-append ve kısmi append toparlanma kontrolü | **HOLD_CANONICAL_AUDIT**; izolasyon teknik testleri PASS, gerçek ledger ve makbuz bekliyor |
| **G5** | Owner yetkili PR #203 review/merge, gerçek güncel main/base uzlaştırması ve merge-sonrası exact-main CI | **HOLD_OWNER_MERGE**; bu planın oluşturulduğu `main` SHA `113d8ffd18a6f36c840770f30f38da6d5900aa43` |
| **G6** | G1–G5 bağımsız doğrulama, resmî Human Threshold ve DoneCheck makbuzuyla final | **HOLD_VERIFIED_FINISH** |

**Muhasebe:** G1 `1/6` teknik kapı başarı; G2–G6 `0/5` resmî kapanış. Tasarım/simülasyon puanları bu sayacı yükseltmez.

## Uygulanabilir blok sistemi

| Blok | Girdiler | Karar, işi ve durum |
|---|---|---|
| **B00 — Korunan tamamlanmış temel** | **G1** | 4/4 gerçek teknik sonuç `PASS_TECHNICAL_ONLY`. Aynı kaynak SHA korunur. Yeniden doğrulama yalnız kaynak değiştiğinde. |
| **B01 — Tek birleşik resmî bitiş** | **G2 + G3 + G4 + G5 + G6** | **TEK AKTİF ÜRÜN BLOĞU.** Owner signer/grant → HumanReview imzası → DoneCheck receipt ve audit → owner merge / exact-main CI → bağımsız Verified Finish. Şimdi **G2 real owner proof HOLD**. |
| **B02 — Canlı destek/öğrenme** | Mühendislik Kası™ V3, OSi blok–yanıt eşleştirmesi, regresyonlar, gerçek 5-dakika gözlemi | B01'i destekleyen paralel teknik nöbet. GitHub owner-event intake PASS; gerçek `schedule` koşusu **HOLD**; ChatGPT nöbeti saatlik. Yeni kanıtlar inceleme dalına izinli aktarılır. |
| **B03 — Bitiş sonrası sonraki işler** | Mevcut diğer ürünlerin kendi onaylı kaynak ve özgün iş listeleri | **BEKLEME.** Owner sonraki ürünün önceliğini Verified Finish sonrası belirler; PLive P01/P02, H1–H3, Website B1 gibi işler kendi sayaçlarıyla korunur. |

## B01 uygulanabilir tek paket: giriş / kanıt / kabul / finiş

**B01 giriş kontrolü:** Güncel `AGENTS.md`, V3 SHA-256 `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`, PR #203 HEAD, Mac Engineer PR #14 testleri, gerçek Mac OSi salt-okunur rapor SHA-256 `2e524438fc647b79d64e4f4bfa47424b8ae77c93a0af29b6649fca23208ae24`. Her yeni turda güncel main/branch okunur.

**Ortak yürütme:** `AUTHENTICATE_EXISTING_SIGNER → VERIFY_EXACT_TASK_RESULT_GRANT → SIGN_CANONICAL_HUMAN_REVIEW → VERIFY_DETACHED_ATTESTATION → CANONICAL_DONECHECK_LEDGER → RECONCILE_LEDGER_AFTER_INTERRUPTION → REFRESH_EXACT_CURRENT_MAIN_AND_REVIEW → AUTHORIZED_PR203_MERGE → POST_MERGE_EXACT_MAIN_CI → VERIFY_INDEPENDENT_DONECHECK_AND_HUMAN_THRESHOLD → INDEPENDENT_VERIFIED_FINISH`.

**Gerçek G2 bitiş ölçütü:** Sahipliği doğrulanmış *mevcut* Ed25519 özel anahtar; public PEM UTF-8 SHA ile eşleşen `keyId`; aynı task/result/reviewer/`accepted` yetkisini veren gerçek mevcut owner trust zinciri; bağımsız kriptografik doğrulama. Tarihsel Gate12 kaynakları, yeni V6.9 scope için kendi başlarına grant sayılmaz. Mevcut signer mekanizması açıklandığında private key yalnız Mac OSi'de kalır. Yeni yetki kaydı gerekirse ayrı owner onayı gerekir.

**G3–G4 bitiş ölçütü:** Owner'ın kabul imzası canonical payload üzerinde doğrulanır; ledger'ın önceki bütünlüğü kontrol edilir; mevcut DoneCheck v1.2 receipt ve ledger başı bağımsız teyit edilir. Yarım kalmış çift audit append durumunda önce existing chain / eventId reconciliation uygulanır.

**G5–G6 bitiş ölçütü:** Current-main diff/mergeability/bağımsız gözden geçirme ve owner merge yetkisi doğrulanır. Resmî merge sonrası yeni `main` exact SHA/CI doğrulanır; `VERIFIED_FINISH` yalnız gerçek DoneCheck ledger + yetkili Human Threshold kabulüyle ilan edilir.

**Tek fiilî sonraki hareket:** Mevcut Mac OSi Ed25519 ROOT ve grant kanıtlarıyla **G2 canonical ROOT admission için mevcut yetkili kaynak ve insan kabulünün resmî bağını** tamamlamak. Bu aşamada mevcut şifreli issuer anahtarı ve önceki saha kanıtları korunur; yeni yetki yazımı yalnız canonical owner mekanizmasının bağımsız kabulünden sonra gerçekleştirilir.

## Süzgeç ve kontrol disiplini

Hakikati gör: Güncel yetkili source/HEAD. Değeri koru: Orijinal kanıtlar, SHA, owner, main. İhtiyaçları tespit et: G2 ve bağımlı G3–G6. Gerekli farkı üret: B01 tek zincir, B02 öğrenme. Eksikleri tamamla: Erişilebilir teknik test, yerel owner yetkisinde kontrollü karar. Kanıtla: simülasyon, gerçek CI, gerçek Mac ve owner D ayrı. Sonraki ihtiyaç: B03 korunmuş portföy işleri. İlerlet: Özgün G2→G6 PASS kanıtı sonrasında `BITTI_DUR`.

**Toplu al → bütünsel değerlendir → önceden karşıt simüle et → gerçek icra → toplu kanıt → bağımsız ve owner kabulü.** Tek aktif ürün bloğu. Yeni kanıt ile ilerle; owner kaynağı erişimi/yetkisi gerektiğinde kesin `GÜVENLİ_DUR` + kaynak/durum + sonraki owner hareketi.

## Simülasyon · açık farklar · kapatılan kontroller

**İlk bağımsız tur:** `49/50 PASS`; negatif sıra değişimi testinin kendi `swap` yöntemi hatalıydı. Hata PASS sayılmadan iki indeksin önce kaydedildiği düzeltme uygulandı; tekrar `50/50 PASS`.

**Eksikler:** Owner/keyId/result/verifier kimliği eksik olma, gerçek yetki iddiası ile bağımsız doğrulama ayrımı, kısmi ledger toparlanması ve `main` güncelleme kapısı. **Gereksinimler:** Tek G2–G6 blok bağımlılığı, gerçek owner yetkisi, ürün SHA, B02 özel kaynak sınırı, G5/G6 bağımsız kabul. **Yanlış varsayımlar:** Simüle edilmiş geçerli şema resmî `PASS` değildir; `keyId` adı sahiplik değildir; G5 current-main eski kayıttan varsayılamaz. Bunlar testlere ve plan doğrulayıcısına işlendi.

**İkinci + üçüncü temiz subprocess simülasyonu:** `65/65 + 65/65 PASS`; ilk 50 senaryoya göre **%30 ek senaryo**. 25/25 adlandırılmış değerlendirme kontrolüyle **100/100 teorik iş-bloku tasarım kabulü**. Gerçek GitHub CI ayrıca kapatılır; `G2–G6 OFFICIAL=HOLD`.

## Devir ve kanıt sözleşmesi

`SOURCE=engurulabory/Engurulaboratuvari`; `PR203_HEAD=63fe22e7c1ce73adf94b0cbdd40924511e8211cd`; `TECHNICAL_G1=PASS`; `B01=HOLD_G2_OWNER_GRANT`; `B02=ACTIVE_PARTIAL_SCHEDULE_HOLD`; `B03=WAITING`; `PERMISSION=CANONICAL_OWNER/HUMAN_THRESHOLD`; `NEXT=G2_OWNER_SCOPE_CRYPTOGRAPHIC_PROOF`.

Bu planı yeni oturumda en güncel GitHub ve yaşayan Mühendislik Kası kayıtlarıyla tekrar karşılaştır. Tasarım puanı ayrı; gerçek uygulama, bağımsız kanıt ve yetkili kabul ayrı. Sonlandırma: `VERIFIED_FINISH → BITTI_DUR`.