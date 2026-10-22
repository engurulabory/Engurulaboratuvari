# ENGÜRÜ Tek Kapı Kabul Akışı™ — Yönetim / İCRA / Owner · V1

**Etkin yöntem bildirimi (22.10.2026):** [**Toplu Kanıt → Toplu Kabul V2**](ENGURU_TOPLU_KANIT_TOPLU_KABUL_AKISI_V2.md) Yönetim ve Mühendislik için güncel yürütme kuralıdır. V1'in per-ID hakikat, kanıt, owner ve bağımsız Yönetim kabul ilkeleri korunur; bir ana mühendislik hedefi için aynı turda **1–10 benzersiz özgün ID** bağımsız kabul edilip tek ledger işleminde kayda geçebilir. Güncel 27/100. V1'deki her yüzde için tek tur koşulu V2 ile güncellendi.


**Tarih:** 22.10.2026 · **Görev:** 24/100 patinajını kabul odaklı iş akışıyla çözmek; mevcut 100 özgün ID, Süzgeç sekiz aşama, owner/Human Threshold ve Ledger korunur. Yeni core, dokuzuncu aşama, paralel canonical kaynak ve otomatik sahte PASS oluşturulmaz.

## 1. İki ayrı hakikat ve açık sorumluluk

**Resmî kabul sayacı:** `ENGURU_100_BIRIM_FINIS_SAYACI_V1.json` ve insan-okur `.md`; **24 PASS / 76 HOLD**. Bu `24/100`, 100 özgün kabul kriterinin 24'ünün kanıtla karşılandığını gösterir; efor yüzdesi/harcanan süre/kaç test koşulduğu değildir.

**İlerleme kanalı:** Son mühendislikte yeni source diff, accepted or isolated build, kanıt, reviewer-ready karar ve çözülen engeller takip edilir; bu sonuçlar *tekil Bxx-yy kabulüyle* eşleşene dek `0` resmî artış gösterir. İkisini birbiriyle karıştırmak yanlış pozitif ilerleme üretir.

| İşlev | Yetkili rol | Çıktısı | Bitiş sınırı |
|---|---|---|---|
| Hedef/sıralama ve özgün Bxx kabul muhasebesi | Yönetim oturumu | `ID → PASS_EVIDENCE/HOLD`, proof+transaction+ledger | Yalnız özgün şart ve gerekiyorsa gerçek Human Threshold |
| Kaynak araştırma, mühendislik, onarım, test, evidence, source review hazırlığı | İCRA mühendisliği | Tek ID adayına `ACCEPTANCE_PACKET`, bağımsız güvenli işler | Gerçek source/test/owner kararı için son eksik kanıtı belirtir |
| Korunmuş source branch/base, 12-kriter reviewer, Native owner, sign/install | Gerçek yetkili owner/reviewer | exact scope+source+expiry/receipt signed/durable | GitHub admin izni tek başına bu atamaların hepsini ispatlamaz |
| Yalnız gerekli insan kararı | Ürün sahibi veya canonical kaynakta yetkilendirilmiş temsilci | Açık konu ve izin sınırı olan karar | Kullanıcının önceki PR #14 yalnız review-branch source-write izni zaten kullanıldı |

## 2. Yeni standart yürütme: İş → Kanıt → Yetki → Anında kabul → Sonraki iş

**A — Yönetim PRE-ACCEPT:** Her yeni emir **tek bir ilk kapanacak özgün ID**, o ID'nin birebir **ORIGINAL_ACCEPTANCE_CONDITION**, kabul için mevcut `EVIDENCE_READY`, gereken `OWNER_RECEIPT`, **tam eksik**, sınırlı mühendislik farkı ve **PASS sonrası sayaç N→N+1** içerir. Başka bağımsız uygun işler yalnız destek olarak sürer; ana hedef tek ve sabittir. `+10`, on adet gerçek tekil ID kabulünün **birikimli aşama eşiğidir**, bir çalışma turu kotası değildir.

**B — İCRA EXECUTE-TO-ACCEPT:** O tek ID için gereken tüm mevcut yetkili kaynakları oku, bütün erişilebilir güvenli farklılığı üret, gerçek test+SHA ve varsa exact Git HEAD/branch/diff/receipt teslim et. `ACCEPTANCE_PACKET` sekiz alanı: `ID | ORIGINAL_CONDITION | PREVIOUS_HOLD | REPO/BRANCH/HEAD/BLOB/SHA | REAL_EXECUTION | TEST_EVIDENCE | AUTHORIZED_OWNER_RECEIPT_OR_EXACT_GAP | PROPOSED_VERDICT`. Kapanışla ilişkili diğer safe work bu paketin ardında sürer. Eski PASS delili yeni sayım değildir.

**C — Yönetim SAME-HANDOFF-DECIDE:** Rapor geldiği **aynı değerlendirme turunda** her aday ID'ye tek karar:
- `PASS_EVIDENCE`: özgün koşul + gerekli gerçek kaynak/test/human gate tamam; yeni orijinal tek ID kabulü.
- `READY_FOR_OWNER`: teknik kanıt tamam, gerekli kanıt yalnız gerçek owner/reviewer grant veya review. Bir kesin karar nesnesi ve gerçek sahibini sun.
- `HOLD_TECHNICAL`: yapılması gereken gerçek kod, kaynak eşliği, saha/regresyon veya lisans kanıtı adıyla ve sonucu üretecek tek somut icra hareketiyle dön.
- `HOLD_SOURCE`: mevcut kaynağın otoritesi/HEAD/branch/yerel fark uyuşmuyor; exact SHA ve korunmuş izole transfer/fark planı ver.
Her HOLD için *yalnız kritik eksik* ve bir sonraki izinli bağımlılık kaydedilir; aynı 76 satırlık rapor her turda yeniden yazılmaz, güncel ana envantere kaynak gösterilir.

