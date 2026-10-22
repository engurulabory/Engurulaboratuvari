# ENGÜRÜ YÖNETİM → İCRA V30 | 24→32 Yetkili Kabul Kapısı

**Tarih:** 22.10.2026. **Kaynak:** [V29 R2 Yönetim muhasebesi](./ENGURU_V29_R2_KABUL_MUHASEBESI_V1.md), [100 özgün ID ledger](./ENGURU_100_BIRIM_FINIS_SAYACI_V1.json). **Başlangıç:** 24/100 PASS_EVIDENCE, 76 HOLD. **Tur hedefi:** 32/100 (+8 yeni, benzersiz, tam kabul). **Resmî H1/H2/H3:** 0/12, F01–F06 0/6; Native ve Verified Finish HOLD.

## Hedef hiyerarşisi
**P0 kalıcı sabit hedef:** ENGÜRÜ Mac Engineer™ yerel Product Engineering Operator → Verified Finish → `BITTI_DUR`.
**P1 bağımlılıklar:** H1 Secure Enclave P-256 signer 4/4 → H2 canonical writer 4/4 → H3 GitHub↔OSi 4/4 → gerçek yetkili Native 0.8 source, licensed icon, signed installed GUI → Progress Core/Mandatory JSON/DoneCheck `verifyTask` → Ed25519 HumanReview → durable `recordVerifiedFinish()`.
**P2 bu tur:** K01/B05-04 iki Git deposunun yetkili branch/base acceptance, K02/F01 canonical owner/Ed25519 12 kriter, K03/F05 yapılmış Native kaynak onarımının yetkili source-owner review kabulü. F01–F06 bütün bağımlılıkları 76 özgün HOLD kontrolünde görünür tut.

**ENGÜRÜ Süzgeci™ 8 aşama:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Pozitif, yapıcı ve gerçekçi mühendislik dili; `STATE→CLAIM→EVIDENCE→NEXT ACTION→VERDICT`. Gerçek yetkide İLERLE, doğrulanmış owner/signer/HumanReview yetki kapısında GÜVENLİ_DUR ve tek kapsamlı insan karar nesnesi.

## V29 R2'den değişmeden devralınan hakikat

- Engineer PR #14 gerçek Native Swift + Info.plist source commit `81df3d09a45e14c559b2e95a545442ce72ea8503`. Swift blob `fdfaa779a76f131f6f49a1a3f9f160e22477916f`, Info blob `a280998cefaaa89556ca2ad1dd08101284250620`.
- Exact-head GitHub Actions `39677202520` SUCCESS; macOS Swift build PASS, runtime 121/121 raporlanmış ve CI test adımı PASS. İzole V29 14/14 pozitif-negatif kaynak regresyonu mühendis raporu kanıtıdır.
- K03 için önceki kullanıcı `review feature branch'de kaynak onarımı` izni **uygulandı**. V30'un asıl ihtiyacı **yetkili source-owner submitted review kararı**, ikon lisans/provenance, kabul edilmiş yerel source/stage/0.8 versiyon eşliği, ardından ayrı signing/install/live saha kapsamıdır. Native patch ve aynı izole build yeni baştan üretilmez.
- Mac gerçek arşiv `PASS_V29_AUDIV13_EVIDENCE_ARCHIVED` kullanıcı Terminal receipt'inde; orijinal V29 raporu SHA `5e800527c5f1d34ba8b9dd24057541c1833cef3e2f0a59e5451413186e93fca8`. Yönetim'e sunulan R2 dosyası ise ayrı SHA `b01cb93e6fc43ea20bf5a51ea361241a2c4872e7bb962d13f362f4a49e2a4a1c`; aynı dosya kimliği gibi kullanılmaz.
- PR #14 ve PR #191 açık, merge edilmedi; submitted reviewer approval sayısı 0. Yönetim ledger 24/100, B05-04/F01/source-owner kabul şartları HOLD.

## V30 gerçek mühendislik işleri ve owner karar nesneleri

