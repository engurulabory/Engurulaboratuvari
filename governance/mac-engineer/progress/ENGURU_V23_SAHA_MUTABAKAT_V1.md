# ENGÜRÜ Yönetim — V23 gerçek saha mutabakatı ve kabul kapısı

**Tarih:** 2026-10-21. **Karar:** `PASS_REAL_ISOLATED_ENGINEERING / GÜVENLİ_DUR_AUTHORITY`. **Son teyitli 100 kontrol:** 22/100, tur hedefi 32/100 (+10), yeni PASS **0**. Resmî H1=0/4, H2=0/4, H3=0/4, F01–F06 kapanan=0/6, Native/Verified Finish HOLD.

## Bağımsız gerçek kanıt denetimi
- Mac `ENGURU_V23_SAHA_20261021T172652449869Z.json` **gerçek dosya SHA-256 PASS**: `381d2982f8495f8625359c3c323cc178678023fae998ed13d6e66ebb89fd9260`.
- `ENGURU_V23_TAM_MUHENDISLIK_DEVIR_20261021T172652449869Z.md` **gerçek dosya SHA-256 PASS**: `831061d77de3ff365399b5aba3817cc21bf8d3f1847cee5d44a55fedfd2422f0`.
- Kullanıcının ek Yönetim devir dosyası, özgün iki dosyadan ayrı bir özet belgesidir; özet dosya SHA: `620a7ec79865ffa2d0d191fc437b6ca0ce33fabd7a298a8c97c9dd30a2acf519`.
- Gerçek saha raporunda orijinal report-render hata `KeyError('source_protection')` ve gerçek sözlük alanı `source_preservation`. Kurtarma önceki koşu kanıtını tekrar doğruladı; kurtarmada Swift yeniden derlenmedi. Paket regresyon 18/18, kurtarma 27/27 PASS (27 test ≠ 27 kabul kriteri).

## Mühendislik kazanımı — F05
- Native 0.8 `launchInFlight=true` ataması, yürütücü varlık denetiminden sonra `try p.run()` önüne taşındı. Fark sınıfı: dar kaynak onarımı.
- Gerçek Mac SDK derleme PASS: Swift SHA `8c427579a71edd24502f89bfa93039acae30f7223e85820dd930284e35e1c6cf`, binary SHA `eeb5a2be81bb1a66d0bb2a4d297a1c633ad6e8988efae4fed5e9bb94f32f6b3a`.
- Gerçek izole Swift guard yürütücüsü 4/4 PASS: missing Python sonrası bayrak temizliği, yeniden deneme, concurrent launch ve shutdown. Negatif derleme 3/3 PASS; 4 kaynak dosyasının izole patch roundtrip PASS.
- `F05_V23_PR14_TO_V08_LAUNCH_RETRY_FIX.patch` (AudiV13) rapor-manifest SHA `947693553748463068011b1fed994c5e37d0b95c7cdedf632982813ba959b55f`. **Patch dosyasının özgün baytları Yönetim incelemesine henüz ayrı sağlanmadı ve PR #14 kaynak dalına işlenmedi.** Bu manifest değeri kaynak onayı değildir.
- Native `/api/status` read-only denemesi `HOLD_RUNTIME_STATUS_UNAVAILABLE` (`URLError`); gerçek `.app` GUI/live restart/concurrency/shutdown/persistency kabulü ayrı HOLD. 0.8 Info.plist, PR #14 0.6 kaynak ve ikon hak/provenance farkları açık.

## F01 — tek yetkili insan kararı
- `F01_TEK_YETKILI_HUMAN_THRESHOLD_KARARI_V23.md` manifest SHA `b928713a9117168ab93051f3dd1fecb8467a38c3f284ba8427668fbbe477da97` (orijinal karar dosyası ayrı bayt kontrolü ve erişim bekliyor).
- A: mevcut canonical 12-kriter sözleşmesi exact owner/reviewer/branch/blob/Ed25519 key authority kanıtı ile bağlanır. B: gerçek yetki boşluğu doğrulanırsa dar kapsam adayına yalnız yetkili Human Threshold kararı ve durable receipt verilir.
- `OWNER_ID`, `OWNER_AUTHORITY_SOURCE`, `REVIEWER_ID`, `REVIEWER_KEY_AUTHORIZATION`, `CRITERIA_SET_SHA`, `BRANCH_COMMIT_BLOB`, `MAC_PROGRESS_DONECHECK_BINDING`, `VERIFYTASK_RESULT`, `HUMAN_REVIEW_RECEIPT` zorunludur. `208a32c7a8b93204c6b9a414086c8d43bf9216b22c7ccbf53ef5dac09cde9ada` yalnız aday SHA'dır.

## 100 kriter ve bitiş kabulü
V23'ün `candidate_matrix` içindeki **27 özgün Bxx-yy kontrolü tamamı HOLD**, yeni sayaca geçecek benzersiz PASS **0**. Teknik source-repair/build ve 27 kurtarma testi orijinal 100 kontrolün yerini tutmaz. Başlangıç **22/100**, hedef **32/100**, fark **10** olarak korunur. Resmî 0/12 ve 0/6.

## V24 kesin yürütme bağı
1. **F01 önce:** Mevcut yetkili owner/reviewer A/B kararını PR #191'deki mevcut inceleme talebine bağlayarak gerçek owner ve yetkili Ed25519 reviewer kararını alınabilir hale getir; gizli anahtar istemeden kararın exact kaynak/receipt alanlarını sun. İnsan kararını insan verir.
2. **F05 paralel:** AudiV13'teki V23 gerçek patch + F01 karar dosyasını SHA ile doğrula ve yetkili owner inceleme yüzeyine dosyanın kendisini güvenli kapsamda teslim et. Reviewer'ın görebileceği patch gerçekten kaynağa uygulanmadıkça kaynak kabulü PASS olamaz. PR #14 source owner review, 0.8/0.6 sürüm mutabakatı ve ikon provenance kararı sonrasında gerçek Native canlı kabul kapıları yürütülür.
3. **Tek tur:** Yetki dışında kalan bağımsız güvenli işlerin tamamı yapılır. Gerçek izin/kanıt engelinde `GÜVENLİ_DUR` + tam kalan işler/engel sahibi/çözüm ve tek kesin karar; aynı test/rapor tekrarından puan üretilmez.

**Kalıcı finiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck Verified Finish → `BITTI_DUR`.