**D — ACCEPTANCE TRANSACTION:** Yönetim `PASS_EVIDENCE` hükmü verince aynı mantıksal kabul işleminde `ID.evidence`, tekil karar kaydı, JSON+Markdown sayaç birlikte mutabık hale getirilir. Bütünlük kuralı:
`COUNT(PASS_EVIDENCE across original 100 IDs) == verified_units`;
`100 - verified_units == remaining_units`;
`previous_state=HOLD` ve `unique Bxx ID`;
`official H1/H2/H3 4/4` yalnız bağımsız yetkili receipt ile yükselir.
Yazımdan sonra GitHub exact HEAD'de yeniden oku, CI+invariants PASS doğrula. **Bu terminal noktası kapanmadan yeni VNN icra emri verilmez.**

**E — NEXT:** `N→N+1` sonrası en yakın kapanabilir özgün ID seçilir. Bir destek F05 dalı ve gerekirse F01 gerçek Human Threshold kararı paralel hazırlanabilir; bir ana kabul işi kalıcıdır.

## 3. Bu dakikanın sahici işaretleri ve çözüm

**Yönetim 24/100**, hedef **32/100**, açık **76**. PR #191 ve PR #14 OPEN, real GitHub submitted reviews 0. V29 gerçek PR14 commit `81df3d09a45e14c559b2e95a545442ce72ea8503` yalnız `EnguruMacEngineerApp.swift` + `Info.plist` changed-files; native SDK CI SUCCESS. V30 gerçek Mac yerel Swift source eski SHA `4864834bebadce99f606860a336e616837111c66e96ec807c50eba2f33e1b27f`, PR onarım SHA `8c427579a71edd24502f89bfa93039acae30f7223e85820dd930284e35e1c6cf`; local shared build stage ABSENT. **Çözüm:** owner scope sonrası gerçek kaynak+stage izole uyumlaştırma ve owner review; eski patch'i yeniden üretme.

**İlk kapanış adayı `B05-07`**: Yönetim PR191 exact HEAD `9076a676de042f41ea296ea5ec76209a3be3bab7` beş workflow SUCCESS, mühendis PR14 HEAD `80bef8a6261e824973cf654b021b493721359329` Product CI SUCCESS; V30 engineer ayrıca default ruleset `#22452401` gereksinimini raporladı. **Özgün kriter:** `Gerekli exact commit CI kontrolleri PASS oldu`. **Değerlendirme açık:** sadece review-branch CI yeterli ise Yönetim teknik dar kapsam PASS verebilir; gerekli yetkili/integrated source HEAD, GitHub branch policy veya H2→H3 gate zorunluysa `READY_FOR_OWNER`/HOLD. Özellikle politika ve exact accepted-source kapsamını bağımsız doğrulamadan statü yükseltme. Bu ID için Yönetim ilk karar konusu: `GEREKLİ CI SETİ + HANGİ EXACT HEAD KABUL KAYNAĞI?`.

**K01 `B05-04`**: V30 Mac control `634/42` ahead/behind, 113 dirty (11 tracked/102 untracked); product `185/0`, 2 tracked. İki depo için canonical owner exact branch/base/dirt/history preservation attestation ayrı; PR #191/#14 review/merge yetkisi ayrı.
**K02 F01**: H1/H2/H3 yetkili 12 kriter source owner ve Ed25519 reviewer ID/public-key/scope/expiry A/B Human Threshold kararı gerçek insan receipt'ine ihtiyaç duyar; H1 Secure Enclave P-256 farklı signer.
**K03 F05**: source onarımı PR #14 üzerinde tamam; source-owner review, icon lisans/provenance, local Swift/stage/source paritesi, code-sign/install/live user acceptance ayrı kapılar.

## 4. Tamamen bitiş odaklı sayaç görünümü

Her Yönetim dönüşünün ilk paneli:
`ACCEPTED_UNITS=N/100`; `NEXT_MILESTONE=32/100`; `CANDIDATES_READY_FOR_MANAGEMENT=` gerçek ID listesi; `READY_FOR_OWNER=` açık ID/konu; `TECHNICAL_DONE=` güncel somut commit/test; `BLOCKER_TO_NEXT_PASS=` **tek** ispatlı engel; `FIRST_SAFE_ACTION=` bir gerçek icra komutu; `H1/H2/H3_OFFICIAL=`.

**Yöntem kararı:** Kullanıcıyı arşivle/test tekrar döngüsü yerine yalnız tam kapsamlı karar isteyen konuya taşı. İCRA teslim paketi yönetimce karar verildiği gün ledger kabulü kapanır. Yetki gerektiren ID için diğer güvenli kapanabilir ID seçilir; kanıtlanmış engel ve çözüm korunur.

**Kalıcı sabit hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck `verifyTask` → Ed25519 HumanReview → durable `recordVerifiedFinish()` → `BITTI_DUR`.
