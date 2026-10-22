# ENGÜRÜ Yönetim — B05-06 özgün kontrol kabul kararı

**Tarih:** 2026-10-22
**KONTROL_ID:** `B05-06`
**ORIGINAL_CONDITION:** Dirty-path ve korunacak farkların sahipliği çözüldü
**PREVIOUS_STATE:** HOLD
**MANAGEMENT_VERDICT:** PASS_EVIDENCE — dar kapsam: owner-approved preservation in place for inventoried paths

## Bağımsız incelenen gerçek kayıtlar
- Gerçek Mac saha raporunda `SELF_TEST=PASS_9_CHECKS`, `SOURCE_PRESERVED=PASS`, `ALL_PATH_FINGERPRINTS=PASS`, 115 Git normal-dirty kaydından açılmış 138 normal dosya kaydı.
- Mac inventory SHA-256 `fc1f5e14921f42addbca2549dbf14c6dd5a210b4b8c7b71ec880f8e934717044`; owner acceptance packet SHA-256 `6864aab52e8043199a9feae5cea15d05dc56601ce7f7d42dcaa51867852aa1c6`. Bu değerler kullanıcı Mac terminali ve GitHub owner karar kaydından alınmıştır. Mac üzerindeki özgün inventory baytları bu Yönetim oturumunda bağımsız yeniden hashlenmemiştir.
- GitHub PR #191 commit `d4cc4cc448586b082141389f77e9773095ae24a2`, eklenen tek dosya `governance/mac-engineer/progress/ENGURU_B05_06_OWNER_SCOPE_DECISION_20261022.json`, Git blob `c2d5d671afeeca909dabaa58e3c25b8ae10ee493`.
- Bu JSON'un 138/138 kabul satırı repo+path anahtarında benzersizdir; 136 control (11 tracked/125 untracked), 2 product tracked. Her satır SHA-256 biçimine sahiptir ve `PRESERVE_IN_PLACE_OWNER_APPROVED` kararını içerir.
- Açık gerçek insan kararı `onaylıyorum...`, karar konusu tam 138 kayıtlı dosyanın mevcut yerinde korunmasıdır. Bağlı `engurulabory` GitHub kimliğinin kontrol repo yetkisi `admin` olarak doğrulandı. GitHub chat→kimlik kriptografik bağ/Ed25519 reviewer imzası **mevcut değildir**; bu B05-06 kapsamlı koruma onayı için ayrı resmî Ed25519 H1/H2/H3 yetkisi iddia edilmez.
- Aynı source commit `d4cc4cc...` üzerinde GitHub Actions beş gerekli workflow `completed/success`: ENGURU Management Progress Verification, Labory Final Gate, PARK Adapter CI, IP Model Trust Gate, IP Model Trust Fleet.

## Karar gerekçesi
Özgün B05-06 şartı **dirty-path ve korunacak farkların sahiplik çözümüdür**. Gerçek path envanteri, hash kimlikleri, her yol için kullanıcı `PRESERVE_IN_PLACE` onayı ve kapsamlı kalıcı GitHub owner receipt'i bu şartı karşılamaktadır.

Bu teknik kabul **B05-04 branch/base ancestry ownership**, **B05-05 local/remote parity**, **B05-09 authorized remote push**, **F01 Ed25519 HumanReview**, **F05 source promotion**, **Mac canlı Native kabul** veya **H1/H2/H3 resmî 4/4** sonucu değildir. Bunlar ayrı HOLD kapılarıdır.

**Sayaç:** `25/100 → 26/100` (bir benzersiz özgün ID); kalan 74. En son Yönetim 100-ID JSON/Markdown ve GitHub CI aynı kabul işleminde doğrulanır.

**Sonraki aday:** `B05-04` için iki repo owner scoped branch/base/merge-base lineage kararı; alternatif olarak daha erken tamamlanabilir özgün kabul ID. İCRA mevcut owner/source/saha delillerini yeniden kullanır, aynı 138 dosyanın koruma onayını tekrar istemez.

**Kalıcı hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck `verifyTask` → Ed25519 HumanReview → durable `recordVerifiedFinish()` → `BITTI_DUR`.
