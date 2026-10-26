# ENGÜRÜ Yönetim → İCRA V29 | Tek İnsan Oturumu, Üç Ayrı Yetki Kararı, Gerçek Kabul

**Tarih:** 21.10.2026 · **Başlangıç 24/100** · **Hedef 32/100 (+8 özgün ID)** · **76 HOLD** · **H1/H2/H3 0/12**, **F01–F06 0/6**, Native/DoneCheck/Verified Finish HOLD.

**Ana hedef (P0):** ENGÜRÜ Mac Engineer™ Product Engineering Operator için gerçek `Verified Finish → BITTI_DUR`.
**Bağımlı sıralama (P1):** H1 P-256 signer 4/4 → H2 canonical writer 4/4 → H3 GitHub↔OSi 4/4 → Native 0.8 → `verifyTask` → Ed25519 HumanReview → `recordVerifiedFinish()`.
**Mevcut kapanış (P2):** B05-04 yetkili branch/base karar receipt; F01 12-kriter owner/Ed25519 A/B; F05 Native 0.8 changed-files source owner izni ve gerçek onarım.

## 1. Kanıtlı V28 devri ve doğru kapı
V28 gerçek Mac AudiV13 Terminal `PASS_V28_AUDIV13_EVIDENCE_ARCHIVED`, `PACKAGE_SHA256=PASS`, `MANIFEST_SHA256=PASS`, `SOURCE_PRESERVED=PASS`. Arşivdeki **özgün V28 raporu** SHA-256 `2aeb90516af1703f63813eb08a9f43e708a0a628748a02e9b4b13980cec5075b`; bu rapora ek **V28 R1** MD ayrı SHA/kimlik taşır. Ana arşiv işinin bitişi kaydedildi; yeni özgün `Bxx-yy` kabulü 0, Yönetim ledger `24/100` sürüyor. İki GitHub PR'ın submit edilmiş review sayısı `0`. GitHub 5/5 Yönetim ve Engineer CI sonucunun source-owner/HumanReview acceptance ile kapsamı ayrıdır.

**Kesinleşmiş engel:** Teknik kaynak, gerçek patch ve dallar hazır; kapıyı kapatan şey `owner/reviewer scoped authorization`, exact-head source mutation/acceptance ve gerçek field receipt'idir. Yeni ZIP/tekrar arşiv/salt-okuma test, bu belirlenmiş İnsan kararının eşdeğeri değildir.

## 2. Yetkili insandan tek oturumda üç AYRI karar nesnesi
Aynı insan görüşmesinde ele alınabilir; **yetkiler birbirinin yerine geçmez**. Her karar `DECISION_ID / SUBJECT / EXACT_SOURCE_BRANCH_COMMIT_BLOB / OWNER_ID / OWNER_AUTHORITY_SOURCE / REVIEWER_ID(if required) / PUBLIC_KEY_SCOPE(if required) / PERMITTED_OPERATIONS / EXCLUSIONS / EXPIRY / DECISION / RECEIPT_SHA256 / TIMESTAMP` alanlarını doldurur. İnsan tarafından ve mevcut canonical otoriteyle kabul edilene kadar `HOLD_HUMAN_DECISION`.

