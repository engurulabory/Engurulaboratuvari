# ENGÜRÜ YÖNETİM — V29 R2 Sahici Kaynak Onarımı ve Resmî Kabul Muhasebesi

**Tarih:** 22.10.2026. **Hüküm:** `PASS_PR14_REAL_SOURCE_AND_CI / HOLD_AUTHORIZED_OWNER_AND_NATIVE_FIELD`.

## Hakikat ve doğrulama

- Kullanıcı V29 R2 devir dosyası `ENGURU_V29_R2_TAM_FINIS_KAPANIS_SOZLESMESI_YONETIM_DEVIR_20261022(1).md`: 195371 byte, model çalışma alanında bağımsız SHA-256 `b01cb93e6fc43ea20bf5a51ea361241a2c4872e7bb962d13f362f4a49e2a4a1c`. Bu R2 dosyasının hash'i, Mac'te arşivlenen **özgün V29** raporu `5e800527c5f1d34ba8b9dd24057541c1833cef3e2f0a59e5451413186e93fca8` hash'inden ayrıdır. Mac'teki arşiv PASS hükmü sağlanan Terminal receipt'idir; bu Yönetim oturumu Mac diske doğrudan erişmiş değildir.
- Engineer [PR #14](https://github.com/engurulabory/enguru-mac-engineer/pull/14), HEAD `81df3d09a45e14c559b2e95a545442ce72ea8503`, OPEN, MERGED=false. Commit API gerçek değişen dosyalar yalnız `execution_prep/native_app/EnguruMacEngineerApp.swift` Git blob `fdfaa779a76f131f6f49a1a3f9f160e22477916f` ve `execution_prep/native_app/Info.plist` blob `a280998cefaaa89556ca2ad1dd08101284250620` olarak doğrulandı. Önceki patch artık gerçek feature-branch source diff'idir.
- Exact-head GitHub Actions run `39677202520`, `ENGURU Mac Engineer Product CI=SUCCESS`; Python runtime ve gerçek macOS Swift stage build job steps PASS. V29 kaynak raporunda 121/121 Python ve 14/14 izole regresyon PASS raporlanmıştır; 14/14 sonuç bu Yönetim oturumunda yeniden koşturulmamıştır.
- Management [PR #191](https://github.com/engurulabory/Engurulaboratuvari/pull/191), HEAD `ff03e1eab85d20ac955338302729415bc48309c5`, OPEN, MERGED=false. PR #14 ve #191 submitted reviewer approval count `0`. GitHub `engurulabory` repo admin olması tek başına 12 kriter Ed25519 owner/reviewer grant'ını ispatlamaz.
- Gerçek yönetim 100-ledger `24/100`, PASS_EVIDENCE 24, HOLD 76; `B05-03` ve `B10-03` korunur. H1/H2/H3 0/12; F01–F06 0/6; Native/live/DoneCheck/Verified Finish HOLD.

## Kabul kararı ve ana kök mekanizma

**İCRA'nın V29 sonucu:** `F05_PR14_SOURCE_COMMIT=PASS`; `SOURCE_DIFF_AND_MACOS_CI=PASS`; `SOURCE_OWNER_ACCEPTANCE=HOLD`; `AUTHORIZED_LOCAL_MAC_STAGE=HOLD`; `SIGNED_INSTALLED_LIVE_NATIVE=HOLD`. Bu teknik kazanım korunur ve V30'da tekrar patch hazırlanmaz.

**Neden yeni Bxx ✓ yok:** `B05-04` owner branch/base receipt; `B02-03/04` canonical 12 kriter owner+Ed25519 reviewer identity/key/scope; `B06-07/08/09` accepted source owner + local HEAD/stage/Info.plist version; `B07-04/06` real owner source-review approval ve scope, tümü hala eksik. Onaylı PR source diff, bu şartları kendiliğinden karşılamaz. Sorunun doğrulanmış kısmı kabul yetkisi/receipt eksikliği; var olabilecek gizli canonical grant bir hipotezdir.

## V30 üç ayrı gerçek karar ve ilerleme zinciri

**K01 / B05-04:** Yetkili *iki repo* branch/base/ancestry owner receipt; güncel control/product base+PR HEAD, local Mac HEAD/dirty/merge-base, 634 control ve 185 product local-only commit preservation. Owner identity + authority source + scope + karar SHA. Source-history remote mutation için ayrıca gerçek H2/H3 yetkisi.

**K02 / F01:** A mevcut exact canonical 12-kriter owner/reviewer Ed25519 key authorization; gerçek boşluk kanıtlanırsa B yetkili dar Human Threshold grant/attestation; kriter SHA, commit/blob, reviewer scope/expiry/revocation, signed receipt. H1 Secure Enclave P-256 ayrı issuer/signature kapısı.

**K03 / F05:** K03 kullanıcı review-branch source-write izni **kullanıldı ve teknik iş tamamlandı**. Şimdiki ihtiyaç **gerçek source-owner/reviewer review kararı** ve ikon license/provenance; owner grant sonrası exact Mac local source-stage-head + 0.8 version/Info.plist karşılaştırması ve resmî kabul. Signing/install/live GUI/rollback ayrı yetki.

**Bağımsız güvenli işler:** `B05-07` current exact-head CI evidence vs original acceptance/branch protection; `B05-06` dirty path owner/protection plan; `B01-09/10` canonical owner/snapshot; `B06-07/08/09` Mac local/stage/source *read-only comparison*; `B08-04` rollback before/after preparation; `B07-07` icon license provenance source search. Bunlar PASS kotası değil, özgün şartları sağlayınca Yönetim'e adaydır.

## Mühendislik teslimi ve kabul sırası

**Son teyitli:** 24/100; V30 tur hedefi 32/100 (+8). **Finiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native signed/installed/live 0.8 → `verifyTask` → Ed25519 HumanReview → durable `recordVerifiedFinish()` → `BITTI_DUR`. Tekil özgün Bxx kontrol yalnız tam source+execution+test+required owner receipt ve Yönetim bağımsız doğrulamasıyla ✓ olur.

**Rapor:** İlk 6 satır gerçek N, +kanıtlı özgün ID; sonra AudiV13 JSON/MD; 76 mevcut HOLD'un her biri için kök neden (kanıt/hipotez ayrımı), gerekli fark, owner, gerçek yürütme/onarım, test ve receipt, kalıcı çözüm, sonraki işe bağımlılık; yeni ZIP/arşiv yalnız gerçek yeni teknik farkın kanıtı için.

**ENGÜRÜ Süzgeci™ mevcut 8 aşama:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Pozitif, kanıtlı dil `STATE→CLAIM→EVIDENCE→NEXT ACTION→VERDICT`; yetkili `İLERLE`, gerçek insan kapısında `GÜVENLİ_DUR`.
