# ENGÜRÜ PLive™ P02 — Tek İnsan Sahipli Güven ve G3 Yetki Politikası V1

**Belge türü:** `PROPOSED_GOVERNANCE_AMENDMENT — HUMAN_APPROVAL_REQUIRED`  
**Karar makamı:** OSi'nin tek insan sahibi; yetki yalnız açık ve izlenebilir insan kararıyla doğar.  
**Tarih:** 19 Ekim 2026  
**Bağlam:** Yerel, tek insan sahipli, tek Mac OSi / ENGÜRÜ PLive P02.  
**Mevcut kanıt:** Local HEAD `269854b8a42a27e9419eae65a3c9e349bdcc7300`; P01 `2/2 LOCKED VERIFIED`; P02 `0/12 HOLD`; G3 V3 `48/48` *izole* simülasyon; P02 gerçek grant/issuer/writer henüz kabul edilmedi. V3.1 uygulaması korunur.  
**Dayanak:** `governance/plive/ENGURU_PLIVE_PROGRESS_FINISH_CONTRACT_V1.json` zaten `humanFinalAuthority=ONE_HUMAN_OWNER_HUMAN_THRESHOLD` hükmünü içerir. `governance/security/SECURITY_REVIEW_CONTRACT_V1.md` güvenlik gözden geçirme, STRIDE, OWASP, Secret Zero, DoneCheck ve insan kararının yerini makine PASS ile doldurmama koşullarını içerir.

## 1. Politika kararı — tek insan / ayrı doğrulanabilir mekanizmalar

ENGÜRÜ OSi'nin tek insan sahibi, bu **kişisel/yerel** kapsam için politika sahibi, risk sahibi ve nihai Human Threshold karar merciidir. Sırf çoklu rol etiketi veya "independent" ifadesi geçtiği için mevcut olmayan ikinci bir insan/kurum **varsayılmaz**.

**Ayrım:** Tek insanın bilinçli politika ve işlem kararı vermesi meşrudur; yazılımın kendi kendine issuer, grant, güven kökü, güvenlik PASS'i veya resmî item PASS'i üretmesi yasaktır. Aynı insanın policy onayı, grant'i ve nihai kabulü otomatik olarak aynı işlem değildir: ayrı kapsam, ayrı kullanıcı eylemi, ayrı kayıt ve ayrı kanıt gerektirir.

**Bağımsızlık yorumu (önerilen dar değişiklik):** Yerel tek sahipli P02 için bağımsız güvenlik **teknik** değerlendirmesi, uygulamadan/yazıcıdan ayrı kaynak-sabitli doğrulayıcı, karşıt test, salt-okunur kontrol ve değişmez gözlem makbuzuyla sağlanabilir. Bu, **ikinci bir insan tarafından yapılmış bağımsız inceleme** diye raporlanamaz. Eğer daha üst yetkili mevcut canonical kuralı açıkça *başka bir insanın imzalı onayını* zorunlu kılıyorsa bu belge onu kendiliğinden geçersiz kılamaz: `HOLD_CONTRACT_CONFLICT` ve kullanıcının açıkça onaylayacağı **resmî sözleşme değişikliği** gerekir.

**Risk sahipliği:** Aynı insanın hem policy sahibi hem item onaylayıcısı olması görev ayrılığı güvencesini daraltır. Bu risk yalnız **tek kullanıcı/tek Mac/iç kullanım/sınırlı item** için bilinçli kabul adayıdır. Kurumsal, çok kullanıcılı, finansal/geri alınamaz dış eylem veya başka güvenlik politikasının ayrı denetçi zorunluluğu bu istisnaya girmez.

## 2. Var olan kurallar ve korunacak kaynaklar

- ENGÜRÜ Süzgeci™ v2.4: **yalnız mevcut sekiz aşama**; pozitif dil, güvenli HOLD ve kanıta dayalı NEXT.
- Tek `Progress Core`; P02 dört mevcut paket / on iki item, dört DoneCheck, yedi mevcut saha önkoşulu, gerçek Human Threshold, native Verified Finish. **Sıfır yeni core, sayaç, aşama, gate veya proje.**
- P01 `2/2 LOCKED VERIFIED`, P06'nun ayrı yetkisi, canlı `~/Applications/ENGURU-PLive-V31.app`, AudiV13 özgünleri, mevcut dirty worktree ve GitHub PR #188/#189 korunur.
- OSi'nin yerel canonical HEAD ve SHA-256 kimliği yeni politika sürümüne girişte **yeniden doğrulanır**; önceki sabit HEAD tek başına sonsuza kadar geçerli izin değildir. GitHub'daki PR taslağı **tek başına yerel aktif politika değildir**.
- Bu belge kabul edilse bile **üretim grant'i, gerçek anahtar, yetkili writer, item state PASS, DoneCheck ve Human Threshold kendiliğinden oluşmaz**.

