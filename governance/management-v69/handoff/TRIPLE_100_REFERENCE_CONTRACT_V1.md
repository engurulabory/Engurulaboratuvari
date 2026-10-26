# ENGÜRÜ V6.9 — Üçlü 100/100 Referans Sözleşmesi V1
DATE=2026-10-24
STATE=DESIGN_TARGET_DEFINED; THEORY_TARGET_DEFINED; SIMULATION_TARGET_DEFINED
ACTIVE_TARGET=01_ARCHITECTURE; TARGETS_02_TO_09=PRESERVED; OSI_MUTATION=0

## Bağlayıcı yöntem
HAKİKAT → TASARIM 100/100 → TEORİ 100/100 → SİMÜLASYON 100/100 → GITHUB TEK GERÇEK İCRA → BAĞIMSIZ KANIT → YETKİLİ KABUL → İLERLE.

Her hedefin hedef puanı 100/100'dür. Hedef puanları gerçek ölçülmüş başarı değildir. Her ölçekte tam puan ancak bağımsız değerlendirmede ölçütün tüm alt koşulları doğrulandığında üretilir.

## Tasarım kabulü — 10 x 10
D01 Pilot Manager tek aktif iş seçimi; D02 dokuz hedefli sıra ve korunmuş özgün kimlikler; D03 tek management ve engineer motoru; D04 bağımsız verifier; D05 durable SQLite ledger/checkpoint/idempotency; D06 exact source-bound provenance ve geri alınabilirlik; D07 canonical owner/Human Threshold yetki sınırı; D08 gerçek main/PR/CI entegrasyon yolu; D09 yerel Mac OSi salt-okunur hazırlık ve kurulum ayrımı; D10 tek-owner/zero-cost/zero-routine kullanıcı akışı.
Her D kontrolü için 10 somut kabul alt maddesi ve kaynak bağlantısı gerekir. D01–D10 yalnız tasarım koşullarıdır.

## Teori kabulü — 10 x 10
T01 koşul invariants; T02 görev dependency DAG; T03 input/output tipleri; T04 yetki ispatı; T05 source/commit/version pin; T06 tutarlılık ve atomiklik; T07 crash/retry/resume; T08 adversarial failure model; T09 producer-verifier ayrılığı; T10 matematiksel/çalıştırılabilir karar kapsamı.
Her T için 10 bağımsız testlenebilir önerme, sınır durumu ve yanlış pozitif önleyici gerekir.

## Simülasyon kabulü — 10 x 10
S01 normal görev; S02 source drift; S03 sahte owner; S04 sahte CI; S05 eksik veya kaymış SHA; S06 yarım kalmış iş/restart; S07 çift çalışma ve idempotency; S08 rollback/disk failure; S09 canonical review/DoneCheck HOLD; S10 hedefler arası bağlı görev zinciri.
Her S altında 10 farklı giriş/çıkış senaryosu ve doğru PASS/HOLD kanıtı gerekir. Üç tam tur çalışır; yeni hata bulunursa onarılıp dördüncü tur çalıştırılır. Simülasyon 100/100 yalnız 100/100 gerçek scenario assertion ile verilir.

## Tek bir birleşik mimarlık kararı
DESIGN_SCORE = verified D controls / 100; THEORY_SCORE = verified T propositions / 100; SIMULATION_SCORE = verified S scenario assertions / 100.
TRIPLE_THEORETICAL_TARGET=100/100+100/100+100/100.
DESIGN_PASS, THEORY_PASS, SIMULATION_PASS ayrı olmalı; birinin puanı diğerini ikame etmez.
Mimarlık Hedef1 THEORY_FINAL ayrıca dış kaynakları ve yetmiş mevcut A–G kriterini çapraz doğrular.
Ayrı gerçek Github acceptance: exact HEAD workflow run, kaynak SHA256, bağımsız verifier, geçerli kapsam ve gerçek owner makbuzu gerektiğinde yetkili saha kanalından.
Saha G2–G6/Human Threshold gerçek imza/DoneCheck kesin olarak ayrıdır.

## Korunan hakikat
Son teyitli Handoff CI belirli eski commitlere aittir. Son HEAD'de gerçek CI run kanıtı halen UNVERIFIED. Eski operasyon makbuzu CURRENT_MAIN_SOURCE_DRIFT; yeni current-main receipt zorunludur. Mevcut analitik 88.5/100 ölçümü ayrı tarihsel referanstır ve yeni üç ölçekte otomatik 100 olmaz. Tasarım 100/100 hedef spesifikasyonu ile 100/100 doğrulanmış tasarım kabulü ayrı kayıtlanır.
