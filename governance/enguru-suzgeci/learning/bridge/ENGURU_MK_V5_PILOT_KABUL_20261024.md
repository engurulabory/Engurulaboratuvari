# ENGÜRÜ Çift Yönlü Köprü V5 — Kanıtlı Teşhis, Çözüm ve Öğrenme

**Kalıcı sabit hedef:** İki pilot, tek Mühendislik Kası; öneri bazlı bilgi paylaşımı; ayrı canonical DoneCheck ve owner yetkisi.

## Tasarım sınırı

- GitHub tarafı `feat/enguru-mk-bridge-intelligence-v5-20261024` inceleme dalı; owner bağlamında yalnız gizlisiz sabit kodlu olaylardan `diagnostics/mac` ve `diagnostics/github` önerileri üretir. Bunlar **değiştirilemeyen**, olay SHA'sına bağlı ve emir içermeyen kayıtlar.
- Mac OSi tarafı aynı `tools/enguru_mk_intelligence_v5.py` modülünü çalıştırır. Önce mevcut V4 taşıma ve karşılıklı öneri, sonra V5 teşhis okuması ve SQLite üzerinde güvenli sonraki adım hizalaması.
- Değerlendirmede **OBSERVED/HYPOTHESIS** ayrımı; kök neden için `UNCONFIRMED`; iki alternatif çözüm ve tersine çevrilebilir inceleme adımları.
- `INSPECT_LOCAL_LEDGER` salt-okunur; diğer tüm adımlar `REVIEW_REQUIRED` olur. Ürün kod yazımı, imza ve resmî kabul 0.
- Sonuçlar **PROVISIONAL** olarak saklanır. Öğrenme sıralamasına yükselme yalnız gerçek, dışarıdan doğrulanmış kanıt aracılığıyla mümkündür; örnek verifier callback testlerde *taklit* edilir. Gerçek güven mekanizması Mac saha otoritesine bağlanıncaya dek otomatik terfi kapalıdır.
- V4 ZIP, V4 plist ve köprü SQLite defteri korunur. V5 tek aktif yerel launchd işçisini hedefler; yeni kaynak paketi önce AudiV13'e SQLite snapshot alır, sonra V4 işçisinden V5 işçisine geçer.

## Denetimli sıralama

B00 gerçek V4 SHA, main, Canonical kaynak -> B01 sabit teşhis ve alternatifler -> B02 üç tur/3 puan -> B03 GitHub inceleme dalı/CI -> B04 Mac onarımlı kurulum ve gerçek `--status` -> B05 karşılıklı V5 raporları ve Mac `READONLY_APPLIED`/`REVIEW_REQUIRED` -> B06 birden fazla bağımsız gerçek vaka -> B07 ölçülen azaltım ve yetkili DoneCheck.

## Resmî kabul ölçütleri

1. Aynı kaynak sürümüne bağlı SHA-256 manifest + farklı ortamda yeniden üretilebilir ZIP.
2. Üç ayrı subprocess karşıt test turu ve bağımsız GitHub Actions CI PASS (exact HEAD).
3. Mac ön saha: SHA kilitli ZIP giriş testi, yedek SHA, aktif V5 LaunchAgent, V4 koruması, gerçek `pending=0`.
4. Mac GitHub V5 `diagnostics/github/GH-...` kaydını alır; yerel next-step veritabanına geçirir ve salt-okunur uygular. GitHub `diagnostics/mac/MAC-...` kaydını üretir.
5. Gerçek yanlış SHA, replay, ağ kesintisi ve geri dönüş saha testi PASS.
6. Farklı başarısızlık türlerinde doğrulanmış sonuçlar ve gerçekten dış kaynakla doğrulanmış outcome/ölçüm PASS.
7. Canonical DoneCheck + Human Threshold sahibi tarafından imzalı yetkili kabul; nihai ürün Verified Finish yalnız orijinal mekanizmayla.

**Statü:** Teorik V5 hedefi ile gerçek V5 saha/ürün yetkisi ayrı muhasebeleştirilir. Yönetim ve İcra motorları, `main` ve mevcut GitHub PR #212–216 korunur.
