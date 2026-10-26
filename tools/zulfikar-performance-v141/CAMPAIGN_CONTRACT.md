# Zülfikar V1.4.1 — Gerçek performans sınavı kapsamı

Tek hedef `ZF.PERFORMANCE.20261026`; görev grubu ve kabul ölçütleri PLAN.json içinde sabittir. Bu kaynak test istemcisidir; mevcut Work subprocess, GitHub Actions ve dom.engine kullanılır. Yeni yürütücü otoritesi, issuer veya DoneCheck motoru kurulmaz.

## Aşama kabul matrisi

| Kapı | Üretilen fark ve gözlenebilir kabul | Kanıt ve sınır |
|---|---|---|
| T01 | Hedef, kaynak envanteri, kullanıcı görev yetkisi, korunan değerler ve riskler: 5/5 | PLAN.json, exact source/tree, canonical SHA kilitleri; check_preparation.py |
| T02 | Sabit hedef, kabul kimlikleri, test/kanıt ihtiyaçları, bağımlılıklar ve durma koşulları: 5/5 | Beş farklı aile × üç farklı evre; plan kod denetimi; yalnız hazırlık kapsamı |
| A01 | Mevcut DÖM → callback ile gerçek görev → ayrı süreç doğrulayıcı → SHA kontrolü → günlük; tek yazar | run_campaign.py, verify_task.py, verify_campaign.py; izole dosyalar |
| A02 | SIM1 normal görev; SIM2 hata/kesinti/yanlış kanıt; SIM3 100 kontrol noktası sonrası değişmiş çıktı | Üç mantıksal karşıt senaryo; gerçek gözlemler ayrıca kaydedilir |
| A03 | Her görev için özgün sonuç ve ayrı gerçek başlangıç/hata/onarım makbuzları; geçerli çıktı ve kaynak SHA | task-result.json, domCoordinator, ayrı süreç ve kalıcı dosya doğrulaması; resmî kabul verilmez |
| A04 | İnceleme dalı, immutable commit, kaynak mührü ve gerçek GitHub runner | Ayrı taslak PR; main ve PR #246 yerinde kalır; merge insan kararındadır |
| A05 | R01–R05 gerçek izole görevleri mevcut DÖM koordinasyonunda çalıştırılır | Teknik aday; gerçek kullanıcı/Mac sahası ve bağımsız kimlik doğrulanmış kabul ayrı HOLD |
| A06 | Bu dal ve kanıt SHA kayıtlarıyla salt-okunur devir hazırlanır | Kurulum başlatılmaz. Owner ileride kabul ederse ayrı Mac planı; geri dönüş mevcut branch/source pinine dönüştür; kullanıcı Mac dosyaları bu kampanyada değişmez |

## Kanıt ve puan disiplini

İlk koşuda dört aile geçti, R04 eski kontrol noktasından değişmiş gerçek çıktıyı 100 adayı olarak döndürdü. Onarım, aynı DÖM içinde yeniden başlatma sırasında hash, güncel kabul ölçütleri, kaynak ve günlük doğrulaması ekler. Görev icrası tekrarlanmaz. Önceki V2 mühür baytları BASELINE_SOURCE_SEAL_V2.json içinde aynen korunur; güncel V2 R1 yalnız değişen iki kaynağın hash'ini ve revizyon bağını içerir.

İlk/son dört hedef ölçümü yalnız bu sabit beş teknik sınavın iç teşhisidir: gerçek görev sonucu, kanıt geçerliliği, döngü dayanıklılığı ve finiş güvenilirliği. Aynı görevdeki tekrarlar yeni bağımsız görev veya yeni kabul sayılmaz. Üç GitHub tekrarı aynı beş ailenin yeniden üretilebilirliğidir. Her tekrarın kendi başlangıç/hata/onarım evreleri vardır. Genel operasyonel puan cetveli altı alanlı özgün ZULFIKAR_V131_OPERATIONAL_SCORECARD_V1.json olarak korunur; 91.25 tarihsel ağırlıklı teşhis bu kampanyayla resmî 100'e dönüştürülmez.

Ayrı süreç/kodla dosya doğrulaması mekanizma bağımsızlığıdır. Aynı oturumun yazdığı doğrulayıcı, ayrı insan veya kimliği doğrulanmış farklı oturum incelemesi yerine sayılmaz. Kaynak hash'i provenance kökünün gerçek bağımsızlığını tek başına doğrulamaz. FINISH_HOLD bu sınırı korur.

## Kesin resmî kapanış şartları

1. Özgün ZF.G1.01: gerçek owner/runtime/issuer görev kapsamı ve yetkili bağımsız uzlaştırma.
2. ZF.G1.02: üç farklı yetkili gerçek ürün görevinin kaynak→çıktı→bağımsız doğrulama→owner kabul zinciri. Bu kampanyanın izole teknik sonuçları katkı sağlar; mevcut üç ürün profiline kendiliğinden atanmaz. PiLive bu kampanyada beklemededir.
3. ZF.G1.03: gerçek kullanıcı sonucu, kalıcı restart/recovery, eş bütçeli gerçek muadil deneyi, bağımsız kabul, mevcut DoneCheck ve Human Threshold.
4. Nihai kaynak/commit ve tüm özgün kriterlere bağlı taze karşıt inceleme; açık zorunlu iş kalmaması.

Bu şartlara bu oturumda yeni yetki üretilemez. Erişilebilir teknik işler tamamlanır, ürünün genel hükmü kanıt düzeyinde HOLD kalır.
