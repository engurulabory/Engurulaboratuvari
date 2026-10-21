# ENGÜRÜ Yönetim — V21 Hüküm ve V22 Karar Kapısı

**Tarih:** 21.10.2026. **Kaynak:** Kullanıcının V21 Mac saha devir beyanı; `ENGURU_V21_F01_F05_FIELD_20261021T155628435206Z.json` rapor SHA-256 `86f990abd4c675407211c4f29bae0818867464da11f80f9d4964c52563fca87d`; kanıt ZIP SHA-256 `e940df16248fd9f96855091423a006f059792f15c9a763c3d9219e54fa907a3a`. Bu Yönetim oturumuna ham rapor/ZIP baytları sağlanmadığından bu SHA'lar **beyan edilmiş**, bağımsız dosya kontrolü bekleniyor.

**V21 gerçek saha beyanı:** paket 15/15 test PASS; V16 patch izole uygulanabilirlik PASS; Swift izolasyon build PASS, binary `168d9560148bb61e20b05aa7abea2a0546f7b23568551e8724997fd2e2c5c784`; V0.8 Info.plist aday SHA `c3260b7fc1bf3470f0421a93b3100fc972f292c64eff7551079bf537ae3c3951`; v0.8 ile PR #14 Swift yaşam döngüsü/yeniden başlatma/eşzamanlı çalışma/kapanış davranış farkları açık; ikon license/owner kaynak bağı açık. Asıl ürün HEAD ve iki dirty path, 185 commit, kullanıcı uygulaması, main korunmuş; canonical/GitHub write 0.

**Kabul sayacı:** Yönetim ledger **22/100**; V21 **+0 yeni benzersiz PASS**; hedef **30/100**, fark **8**. `B02-05`, `B02-06`, `B02-07`, `B02-08`, `B06-07`, `B06-08`, `B06-09`, `B07-07` hâlâ `HOLD`. İzole patch/build PASS, yetkili `canonical` kaynak kabulü veya lisans izni yerine geçmez. H1/H2/H3 **0/12**, kapanmış F01–F06 **0/6**, Verified Finish HOLD.

## YÖNETİM — tek sonraki karar

**F01:** V21 `F01_TEK_HUMAN_THRESHOLD_KARARI.md` SHA `23ca4fce83ba7b9da4a6749dbf77914d75cc880909dd359678093afa7a53070b` *karar adayıdır*. Aday 12 kriter SHA `208a32c7a8b93204c6b9a414086c8d43bf9216b22c7ccbf53ef5dac09cde9ada`, resmi owner-onaylı `CRITERIA_SET_SHA` değildir. **Yetkili canonical owner/reviewer** mevcut A sözleşmesini tanımlayıp kanıtla bağlar veya B dar kapsamlı yetkilendirmeyi gerçekten karara bağlar: `OWNER_ID/SOURCE, REVIEWER_ID/Ed25519_AUTHORITY, CRITERIA_SET_SHA, BRANCH_COMMIT_BLOB, MAC_PROGRESS_DONECHECK_BINDING, VERIFYTASK, HUMAN_REVIEW_RECEIPT`. Yerel source inceleme `a37c2f...` ile main `a3fa94...` farkını korunmuş kanıttan devral. Bu karar, salt chat/onay beyanıyla resmî PASS sayılmaz.

**F05:** PR #14 kaynak sürümü 0.6 ile çalışan ürün 0.8 arasında **yaşam döngüsü ve recovery semantiğini koruyan izole birleşik kaynak farkı** üret ve gerçek pozitif/negatif native regresyonla doğrula. Mevcut V16 patch ve hazır .app SHA'larını yeniden kullan. Sürüm düşürme, .icns kaynak ilanı, signing/install, canonical source promotion ve kullanıcı uygulamasına yazım yalnız kendi yetkili kapılarından geçer. İkon licence/Git owner provenance aynı source-review kararına açık ayrı kanıttır.

## V22 verim kapısı

Yeni İCRA turundan önce **yetki kararının gerçek kaynağı** ve/veya **tamamlanabilir F05 kaynak onarımının yeni sınanabilir farkı** hazır olmalıdır. F01 human karar hâlâ HOLD ise F05'in bütün izole güvenli işlerini tamamla, ardından **tek karar dosyası** ile `GÜVENLİ_DUR`. Aynı rapor/aynı SHA tekrarları yeni iş sonucu değildir; sekiz HOLD kontrolü için ancak özgün kabul koşulu gerçekleştiğinde ✓ yazılır. **30/100 hedefi korunur; yetkisiz PASS iddiası üretilmez.**

**Yanıt:** `STATE`; `SAYAÇ 22→N/100`; `YENİ_PASS`; `F01`; `F05`; `RESMÎ | RAPOR_SHA256 | TEK SONRAKİ KARAR`.

**Kalıcı sabit hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native Mac Engineer OSi → Verified Finish → `BITTI_DUR`.
