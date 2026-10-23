# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™ V2, 100/100 hedefli tasarım

**Rol:** Mevcut ENGÜRÜ Süzgeci™ sekiz aşamasının *içindeki* kalite/öğrenme adaptörü. Yeni mühendislik çekirdeği, yeni issuer veya yeni owner yetkisi değildir.

## Gelişmeyle çalışan kapalı döngü

`REAL_OBSERVATION -> STRUCTURED_EVENT -> SCOPE/PIN/SECRETS -> DEDUPE -> CLASSIFY -> CANDIDATE_PATCH -> TEST -> HUMAN/INDEPENDENT_REVIEW -> APPROVED_RULE/CI -> MAC_FIELD_FEEDBACK`

Yeni gerçek durum bir Mac saha JSON raporuyla veya PR #203/#206'da yetkili hesap tarafından verilen yapılandırılmış olay yorumuyla geldiğinde, adaptör olayı sınıflandırır. İlk sürümde değişiklik yalnız Mühendislik Kası **taslak inceleme dalındaki aynı Markdown dosyasına** aday ekler. Bu ilkeleri uygular:

* Kanıt kaynağı gerçekten bağımsız doğrulanmadıysa: `UNVERIFIED_EVIDENCE_POINTER`, yalnız inceleme adayı.
* Varlık/yokluk iddiası: `examinedCount=0` olduğunda `ZERO_COVERAGE_IS_NOT_ABSENCE_PROOF`.
* `evidenceLevel=D`, owner imzası değil; gerçek canonical owner authority ile bağımsız doğrulama zorunlu.
* Aynı olay ID ve aynı canonical payload: `IDEMPOTENT_SAME_EVENT`; farklı içerik: `HOLD_EVENT_ID_CONTENT_CONFLICT`.
* GitHub markdown yorumu, politika/prompt yürütme komutu değildir: metin olarak veri.
* Secret/özel anahtar, sahte yetki, yanlış ürün ID, eksik SHA, duplicate JSON key veya uygunsuz boyut: `HOLD`.
* Olay sınıflandırma ve regresyon önerisi **otomatik**; üretim kodu onarımı, canonical kuralı değiştirme, Mac imzası, merge ve `VERIFIED_FINISH` yalnız gerçek kabul kapılarıyla.

## Canlı GitHub akışının aktifleşme koşulları

Dosyalar `engurulabory/Engurulaboratuvari` **PR #206 ayrı inceleme dalında** bulunur. GitHub `issue_comment` workflow'u GitHub Actions gereği **yalnız workflow yetkili default branch'e alındıktan sonra** otomatik tetiklenir. Tam çalışması için:

1. Owner, GitHub taslak PR #206 için inceleme/merge kararını verir; canonical V3 ve üretim PR #203 ayrı tutulur.
2. GitHub repo Actions Variable `ENGURU_MK_OWNER_LOGIN` **gerçek tek yetkili GitHub kullanıcı adı** olarak owner tarafından ayarlanır. Değer bilinmiyorsa olay kabulü `HOLD`.
3. Workflow `contents:write` yetkisi ve repo branch push policy izinli olmalıdır. Bot yalnız `docs/enguru-osi-muhendislik-kasi-20261023` inceleme dalına yazar. Default `main` ve product PR #203 değişmez.
4. Olay şu şemada **tam bir PR #203 veya PR #206 yorumu** olarak owner hesabından gönderilir:

```enguru-mk-event
{"schema":"enguru.mk.evidence-event/v1","eventId":"MK-EVT-EXAMPLE-001","taskId":"ENGURU_MANAGEMENT_V69_PR_203","observedAt":"2026-10-23T13:00:00+03:00","type":"MISMATCH","evidenceLevel":"A","sourceUri":"https://github.com/engurulabory/Engurulaboratuvari/pull/203","sourceSha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","expected":"Beklenen gerçek olay","observed":"Gözlenen farklı durum","causeStatus":"HYPOTHESIS","fixProposal":"Önerilen yeni regresyon kontrolü","testState":"NOT_EXECUTED"}
```

Yukarıdaki SHA **örnektir**; gerçek olayda gerçek kanıt SHA'sı gerekir. GitHub yorumunda sadece kanıt işaretçisi bulunduğunda `UNVERIFIED_EVIDENCE_POINTER` olarak saklanır; bağımsız saha kabulü verilmez.

**Mac JSON ingest:** `python tools/enguru_muhendislik_kasi.py --event event.json --record governance/enguru-suzgeci/ENGURU_OSI_MUHENDISLIK_KASI_CANLI_KAYIT_V1.md --output candidate.md --receipt receipt.json`. Kanıt dosyasını `sourcePath` içinde güvenli yerel yol olarak ver; program SHA-256 gerçek dosyayla karşılaştırır. Bu işlem orijinal kaydı değiştirmez. Gerçek dosyayı AudiV13'te koru; çıktı kanıt ve owner incelemesi sonrası aynı GitHub review dalına yazılır.

## Kabul ve puan ayrımı

**Teorik tasarım hedefi 100/100:** 10 ön-kabul ilkesinin tümü (sabit hedef/rol, sıkı şema, gerçek kanıt düzeyi, kapsam, deduplikasyon, güvenlik, birden çok negatif test, idempotent replay, inceleme dalı yazım sınırı, gerekli owner kararı) tanımlıdır. Her test çalıştırmasında kontrol edilir.

**Gerçek kapı:** 30 izole test × 3 tekrarlı simülasyon = 90 gerçek izole test `PASS` hedefi; GitHub Actions CI PASS ve üretim dışı end-to-end GH event tetikleme ayrı; üretim Mac owner signer ve Verified Finish ayrı.

**Öğrenmenin kendini değiştirmesi:** Kanıt geldikçe aynı Markdown'a sürümlü olay ve yeni kontrol önerisi yazılır; önerinin yürütme mantığına alınması için gerçek test + owner/inceleme gerekiyor. Böylece otomatik içerik büyümesi ile güvenli yazılım değişimi birbirinden ayrılır.