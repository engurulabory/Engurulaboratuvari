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
