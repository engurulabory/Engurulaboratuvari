# ENGÜRÜ PLive P02 — Üç Hazırlık Hedefi Sabit Kapsam Kararı V1

**Karar:** Kullanıcının 2026-10-20 onayıyla, P02 Verified Finish hazırlığı **3 sıralı hedef × 4 kabul ölçütü** kapsamında yürütülür. Bu belge bir **GitHub aday mühendislik çalışma kilididir**; Mac canonical state mutasyonu, Apple signer yetkilendirmesi, native PASS, yeni core/gate/sayaç veya Human Threshold kararı değildir.

**Öncelik:** H1 4/4 gerçek kanıtla PASS → H2 4/4 PASS → H3 4/4 PASS → yetkili yerel Mac OSi saha yürütmesi. Geçiş kararı kanıtı tam olan hedef için ayrı verilir. Hazırlık puanı kaynak ve alan tanımlı kanıt sayısının 12’ye bölünmesidir; bir hedefin sonucu ancak kendi dört koşulunun tamamı PASS olduğunda `100/100` olur. Kısmi koşullar terminal native veya Progress Core sayaçlarını artırmaz. Hazırlık ölçüsü resmî OSi 25 × 4 saha puanı değildir.

## H1 — Gerçek Apple signer / issuer (4/4)
- H1.1: Yetkili signer'ın exact kaynak→build→binary→Team ID kimlik ve codesign provenance bağı, bağımsız readback.
- H1.2: Gerçek Mac'te signer binary ile eşleşen signing/provisioning/entitlement ve erişim grubu koşulları teknik incelemede PASS.
- H1.3: İnsan varlığıyla gerçek cihaz anahtar üretme/erişme, imzalama ve bağımsız imza doğrulama pozitif saha işlemi PASS; key custody güvenli.
- H1.4: Sözleşme ve policy SHA'sına bağlanan gerçek issuer public-key/trust/revocation kaydının bağımsız teknik güvenlik kabulü PASS.
**Mevcut kanıt:** SIGNING_RECEIPT `codesignVerified=true`, ancak `applicationIdentifierPresent=false`, `keychainAccessGroupsPresent=false`, `secureEnclaveExecuted=false`, `nativeAuthority=HOLD`. Önceki G3 Mac signing field `eligibleAuthorizedProfileCount=0`; sonraki key create `-34018`; neden kesin kanıtlanmış değildir. **H1=HOLD (0/4 kriter tam doğrulanmış)**. Keychain, grant veya resmî state yazması CI tarafından yapılmaz.

### H1 Apple-supported packaging constraint (engineering finding, same 4 criteria)

Apple TN3125 and *Signing a daemon with a restricted entitlement* distinguish
standalone signed tools from app-like bundles. If the existing signer genuinely
needs **restricted** `keychain-access-groups` or related entitlement, a standalone
executable has no place to embed the authorizing provisioning profile; the
owner-authorized build should be an appropriately signed `.app`-like bundle
with `Contents/Info.plist`, `Contents/MacOS/<executable>`, and (when
required) `Contents/embedded.provisionprofile`. Xcode should match the actual
Team, Bundle ID and approved capability. Existing installed PLive V3.1 remains
unchanged. A profile's presence, signed executable, or CI test is not issuer
qualification. The prior `-34018` observation alone cannot attribute a root
cause; live key use and independent trust acceptance decide H1.3/H1.4.

The **existing** `plive_p02_g3a_native_signer_metadata_readonly_v1.py`
now inspects either a standalone signed executable or an app-like bundle,
recording embedded profile presence separately as `PRESENT_UNVERIFIED` and
retaining `HOLD_G3A_NATIVE_AUTHORITY`. This is H1.1/H1.2 engineering
support, not a fifth H1 criterion.

**Official Apple references:**
- https://developer.apple.com/documentation/technotes/tn3125-inside-code-signing-provisioning-profiles
- https://developer.apple.com/documentation/xcode/signing-a-daemon-with-a-restricted-entitlement

