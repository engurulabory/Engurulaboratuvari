# ENGÜRÜ Ana Çalışma Yöntemleri™ — Aşama 2–4 Gerçek İcra ve Kabul Sınırı V1

**Tarih:** 2026-10-24  
**Görev:** Kabul edilen Ana Terazi™ `TEORİ=100/100; TASARIM=100/100; SIM1=SIM2=SIM3=100/100` ve altı alan uyarlamasının 2, 3 ve 4. aşamalarını gerçek kanıtla mümkün olduğunca ilerletmek.  
**Canonical:** [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) · [V3 kilidi](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) · [DoneCheck Authority](../mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md) · [GitHub-first / Mac milestone](../mac-engineer/GITHUB_FIRST_MILESTONE_MAC_WORKING_MODEL_V1.md).  
**Kapsam:** `PR #221` inceleme dalı; `main`, kaynak kilidi ve resmî kanıt otoriteleri korunur.

## Aşama 2 — Bağımsız tasarım incelemesi

### Erişilebilir teknik ikinci bakış
[Alternatif kaynak denetimi](../../tools/enguru_method_second_look_v1.py), mevcut tasarım puanlayıcısından ayrı bir doğrulayıcıdır. Gerçek V3 içeriğinin SHA-256'sını lock ile karşılaştırır; 8 aşamayı, 48 sabit D kimliğini, tekil oracle'ları, altı üretim alanını, özgün 211/240 baz puanı, 5 × 100/100 terazisini, review/DoneCheck/insan eşiklerini ve kaynak ayrımını denetler.

**Beklenen teknik sonuç:** `TECHNICAL_SECOND_LOOK=PASS_10_OF_10` — yalnız test çalıştıktan sonra kaydedilir.

### Gereken bağımsız insan review
Mevcut PR üreticisi ve denetleyici kodları aynı çalışma ekosisteminden çıkmaktadır. Mekanizma ayrılığı, **bağımsız yetkili reviewer kimliği** değildir. Yetkili farklı GitHub hesabı veya önceden kabul edilmiş ayrı reviewer, gerçek PR diff ve geçmişine karşı tasarımın semantiğini gözden geçirip GitHub review eylemi kaydetmelidir. Yetkili reviewer olmadan `INDEPENDENT_HUMAN_DESIGN_REVIEW=HOLD`.

**Gözlem ölçütleri:** 48 ölçütün içerik yeterliliği, 6 adaptörün tüm ürünlere taşınabilirliği, modelin verdiği 100 ile gerçek doğrulamanın sınırları, bağımsız reviewer kimliği, yetki/harcama/gizlilik, istemli yanlış olumlu sonuç, yeniden kurulum ve deney tekrarı. Bulgu/itiraz: `HOLD + CONTROL_ID + EVIDENCE + NEXT_ACTION`.

## Aşama 3 — Gerçek GitHub + OSi mühendislik pilotu

### 3A. GitHub'da fiilen çalışabilen motor alanı pilotu
[Gerçek GitHub motor pilotu](../../tools/enguru_method_github_pilot_v1.py), ana üretim koduna yeni core eklemeyen, sistem geçicisi klasörde başlayan gerçek bir süreçtir:

1. Altı alanın **gerçek checkout JSON** içeriğini oku, kontrol sayısını ve kaynak SHA-256'sını hesapla.
2. Ayrık fiziksel SQLite `checkpoint.sqlite3` dosyasında tek görev kaydını ve tek fiziksel kanıt artefaktını yaz.
3. [Ayrı yürütülebilir doğrulayıcı](../../tools/enguru_method_github_pilot_verify_v1.py) ile bağımsız **mekanizma** üzerinden source SHA, ledger, artifact SHA ve içerik tutarlılığını tekrar doğrula.
4. İkinci Python sürecinde aynı görevi yeniden yürüt, `PASS_REPLAY_IDEMPOTENT` ve ledger `1` kaydını koru.
5. Kanıtı değiştir; gerçek doğrulayıcının `HOLD` verdiğini gözle, orijinal içeriği geri getir.
6. Eski kaynak/HEAD'i farklı kaynak baytlarıyla yeniden yürütmeyi dene, `HOLD_SOURCE_OR_ARTIFACT_DRIFT` bekle; yeniden doğrulamada `PASS` ara.

Bunlar GitHub runner üzerinde gerçek `SQLite`/dosya/process işlemleridir. **Gerçek ENGÜRÜ üretim motorunun tamamının çalıştığı veya Mac OSi kurulumunun doğrulandığı anlamına gelmez.** Test klasörü otomatik temizlenir, kullanıcı Mac dosyaları ve canonical `main` korunur.

### 3B. Gerçek OSi saha kabulü
Gerçek Mac OSi sistem erişimi ve yetkili kullanıcı tasarım kararı bu çalışmada mevcut olmadığından `OSI_REAL_FIELD=HOLD`. Bir gerçek üretim vakasının altı alandan seçimi, o ürün için owner tasarım onayı, Mac yerel görev yürütmesi, restart, bağımsız saha makbuzu ve DoneCheck zincirine devri gerekir. Mevcut Mac kanıtları ancak geçerli gerçek kaynakla yetkili bağ kurulduğunda sayılır.