## 3. G3 mevcut dört kabul bağının uygulanabilir protokolü

### G3-A — İnsan tarafından onaylı güven politikası ve gerçek issuer

1. Tek insan sahibi bu metni kapsam/riskiyle açıkça **POLICY_APPROVED** olarak kabul eder; kapsam yalnız `ENGURU_PLIVE_P02_USER_SCREEN`, başlangıç item `P02.S01.01`, belirlenmiş yerel cihaz ve sürüm.
2. GitHub PR'daki metin sabit bir commit/SHA ile korunur; insan onayı ile policy byte SHA, karar zamanı, karar kapsamı ve yerel OSi kaynak SHA'sı **ayrı bir yerel karar receipt'ine** bağlanır. Yerel receipt kişiyi veya gerçek cihazı doğrulamayan basit bir sohbet ifadesinden ibaret kalmaz; mevcut Human Threshold ve mümkün olan kullanıcı varlığı/cihaz kökeni mekanizmasıyla teyit edilir. Politika kaydı grant değildir.
3. Mümkünse mevcut güvenli imza/Keychain kimliği ve doğrulayıcı **yeniden kullanılır**; hangi issuer ID ve public-key fingerprint'in hangi onaylı policy'ye bağlı olduğu kanıtlanır. Anahtar üretimi ancak açık insan rızasıyla, yerel güvenli arayüz üzerinden; ChatGPT/GitHub'a özel anahtar, seed veya token aktarılmaz.
4. Mevcut Ed25519 doğrulama adayı **bağımsız policy/trust kökenini kendiliğinden kurmaz**. Secure Enclave'ın Ed25519 anahtarı tuttuğu varsayılmaz. Önceki klasik Keychain denemesinin `-34018` HOLD durumu kapatılmadan Keychain güvenliği PASS gösterilemez; mevcut onaylanmış eşdeğer mekanizma varsa kod/entegrasyon/tehdit modeliyle ayrıca doğrulanır.

### G3-B — Yalnız yetkili item için imzalı grant

Kullanıcı **ikinci ve ayrı işlem** olarak `P02.S01.01` kapsamlı pilot yürütmeyi onaylar. Gerçek grant `projectId`, `itemId`, `action=P02_ITEM_PASS`, exact `HEAD`, canonical state `preimageSha256`, gerçek item `evidenceSha256`, onay kanıtı SHA, issuer/key ID, tek kullanımlık nonce ve geçerlilik süresini bağlar. Var olan verifier, **dışarıdan policy-pinli** issuer anahtarı ve iptal politikasıyla imzayı doğrular; fixture veya kullanıcının sunduğu rastgele public key yetki oluşturmaz.

Yanlış issuer, iptal, süresi dolma, yanlış proje/item/eylem/HEAD/ön-imaj/kanıt, replay, imza tahrifi ve policy uyuşmazlığı = **HOLD**. İmzalayıcı bir sonraki iteme veya başka projeye otomatik genişleyemez.

### G3-C — Yetkili, tekrar-önlemli canonical writer

Mevcut writer/DoneCheck/Progress Core sözleşmesine bağlı, ayrı test edilen **gerçek** P02 writer köprüsü kullanılacaktır; yeni otorite veya ikinci sayaç oluşturulmaz.

Gerekli saha kanıtı: tek-yazıcı kilidi, kaynak preimage CAS, kalıcı nonce tüketimi, kapsam/pin/path/symlink/izin retleri, append-only receipt, before/after SHA, crash/restart/replay, fail-closed belirsizlik, native postwrite `--mini/--verify` ve mevcut DoneCheck. SQLite nonce rezervasyonu ve JSON canonical dosyası **iki dayanıklılık alanıdır**; fiziksel olarak tek atomik işlem varsayılmaz. Güç kesintisi veya kısmi commit'te `HOLD_UNCERTAIN_DURABILITY`, manuel uzlaştırma gerekir; otomatik yeniden deneme veya sahte PASS yoktur. Aynı UID'nin tüm dosyalara yazabildiği tehdit açık residual risk olarak raporlanır; yalnız POSIX izinleriyle saldırgan kökeni ayrımı iddia edilmez.