## H2 — Mevcut tek canonical P02 writer (4/4)
- H2.1: Mevcut P02 canonical state sahibi ve yetkili mutasyon entrypoint'i Mac kaynaklarında kesin kaynak/izin/sahiplik kanıtıyla onaylı.
- H2.2: Tek writer sözleşmesi mevcut state, worklist, Progress Core, human/security policy ile kaynak seviyesinde bağlanmış.
- H2.3: Aynı writer üzerinden dayanıklı CAS, nonce reservation/replay, append-only journal, crash/recovery ve concurrency karşıt testleri PASS; JSON+journal çiftini atomik diye sunma.
- H2.4: Gerçek writer'ın kontrollü izole state kopyasında grant-to-transition pozitif işlev, bağımsız readback ve Progress Core projeksiyon testi PASS; resmî P02 state korunur.
**Mevcut kanıt:** P02 canonical state/worklist/contract var; `enguru_osi_runtime.py` yardımcıları writer authority değildir; `enguru_progress.py` projection/verification görevindedir. Policy `writerApproved=false`. **H2=HOLD (0/4)**.

## H3 — GitHub Twin + Mac OSi gerçek entegrasyon hazırlığı (4/4)
- H3.1: Mac ile GitHub Twin’in üretime konu exact kaynakları (HEAD/branch/diff/SHA) ve yetkili merge/review bağları uzlaştırıldı.
- H3.2: H1 issuer/trust, G3-B signed grant, H2 writer ve G3-D geçiş çağrıları gerçek kod arayüzünde bütünleşti; bunların harici insan/izin gereksinimleri korundu.
- H3.3: Aynı gerçek entegrasyon kodunda pozitif/negatif, kaynak kayması, sahte kanıt, revocation, replay, concurrency, crash/restart ve risk sınırları bağımsız PASS.
- H3.4: Tek testli native saha yürütme teslimi P02 12 item / 4 DoneCheck / 7 saha önkoşulu / G03-G04 / bağımsız security / ayrı Human Threshold / finish readback koşullarını kapsar ve çalıştırılabilirliği testlidir.
**Mevcut kanıt:** GitHub PR #188→#189→#190 taslak zincirinde aday CI başarılı; ancak gerçek signer/writer entegrasyonu ve native yürütme HOLD. **H3=HOLD (0/4)**.

## Native bitiş sınırı (değişmez)
**Altı kapı:** G3-A, G3-B, G3-C, G3-D, P02 12/12 saha, ayrı Human Verified Finish. P01 2/2 VERIFIED ve P06 korunur; Mac dirty worktree korunur; mevcut V3.1 uygulaması korunur. Mac OSi resmî P02 `0/12_HOLD`, native `0/6_PASS`, Verified Finish `HOLD`; sonraki saha kanıtı gelene kadar böyledir. Son hedef `BITTI_DUR`.

## Başka iş sırası
**"GitHub Twin ve Yerel Mac OSi 100/100 Hazırlık Standartları"** başlığı sonraki iş olarak **BEKLEMEDE**. P02 Verified Finish sonrasında başlatılır.

## H1 sahaya güvenli handoff
Yetkili Mac sahibi, aynı signed helper'ın exact binary/identity/provisioning ve user-presence koşullarını Xcode/Apple Developer yapılandırmasında tamamlar. Önceki `-34018` hata kodu tek başına kök neden tespiti değildir. Gerçek Mac signer deneyi ancak sahibin açık onayıyla mevcut sınırlı scope'ta yapılır; secret/private key dışarı aktarılmaz. Başarılı çıktının pinned binary/signing receipt, gerçek cryptographic challenge/signature verification ve bağımsız trust acceptance kanıtı değerlendirilir. Yetkisiz veya uyumsuz durumda H1 HOLD olarak kalır.