### K01 — B05-04 / branch-base, geçmiş ayrışması
**Kapsam:** Control [PR #191](https://github.com/engurulabory/Engurulaboratuvari/pull/191), product [PR #14](https://github.com/engurulabory/enguru-mac-engineer/pull/14). V27 local control `269854b8a42a…`, product `26925c21c781…`; control base `5907b0f3ef95…`, product base `5432b9b13549…`. Control 634 local-only ve ürün 185 local-only commit korunur. Control base→local ancestor FALSE; product TRUE. Exact PR HEAD/merge-base/dirty SHA karar anında yeniden okunur.

**Sorulan karar:** Mevcut branch/base/ancestry ve iki bağımsız yerel geçmişi koruyan dar owner receipt'i hangi doğrulanmış repo owner yetkisiyle kabul ediliyor? **İZİN:** Salt-okuma ancestry ve scope-bound branch/base attestation kaydı. **AYRI KAPI:** Git push/rebase/reset/merge, H2/H3 remote writer grant.

**Kapanış:** Owner kimliği ve bu iki repo için geçerli yetki kaynağı, exact HEAD/base/merge-base ve local divergence, korunmuş dirty ve local worktree, owner karar SHA/receipt → `B05-04` Yönetim tekil kabul incelemesi. Teknik ancestry PASS tek başına yeterli değildir.

### K02 — F01 / 12-kriter owner ve Ed25519 Human Threshold
**A:** Var olan H1/H2/H3 4+4+4 canonical 12 kriter yetki kaynağı, owner ID, Ed25519 reviewer public-key authorization, kapsam/süre/revocation, `CRITERIA_SET_SHA` ve exact Git blob kanıtlanır. **B:** Gerçek kanıtlanmış yetki boşluğunda, mevcut dar kapsam yetkili owner/reviewer Human Threshold grant ve signed durable receipt üretir.

**Kapanış:** `OWNER_ID / OWNER_AUTHORITY_SOURCE / REVIEWER_ID / REVIEWER_PUBLIC_KEY_AUTHORIZATION / CRITERIA_SET_SHA / BRANCH_COMMIT_BLOB / MAC_PROGRESS_MANDATORY_JSON_BINDING / VERIFYTASK_RESULT / SIGNED_HUMAN_REVIEW / DURABLE_AUDIT_RECEIPT`. Uygulayıcı mühendis owner, reviewer veya imza otoritesi rolünü kendiliğinden üstlenmez; H1 Secure Enclave P-256 ayrı kayıttır.

### K03 — F05 / ürün source-owner changed-files review izni
**Gerçek patch hazır:** PR #14 `execution_prep/native_app/review/F05_V23_PR14_TO_V08_LAUNCH_RETRY_FIX.patch`; SHA-256 `947693553748463068011b1fed994c5e37d0b95c7cdedf632982813ba959b55f`. V26 izole kaynak `EnguruMacEngineerApp.swift` SHA-256 `8c427579a71edd24502f89bfa93039acae30f7223e85820dd930284e35e1c6cf`, `Info.plist` SHA `c3260b7fc1bf3470f0421a93b3100fc972f292c64eff7551079bf537ae3c3951`. Gerçek Mac SDK ve negatif stage PASS teknik adaydır.

**Sorulan karar:** Yetkili source owner, mevcut PR #14'ün **yalnız review feature branch** gerçek Native Swift/Info.plist ve iki stage dosyasında bounded changed-file patch application + CI + source review yürütmesini onaylıyor mu? **AYRI KAPILAR:** main merge; icon owner/license; codesign, install, aktif Mac app mutasyonu ve canlı GUI görevi. Her biri özgün yetki/saha receipt'iyle ilerler.

**Kapanış:** Real changed-file diff + exact new PR HEAD/changed blob/SHA, macOS CI, source-owner reviewer review, 0.8 sürüm eşliği, ikon provenance ve sonra ayrı canlı kullanıcı kabulü.

## 3. İCRA'nın önündeki gerçek mühendislik zinciri
- **İlk:** Güncel PR/ledger SHA ve V28 Archived PASS'i tek sefer doğrula; üç karar nesnesini *oylanabilir/karar verilebilir biçimde* hazırla. Karar verebilecek gerçek sahibi, kaynak ve gereken onay kapsamını ayrıştır. PR review talep mekanizmasına yalnız yetkili kayıtta tanımlı kişi/rol bağlanır.
- **K01 izin/kabulü sağlanırsa:** Aynı tur `B05-04` owner scope receipt ve özgün kriter kanıtını tamamla; Yönetim kabul adayını ilet.
- **K03 source-write yetkisi sağlanırsa:** PR #14 review branch'de Native changed-file patch'i güvenli izinli izole Git çalışma alanından uygula; real SHA/negative test/CI, inceleme ve kalan ikon/Native gate ihtiyaçlarını kapat. Owner source kabulü ayrı gerçek receipt.
- **K02 yetkisi sağlanırsa:** F01 12-kriter source/Ed25519 scope kararını ve Mac→Progress Core→Mandatory JSON→`verifyTask` bağını gerçek pozitif-negatif receipt'lerle işle. H1 sonra H2, sonra H3 ve F06 sırası korunur.
- **Yetki eşiğinde:** Bütün diğer bağımsız güvenli işleri tamamla; tek karar oturumu için **üç ayrı imza/receipt alanı** ile `GÜVENLİ_DUR`. Eski test/rapor sayısı yeni kontrol sayılmaz.

## 4. 24→32 özgün kontrol planı
Öncelikli adaylar: `B05-04`; `B01-09`; `B01-10`; `B02-03`; `B02-04`; `B06-07`; `B06-08`; `B06-09`. Sadece gerçek özgün kabul koşulu tamamlananlar tekil `PASS_ADAYI` olur; Yönetim bağımsız check sonrası ledger'a ekler. 24→N gerçek sayaç; `32−N` kalan. Devam tur eşikleri N bazından +10, nihai hedef `BITTI_DUR`.

**Zorunlu tam V29 raporu:** 6 satır `STATE / SAYAÇ / YENİ_PASS / F01 / F05 / RESMÎ`; AudiV13 gerçek JSON/MD ve varsa gerçek ZIP linki; 76 açık özgün kontrolün her birine ayrı mevcut kaynak/gerçek neden–hipotez/owner/onarılan fark/pozitif-negatif test/kanıt/Human Threshold/NEXT; F01–F06, H1 4/4/H2 4/4/H3 4/4/Native/DoneCheck/Verified Finish kapı matrisi. Gerçek sahibi bulunmamışsa `OWNER_ID=UNVERIFIED` açık statüsüyle kalır. Reviewer approval yoksa `HOLD`.

**ENGÜRÜ Süzgeci™ sekiz aşama:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Pozitif doğru dil, `STATE→CLAIM→EVIDENCE→NEXT ACTION→VERDICT`, `İLERLE/GÜVENLİ_DUR`. Hedefe dış yetki ve gerçek kabul receipt'iyle ilerlenir.
