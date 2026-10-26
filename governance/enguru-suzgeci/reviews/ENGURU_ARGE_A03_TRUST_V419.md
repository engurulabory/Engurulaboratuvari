# ENGÜRÜ V4.19 — A03 güven zinciri birleşik inceleme dosyası

## Sözleşme
STATE: REVIEW_ONLY / A03_AUTHORITY_HOLD / OSI_UNTOUCHED

Bu dosya V4.16–V4.18 kaynak keşiflerini tek inceleme paketi olarak birleştirir. ENGÜRÜ Süzgeci™ v2.4 sekiz aşaması, dört ayrı sayaç ve 6 blok/40 özgün iş korunur.

## Doğrulanmış kaynaklar
- DoneCheck reviewer Ed25519: https://github.com/engurulabory/donecheck/blob/main/src/runtime/node/reviewer-attestation.ts
- DoneCheck Verified Finish runtime: https://github.com/engurulabory/donecheck/blob/main/src/runtime/node/verified-finish-runtime.ts
- DoneCheck v1.2 ürün sınırları: https://github.com/engurulabory/donecheck/blob/main/docs/FULL_PRODUCT_CONTROLS.md
- ENGÜRÜ authority model: governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md
- ENGÜRÜ Hybrid Handoff v1 validator: tools/hybrid_handoff/validate_hybrid_handoff.py

## Kabul ve güven ayrımı
1. GitHub şema doğrulaması, kaynak SHA doğruluğu ve gerçek kaynak sahipliğinden ayrıdır.
2. Testteki reviewer/issuer booleans, gerçek imzalı grant veya trust anchor kanıtı değildir.
3. A03 özgün scope-bound grant; owner/issuer; bağımsız reviewer identity; yetkili public-key registry; sürüm/commit/source digest; son geçerlilik; gerçek makbuz her biri ayrı doğrulanır.
4. DoneCheck reviewer attestation, A03 issuer grant'i değildir.
5. Kâşifi'nin özgün canonical kaynağı henüz HOLD; KSF01–08 eşleştirmesi öneri statüsünde.
6. `main`, Mac OSi, gerçek signer ve audit ledger üzerinde değişiklik yapılmaz.

## %20 adversarial giriş/çıkış simülasyonu
Beş kontrol: trust anchor, A03 task grant, bağımsız reviewer, source pin, DoneCheck finish. Her seferinde birini (%20) kaldır; güvenli HOLD bekle. Kontrollerin hepsi var *varsayıldığında* olumlu tasarım kontrolü PASS bekler; gerçek kabul iddiası değildir. Bitiş simülasyonu gerçek saha kanıtı yaratmaz.

## Dört sayaç
- Tasarım/simülasyon: 100/100, **öz kapsam değerlendirmesi**.
- GitHub hazırlık: 50/100, yetkili gerçek kanıt bekliyor.
- Mac OSi saha: 0/100.
- Resmî kontrol: 0/40.

## NEXT ACTION
A03 görev yetki kayıtları ve Kâşifi canonical kaynak yolunu yetkili kaynakta kesinleştir; gerçek kanıtla source-pinned handoff ekini inceleme dalında sınayarak GitHub→OSi devir kabulüne hazırla.