**Durum:** `PREPARATION_3_GOALS_SCOPE_LOCKED_ON_GITHUB_CANDIDATE / H1_0_OF_4_HOLD / H2_0_OF_4_HOLD / H3_0_OF_4_HOLD / NATIVE_0_OF_6 / P02_0_OF_12 / VERIFIED_FINISH_HOLD`.

### H1 production-app stage — real build evidence, native authority unchanged

- Verified original Mac diagnostic Python source SHA-256: `9a13b4a3815257f789246f02f6b37bb6abd7ce061d30086ac535002ec73c9067`.
- Extracted original Swift source SHA-256: `b4dae8d509b5e434cccc60324c4eed6fd4373a7e0db7791de3e9bc719736a2f4`; identical source now tracked as `tools/plive_p02_g3a_signer_main_v1.swift`.
- Existing G3 CI workflow additionally compiles ARM64 Swift on `macos-15`. Run `39412898216` successfully completed both the pinned build job and scoped authorization negative tests. These are candidate compilation checks, **no Apple issuer enrollment, provisioning authorization, Secure Enclave private key use or canonical P02 write**.
- User-facing Mac builder ZIP: `ENGURU_H1_SIGNER_APP_STAGE_V1.zip`, SHA-256 `ca16857fc313a54e706eaf780b3c62f8513d58d1308c05df8105c99ce463abe1`. Bundled self-test PASS and 7/7 local regression tests PASS. This ZIP is delivered via ChatGPT **separately**, not committed to GitHub.
- Its sole field execution is owner-initiated `--stage`: compile an *unprovisioned* `ENGURU-G3A-Signer.app` inside AudiV13 and write a local build receipt. No signing or key access occurs. H1.1 still requires genuine signed source-to-binary producer attestation; H1.2–H1.4 require owner-authorized Apple signing, **a provisioning profile only if a restricted entitlement is actually claimed**, successful real user-presence Secure Enclave challenge, and independent issuer trust acceptance.
- Target only H1. No new gate or independent canonical state writer. **H1=0/4 HOLD, native=0/6, P02=0/12, Verified Finish HOLD.**

### H1 local Apple identity and profile observation (2026-10-20)

- Mac owner readback reported *two* valid Apple Development code-signing identities with certificate OU/Team ID `DNMRGL53T4` and verified signer `ENGURU-G3A-Signer.app` source/binary/build receipt hashes. The app stage is currently unsigned with no embedded profile.
- Owner scanned standard cached macOS provisioning locations: `LOCAL_MACOS_PROFILE_FILES=0; EXACT_LOCAL_PROFILE_CANDIDATES=0`. This is proof of absence **in the checked locations**, not proof the Apple Developer account cannot provision or that provisioning is necessary for this app.
- Exact pinned Swift source uses `kSecAttrTokenIDSecureEnclave`, `SecAccessControl.userPresence` and an app-specific key tag. It **does not explicitly request `kSecAttrAccessGroup`** or a restricted `keychain-access-groups` entitlement. Under Apple TN3125, ordinary macOS code without restricted entitlement requires no provisioning profile. The `-34018` from earlier *different* signer diagnostic does not independently establish the cause for this staged app. Do not add arbitrary entitlements simply to make profiles appear.
- Correct next bounded action: preserve unsigned source/build receipt, make a separately named copy of the compiled app in AudiV13, and let the Mac owner explicitly choose a valid Team OU-matched Apple Development code-signing certificate. Sign **only that copy**, then verify real signature, Team ID and effective signed entitlement state. Record a detached readback receipt. A successful developer code signature is a code-signing milestone, **not** native Secure Enclave issuer acceptance, grant issuance or P02 write. H1 still HOLD until all four criteria are fulfilled.
- Reference: Apple TN3125 https://developer.apple.com/documentation/technotes/tn3125-inside-code-signing-provisioning-profiles and errSecMissingEntitlement https://developer.apple.com/documentation/security/errsecmissingentitlement.

### H1 owner-signed macOS app observed; live Secure Enclave next (2026-10-20)

