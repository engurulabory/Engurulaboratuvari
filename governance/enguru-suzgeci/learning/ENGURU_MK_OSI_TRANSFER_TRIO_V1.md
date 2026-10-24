# ENGÜRÜ Mühendislik Kası™ — OSi Transfer Üçlü İyileştirme V1

## Kalıcı sabit hedef

**Yalnız aktarım ve öğrenme disiplini:** GitHub'da ayrı oturumlarda bitirilecek Yönetim ve İcra motorlarının gerçek Mac OSi aktarımını güvenilir kılmak. ENGÜRÜ Süzgeci™ v2.4 sekiz aşama, P01-C/D/E/F/G, Human Threshold™, DoneCheck™ v1.2, mevcut issuer ve audit ledger tek yetkili kaynak olmaya devam eder. Yeni ayrı çekirdek, bağımsız imzalayıcı, zamanlayıcı, yetki veya yeni ürün kabulü oluşturulmaz.

## Bütünleşik 3 kazanım

**A. Sahaya giriş / ön kontrol:** `preflight`, paket ve gerçek uygulama dosyası için değişmez SHA-256, symlink/size sınırı, görünür Product Operator (`poStatusBlock` + `poTechnicalDetails`) işaretçileri, Python/Node sürüm politikası, Node TAP raporlayıcı şartı ve owner etkileşim süre bütçesini *salt okunur* değerlendirir. Bu test `http://localhost` yanıtını veya görünür WebView render'ını doğrulamaz; canlı HTTP ve gözle görünür yüzey aynı kabul aşamasında ayrıca kanıtlanır. Salt-okunur PASS sahada kurulum PASS'i değildir.

**B. Gerçek hata → regresyon adayı:** `learn`, tek görev için (`ENGURU_MANAGEMENT_V69_PR_203`) mevcut Mühendislik Kası `enguru_muhendislik_kasi.parse_event` sözleşmesini kullanır; özgün hata kanıtının **gerçek dosya bayt SHA'sını** kontrol eder, `TASK_ID` + `BLOCK_ID`, `failureClass`, gerekçeli öneri, tekrar edilebilir olay kimliği, gizli içerik ve özel depo sınırlarını uygular. Owner izniyle yayımlanabilecek **yerel inceleme adayı** oluşturur. Otomatik GitHub yorumu veya yaşayan kayıt/main yazımı 0; bağımsız doğrulama ve kod testleri sonrasında mevcut öğrenme inceleme dalına alınabilir. `causeStatus=CONFIRMED` ancak bağımsız gerçek yetkili kanıttan sonra yönetilir; bu yardımcı araç bu kararı vermez. Başka task ID'leri mevcut canonical kapsamları yayımlandığında ayrıca entegre edilecek; bu sürümün bounded learning görevi V6.9'dur.

**C. Gerçek P01–P06 verimlilik ölçümü:** `metrics`, baseline/after özgün saha gözlem dosyalarının bayt SHA'sını, task/observation ID ve faz eşleşmesini kontrol eder. P01 medyan manuel adım, P02 tekrarlanan teşhis, P03 erken bitiş, P04 medyan onarım dakikası, P05 gerçek schedule aralıkları, P06 doğrulanmış kapı sayısı **girdi gözlemi** olarak karşılaştırılır. Sadece kaynak baytının SHA'sı gerçek olayın bağımsız doğrulanması değildir; **etkinlik kazanımı resmî iddiası HOLD**. Mevcut Mühendislik Kası V3 P01–P06 tanımları aynen korunur.

## Kullanım

Dosya `ENGURU_MK_OSI_TRANSFER_TRIO_FIELD_V1.zip` Downloads içinde bulunduğunda:

```bash
python3 -B "$HOME/Downloads/ENGURU_MK_OSI_TRANSFER_TRIO_FIELD_V1.zip" --self-test
python3 -B "$HOME/Downloads/ENGURU_MK_OSI_TRANSFER_TRIO_FIELD_V1.zip" --preflight --input "$HOME/osi-preflight.json" --output "$HOME/Desktop/AudiV13/osi-preflight-result.json"
python3 -B "$HOME/Downloads/ENGURU_MK_OSI_TRANSFER_TRIO_FIELD_V1.zip" --learn --input "$HOME/osi-learning-field.json" --output "$HOME/Desktop/AudiV13/osi-learning-candidate.json"
python3 -B "$HOME/Downloads/ENGURU_MK_OSI_TRANSFER_TRIO_FIELD_V1.zip" --metrics --input "$HOME/osi-metrics-input.json" --output "$HOME/Desktop/AudiV13/osi-metrics-result.json"
```

