# ENGÜRÜ SYSTEM 100 HARDENING PASS™ v1

## Niyet
ENGÜRÜ Labory + GitHub sistemini yeni çekirdek üretmeden; mevcut doğrulanmış parçaları sadeleştirerek, tekilleştirerek ve kanıt zincirini sertleştirerek 100/100 seviyesine mümkün olduğunca yaklaştırmak.

## Ana kural
Yeni ihtiyaç önce mevcut çekirdekte çözülür. Sıra: **reuse → extend → adapter → new core**. Yeni core ancak ilk üç seçenek kanıtla yetersiz kaldığında açılır.

## Tek sistem görünümü
Bir insan şu beş sorunun cevabını tek kanonik yüzeyden görebilmelidir:
1. PRODUCTS — Hangi ürünler var ve gerçek durumları ne?
2. CORES — Hangi yeniden kullanılabilir çekirdekler var ve kanonik sahibi kim?
3. RUNTIME — Hangileri gerçekten çalışıyor/deploy edilmiş?
4. EVIDENCE — Son doğrulama kanıtı nerede?
5. NEXT ACTION — Bir sonraki kapatılacak gerçek açık ne?

Kanonik makine yüzeyi: `governance/ENGURU_SYSTEM_TRUTH_V1.json`.

## 100 hedefleri

### A. Mimari düşünce — 100
- Control plane ile product execution plane sınırı nettir.
- Ürün reposu ürün mantığını taşır; Labory ortak governance/steward/map/security kontrolünü taşır.
- Aynı yetenek iki yerde kanonik olamaz.

### B. Governance / kanıt — 100
- `state → claim → evidence → next action` korunur.
- PASS yalnız mevcut kanıtla verilir.
- Irreversible / payment / publish / legal / deletion işlemleri Human Threshold™ altında kalır.

### C. Ürün–çekirdek ayrımı — 100
- Her aktif varlık PRODUCT / CORE / PRODUCT_CORE / CONTROL_PLANE / RELEASE_MIRROR / EXPERIMENT olarak tekil sınıflıdır.
- Builder içindeki geçici cross-product governance kopyaları kanıtlı geçiş sonrası adapter seviyesine indirilir.
- DoneCheck dual-repo modeli provenance ile korunur; kör birleştirme yapılmaz.

### D. Repository düzeni — 100
- Canlı erişilebilir repo sayısı ile Product & Core Map aynı truth snapshot'ı kullanır.
- Eski/erişilemeyen repo kayıtları silinmez; `historicalOrUnresolved` altında tutulur.
- Büyük move/delete/merge/rename işlemi Map PASS + Human Threshold olmadan yapılmaz.

### E. Güvenlik — 100
- Her governed repo `.enguru/ip-model-trust.json` taşır.
- Fleet workflow merkezi Gate'in tam commit SHA'sına pinlidir.
- Known token/private-key formatları global fail-closed kalır.
- Secret fixture ile gerçek credential ayrımı test edilir.
- T4 cloud disclosure Human Threshold olmadan PASS alamaz.

### F. Steward — 100
- Steward 2–3 günlük bakım döngüsünde inventory drift, stale map, unregistered asset, missing manifest, stale release mirror ve evidence drift arar.
- SAFE_AUTO yalnız non-destructive metadata/docs düzeltmeleridir.
- REVIEW mimari/ownership kararlarıdır.
- HUMAN_THRESHOLD destructive/high-impact kararlardır.

### G. Operasyonel sadelik — 100
- Kullanıcı günlük çalışmada 4 ana kavram görür: **Products / Cores / Evidence / Archive**.
- Governance detayları arka planda çalışır; kullanıcıyı yeni isimlerle boğmaz.
- Bir ihtiyacı çözmek için aynı anda birden fazla worklist/source-of-truth kullanılmaz.
- Her repo README'si tek cümlede rolünü ve kanonik sahibini söyleyebilir.

## Öncelik sırası
1. Current repository truth snapshot.
2. Product/Core Map v2 alignment.
3. Security Fleet v1.2 closure.
4. Steward drift check + 2–3 day cadence evidence.
5. Transitional governance duplicate reduction plan.
6. Release mirror freshness decision.
7. One-surface system status render.
8. Final DoneCheck™ + Human Threshold™.

## Final kabul
`Repository Truth PASS → Product/Core Map PASS → Repository Order PASS → Security Fleet PASS → Steward PASS → Simplicity PASS → DoneCheck PASS → Human Threshold → VERIFIED FINISH`

Bu zincirde tek bir HOLD varsa sistem genel hükmü HOLD kalır.
