# ENGÜRÜ — Bütünleşik Geriye Kalan Mühendislik Farkları V2

**Karar / çalışma dili:** "tek sonraki mühendislik farkı" yerine **"bütünleşik geriye kalan mühendislik farkları"**. Planlama ve mühendislik hazırlığı uçtan uca tek SORTİ 04–05 zincirinde yapılır; Mac üzerinde insan yetkisine bağlı geçişler, gerekli önkoşulları tamamlanmadan çalıştırılmaz.

**Yetki:** ENGÜRÜ Süzgeci™ v2.4 canonical **sekiz aşama**; dokuzuncu aşama, yeni core, shadow progress, paralel writer, ayrı proje veya otomatik insan onayı yok. Tek mevcut P02: 4 paket / 12 item, mevcut 4 DoneCheck / 7 saha önkoşulu / tek Progress Core. P01=2/2 VERIFIED korunur; P06 ayrı.

**Hakikat sınırı:** Son gerçek Mac koşusu `PASS_READONLY_6_STEP_RECONCILIATION__OFFICIAL_HOLD`, `SIGNER_DECISION=HOLD_NO_AUTHENTICATED_ISSUER_AND_NO_EXACT_BUILD_BINARY_LINK`, adım 01–06 HOLD; `P02_OFFICIAL=HOLD`, `VERIFIED_FINISH=HOLD`, repository/keychain/signature operasyonları sıfır. Kanıt SHA: `69cccdc852911b6bc957c4657279b2666b50b5e9c058d49f1e13044cfb090567`. Yerel OSi HEAD `269854b8a42a27e9419eae65a3c9e349bdcc7300`; GitHub Twin farklı aday dalıdır.

## Tek bütünleşik execution DAG / bağımlılık zinciri

| Gate | Mühendislik farkı / hazırlık (paralel kaynak ve adversarial çalışma) | Gerçek yetki / geçiş bağımlılığı | Kabul makbuzu |
|---|---|---|---|
| 01 G3-A | Exact Swift source/build-command/input hash → signed binary hash provenance; Team ID, Bundle ID, entitlements, profile eligibility; Keychain `-34018` nedeninin yetki sınırı | Bağımsız yetkili signer qualification + insan varlığı / anahtar koruması | MAC_G3A_AUTHENTICATED_ISSUER |
| 02 G3-B | Revocable trust root, pinned trust provenance; exact `P02.S01.01` project/item/action/HEAD/preimage/evidence/approval/nonce/expiry verification; tam negatif testler | Gerçek G3-A issuer + bağımsız enrollment/onay + authentic signed grant | MAC_G3B_SCOPED_GRANT |
| 03 G3-C | Mevcut writer'a uygun CAS/nonce/journal/crash/restart/replay/red-team; iki kalıcılık alanını tek fiziksel transaction sayma | Bağımsız writer güvenlik kabulü, gerçek canonical source ve grant doğrulaması | MAC_G3C_DURABLE_WRITER |
| 04 G3-D | Pre/post native Progress Core projections ve `P02.S01.01` tek geçiş rehearsal | 01+02+03 PASS + exact human authorization; belirsizlikte HOLD/no automatic retry | MAC_G3D_FIRST_ITEM_READBACK |
| 05 P02 saha | Kalan 11 item dahil 12/12, 4/4 DoneCheck, 7/7 önkoşul; G03 gerçek UX / G04 OS recovery; bağımsız security | 04 gerçek native PASS; mevcut canonical item-by-item yetkisi | MAC_P02_FIELD_ACCEPTANCE |
| 06 Human finish | Bütün sayaç/evidence/revocation/source/receipt tekrar bağlama ve bitiş karşıt sınaması | Ayrı gerçek Human Threshold ACCEPTED + native verified finish readback | MAC_VERIFIED_FINISH / BITTI_DUR |

**Hazırlık ortak / saha geçişi kademeli:** Altı gate için tüm source/review/test mimarisi bir seferde hazırlanıp sınanır. Yetki gerektiren eylem daha önceki bağlar PASS olmadan yürütülmez. Hazırlığın PASS olması geçiş PASS'i değildir.

## ENGÜRÜ Süzgeci™ 8 aşama eşlemesi

1. **Hakikati gör:** local HEAD, canonical P01/P02, G3 politika ve son receipt; GitHub candidate ayrı.
2. **Değeri koru:** AudiV13 original, PLive V3.1, dirty worktree, P01/P06, Keychain ve insan eşiği.
3. **Eksikleri ve ihtiyaçları tespit et:** 01–06 tüm bağımlılık/evidence gap tek matris.
4. **Gerekli farkı üret:** en dar mevcut repo dosyalarında source/test/qualification taslağı, yeni core yok.
5. **Eksikleri tamamla, ihtiyaçları karşıla:** tüm zincirin statik/dinamik *aday* simülasyonu, fail-closed negatif test, insan önkoşullu native plan.
6. **Kanıtla:** GitHub exact HEAD CI ile ayrı macOS field signed issuer/grant/writer/native readback; güven ayrımı.
7. **Bir sonraki ihtiyaçları belirle:** tamamlanmamış bağımlılıkları tek receipt / 01–06 matriste güncelle.
8. **İlerlet:** yetki sağlandıysa ilgili bounded native geçiş, ardından altı kapının hepsini tekrar bağlayan son acceptance.

## Güvenlik ve sınır

- Mac native G3-A `-34018`; eski signed helper için eligible authorized profile `0`, applicationIdentifier/keychainAccessGroups false gözlemleri kesin kök neden kanıtı sayılmaz.
- PR #188/#189/#190 draft güven sınırları korunur. CI candidate PASS, yerel G3 issuer veya P02 item PASS değildir.
- Mac'te imzalama, Keychain, issuer üretme, grant verme, production writer, resmî item increment, merge, app resign **bu sözleşmenin salt-okunur kısmının dışında**. Ayrı açık yetki gerekir.
- Nonce, crash, stale HEAD, forged proof, symlink/path, policy drift, revoked trust, wrong team/profile, replay, state split, malicious ZIP, independent review yokluğu -> HOLD.
- Her gate için `planned / engineering-tested / locally-authorized / field-verified` ayrı gözlemlenir. Yalnız field-verified resmî sayaçlara yansır.

**Bütünleşik finish kuralı:** 01–06 genuine native PASS + P02 12/12 + 4/4 + 7/7 + bağımsız security PASS + Human Threshold ACCEPTED + native `finishState=VERIFIED` ⇒ `BITTI_DUR`. Diğer bütün durumlarda `HOLD`.

**NEXT ACTION:** PR #190 üzerinde altı gate'in kod ve bağımsız adversarial test hazırlığını ortak yürütmek; önceki Mac receipt'in kanıt boşluklarını gerçek native human-authorized acceptance ile kapatmak. Her küçük diagnostik için yeni SORTİ başlatılmayacak.
