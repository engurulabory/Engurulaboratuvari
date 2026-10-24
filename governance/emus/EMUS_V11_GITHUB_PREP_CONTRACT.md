# EMÜS V1.1 — GitHub Hazırlığı ve Kanıtlı Geçiş Sözleşmesi
Tarih: 2026-10-23
STATE: GH_IN_PROGRESS / DESIGN_THEORETICAL_100_100 / FIELD_HOLD
SOURCE_MAIN_COMMIT: 113d8ffd18a6f36c840770f30f38da6d5900aa43

## Kalıcı sabit hedef
ENGÜRÜ Maya Üretim Sistemi™ (EMÜS), Mac OSi içinde ücretsiz ve yerel-öncelikli çalışacak. Zorunlu ücretli API bağımlılığı 0. Tanımlı gerçek görev, dayanıklılık, sadelik ve güvenilirlik kabul testlerinin tamamı PASS hedeflenir. Teorik kapsam puanı gerçek görev başarı yüzdesi sayılmaz.

## Canonical ilkeler
- Mevcut ENGÜRÜ Yönetim + İcra + Mac Engineer™ çekirdeği, ENGÜRÜ Süzgeci™ sekiz aşaması, DoneCheck™ ve Human Threshold™ korunur.
- `AGENTS.md` ve `governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md` başlangıç kaynağıdır.
- `governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json` dosyasındaki kaynak SHA-256 kilidi değişmez; yürütmede yeniden doğrulanır.
- Mevcut yetenekler yeniden kullanılır; yeni çekirdek/otorite ancak özgün canonical karar ve yetkiyle değerlendirilir.
- Tasarım, gerçek yürütme, kanıt, bağımsız doğrulama ve yetkili kabul ayrı muhasebeleştirilir.
- Her özgün kontrol yalnız bir kez sayılır. Her açık şart `HOLD`, erişilebilir gerçek engel `BLOCKED` olarak açıklanır.

## Korunan kazanımlar
K01: çok araçlı insan yönlendirmeli icra, görev sürekliliği.
K02: mevcut kalıcı görev defterini, checkpoint, idempotency, kurtarma ve yan etki uzlaştırmasını koru; SQLite yalnız gerçek eksik bağımsız kanıtla doğrulanırsa adaydır.
K03: risk sınıflı yetki, en dar kapsam, audit ve Human Threshold™.

## G01–G10 tasarım denetimleri
- G01: görev yeterlilik ve model/araç kapasite kapısı; yetersiz görev `HOLD_CAPABILITY`.
- G02: mevcut JSON tabanlı görev belleği ile Mac Engineer kalıcı görev mekanizmalarını önce bağımsız karşılaştır; atomiklik, checkpoint, restart, idempotency ve kurtarma testleriyle gerekli backend farkını kanıtla.
- G03: tek varsayılan yerel model çalıştırıcı; RAM/disk/süre bütçesi ve gereksinim bazlı bağımlılık.
- G04: görev bazında beklenen çıktı, kanıt, gerçek test ve bağımsız doğrulama sözleşmesi.
- G05: veri, sır, dosya ve ağ yetkisi; yan etki öncesi Human Threshold™ kapısı.
- G06: canonical öncelikli kaynak kökeni, çelişki çözümü, saklama ve silme.
- G07: önceden sabitlenen, sonuç sonrası daraltılamayan gerçek görev benchmark'ı; başarı, hız, kaynak ve maliyet ölçümü.
- G08: manifest/lock, lisans uyumu, preflight, dry-run, geri dönüş ve cihazı koruma.
- G09: model/Skill/görev sürüm sabitleme, güvenli yükseltme, rollback ve audit bütünlüğü.
- G10: GitHub kanıtlı bitiş → ayrı Mac OSi preflight → gerçek saha → bağımsız yetkili kapanış.

