# ENGÜRÜ Yönetim → İCRA V23 | Tam Mühendislik Finişi

**Kaynak:** PR #191 kontrol listesi, PR #14 mühendislik kaynağı, V22 gerçek Mac raporu SHA-256 `80a8a7f9d4f2f27c2274a823fffaa442cd65331378f4ed2d227bcf31f8b5c745`. **Yetki:** Yönetim kabul sayacını yönetir, İCRA güvenli mühendislik yürütmesini sahiplenir, canonical owner/reviewer korumalı kararı verir.

## Hedef hiyerarşisi
- **P0 Ana hedef:** ENGÜRÜ Mac Engineer™ yerel Product Engineering Operator ürününü tam yetkili Verified Finish ile `BITTI_DUR` durumuna ulaştır.
- **P1 Kabul sırası:** H1 Secure Enclave P-256 signer 4/4 → H2 canonical writer 4/4 → H3 GitHub↔OSi 4/4 → Native OSi gerçek saha kabulü → DoneCheck `verifyTask` / yetkili `recordVerifiedFinish()`. Altı F01–F06 engelinin bağımlılıkları bütünde korunur. PiLive ayrı sonraki ürün.
- **P2 Güncel iş:** F01 tek ana iş; F05 tek bağımsız destek. F01: yetkili 12-kriter/owner/reviewer A/B Human Threshold kararı ve Mac–Progress Core–DoneCheck bağlantısı. F05: V22 Native 0.8 dört dosyalık gerçek birleşik kaynak patch'ini yetkili PR #14 review'a taşı; ikon provenance, sürüm/source kabulü ve canlı lifecycle regresyonu şartlarını kapat.

## İCRA'nın bütün görevleri

**Sorumluluk:** Mimari, envanter, kaynak/HEAD analizi, doğrulanmış kök neden, bağımlılık ve maliyet planlama, çözüm tasarımı, gerçek kod yazımı, onarım, build, entegrasyon, Mac çalışma, CI/Git/PR, güvenlik ve provenance, pozitif/negatif/adversarial test, restart/concurrency/shutdown/recovery, gerçek kanıt SHA, Human Threshold sınırı, DoneCheck, dokümantasyon, kabul, rapor ve sonraki kesin karar.

**Tek tur döngüsü:** (1) son doğrulanmış SHA/canonical kaynakları oku; (2) P0/P1/P2 ve F01–F06 bağımlılık/owner/acceptance eşle; (3) en yüksek değerli uygulanabilir güvenli onarımı seç; (4) mevcut mimaride gerçek diff/patch ve entegrasyonu uygula; (5) gerçek SDK, pozitif/negatif, recovery ve ilgili canlı testleri koş; (6) kaynak/uygulama/dirty/history korumasını karşıt testle; (7) her tekil kontrol ID için tam receipt çıkar; (8) kalan yapılabilir bağımlılıkları bitir, gerçek insan kapısında tek kesin karar üret. İlk teşhis veya ilk PASS sonrasında döngü sürer.

## Kalıcı kabul şartları
- Her `Bxx-yy`: orijinal 100 ID'nin tam kabul ölçütü, önceki HOLD, yetkili scope/owner gerekliyse gerçek izni, kaynak commit/blob ve hash, gerçek pozitif/negatif test, doğrulanmış receipt; mühendis `PASS_ADAYI`, Yönetim yalnız karşılanmış ID'yi ✓ sayar.
- H1 4/4 gerçek yetkili P-256 signer/challenge/grant/receipt; H2 4/4 H1 yetkisiyle atomic/idempotent writer ve audit; H3 4/4 H2 yetkisiyle exact remote ancestry/parity, owner review/CI ve remote receipt.
- Native: source, ikon lisansı/provenance, sürüm 0.8, gerçek signing/kurulum, restart/eşzamanlı çalışma/kapanış/kalıcılık kullanıcı testi; DoneCheck: `verifyTask`, yetkili Ed25519 HumanReview ve `recordVerifiedFinish()` durable audit. Gerçek 12/12, Native ve DoneCheck sonrası `BITTI_DUR`.
- Teknik derleme ve salt-okuma inceleme resmî kabulden ayrıdır. Çalışan 0.8, tarihsel v0.6, 185 local commit, tracked dirty yollar ve AudiV13 korunur.

## Yönetim ilerleme partileri

**Şimdi:** 22/100; önceki 30/100 ara hedef, **V23 tur hedefi 32/100 (+10 yeni kanıtlı kontrol)**. Her yeni raporda gerçek N'yi Yönetim bağımsız değerlendirir; sonraki tur N→N+10. Bu sayaç ürünün fiilî yüzde tamamlanma tahmini değildir. 32'ye varınca tüm uygun güvenli işlere devam; yetki kapısında 32-N farkını ve kesin kararı göster. Hedef sayı için yeni kriter üretme veya eski PASS'i yeniden sayma.

## V22'den devralınan gerçek iş

**F01:** `F01_TEK_HUMAN_THRESHOLD_KARARI_V22.md` SHA `666c73f2ac30b912f23735a78d0191bd2905a11d7d7f8cb960e1255c02f7c67c` rapor-manifest değeri; owner/reviewer Ed25519 ve canonical 12 kriter kararı HOLD. PR #191 inceleme talebi kayıtlı; yetkili karar receipt'i bekleniyor.
**F05:** `F05_V22_PR14_TO_V08_UNIFIED_REVIEW.patch` SHA `7b2b8b44a2a07d5e4c4ed32c109a0e38066361220181a58b0f5e8a5afa75ebf3` rapor-manifest değeri; gerçek Swift build RC0, kaynak SHA `4864834bebadce99f606860a336e616837111c66e96ec807c50eba2f33e1b27f`. PR #14 owner review kaydı var; gerçek patch baytları yetkili inceleme yüzeyine SHA doğrulamasıyla ulaştırılır. Restart/concurrency/shutdown canlı davranış testi ayrıca gerekir.

## Zorunlu devir raporu

**Başta altı satır:** STATE; SAYAÇ=22→N/100 HEDEF=32 KALAN=32-N; YENİ_PASS=ID; F01; F05; RESMÎ H1/H2/H3, F01–F06, Native, Verified Finish, RAPOR_SHA256 ve SONRAKİ.

**Sonra tam rapor:** (1) yapılan her gerçek mühendislik işi ve exact kanıt; (2) ayrı kontrol ID kabul matrisi; (3) P0/P1/P2 ve F01–F06 üzerinden **kalan tüm işler**; (4) her **engel + kanıtlanmış neden + bağlı ID + yetkili sahibi**; (5) her engelin **somut çözümü, gerekli kanıt/izin, sonraki eylemi**; (6) güvenlik/kaynak koruması ve git diff; (7) bitiş şartlarına göre H1/H2/H3/Native/DoneCheck/Verified Finish özeti. İzlenen rapor ve sonuç AudiV13 altında gerçek JSON/MD dosyasıyla kanıtlanır.

**Teslim biçimi:** ZIP gerekiyorsa gerçek indirme bağlantısı/ad/SHA ayrı; Mac Terminal komutu tek eksiksiz `zsh` kopyala-yapıştır kod bloğu; kısa sonuç ayrı. Human Threshold veya owner review kapısında diğer güvenli işleri tamamlayıp `GÜVENLİ_DUR` ve **tek kesin insan kararı** sun.

**Kalıcı sabit finiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → Verified Finish → `BITTI_DUR`.