Bağımsız teknik kontrol: mevcut `SECURITY_REVIEW_CONTRACT_V1` üzerinden STRIDE/OWASP kapsama raporu, kaynak sabitleme, G3 V2/V3 48/48 izole testi **yeniden kullanımı**, üzerine yalnız gerçek yetki ve OS dayanıklılığı için eksik saha testleri. Kritik/yüksek bulgu açıksa sonuç HOLD. Model kendi kodunu geçerli sayarak kendini onaylamaz.

### G3-D — İlk sınırlandırılmış gerçek iş

Yalnız G3-A, B, C gerçek kanıtları ve ayrı pilot onayı PASS olduğunda mevcut yetkili writer tarafından sadece `P02.S01.01` geçişi yapılır. Önce/sonra native Progress Core ve bağımsız receipt kontrolü yürütülür. Paketin `ITEM_STATE_PASS + ITEM_HEAD_PRESENT + PACKAGE_STATE_PASS + PACKAGE_DONECHECK_PASS` koşulları sağlanmadan `countedPass` yükselmiş varsayılmaz. P01/P06 ve kalan 11 item yetki dışındadır.

## 4. Son finişe kadar aynı hedef

S01 tamamlanınca mevcut S02 (aktif iş / A→B→A), S03 (beş alan kaynaklı sınıflandırma / G03 insan sahası / kullanıcı etkileşimi), S04 (G04 tam OS/journal sürekliliği / bağımsız teknik güvenlik / dört DoneCheck / yedi saha / nihai insan kabulü) yürür.

**BİTTİ → DUR** yalnız native P02 `12/12`, mevcut DoneCheck `4/4`, mevcut saha önkoşulu `7/7`, gerçek yetkili Human Threshold `ACCEPTED` ve native `finishState=VERIFIED` koşullarında. Politika onayı, ürün bitiş onayı yerine geçmez.

## 5. Kabul ve devreye alma — yürütülecek tek karar

Bu belge ve GitHub kaydı **POLICY_PROPOSED** durumundadır; yazılan hiçbir şey tek başına canonical OSi yetkisi değildir.

**Şimdi kullanıcıdan istenen açık karar:**  
> "ENGÜRÜ PLive P02 Tek İnsan Sahipli Güven ve G3 Yetki Politikası V1'i, yalnız yerel tek Mac ve mevcut P02 kapsamı için politika adayı olarak **ONAYLIYORUM**. Kriptografik grant, üretim writer ve Verified Finish için gerçek saha kanıtının ayrıca zorunlu olduğunu kabul ediyorum."

Onaydan sonra sıralama:
1. Exact GitHub SHA ile ilgili policy metni, mevcut OSi governance/human authority üstünlük kuralları ve P02 Work Contract karşılaştırılır; çelişki varsa **sevk edilmeden düzeltilir ve yeniden onay istenir**.
2. Yalnız onaylı, kaynak sabitli **bounded policy diff** Mac OSi'ye uygulanır; local Human Threshold kararı ve provenance receipt üretir; mevcut kullanıcı çalışması/P01/P06 korunur.
3. Gerçek Mac'te signer/Keychain güven sınırı, bağımsız validator, yetkili writer G3-A→D sınamaları yürütülür; güvenli değilse sadece eksik bağ HOLD kalır.
4. İlk pilot için ayrı gerçek insan onayı; sonra gerekli kanıtla dar iş ve mevcut 12/4/7 bitiş zinciri.
5. Politikayı değiştirme/iptal/yenileme ve sonraki scope'lar için yeni açık insan kararı gerekir. Açık anahtarın değiştirilmesi, policy SHA değişimi, cihaz değişimi, grant iptali veya süresinin dolması yazmayı otomatik durdurur.

**Güvenlik sınırı:** Bu metin ikinci insanı zorunlu kılan varsa mevcut üst-kuralı *kendiliğinden kaldırmaz*. Onaylanan dar tek-sahip istisnasının canonical kayda doğru işlenmesi ve yetkili güvenlik incelemesi ayrı **saha doğrulama yükümlülüğüdür**. Dış kurum için bağımsız ikinci insan hükmü **PASS** ilan edilemez.

**State:** `PROPOSED_FOR_SOLE_OWNER_POLICY_DECISION` · **Claim:** tek insan final makamının mevcut canonical dayanağı var · **Evidence:** G3 48/48 izole; P01 2/2, P02 0/12; gerçek grant yok · **Next Action:** açık owner policy kararı → güvenli local kayıt/uygulama → gerçek G3 saha kabulü.