## Aşama 4 — Kanıtlı olgunluk / resmî kabul

[Salt-okunur kabul hazırlık denetleyicisi](../../tools/enguru_method_closeout_readiness_v1.py), dört gerçek CI makbuzunu karşılaştırır: Ana Terazi; altı alan üç turlu yöntemi; Aşama 2 teknik ikinci bakış; Aşama 3 gerçek GitHub pilotu. Sonuçları `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT` ile makine-okunur şekilde ayırır.

`PASS_READINESS_EVIDENCE_OFFICIAL_HOLD` yalnız GitHub kapsamındaki producer/evidence hazırlığını ifade eder; **DoneCheck v1.2'nin canonical makbuzu değildir**. Makine yetkisi ve Human Threshold™ kabulü için kendiliğinden imza, yayımlama, harcama veya merge yetkisi üretmez.

### Korunan kesin durumlar
```text
A1_5X100_THEORETICAL=PASS_PREVIOUS_EXACT_HEAD
A2_TECHNICAL_SECOND_MECHANISM=CI_TO_BE_CHECKED
A2_INDEPENDENT_HUMAN_REVIEW=HOLD_DIFFERENT_AUTHORIZED_REVIEWER
A3_REAL_GITHUB_ENGINE_TEST=CI_TO_BE_CHECKED
A3_REAL_MAC_OSI_FIELD=HOLD_AUTHORIZED_OSI_FIELD_EVIDENCE
A3_REAL_USER_CO_DESIGN_PER_PRODUCT=HOLD_CASE_SPECIFIC_DECISION
A4_EVIDENCE_READINESS=CI_TO_BE_CHECKED
A4_DONECHECK_V12=HOLD_CANONICAL_AUTHORITY
A4_HUMAN_THRESHOLD=HOLD_OWNER_APPROVAL
PR221_MAIN_MERGE=HOLD_REVIEW_READY_UNMERGED
VERIFIED_FINISH=HOLD
```

**Sıralı gerçek kapanış:** (i) farklı yetkili reviewer'ın PR incelemesi → (ii) kullanıcıyla seçilmiş gerçek ürün kurgusu + OSi yerel saha icrası ve imzalı/doğrulanmış delil → (iii) korunmuş branch review/merge, exact-main ve DoneCheck v1.2 doğrulaması → (iv) gereken Human Threshold™ → `VERIFIED_FINISH → BITTI_DUR`.

**Kalıcılık:** Üç aşamanın gerçekten tamamlanan alt işlerinin kanıtı korunur; gerçek bitiş yetkisi oluşana kadar açık şartlar ayrı HOLD kalır.


## Gerçek GitHub kanıtı — Aşama 2–4 teknik kaydı

- İlk gerçek bütünleşik koşu: [GitHub Actions #40131176035](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40131176035), commit `966ea16bee7f281f4fde550beb310b555e383599`.
- Bu koşuda Design48 + Labory Final Gate + IP Model Trust Gate + IP Model Trust Fleet + PARK Adapter CI: **5/5 completed/success**.
- Aşama 2 `TECHNICAL_SECOND_LOOK=PASS_10_OF_10`; `HUMAN_REVIEW_COUNT=0` (son kontrol).
- Aşama 3 `REAL_GITHUB_ENGINE_PILOT=PASS_6_OF_6`: tek kalıcı SQLite satırı, değişmeyen gerçek kaynak SHA, iki ayrı Python süreci, eski kaynak reddi, değiştirilmiş makbuz reddi, onarım sonrası bağımsız mekanizma doğrulaması.
- Aşama 4 `PASS_READINESS_EVIDENCE_OFFICIAL_HOLD`: DoneCheck v1.2, gerçek Mac OSi ve gereken Human Threshold kabulü `HOLD`.
- Makbuz: [enguru-design48-theory-receipt #12574713394](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/40131176035/artifacts/12574713394).
- PR #221 bağımsız reviewer erişimi için **ready for review** durumuna geçirildi; `merged=false`. Reviewer kimliği/kararı ayrı kabul kapısı olarak beklenir.
- Bu ek kaydın ardından daha yeni commitler oluşursa **son HEAD'in CI koşusu ayrıca doğrulanır**.


## 25 Ekim 2026 — Birleşme sonrası hakikat güncellemesi

Bu belgenin önceki `PR221_MAIN_MERGE=HOLD` ve review-ready satırları **24 Ekim tarihli ara durumun tarihsel kaydıdır**. Gerçek PR #221 25 Ekim'de exact HEAD `bbbebb4e8fdd7951567013e91a67fb7667644f83` üzerinden `main` commit `9900f4ca7a17f99898521bdab1bfbe86784ecc07` olarak birleşti. Üç `main` push CI kontrolü PASS. GitHub main ruleset #22452401, gerekli GitHub reviewer sayısını **0** ve gerekli CI'ı `labory-final-gate` olarak belirtiyor. Bağımsız tasarımın anlamsal incelemesi bir mühendislik kalite ihtiyacıdır; repo koruma kuralının zorunlu ikinci GitHub hesabı koşulu şeklinde sunulamaz. Mac OSi ve resmî DoneCheck™ sahası HOLD kalır.
