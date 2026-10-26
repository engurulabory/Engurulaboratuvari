# ENGÜRÜ Yönetim V27 — B10-03 Tarihsel v0.6 Provenance Teknik Kabulü

**21.10.2026 · STATE=PASS_EVIDENCE_B10_03_TECHNICAL_HISTORICAL_PROVENANCE · Önceki HOLD → kabul PASS_EVIDENCE · Yönetim sayacı 23→24/100.**

**Özgün şart:** `B10-03 — Tarihsel v0.6 kilitli ürün provenance korundu`. Kabul **yalnız geçmişte kilitlenmiş v0.6 kaynak–uygulama yürütülebiliri–yedek devamlılığı** için verilir. Güncel Native 0.8 sürüm kaynak kabulü, bütün `.app` dosya zincirinin bağımsız doğrulaması, signing/install, H1/H2/H3 ve Verified Finish bu kararın kapsamı dışındadır.

## 1. Kaynak ve hakikat

**Canonical kilit:** Yönetim PR #191 kaynak HEAD `c74738d951058b68a44e86c889fc7dc663566b75` altında:
- `governance/mac-engineer/PRODUCT_ROADMAP_V1.json` Git blob `9b62c0e4a8b85cf5764ef7bdfd98c783043f2860`: `v06FinalLock.state=VERIFIED_FINAL_LOCKED`, `mergedPr=165`, canonical merge `777904a957dfd475713dfd5de7b499c88247f4de`, exact-main gate kayıtları PASS.
- `governance/mac-engineer/SESSION_STATE_V1.json` blob `221163508963881434bd1d491468c12544642618`: `observedV06CanonicalCloseout` aynı resmi merge, local field VERIFIED_PASS, 7/7 real task, Mandatory DoneCheck PASS; `observedRuntimeAppProvenance`: `productSourceSha=28b901ab3303f4be3c7356b11218b62422f2da42`, `installedAppVersion=runtimeBuildAppVersion=0.6`, `allSourceShaEqual=true`, `allNativeHashEqual=true`, `nativeExecutableSha256=168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784`.
- PR #165 gerçekten **2026-09-22T17:47:13Z** tarihinde canonical `main`e merge edilmiştir; gerçek merge SHA `777904a957dfd475713dfd5de7b499c88247f4de`.
- `governance/mac-engineer/ARCHIVE_DECISION_V06.md` blob `9ca89e354e70f84cac6421df2922991b6762d804` exact-SHA install backup ve tarihsel provenance'ın koruma kararını içerir.

**Gerçek Mac korunma:** `ENGURU_V27_20261021T202457108071Z_YONETIM_KANIT.zip` gerçek byte SHA-256 `608ca91901524f4f5a60f66a099618e14f0b9d5727b5e110e2f4abc4a5f5dfa1`, ZIP CRC PASS; `ENGURU_V27_20261021T202457108071Z_SAHA.json` SHA-256 `7823e1fba1b4e67d088ff4ed886afc956ae1ae5b7c74c6ecb377fff16fd426a9`. 36 Mac `.app` backup adayından `ENGÜRÜ Mac Engineer_20260924T055750Z.app` sürüm **0.6** ile exact `nativeExecutableSha256=168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784` taşır ve resmî `SESSION_STATE_V1.json` kaydıyla eşleşir. Gerçek repo/app öncesi–sonrası `PASS_MAC_REPOS_AND_APPS_UNCHANGED`; tarihsel backup korunmuş. Teknik kaynak-kilit-yürütülebilir-yedek zinciri bağımsız sahada ve canonical GitHub kayıtlarında mutabıktır.

## 2. Kabul ölçütü ve bağımsız ikinci bakış

Özgün tekil B10-03 metni **tarihsel kilitli ürün provenance'ının korunmasıdır**. Canonical PR165 final-lock, kilitli sürüm/ürün executable kimliği, tarihsel Mac backup exact executable SHA ve gerçek preservation; **bu dar tekil şart için yeterli gerçek kanıttır**. V27 otomatik saha `HOLD_FINAL_LOCK_NOT_YET_LINKED` sonucu **aynı resmi merge/backup kanıtlarının o yürütücüde tek authority receipt içinde birleştirilmemesinden** doğmuştu; bu yeni Yönetim değerlendirmesi onaylı mevcut canonical kilit + tarihsel devamlılık verilerini **yalnız bu teknik ID için** mutabık kılar.

**Açık kalite kapısı:** Tam `.app` ağaç/Info.plist/icon/file-manifest eşitliğinin salt-okuma karşıt testi ileride ayrıca tamamlanacaktır. Bu test, güncel Native versiyon source+icon kabulü ve nihai rollback/installer kanıtı kapsamında kalır. Bu karar **tam bundle eşdeğerliği iddiası üretmez**. PR #165'in önceki v0.6 final-lock hükmünden güncel 0.8 onayı türetilmez.

**Başka statüler:** `B05-04` HOLD (yetkili branch/base owner receipt ve control local history ayrışma kararı); `B01-09/10`, `B06-07..10`, F01 owner/Ed25519/H1/H2/H3 0/12, F01–F06 0/6, Native/DoneCheck/Verified Finish HOLD.

## 3. Kapanış ve ileri hareket

`B10-03=PASS_EVIDENCE` özgün özgün ID olarak bir kere sayılır; eski v0.6 lock zaten teknik doğrulanmış olsa bile V27 yeni, gerçek Mac backup eşleşmesi bu teknik kontrol için doğru eksik bağı tamamladı. Başlangıç 23/100, yeni 24/100, açık 76; 32 hedefe 8.

**Sonraki:** `B05-04` source-owner branch/base attestation; F01 tek canonical owner/reviewer Ed25519 Human Threshold A/B kararı; F05 patch içeriğinin gerçek Native Swift/Info owner-reviewed candidate source/CI olması, ikon provenance ve yetkili canlı saha. Hepsi orijinal kullanıcı işi ve güvenli Finiş bağına sahiptir.

**Süzgeç:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT`.