**K01 — B05-04:** V27 Mac control/product exact HEAD+merge-base ve 634/185 local-only geçmişini, güncel PR14/PR191 HEAD/dirty ile salt-okuma yeniden bağla. İki depo canonical source owner'ın kimliğini, repo izin kaynağını, scope, expiry ve anlaşılır divergent-history preservation kararını doğrula. Gerçek owner receipt `DECISION_ID, OWNER_ID, AUTHORITY_SOURCE, REPO, BRANCH, BASE, PR_HEAD, LOCAL_HEAD, MERGE_BASE, DIRTY_SHA, PERMITTED_SCOPE, TIMESTAMP, RECEIPT_SHA` ile alınır. Bu B05-04 kabulünü değerlendirir; H2/H3 merge/push/reset yetkisini ayrı tutar.

**K02 — F01:** 12 kriterin mevcut canonical owner/reviewer Ed25519 yetkisi A yolu exact source/commit/blob ile bulunur; gerçekten kaynak boşluğu ispatlanırsa B mevcut dar kapsam Human Threshold™ kararına gidilir. Reviewer public key ve kimlik, scope, expiry/revocation, kriter SHA, Mac→Progress Core→Mandatory JSON→`verifyTask` binding ve gerçek signed durable receipt zorunlu. H1 signer Secure Enclave P-256 kendi otoritesindedir.

**K03 — F05:** Kullanıcının yetkili inceleme dalı kod onarımı yapıldı. Yetkili ürün source owner tarafından **gerçek submitted PR review** ve commit `81df3d09...` source acceptance receipt'i alınır. Source-owner kimliği/authority scope bulunamıyorsa `OWNER_ID=UNVERIFIED` olarak tek net owner karar talebi sunulur. İkon/0.8 sürümü, Mac local stage/source SHA ve before-after read-only kanıtı ayrıca hazırlanır. Signing/install/live GUI/status/restart/concurrency/persistency/rollback yalnız ilgili ayrıca yetkilendirilmiş saha prosedürüyle.

**Bağımsız kabul adayları:** `B05-07` exact PR commit CI / gerekli CI matrisi ve branch-protection scope; `B05-06` user dirty paths ve owner-preservation receipt; `B01-09/10` verified source owner/snapshot; `B06-07/08/09` yetkili source-stage-Info+0.8 bağları; `B07-04/06` real source owner review + CI. Yalnız özgün şartı TAM olan ID ayrı `PASS_ADAYI`; bunlar önceden kabul edilmiş varsayılmaz.

## 24→32 ve Verified Finish kabul sözleşmesi

Her yeni ID: `ORIGINAL_BXX_ID | EXACT_CONDITION | PREVIOUS_HOLD | SOURCE_REPO_BRANCH_HEAD_BLOB_SHA256 | REAL_EXECUTION | POSITIVE+NEGATIVE_TEST | REQUIRED_OWNER/REVIEWER_RECEIPT | EVIDENCE_SHA256 | MANAGEMENT_VERDICT`. Mühendis yeni kontrolü önerir; Yönetim bağımsız doğrular. Human review ve owner makamı sahici kararı verir. F01–F06 altı alan, H1/H2/H3 4+4+4, Native, DoneCheck ve verified-finish kapıları birbirlerinin yerine sayılmaz.

İCRA tek turda bütün izinli ve güvenli işleri üretip sonuçlandırır; tamamlanan eski testleri yeniden puanlamaz. **Rapor:** ilk altı satır `STATE / SAYAÇ=24→N,HEDEF=32,KALAN / YENİ_PASS / F01 / F05 / RESMÎ+RAPOR_SHA+SONRAKİ`. Ardından AudiV13 JSON/MD içinde **76 açık kontrolün her biri**, yapılan onarım/kabul kanıtı, kalan işler, kanıtlı kök neden ile hipotez ayrımı, her engelin owner/izin çözümü/sonraki bağımlılığı; resmî finiş matrisi. Gerekiyorsa gerçek ZIP/SHA bağlantısı ve bir tam `zsh` Mac Terminal bloğu.

**Kalıcı finiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck → HumanReview → Verified Finish → `BITTI_DUR`.