`--learn` için Mac'in mevcut `~/Enguru/Projects/Engurulaboratuvari/tools/enguru_muhendislik_kasi.py` canonical kaynak kopyası zorunludur ve mevcut GitHub blob `4111e7cff3f71039251fd03e0bfda9642c8612de` eşleşmelidir; source drift halinde `HOLD`. Bu kaynak ana ürün izleme dosyasını, Mac imza/ledger kayıtlarını veya özel anahtarları değiştirmez.

### A şeması (çalıştırmadan önce gerçek yollar ve SHA'larla doldurulacak)

```json
{
 "schema":"enguru.mk.osi-preflight/v1",
 "taskId":"ENGURU_MANAGEMENT_V69_PR_203",
 "sources":[{"role":"ui","path":"/Users/OWNER/Enguru/Runtime/MacEngineer/runtime/static/index.html","sha256":"REAL_64_HEX_SHA256","requiredMarkers":["poStatusBlock","poTechnicalDetails"]}],
 "runtime":{"pythonMinMajor":3,"nodeMinMajor":22,"nodeExpectedMajor":26,"nodeTestReporter":"tap"},
 "interactive":{"ownerConsentRequired":true,"timeoutSeconds":3600}
}
```

Özgün kaynakları yedekli tut; oluşacak çıktı yolu yeni olmalı (exclusive create). Kullanıcının Mac'indeki gerçek Python ve Node sürüm eşikleriyle hizalan; PHP/npm vb yeni bağımlılıklar kurulmaz. Gerçek UI ve HTTP testi ayrıca gerçekleştirilir.

### B şeması

```json
{
 "schema":"enguru.mk.osi-learn/v1","taskId":"ENGURU_MANAGEMENT_V69_PR_203",
 "blockId":"OSIBLOCK-20261024-ABCDEF","failureClass":"RUNTIME_DRIFT","causeStatus":"HYPOTHESIS",
 "sourcePath":"/Users/OWNER/Desktop/AudiV13/PUBLIC_REDACTED_EVIDENCE.json","sourceSha256":"REAL_64_HEX_SHA256",
 "sourceUri":"https://github.com/engurulabory/Engurulaboratuvari/pull/203",
 "expected":"Node TAP raporu","observed":"Node sürüm raporlama farkı","observedAt":"2026-10-24T12:00:00+03:00"
}
```

Desteklenen `failureClass`: `PACKAGE_ABSENT`, `RUNTIME_DRIFT`, `UI_SURFACE_MISMATCH`, `INTERACTIVE_TIMEOUT`, `LEDGER_PARTIAL`, `OTHER`. OSi özel içerikleri kamuya açık kayda yalnız owner'ın ayrıca onayladığı gizlisiz özetiyle aktarılır.

### C şeması

Her observation kaynağı schema `enguru.mk.osi-field-receipt/v1` ve `taskId`, `observationId`, `phase` (`baseline` / `after`), `observedAt`, `manualSteps`, `repeatedDiagnosis`, `prematureFinish`, `repairMinutes`, `verifiedGateCount`, `scheduleRunTimes` alanlarını taşır. Ölçüm girdisi:

```json
{
 "schema":"enguru.mk.osi-metrics/v1","taskId":"ENGURU_MANAGEMENT_V69_PR_203",
 "observations":[
  {"observationId":"BASELINE_01","phase":"baseline","taskId":"ENGURU_MANAGEMENT_V69_PR_203","sourcePath":"/path/BASELINE_01.json","sourceSha256":"REAL_64_HEX_SHA256"},
  {"observationId":"AFTER_01","phase":"after","taskId":"ENGURU_MANAGEMENT_V69_PR_203","sourcePath":"/path/AFTER_01.json","sourceSha256":"REAL_64_HEX_SHA256"}
 ]
}
```

Temel kabul: test ortamı simülasyon 3×30/30 = 90/90, 25/25 tasarım kontrolü = 100/100 *teorik kapsama*. Gerçek Mac kaynak/SHA uyumu, canlı UI/HTTP, owner review, gerçek P01–P06 ölçümleri ve resmî ürün kabulü ayrıca kanıtlanır. Çıktı `OFFICIAL_ACCEPTANCE=HOLD` durumunu muhafaza eder. GitHub için ayrı owner-onaylı inceleme PR'ına kaynak alınabilir; `main` otomatik güncellenmez.