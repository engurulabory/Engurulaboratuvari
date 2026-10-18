# ENGÜRÜ PLive P02 — OSi Tek Sahipli Politika Saha Kaydı ve G3 İlerleme Bağı

**Alan:** `ENGURU_PLIVE_P02_USER_SCREEN` · ilk izinli iş `P02.S01.01` · mevcut sekiz ENGÜRÜ Süzgeci™ aşaması.

**OSi tarafından gerçekten gözlenen yerel kayıt:** `PASS_OWNER_POLICY_RECORDED__G3_REAL_AUTHORITY_HOLD` (19 Ekim 2026 tek Mac kapsamı).

- **Onaylanan politika SHA-256:** `48f46754c4a94e28d66e7e6a272284afae60791d631f556d6826f6775744fb9e`
- **Saha makbuzu SHA-256:** `f3bcb7f3c6804d26aed53bab394a0500b76c86c10aef0af992c423a913aa3494`
- **İnsan politika kararı:** `EXPLICIT_USER_APPROVED_2026_10_19` — tek insan sahibi, yalnız yerel tek Mac. Sohbet kararı cihaz kimlik doğrulaması veya imzalı grant değildir.
- **OSi yeni kayıtlar:** `governance/plive-p02-user-screen/ENGURU_PLIVE_P02_TEK_INSAN_GUVEN_G3_POLITIKASI_V1.md` ve `ENGURU_PLIVE_P02_TEK_INSAN_POLITIKA_KARARI_V1.json`. Yerel olarak iki **yeni dosya** açılmıştır, önceden izlenen diğer canonical dosyalar değiştirilmemiştir. OSi Git HEAD hâlâ `269854b8a42a27e9419eae65a3c9e349bdcc7300`; bu kayıtları `git commit` veya merge yapılmış kabul etmeyin.
- **Sözleşme doğrulaması:** `PASS_KNOWN_SCOPE_CONTRACTS` — inceleme iki bilinen sözleşmeye sınırlıdır; bütün üst yetki politikaları veya bağımsız güvenlik incelemesi için genel PASS iddiası yok.
- **Ön/son native:** P01 `2/2 VERIFIED`; P02 `0/12 HOLD`; 7 sabit kaynak pini geçerli; önceki tracked dirty worktree korunmuş. `canonicalOtherSourcesWrites=0`.

## Bitmiş olan tek iş

**G3-A yönetişim kararı ve yerel kayıt:** `OWNER_POLICY_APPROVED__LOCAL_RECORD_PASS`. Bu çalışma için ikinci insan varsayarak yeniden politika onayı istenmez.

## İlk gerçek mühendislik farkı ve sırası

1. **G3-A cihaz imzalayıcısı:** Önceki Mac saha makbuzları `signingIdentityCount=1`, `eligibleAuthorizedProfileCount=0` ve klasik Keychain `SecItemAdd=-34018` göstermiştir. Var olan Xcode/app signing, effective entitlement, keychain access groups, gerçek profili ve cihaz kaynaklı kullanıcı varlığını **sadece kaynak kimliği doğrulamasıyla** nitele. Önceden onaylı güvenli ve eşdeğer bir veri koruma yolu doğrulanmadan klasik Keychain'e güvenlik azaltıcı otomatik geçiş **yoktur**. Ed25519 Secure Enclave'de bulunur iddiası yapılamaz.
2. **G3-A trust binding:** Gerçek cihaz kökenli issuer ID ve public-key fingerprint, **onaylı politika SHA-256'sına** ve yerel Human Threshold kayıt kökenine bağlanır; özel anahtar Mac dışında görülmez. Makine kriptografik fixture'ından kendi kendine güven kökü üretilemez.
3. **G3-B grant:** Ayrı ve açık kullanıcı pilot onayı + gerçek `project/item/action/HEAD/state-preimage/evidence/expiry/nonce` bağı; revocation ve fail-closed yanlış-scope testleri. Politika onayı tek başına grant değildir.
4. **G3-C writer:** Mevcut V2 Ed25519 / V3 scratch 48/48 testini yeniden kullan. Gerçek bounded writer, atomik nonce/CAS, append-only after receipt, OS restart ve kalıcı recovery/adversarial evidence ile ayrıca kabul edilir. SQLite ve JSON iki ayrı durability alanı; belirsiz sonuç HOLD, otomatik retry yok.
5. **G3-D tek geçiş:** Yalnız `P02.S01.01` için gerçek ön/son kaynak kanıtı + native Progress Core ve S01 DoneCheck; resmî count yalnız mevcut dört item/package koşuluyla yükselir.

**Güvenlik sınırı:** Yeni core, sayaç, dokuzuncu aşama veya paralel writer yok. `P01`, `P06`, `AudiV13`, kurulu `PLive V3.1`, kullanıcı çalışması korunur. Bu GitHub belge kaydı **OSi'ye otomatik deploy**, gerçek keychain kimliği, yerel policy Git commit veya üretim grant'i değildir.

**Bir sonraki yapılabilir mühendislik kararı:** Signer'ın gerçek Mac signing/provisioning düzeltmesi ve kaynağa sabit user-presence testi. Ayrı gerçek grant/writer onayı ve gerçek bağımsız teknik review tamamlanmadan P02 resmî PASS/Verified Finish yok.
