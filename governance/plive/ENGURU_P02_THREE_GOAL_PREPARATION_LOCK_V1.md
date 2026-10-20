# ENGÜRÜ PLive P02 — Üç Hazırlık Hedefi Sabit Kapsam Kararı V1

**Karar:** Kullanıcının 2026-10-20 onayıyla, P02 Verified Finish hazırlığı **3 sıralı hedef × 4 kabul ölçütü** kapsamında yürütülür. Bu belge bir **GitHub aday mühendislik çalışma kilididir**; Mac canonical state mutasyonu, Apple signer yetkilendirmesi, native PASS, yeni core/gate/sayaç veya Human Threshold kararı değildir.

**Öncelik:** H1 4/4 gerçek kanıtla PASS → H2 4/4 PASS → H3 4/4 PASS → yetkili yerel Mac OSi saha yürütmesi. Geçiş kararı kanıtı tam olan hedef için ayrı verilir. Hazırlık puanı kaynak ve alan tanımlı kanıt sayısının 12’ye bölünmesidir; bir hedefin sonucu ancak kendi dört koşulunun tamamı PASS olduğunda `100/100` olur. Kısmi koşullar terminal native veya Progress Core sayaçlarını artırmaz. Hazırlık ölçüsü resmî OSi 25 × 4 saha puanı değildir.

## H1 — Gerçek Apple signer / issuer (4/4)
- H1.1: Yetkili signer'ın exact kaynak→build→binary→Team ID kimlik ve codesign provenance bağı, bağımsız readback.
- H1.2: Gerçek Mac'te signer binary ile eşleşen signing/provisioning/entitlement ve erişim grubu koşulları teknik incelemede PASS.
- H1.3: İnsan varlığıyla gerçek cihaz anahtar üretme/erişme, imzalama ve bağımsız imza doğrulama pozitif saha işlemi PASS; key custody güvenli.
- H1.4: Sözleşme ve policy SHA'sına bağlanan gerçek issuer public-key/trust/revocation kaydının bağımsız teknik güvenlik kabulü PASS.
**Mevcut kanıt:** SIGNING_RECEIPT `codesignVerified=true`, ancak `applicationIdentifierPresent=false`, `keychainAccessGroupsPresent=false`, `secureEnclaveExecuted=false`, `nativeAuthority=HOLD`. Önceki G3 Mac signing field `eligibleAuthorizedProfileCount=0`; sonraki key create `-34018`; neden kesin kanıtlanmış değildir. **H1=HOLD (0/4 kriter tam doğrulanmış)**. Keychain, grant veya resmî state yazması CI tarafından yapılmaz.

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
