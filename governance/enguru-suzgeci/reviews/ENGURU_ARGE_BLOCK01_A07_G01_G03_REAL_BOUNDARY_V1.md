# BLOK 01 A07 — G01/G02/G03 Kanıtlı Saldırı Orakeli ve Uygulama Sınırı

SOURCE OF AUTHORITY: V4.2 40 iş sözleşmesi; A07 = G01–G03 saldırı girdisi, orakel ve gereksinim/test ayrımı.
STATE: G01_IN_PROCESS_GUARD_IMPLEMENTED / G01_DURABLE_RECONCILIATION_HOLD / G02_REAL_RELATIONAL_AUTH_HOLD / G03_REAL_TIME_AUTH_HOLD
SCOPE: GitHub review-only; NOT actual Mac OSi field PASS or official A07 acceptance.

| Garanti | Gerçek saldırı girdisi | Kabul orakeli (saha şartı) | Test edilen gerçek kod/kanıt | Eksik üretim bağlantısı |
|---|---|---|---|---|
| G01 dış etki / idempotency | Aynı fatura key'i ile farklı müşteri/ödeme; eşzamanlı aynı key; sağlayıcı belgeyi ürettikten sonra mail onayının kaybı; işlem sırasında restart | Aynı yetkili sipariş için tek dış fatura etkisi; farklı müşteri kimliğinde HOLD; kayıp onay sonrası provider sorgusu ve kanıtlı uzlaştırma; restart'ta da tek etki | `cores/billing/billing_core.py` request fingerprint ve atomik in-process reserve/commit; `tests/test_arge_block01_a07_runtime_v1.py` gerçek fonksiyon çağrısı, fault injection, concurrency | Bilinen kalıcı idempotency rezervasyonu, provider-reference correlation, lost-ack reconciliation, crash/restart actual provider testleri gerekir |
| G02 ilişkisel yetkilendirme | Bir tenant kullanıcı kimliği ile başka tenant fatura/evidence kaydı; rol/nesne/eylem mismatch; imzasız veya süresi dolmuş grant | Her okuma/eylemde principal–tenant–resource–action ilişkisi canonical grant ile eşleşir; çapraz tenant sıfır görünürlük ve dış etki | `shared_ai/security_review.py` güvenlik bulgusu ve trust boundary için review HOLD mekanizması vardır; fatura çekirdeğinde tenant-ilişkisi enforcement kanıtlanmadı | Gerçek tenancy/grant authority ile nesne bazlı policy enforcement, negatif saldırı testleri ve verifier |
| G03 zamansal kaynak doğruluğu | Eski müşteri vaka sayfası CURRENT diye kullanılır; yeni karşıt kaynak daha güncel; expires/observed_at eksik veya future timestamp | Kaynak kimliği/sürüm/çapa, gözlem ve geçerlilik zamanı, geçerli kriptografik köken ve karşıt kaynak çözümlemesiyle eskimiş iddia HOLD | V428 `source_conflicts`: Replit Temporal tarihsel kullanımı ve daha yeni Restate vakası, `tests/test_arge_block01_18_cases_v428.py` karşıt güncellik kaydı | İmzalı source provenance, güncel as-of interval ve runtime clock guard/bağımsız kaynak doğrulaması |

## Kabul sınırları

1. A07 için gerçek mühendislik test PASS, G01–G03'ün aynı anda gerçek saha PASS olduğu anlamına gelmez. `MemoryIdempotencyStore` in-process'tir ve process restart süresince durable persistence sağlamaz.
2. Review-only BillingCore değişimi tek müşteri/ödeme fingerprint'i ve pending reservation ile replay güvenliğini yükseltir. Provider response ve mail sonrası crash için prod-ready exactly-once iddiası yetkili uçtan uca kurtarma testi gelince değerlendirilecektir.
3. G02 policy review mekanizması runtime tenant-role-object authorization yürütücüsü değildir. G03 V428 karşıt güncellik testi canlı zaman/kripto köken doğrulayıcısı değildir.
4. Beklenen resmî çıktı şu anda `A07=HOLD`; owner/issuer/reviewer ve Human Threshold kararları ayrı canonical makamda kalır.
5. Kod değişikliklerinin konusu mali belge dış etkisi içerdiği için `main`a merge kararı yalnız bağımsız code review + producer test kanıtı + mali süreç sahibinin Human Threshold onayıyla verilir.

NEXT: G01 için gerçek, kalıcı source of truth store ve provider status/reconciliation bridge; G02 için tenant-aware yetki referansına bağlanan test; G03 için sürüm ve geçerlilik zamanı yetkili imzalı delil. Ardından üçü aynı A07 kapsam kapısında uzlaştırılır.