## Birleşik ana iş listesi — 6 blok / 28 iş
### GH-01 (4)
1. Güncel `main` SHA + yetkili kaynak ve V3 kilidini doğrula.
2. ENGÜRÜ Yönetim, İcra, Mac Engineer™, Süzgeç ve DoneCheck mevcut kaynaklarını envantere al.
3. K01–K03, G01–G10: `EXISTS / PARTIAL / MISSING / UNKNOWN` eşleştirmesi ve dosya+commit kanıtı.
4. Gerçek `GAP_MATRIX` ve bağımlılık sırasını kilitli sürüm olarak hazırla.
### GH-02 (5)
5. Görev şeması, durum makinesi, kabul kriterleri.
6. Mevcut kalıcı kayıt/checkpoint/idempotency ve bağımsız kurtarma sözleşmesi; SQLite için kanıtlı gereksinim kapısı.
7. Model/RAM/disk/süre ve tek çekirdek bütçesi.
8. Yetki/tehdit modeli/kanıt kökeni ve insan eşikleri.
9. Gerçek görev benchmark'ı, lisans ve sıfır ücretli API sözleşmesi.
### GH-03 (5)
10. Mevcut çekirdeğe gerekli kod farkını uygula.
11. Yerel model/araç adaptörleri.
12. Dayanıklı görev defteri ve restart recovery.
13. Skill zinciri, görev sürekliliği, macOS rutinleri.
14. G01–G10 gerçek birim/entegrasyon/karşıt testleri.
### GH-04 (5)
15. 24 karşıt senaryoyu otomatik gerçek testlere dönüştür.
16. CI, lock, kaynak ve yeniden üretilebilirliği denetle.
17. Bağımsız reviewer incelemesi.
18. DoneCheck™, owner/issuer authority ve kanıt defteri uzlaştırması.
19. Yetkili GitHub hazırlık kapanışı.
### OSi-01 (4)
20. Mac M5 Pro/24 GB preflight.
21. Yerel ücretsiz model ve lisans/maliyet doğrulaması.
22. Mevcut OSi yapıları korunarak atomik yerel kurulum.
23. Kaynak, izin, digest ve rollback testleri.
### OSi-02 (5)
24. Önceden sabitlenen gerçek görev benchmark'ı.
25. Dayanıklılık, sadelik, güvenilirlik, maliyet ölçümü.
26. Erişilebilir kusurların giderilmesi ve tekrar gerçek test.
27. Bağımsız doğrulama ve Human Threshold™.
28. Yetkili DoneCheck™ ve `VERIFIED_FINISH → BITTI_DUR`.

## Kabul/kanıt muhasebesi
Her işte: `TASK_ID, CONTROL_ID, SOURCE_REF, SOURCE_SHA, REQUIREMENT, PASS_CONDITION, EVIDENCE_URL, TEST_RESULT, VERIFIER, AUTHORITY, STATE, NEXT_ACTION`.
`GH_PREP=PASS` ancak 1–19 için zorunlu gerçek kanıt, CI, bağımsız inceleme ve yetki tam ise.
`OSI_READY=PASS` ancak GH-04 PASS ve ayrı 3–5 karşıt hazır oluş simülasyonu (kaynak/bağımlılık; lisans/kaynak; kurulum/rollback; güvenlik/yetki; benchmark/kabul) tamam ve blok girişleri doğrulanmışsa.
`VERIFIED_FINISH=PASS` ancak OSi'de 20–28 gerçek test ve yetkili kabul tam ise.

## GH-01 ilk gözlemler — bağımsız saha kabulü değildir
- Repo: `engurulabory/Engurulaboratuvari`, default `main`.
- Okunan `AGENTS.md` Git blob SHA: `0a08f2e4202bbf240760cb0abd30e6a826531688`.
- Okunan V3 kaynağı blob SHA: `7f47f3c6d3ee5c5138e53b67ae46cced37cb1a61` (lock içindeki blob ile eşleşiyor).
- LOCK SHA-256 beyanı (bayt düzeyinde doğrulama HOLD): `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`; kaynak baytlarının ayrı SHA-256 doğrulaması sıradaki kanıt işi.
- `EMUS` code search default branch: 0 sonuç; bu tek başına yokluk kanıtı değildir.
- İlgili `tools/mac_engineer_control.py`, `tools/mac_engineer_local_donecheck.py` bulundu; güncel ürün/otorite kapsamı ayrıca doğrulanacak.
- Gerçek GH-01: PARTIAL; GH-02–04: HOLD; OSi: HOLD.

## GitHub kapsam sınırı
Bu dosya yalnız inceleme dalında bir hazırlık sözleşmesidir. `main` değişikliği, merge, resmî yetki ve Mac OSi kurulumu ayrıca kanıt/insan karar kapısına bağlıdır.

## Tek bütünleşik 19 işlik GitHub icra paketi — 2026-10-23
Paket: EMUS_V11_GITHUB_19_INTEGRATED_REVIEW; kaynak: PR #210. PASS yalnız tam test, kanıt ve ilgili yetkili kabul sonrası yazılır. OPEN/PARTIAL değerleri mevcut kanıtın sınırıdır.

