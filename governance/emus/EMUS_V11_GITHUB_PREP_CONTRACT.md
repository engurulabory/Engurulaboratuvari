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
K02: SQLite görev defteri, checkpoint, idempotency, kurtarma ve tutarlı yan etki uzlaştırması.
K03: risk sınıflı yetki, en dar kapsam, audit ve Human Threshold™.

## G01–G10 tasarım denetimleri
- G01: görev yeterlilik ve model/araç kapasite kapısı; yetersiz görev `HOLD_CAPABILITY`.
- G02: SQLite/WAL, migration, atomiklik, checkpoint, restart, idempotency ve denetlenebilir geri kazanım.
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
6. SQLite/checkpoint/idempotency ve bağımsız kurtarma sözleşmesi.
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
- LOCK SHA256 metni: `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`; kaynak baytlarının ayrı SHA-256 doğrulaması sıradaki kanıt işi.
- `EMUS` code search default branch: 0 sonuç; bu tek başına yokluk kanıtı değildir.
- İlgili `tools/mac_engineer_control.py`, `tools/mac_engineer_local_donecheck.py` bulundu; güncel ürün/otorite kapsamı ayrıca doğrulanacak.
- Gerçek GH-01: PARTIAL; GH-02–04: HOLD; OSi: HOLD.

## GitHub kapsam sınırı
Bu dosya yalnız inceleme dalında bir hazırlık sözleşmesidir. `main` değişikliği, merge, resmî yetki ve Mac OSi kurulumu ayrıca kanıt/insan karar kapısına bağlıdır.