- Owner Mac console report: `STAGED_SOURCE_BINARY_RECEIPT=PASS`, identity 1 with Team OU `DNMRGL53T4` selected and explicit `IMZALA` entered. On a newly created AudiV13 app copy, `SIGNED_TEAM=PASS SIGNED_BUNDLE_ID=PASS CODESIGN_VERIFY=PASS`; `STATE=PASS_DEV_SIGNED_APP_ONLY_NATIVE_AUTHORITY_HOLD`.
- Exact signed app: `~/Desktop/AudiV13/ENGURU_G3A_OWNER_SIGNED_APP_20261020T120418Z_dbd7536a/ENGURU-G3A-Signer.app`. Owner reported receipt `H1_SIGNING_RECEIPT.json` SHA-256 `96bbec1a7a1f683e71a1452db54f5b4e0bdb9ed4513d4f141625411d26ac00ce`. Independent retrieval of owner receipt bytes is still pending. Do not claim H1.1 PASS solely from console testimony; code-signing field evidence is positive.
- Next bounded owner-authorized step is `ENGURU_H1_SECURE_ENCLAVE_CHALLENGE_V1.py` SHA-256 `90fc2710b7c8afbb9d56a77e8a5b339b39c13569872ca8f92f1e741dcceb47ac`, delivered separately via ChatGPT. It validates pinned receipt/build/source/signed-binary and macOS code signature *before* permission, then requires exact owner text `H1_CANLI_IMZA`. Running the exact signed Swift signer may create a persistent, nonexportable Secure Enclave P-256 Keychain key; userPresence prompt may occur. Signed challenge is independently verified by OpenSSL, output recorded only in AudiV13; no grant, native writer, or P02 mutation. Offline OpenSSL signature validation plus tampered-message and scope parser tests: 4/4 PASS. **No live Secure Enclave attempt or issuer acceptance has occurred.**
- H1 0/4 HOLD pending full independent conditions; H2/H3 pending; native 0/6, P02 0/12, Verified Finish HOLD.

### H1 first consented Secure Enclave attempt — diagnostic HOLD (2026-10-20)

Mac owner's first **explicitly approved** `H1_CANLI_IMZA` attempt passed V1 tool SHA-256, 4/4 OpenSSL/scope self-test, pinned signed app/build provenance, Team/Bundle `codesign` preflight. The actual signed Swift executable returned `SECURE_ENCLAVE_EXIT_CODE=50`, `SIGNER_STATE=HOLD_GUVENLI_DUR`; `STATE=HOLD_SECURE_ENCLAVE_OPERATION`. **No successful live signature or independent issuer acceptance.** The exact Swift failure cause is unknown from the exposed output, and a key may or may not have been created during the failed attempt.

Found local tool diagnostic issue: the V1 Python live wrapper filtered the Swift `BLOCKER=...` diagnostic through `[A-Za-z0-9_:\\-]+`, which **drops** common CFError domain names with periods and punctuation. The signed Swift source emits both `STATE` and `BLOCKER`; the V1 wrapper can hide the latter. Do not attribute the failure to `-34018`, entitlement, user presence, Keychain or provenance from this limited stdout alone.

A **bounded diagnostic-only** V2 owner handoff changes only error formatting while preserving all V1 source/binary/receipt pins, human consent, challenge structure, OpenSSL verification, native authority HOLD and no P02 writer. SHA-256 `658ec11dc49a11e38e03acd736f4552274f12ae61cf26763540973bf77e70aef`. V2 existing local self-test 4/4 PASS and three added adverse diagnostics tests PASS (CFError dotted domain preserved in sanitized form, private output not echoed, missing owner consent prevents invocation). **Tests are simulated; no second Mac Secure Enclave attempt has happened.** Owner may decline the repeat; only fresh explicit owner permission authorizes it. H1 0/4 HOLD, H2/H3 pending, native 0/6, P02 0/12, Verified Finish HOLD.
