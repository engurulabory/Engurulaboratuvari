# ENGÜRÜ Yönetim İCRA V6.9 — Hedef 02 İş Yapma Yeteneği · Teorik 100/100 Kabul Planı
STATE=TARGET_02_ACTIVE; TARGET_01_OWNER_DESIGN_ACCEPTED; INDEPENDENT_ARCH_REVIEW=HOLD; OSi_MUTATION=0

## Özgün hedef
Yönetim hedefi bir kez alır, özgün görev ID üzerinden gereksinimleri ölçer, dependency DAG ile görevleri sıralar, Mühendis İCRA'ya kanıt sözleşmesiyle devreder, gerçek kod/test/kanıt çıktısını bağımsız incelemeye sunar. Eksik varsa doğrulanmış iş bloğuna döner, sonuç tamam ise DoneCheck ve yetkili kabule ilerler.

## 10 yeterlilik kriteri · B01–B10
B01 görevin ölçülebilir hedef ve kabulü; B02 kaynak ve uygulanabilirlik kontrolü; B03 bağımlılık DAG ve kilitli sürümler; B04 kaynak/rol/yetki ayrımı; B05 mühendis icrasının gerçekten yürütüldüğüne ilişkin makbuz; B06 build ve test PASS, hata enjeksiyonu; B07 özgün task_id → evidence_id bağları; B08 hata sonrası sınırlı tekrar ve checkpoint; B09 bağımsız reviewer ve rollback kabulü; B10 bitiş kapısı ile devam/HOLD ayrımı.

## Eksik ihtiyaç analizi
- Mevcut tools/management_v69_target02_execution.py bir PLAN ve boolean receipt modeli test eder; gerçek mühendis icra çıktısına bağlı B05–B08 kanıtı HOLD.
- SOURCE ve exact-head drift, eski evidence, güvensiz görev ağacı, döngü, paralel dosya çakışması, durdurulan işlem ve yetkisiz tekrar için yeni karşıt senaryolar gerekir.
- Mühendis PR #14 runtime ile Engineer PR #18 tasarım sözleşmesi gerçek üretim bağı kurmadığı için B05, B06 ve B07 üretim kanıtı HOLD.
- Tam teorik kabul için her B01–B10 özgün kriterine ayrı uygulama kabul/karşıt test, üç bağımsız exact-head CI run ve bağımsız review gerekir.

## Kapalı devre icra
01 hedef/acceptance; 02 yetkili salt-okunur kaynak; 03 kaynak ve DAG; 04 engineer handoff; 05 gerçek build/test; 06 anti-drift ve adversarial; 07 checkpoint/recovery; 08 receipt; 09 reviewer; 10 owner donecheck sınırı.

## Kanıt ilkesi
TASK_MODEL_PASS yalnız karar simülasyonu; RUNNER_PASS gerçek GitHub CI; ENGINEER_EXECUTION_PASS gerçek mühendis kaynak/receipt; TARGET02_THEORETICAL_100 yalnız B01–B10 kanıtlı bağımsız kabul. Field ve resmi DoneCheck sonradan.