| İş | Gerekli çalışma | Kanıt hükmü |
|---:|---|---|
| 1 | Main, kaynak ve V3 kilidi | PARTIAL |
| 2 | Beş çekirdek envanteri | PARTIAL |
| 3 | K01–K03 / G01–G10 kaynak haritası | PARTIAL |
| 4 | Gap matrisi ve bağımlılık kilidi | PARTIAL |
| 5 | Görev şeması ve durum makinesi | PARTIAL |
| 6 | Defter, checkpoint, idempotency, recovery | PARTIAL |
| 7 | Tek model ve kaynak bütçesi | PARTIAL |
| 8 | Yetki, tehdit, köken ve insan eşikleri | PARTIAL |
| 9 | Benchmark, lisans, ücretsiz API | PARTIAL |
| 10 | Kanıtlı çekirdek kod farkı | PARTIAL |
| 11 | Yerel model ve araç adaptörleri | OPEN |
| 12 | Dayanıklı defter ve restart | PARTIAL |
| 13 | Skill zinciri ve macOS rutinleri | OPEN |
| 14 | G01–G10 birim/entegrasyon/karşıt testleri | PARTIAL |
| 15 | 24 gerçek karşıt senaryo | OPEN |
| 16 | CI, lock ve yeniden üretilebilirlik | PARTIAL |
| 17 | Bağımsız reviewer | OPEN |
| 18 | DoneCheck, owner, issuer, ledger | OPEN |
| 19 | Yetkili GitHub kapanışı | OPEN |

Bütünleşik kabul bağımlılıkları: canonical kaynak SHA ve yetki → Mac Engineer/WorkingMemory kaynak-pinned görev kimliği ve restart gerçek testi → DoneCheck verifyTask gerçek sonucu → G01–G10 ve 24 adversarial senaryo → CI/lock → bağımsız reviewer → owner/issuer/ledger → yetkili GH-04 kabulü.

Negatif koruma testleri Labory CI üzerinde PASS; özel Mac Engineer testleri tarihsel Product CI ile kanıtlandı. Bunlar birleşik entegrasyon, 24 adversarial senaryo ve insan yetkisi yerine sayılmaz. Eksik herhangi bir zorunlu kanıt için iş OPEN veya PARTIAL kalır. GITHUB_VERIFIED_FINISH=HOLD.

## Altı açık iş — üç turlu karşıt değerlendirme (2026-10-23)
Kapsam: #11 yerel adaptör, #13 Skill/macOS, #15 24 karşıt vaka, #17 reviewer, #18 DoneCheck/owner/issuer/ledger, #19 GitHub kapanışı. Puanlama: her iş için zorunlu test, kanıt ve yetki birlikte PASS ise 1, aksi halde 0; bu altı işin kapanışı 6/6 = 100/100.

| Tur | Değerlendirme | Sonuç / puan |
|---|---|---|
| 1 — İşlevsel simülasyon (mantıksal) | #11 gerçek yerel adaptör testi, #13 gerçek Skill/macOS testleri ve #15 tam 24 adversarial koşu kanıtı arandı | 0/6 kapanış = 0/100; üç teknik iş OPEN |
| 2 — Karşıt güvenlik simülasyonu (mantıksal) | Özel Mac Engineer kaynağı, sürüm kilidi, görev kimliği, yanlış SHA ve kanıtsız erken PASS senaryoları kontrol edildi | 0/6 kapanış = 0/100; Labory negatif CI kanıtları PASS, yeni final-PASS negatif testi CI sonucu bekliyor |
| 3 — Yetki/kapanış simülasyonu (mantıksal) | #17 bağımsız reviewer, #18 gerçek DoneCheck verifyTask + owner/issuer/ledger ve #19 tüm bağımlılıklar kontrol edildi | 0/6 kapanış = 0/100; yetkili kabul HOLD |

Bu puanlar 6 açık işin **resmî tamamlanma skorudur**; kod kalitesi veya teorik tasarım skoru değildir. Üç mantıksal simülasyon gerçek test, özel ürün grant'i veya insan kabulü oluşturmaz. Yeni WorkingMemory checkpoint ve authority testi Labory CI run `40000613508` job `120575404073` step 10 completed/success; dört workflow success. Kanıtsız final-PASS reddi testi commits `ec297f8c01e092dc22224577f27517630576566e` ve `257a4d95c650aa97e6306461f362e2e0f9199875` ile CI'ye eklendi; sonucu ayrıca doğrulanacak.

Karar: `SIX_OPEN=6`; `SIX_ACCEPTED=0`; `GITHUB_19_ACCEPTED=0`; `GITHUB_VERIFIED_FINISH=HOLD`. Kalıcı sabit hedef tüm 19 iş için gerçek Verified Finish.

## P1–P4 planı — çift simülasyonla düzeltilmiş bütünleşik yürütme

Kapsam: üstteki GH-01→GH-04 **19 özgün iş** korunur; P0–P4 adları yalnız aynı işlerin geçiş kapılarıdır, yeni iş veya yeni core değildir. Bu bölüm P1–P4 sıralamasının yürütme düzeltmesidir. Paket kimliği EMUS_V11_GITHUB_19_INTEGRATED_REVIEW; yetkili bitiş hala HOLD.

