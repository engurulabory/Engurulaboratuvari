# V6.9 Mimarlık — güven kökü uzlaştırma kararı V1
STATE=SOURCE_REVIEW_COMPLETE; AUTHORITY_BRIDGE=HOLD_REAL_OWNER_RECEIPT
MAIN_TARGET=NINE_CAPABILITIES_100_100; ACTIVE_TARGET=01_ARCHITECTURE
OWNER=engurulabory; EXTRA_PAID_API_TARGET=0; ROUTINE_MANUAL_STEPS_TARGET=0; OSI_MUTATION=0

## Canonical sınır
main/AGENTS.md: ürünün yetkili canonical sözleşmesi ve insan onayları önceliklidir. Süzgeç V3 ortak yöntemdir; tasarım 100/100 saha yetkisi yaratmaz.
main/tools/enguru_p06_authenticated_producer_adapter.mjs: Ed25519 ile producer provenance attestation doğrulama örneğidir. `AUTHENTICATED_PROVENANCE_CANDIDATE_ONLY_OFFICIAL_HOLD`; resmi issuer, DoneCheck ve Human Threshold HOLD. Adapter producer scope'u owner grant scope'u olarak kullanılamaz.
main/tools/enguru_management_v69_operation.py: tarihi receipt'in source_commit'i güncel main sha ile farklı olduğunda CURRENT_MAIN_SOURCE_DRIFT ve exit 50 doğrudur. Tarihi makbuz değiştirilemez; yeni current-main görev makbuzu kendi yetkili mekanizması üzerinden üretilir.

## İş ayrımı
1. Kaynak ve gerçek exact-HEAD SHA-256: otomatik bağımsız teknik test.
2. Makine kanıtı: isolated verifier, adversarial + CI immutable receipt; producer ve verifier ayrı.
3. Owner G2/G3: mevcut canonical owner grant, yetkili Ed25519 signer ve task/source bound gerçek doğrulama. Saha imzası yalnız gerektiğinde owner OSi yetkisinde.
4. DoneCheck v1.2/Human Threshold: farklı nihai kapı; tek owner korunur; teknik verifier resmi owner değildir.
5. Kaynak drift: tarihsel raporu koru; current-main için bağımsız yeni receipt; geçmiş receipt'in PASS statüsü current-main kabulü değildir.

## İlerleme
Design model accepted; GitHub technical preparation active; genuine owner signing authority and current-main receipt HOLD. Ana mimari final ve resmî G2–G6 HOLD; Mac OSi işlem 0. Dokuz yetenek sırayla korunur.
