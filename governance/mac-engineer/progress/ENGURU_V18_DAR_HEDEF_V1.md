# ENGÜRÜ Yönetim → İCRA V18 | Bütünleşik geniş yürütme

**Kalıcı sabit hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → Verified Finish → `BITTI_DUR`.

**Başlangıç:** 21/100. **Çalışma hedefi:** 31/100 (+10 kanıtlı kontrol); uygun kanıtla **üst hedef 41/100 (+20)**. 31'e ulaşıldığında kapsam içindeki işleri sürdür. Yetki/kanıt sınırına veya F01–F05 bütünsel kapanışına kadar tamamlayıcı yürüt.

**F01 — Ana iş:** Mevcut V13 12 kriter kararını ve PR #191 incelemesini kullan. Gerçek canonical owner/reviewer yetkisini, kesin kriter SHA'sını, DoneCheck `verifyTask` ve Mac runtime–Progress Core™–Mandatory DoneCheck JSON bağlantısını kaynak, test, karar ve receipt zinciriyle tamamla. İnsan kararı gereken yerde tek kesin Human Threshold™ kararı, yetkili sahibi ve bağlı kanıtla `GÜVENLİ_DUR`.

**F05 — Bağımsız destek:** V16 çalışan Swift stage, izole patch ve SHA'ları koru. Yerel HEAD ↔ origin/main ↔ PR #14 Git ancestry/nesne farkını **izole Git çalışma alanında** doğrula; mevcut patch'i kaynak sahibinin incelemesine hazırla; ikon kaynak/lisans/provenance adaylarını bağla; üretim kaynak sürümü, Info.plist ve gerçek Native regresyonu için yetkili kabul öncesi yapılabilen bütün bağımsız test/simülasyonları tamamla. Kaynak sahibi onayından sonra canonical promotion, signing, kurulum ve canlı kullanıcı sınaması ayrı yetkili işlem kapılarından ilerler.

**Yürütme disiplini:** Toplu bağımlılık analizi → kaynak doğrulama → gerçek neden → en küçük kalıcı fark → karşıt test → tamamlanmış kanıt → yeni uygun iş. Gereksiz yeniden derleme, tekrarlı keşif ve yeni motor yerine kanıtlanmış yeteneği yeniden kullan. Yerel Git HEAD, dirty-path, kullanıcı uygulaması, kilitli v0.6 ve AudiV13 korunur. H1/H2/H3 resmî sayaçları yalnız yetkili gerçek kabul ile ilerler. 100 birim sayacı, zaman/efor tahmini yerine 100 sabit kontrolün kanıtlı PASS sayısıdır.

**Kabul / duruş:** Her kontrol yalnız kendi şartını sağlayan gerçek saha Evidence ile ✓ kazanır. Hedef sayı bir kotadan ziyade yürütme kapasitesidir; gerçek sonuç az veya çok olabilir. Erişim, owner veya Human Threshold™ yetkisi beklendiğinde `GÜVENLİ_DUR`; yapılabilen bağımsız işler tamamlandıktan sonra tek kesin karar istenir. Nihai ürün finişi yalnız yetkili Verified Finish receipt'iyle `BITTI_DUR`.

**İCRA yanıtı — en çok 6 satır:**

`STATE=İLERLE/GÜVENLİ_DUR`
`SAYAÇ=21/100 → N/100 (+kanıtlı)`
`YENİ_PASS=gerçek kontrol ID'leri veya YOK`
`F01=sonuç + kesin kalan karar`
`F05=sonuç + kesin kalan karar`
`RESMÎ=H1/H2/H3 x/12; KAPANAN y/6; RAPOR_SHA256=...; SONRAKİ=...`

**Yönetim kuralı:** Bir İCRA turu gerçek yetenek sınırına kadar geniş yürür; tek bir kontrol PASS ile kendiliğinden sonlanmaz. Her turda yalnız iki aktif iş: ana F01, bağımsız F05.