### Kanıtlanmış gereksinim ve düzeltmeler

1. Önceki P3'te bırakılmış **kaynak/commit SHA, özel depo okuma yetkisi, V3 kilidi, G01–G10 kabul kriterleri ve 24 karşıt senaryo sürüm kilidi**, P1/P2'den **önce giriş kapısı** olarak doğrulanır. P3'te bunların bağımsız yeniden uzlaştırması yapılır.
2. Mac Engineer özel ürün kaynağı Labory public dalına kopyalanmaz. Yetkili kaynak erişimi için mevcut ürün sahibinin grant kapsamı gerekir; bu grant görülene kadar iki-depo gerçek test HOLD.
3. Çalıştırma sırası: **P0 kaynak/ölçüt preflight (#1–5, #8, #9) → P1 gerçek çekirdek/yerel adaptör/Skill entegrasyonu (#6, #10–13) → P2 benchmark/G01–G10/24 adversarial gerçek CI (#7, #9, #14–16) → P3 19 satırın bağımsız kanıt uzlaştırması → P4 reviewer (#17), DoneCheck verifyTask + owner/issuer/ledger (#18), yetkili kapanış (#19)**.
4. DoneCheck verifyTask'ın makine doğrulama sonucu, bağımsız reviewer'ın kararı, owner/issuer yetkisi, imza ve resmî ledger ayrı çıktılardır. Bir PASS diğerine yetki sağlamaz.
5. Her ana işin kapanış kaydı: TASK_ID, SOURCE_COMMIT/SHA, ACCEPTANCE_CRITERIA, EXECUTION_RUN, RAW_RESULT, NEGATIVE_CASE, VERIFIER, AUTHORITY ve STATE. Kayıt eksikse o iş PARTIAL/HOLD; resmi tamamlanma sayaç artışı 0.
6. Model bütçesi ve 0 ücretli API, 24 karşıt testin **önceden tanımlı ve dondurulmuş** kapsamı, macOS yürütmesi ve rollback ölçülebilir koşullar olarak kalır. Simülasyon saha testi yerine geçmez.

### İki tekrar karşıt simülasyon — plan tasarım puanı

Puanlama şeffaf: 10 plan denetimi, her biri 10 puan. Denetimler: (A) 19/19 kapsam, (B) kaynak önkoşulu, (C) özel depo yetkisi, (D) bağımlılık sırası, (E) gerçek çift-kaynak testi, (F) benchmark kilidi, (G) 24 adversarial senaryo, (H) güvenlik/kaynak bütçesi, (I) bağımsız reviewer/issuer ayrımı, (J) gerçek kapanış ve erken-PASS koruması. Her madde plan üzerinde eksiksiz açık ise 10; eksikse 0. **Bu rakamlar yalnız plan mantıksal denetimidir; GitHub icra başarısı değildir.**

| Simülasyon | Karşıt giriş | Bulunan açık | Plan puanı |
|---|---|---|---|
| 1 — ilk P1→P4 taslağı | Özel repo yetkisi yok, kaynak SHA değişmiş, test eşiği belirsiz | Kaynak denetimi P3'e gecikiyor; test kapsamı ve yetki önkoşulları geç yazılmış | 60/100 (A,E,F,G,I,J) |
| 2 — düzeltilmiş kapılar | Yetkisiz checkout, 24 vaka kapsam kayması, sahte verifyTask PASS, geçmiş CI'nin yeni commit diye sayılması | P0 kaynak/grant, önceden kilitli benchmark ve ayrı resmî kabul şartlarıyla bu mantıksal açıklar kapandı | 100/100 plan mantığı |
| 3 — yeniden karşıt doğrulama | Görev kimliği iki depoda farklı; CI yeşil fakat gerçek entegrasyon yok; reviewer imzası yok | Bu hallerin her biri HOLD olarak tanımlı; ana 19/19 sayacı yükselmiyor | 100/100 plan mantığı |

**Yürütme hükmü:** `PLAN_LOGIC=100_100_SIMULATED`; `REAL_GITHUB_ACCEPTANCE=0_19` (iş bazlı bağımsız kapanış henüz yok); `GH_INTEGRATION=HOLD_TEST`; `OWNER_ISSUER_REVIEWER=HOLD`. Bu bölüm hiçbir resmî kabul veya Mac OSi saha PASS iddia etmez.

**Sonraki somut icra:** P0 giriş kanıtlarını güncel HEAD ve mevcut gerçek yetkiyle pinle; özel ürünün yetkili checkout'u doğrulanırsa P1 çift-kaynak gerçek testi çalıştır. P2 ve P4 yalnız bağımlı PASS kanıtıyla kapanır.
