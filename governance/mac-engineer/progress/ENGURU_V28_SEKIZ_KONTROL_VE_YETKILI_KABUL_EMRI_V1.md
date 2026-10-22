# ENGÜRÜ YÖNETİM → İCRA V28 — 24→32 Finiş İlerletme Emri

**21.10.2026 · Güncel Yönetim kararı: 24/100 PASS_EVIDENCE; 76 HOLD; tur hedefi 32/100 (+8).** Kaynak [B10-03 kabulü](./ENGURU_V27_B10_03_HISTORICAL_LOCK_TEKNIK_KABULU_V1.md) ve [100'lü ledger](./ENGURU_100_BIRIM_FINIS_SAYACI_V1.json). V27 gerçek Mac JSON SHA-256 `7823e1fba1b4e67d088ff4ed886afc956ae1ae5b7c74c6ecb377fff16fd426a9`, dış ZIP SHA-256 `608ca91901524f4f5a60f66a099618e14f0b9d5727b5e110e2f4abc4a5f5dfa1`, V27 R1 bağımsız GitHub ve Mac kaynak değerlendirmesi devamlılık kaynağıdır. GitHub feature dalı Yönetim kaydı resmî Mac canonical merger veya HumanReview yerine geçmez.

## 1. Kalıcı hedef ve çalışma dili

P0 tek ürün: ENGÜRÜ Mac Engineer™ Product Engineering Operator güvenli kanıtlı Verified Finish → `BITTI_DUR`. P1 H1 Secure Enclave P-256 4/4 → H2 canonical writer 4/4 → H3 GitHub↔OSi 4/4 → Native 0.8 signed/live → Mandatory JSON / DoneCheck v1.2 `verifyTask` → Ed25519 HumanReview → yetkili `recordVerifiedFinish()`. P2 F01 ana owner/reviewer/criteria grant; F05 bağımsız kaynak ve GUI kabul. F01–F06 bütün bağları aynı anda görünürdür.

ENGÜRÜ Süzgeci™ sekiz aşama: Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Pozitif gerçeklik dili: `mevcut hakikat + gerekli fark`; `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT`; `İLERLE` gerçek kaynak+yetki+kanıt, `GÜVENLİ_DUR` açık Human Threshold'la.

## 2. V27 özgün karar ve ikinci göz

- **`B10-03=PASS_EVIDENCE`:** canonical v0.6 PR #165 real merge `777904a957dfd475713dfd5de7b499c88247f4de` (GitHub roadmap/session exact blobs `9b62c0e4a8b85cf5764ef7bdfd98c783043f2860` / `221163508963881434bd1d491468c12544642618`) + Mac korunmuş v0.6 backup executable SHA `168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784`. Tekil dar tarihsel provenance PASS; tam app bundle, icon/license, güncel v0.8 ve release bağı ayrı HOLD.
- **`B05-04=HOLD`:** kontrol repo main `5907b0f3...`, yerel HEAD `269854b8...`, PR `c74738d9...`; control base yerel HEAD atası değil; 634 local-only ve 101 PR-only commit. Ürün main `5432b9b1...`, local `26925c21...`, PR `fa93a318...`; 185 local-only ve 60 PR-only commit. Git merge-base hesapları taze Mac kanıtında. **Gerçek eksik:** yetkili repo/source owner branch/base lineage ve her iki divergence'ın preservation planı için exact SHA'lı scope-bound karar receipt. H2 remote-write, merge, replay, owner/Ed25519 insan kanıtı ayrı.

## 3. V28 tek bütünleşik mühendislik yürütmesi

**A — 32/100'e en kısa bağımsız kapanış:** Mevcut 76 HOLD kontrolün özgün şartını ve yeni kanıt potansiyelini değerlendir. Önce `B05-04` owner lineage record; `B01-09/B01-10` source owner and unified F01–F06 snapshot; `B06-07/08/09` accepted Native stage/entrypoint/0.8 source version; `B02-03/04` canonical owner/reviewer. Yetkili karar önkoşulu oluşmayan ID'ye PASS adayı atama; daha erken gerçek kapanacak başka mevcut ID varsa onu seç. 32 hedefi otomatik kabul değildir; gerçek N ve 32-N raporlanır.

**B — B05-04 gerçek karar:** V27 local/PR/main graph, exact merge-base ve fork preservation receipt'ini mevcut GitHub repo source owner'a bağla. İki repo branch/base sahibi ve korunacak dirty/634+185 local commits için gerçek scoped kabul kararı veya tek kesin Human Threshold dosyası. Owner'ın onayladığı lineage receipt oluşunca özgün B05-04 Yönetim acceptance incelemesine sun. Veriye dokunan rebase/reset/merge/push scope ayrı yetkili.

**C — F01 gerçek ilerleme:** GitHub PR #191 `F01_TEK_YETKILI_HUMAN_THRESHOLD_KARARI_V23.md` mevcut gerçek dosyası ve canonical DONECHECK authority modelini temel al. Owner/reviewer/Ed25519 public key/scope/expiry/revocation/12-criteria exact source A/B kanıtını sonuçlandırılabilir tek karara indir. İnsan yetkisi gerçekleşince Mac producer→Progress Core→Mandatory JSON→`verifyTask` gerçek pozitif/negatif bağlarını ve full receipt'i tamamla. H1 P-256 signer yetkisi Ed25519 reviewer'dan ayrıdır.

**D — F05 gerçek kaynak inceleme:** GitHub PR #14 review patch'i `F05_V23_PR14_TO_V08_LAUNCH_RETRY_FIX.patch` SHA `947693553748463068011b1fed994c5e37d0b95c7cdedf632982813ba959b55f`; V26 isolated Swift source `8c427579a71edd24502f89bfa93039acae30f7223e85820dd930284e35e1c6cf`. Yetkili **source-write grant** kayıtlıysa yalnız review feature branch üzerinde gerçek `EnguruMacEngineerApp.swift`/`Info.plist`/stage diff'ini exact SHA ve CI ile uygula, owner review'a gerçek changed-files sun. Kullanıcının önceki izni **yalnız review artefaktı yayınıydı**; gerçek Swift kaynak mutasyonu için ayrı source-owner kapsamı gerekir. İkon kaynak/hak/lisans owner receipt, 0.8 sürüm kabulü ve yetkili signing/install/live GUI/status/Doctor/restart/concurrency/shutdown/persistency/rollback ayrı kapıda sonuçlandırılır.

**E — F02/H1, F03/H2, F04/H3, F06/DoneCheck:** Her ana bağımlılığın yetki gerektiren bir sonraki şartını ve hazırlanabilir bağımsız güvenli testini aynı yürütmede ele al; H1 4/4 yetkisiyle H2 writer, sonra H3 remote transaction; Native saha ve gerçek `verifyTask`/HumanReview/`recordVerifiedFinish()` sonrası BITTI_DUR. Yetki sahibi kararı gereken kısımlarda tek net owner kararı ve tam exact receipt ihtiyacıyla GÜVENLİ_DUR.

## 4. Bitiş/kabul ve teslim

Her özgün `Bxx-yy`: önceki HOLD + **özgün şart** + gerçek kaynak/commit/blob/SHA + pozitif/negatif test + varsa yetkili owner/HumanReview receipt + Yönetim independent acceptance. Önceki B05-03, B10-03 ve tüm 24 kabul tekrar sayılamaz. Tam `.app` bundle hash/audit, native icon ve final user acceptance kendi ayrı kapısında değerlendirilir.

**Altı satır:** `STATE`; `SAYAÇ=24→N/100; HEDEF=32; KALAN=32-N`; `YENİ_PASS=ID/SHA/owner`; `F01`; `F05`; `RESMÎ=H1/H2/H3,NATIVE,DONECHECK,VERIFIED_FINISH,RAPOR_SHA256,SONRAKİ`.

**Tam AudiV13 JSON/MD:** bütün gerçek yapılan mühendislik, 76 HOLD kontrolün tekil kabul durumu, F01–F06 eksik/kanıtlı neden/hipotez ayrımı, **kalan tüm işler**, her engelin **sahibi, gerçek onarımı, gerekli yetkili kararı, exact receipt ve sonraki bağımlılığı**, before/after SHA ve Native v0.8/v0.6/dirty/commit koruma. Bir turda tüm izinli güvenli işleri bitir; kaynak/insan kapısında tek tamamlanmış karar dosyasını ilet.

**Kalıcı finiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck → HumanReview → Verified Finish → `BITTI_DUR`.
