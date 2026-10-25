# ENGÜRÜ Yönetim V6.9 — GitHub bağımsız inceleme temeli

## Kalıcı sabit hedef
Yalnız Yönetim V6.9'u GitHub'da güvenilir çalışır duruma taşı. İcra V6.9 kullanıcının ayrı mühendislik alanıdır. Diğer ürün ve görevlerin durumları korunur.

## Canonical hiyerarşi
`main/AGENTS.md` → Evrensel V3 ve kaynak kilidi → ürünün özgün canonical yetki ve sözleşmesi → Human Threshold™.
ENGÜRÜ Süzgeci™ sekiz aşamalı yapı, P01-C/D/E/F/G, DoneCheck™ ve pozitif İLERLE / GÜVENLİ_DUR korunur.
K01–K06 / 32 kontrol, İcra V6.9'un kendi hedefleridir; Yönetim bu sayaçları ancak doğrulanmış kaynakla gösterir, kendine mal etmez.

## Çalışan asgari yönetim kabiliyeti
`python3 tools/enguru_management_v69.py --worklist governance/management-v69/EXAMPLE_TASKS.json`
Komut salt-okunur olarak görev envanterini, döngü/bağımlılık hatalarını, READY adaylarını, PAUSED/HOLD kayıtlarını ve eksik kabul gerekçelerini gösterir. `record_declared_accepted` yalnız girdide bildirilen şartlara göre hesaplanır, gerçek imza veya bağımsız kanıt olarak kabul edilmez. `evidence_authority=UNVERIFIED_INPUT_RECORDS` sabittir.

## Yetki ve güvenlik
Bu aday yalnız raporlama yapar. GitHub kaynaklarını güncelleme, issue/PR açma, iş başlatma, otomatik merge, Human Threshold kabulü veya ikincil DoneCheck otoritesi içermez. Mevcut `tools/enguru_five_minute_controller.py`, `governance/controller/`, İcra V6.9 dalları ve `main` korunur. CI yalnız PR doğrulaması ve elle başlatılabilen salt-okunur sınamadır; zamanlanmış görev yoktur.

## Tek kabul sınırı
A: Kod ve karşıt testler PR CI PASS.
B: GitHub'daki gerçek kaynak kimlikleri ve V3 SHA-256 bağı kanıtlı.
C: Yönetim raporu gerçek kaynak/kanıt/bağımsız doğrulayıcı/yetki düzeylerini ayrı gösterir.
D: Sahip onayıyla gerekli GitHub yayımı ve gerçek çalışma gözlemi.
A–D yerine gelene kadar `HOLD_GUVENLI_DUR`.

## Bu PR'ın teslim durumu
Foundation candidate only. İcra v6.9 çalışmaları ayrı ilerler. Yeni canonical yetki veya Verified Finish iddiası yoktur.


## Yönetim ürün kabulü ile yönetilen görev kabulünün ayrımı

Yönetim V6.9'un ürüne ait kabul şartları: (A) kontrollü GitHub kodu ve CI, (B) güncel canonical kaynak/kimlik, (C) gerçek görev ve kanıt durumlarını yanlış yetki üretmeden okuyabilme, (D) bağımsız ürün incelemesi, yetkili merge ve gerekli post-merge gözlemidir.

Mevcut Denetleyici görevleri `LABORY_PILOT_SOURCE`, `LABORY_PILOT_TEST` ve `LABORY_SAFE_REPAIR` Yönetim V6.9'un **girdi olarak izlediği** ayrı ürün işleridir. Bunların `0/3` resmî kabul sayacı, Yönetim V6.9 ürününe aktarılamaz. Yönetim; bağımsız DoneCheck ve owner kanıtı olmayan girdiye `HOLD` kararı vererek doğru çalışabilir. `README`, CI ve public receipt Yönetim V6.9'a Human Threshold yetkisi kazandırmaz.

### GitHub operasyon gözlemi ve aktarılabilir kanıt

`tools/enguru_management_v69_operation.py --live`, kayıtlı task ID'yi gerçek GitHub kaynak dosyasına, exact `main` SHA'ya, bot hesabına, public receipt hash'ine, görev fingerprint'ine ve gerçek worker job'a bağlar. PR CI, salt-okunur bu değerlendirmeyi `enguru-management-v69-live-evidence` adlı kısa süreli indirilebilir artefakta dönüştürür. Bu artefakt **Yönetim V6.9'un çalışan gözlem yeteneğinin kanıtıdır**; dahili Denetleyici receipt baytları ve bağımsız DoneCheck imzası yerine geçmez.

**Doğrulanmış gözlem:** Kaynak, worker ve public receipt için `PASS_GITHUB_PROVENANCE_OFFICIAL_HOLD`.

**Resmî ürün kabulü:** Bağımsız Yönetim V6.9 incelemesi, gereken DoneCheck™ ve owner Human Threshold™ kararı, yetkili GitHub PR merge ve post-merge gözlemine kadar `HOLD`. İnsan onayları gerçek yetkili mekanizma üzerinden verilir.

**Denetleyici görev kabulü:** Kendi canonical yetki ve DoneCheck kapılarında ayrıca ilerler; mevcut `PAUSED_AUDITED` ve `READY` durumlarına Yönetim V6.9 müdahale etmez.
