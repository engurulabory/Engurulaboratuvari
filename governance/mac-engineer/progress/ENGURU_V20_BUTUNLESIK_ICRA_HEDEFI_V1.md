# ENGÜRÜ YÖNETİM → İCRA V20

**Başlangıç:** 22/100 kanıtlı. **Çalışma hedefi:** 32/100 (+10); uygun kanıtla daha fazla, hedefe ulaşınca kapsamdaki diğer yapılabilir işlere devam. Resmî H1/H2/H3 0/12, F01–F06 0/6, Verified Finish HOLD.

**Ana F01:** V13 4+4+4 tek karar ve PR #191 yetki incelemesinden mevcut owner/reviewer, authority source, kriter SHA ve Mac → Progress Core™ → Mandatory DoneCheck JSON → `verifyTask` zincirini kaynakta araştır, yetkili alanları kanıtla, güvenli entegrasyon/test adımlarını tamamla. İnsan yetkisi gerekiyorsa yalnız **tek kesin Human Threshold™ kararı** sun ve o kapıda `GÜVENLİ_DUR`.

**Destek F05:** V19 `B07-02=PASS` ve gerçek Git `185 local / 31 PR` ancestry kanıtını kullan. V16 patch'i ile mevcut ürün HEAD'inin iki tracked dirty yolunu koruyarak yalnız izole ortamda source review farkını analiz et; PR14 stage, Info.plist, ikon adayları/lisans/Git provenance için yapılabilir test ve owner review hazırlığını bütün bağımlılıklarıyla yürüt. Kaynak sahibi kabulü sonrası canonical promotion/merge ve Native signing/install/live smoke ayrı Human Threshold™.

**Kural:** Bir turda bütün güvenli, bağımlılık sırasına uygun işleri kaynak → test → gerçek kanıt zinciriyle bitir; yüzde hedefi erken duruş kotası değildir. Yalnız yeni benzersiz 100-kontrol ID ✓ sayılır.

**İCRA yanıtı (6 satır):**
`STATE=İLERLE/GÜVENLİ_DUR`
`SAYAÇ=22/100→N/100`
`YENİ_PASS=ID'ler / YOK`
`F01=tek kesin karar veya PASS`
`F05=sonuç/kanıt`
`RESMÎ=x/12; KAPANAN=y/6; RAPOR_SHA256=...; SONRAKİ=...`

**Sabit bitiş:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → Verified Finish → `BITTI_DUR`.
