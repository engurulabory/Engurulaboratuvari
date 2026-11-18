# ENGÜRÜ Mühendis OSi™ — Kalıcı ve Sabit Temel, Hedef, Mühendislik ve Finiş Sözleşmesi V2

**Tarih:** 13 Kasım 2026 · **Ürün ID:** `ENGURU_MUHENDIS_OSI` · **Sahip kararı:** önceki mimar ağırlıklı adı görevine uygun **İleri Seviye Yazılım ve Sistem Mühendisi** olarak güncelle. Geçmiş ürün ID `ENGURU_USTAMIMAR_OSI` eski sürümlerin kaynak ve olay aliasıdır; geçmiş makbuzlar yeniden yazılmaz.

## 1. Kalıcı ve sabit iki hedef
**Hedef 1 (AKTİF):** Gerçek tarayıcıda açılan HTML ekranıyla **görev → plan → owner onayı → doğrudan tarayıcı HTTP → tek mevcut yerel yürütücü → gerçek dosya/kod → gerçek davranış testi → SHA/SQLite → aynı HTML ekranında makbuz → yenileyip geri okuma** zincirini tamamla. Zorunlu 12 `H1-C01..H1-C12` gerçek kanıtı, farklı görev, güvenlik, bağımsız doğrulama ve gereken owner kabulü tamamlandığında `HTML_PROTOTYPE=PASS`.

**Hedef 2 (ASKIDA):** Hedef 1'in kabul edilen aynı ürününü Yerel Mac OSi ana sisteminde kurmak, Mac Engineer/gerçek Ollama ile çalıştırmak. Açılış yalnız sonraki **owner MAC_INSTALL_GO** ile. ENGÜRÜ Builder OSi ayrı üretim fabrikasıdır.

**Sıfır yeni maliyet:** ücretli API ve abonelik zorunluluğu 0. **Sıfır günlük teknik prosedür hedefi:** HTML tek ekranından görev/onay/kanıt; iş sırasında terminal ve servis idaresi 0. Bu hedefin gerçek kullanıcı kabulü **HOLD**; güvenlik için owner onayı korunur.

## 2. Mühendislik görevi, sınır ve kaynak
ChatGPT/Zekü: mimari/strateji/sözleşme yönetimi. **ENGÜRÜ Mühendis OSi™:** verilmiş mimariyi çalışan yazılıma çeviren, kod teşhis eden, güvenli onaran, ayrı test ve regresyon çalıştıran, tekrar okunur sonuç üreten iş aracı. Tek owner, tek asıl yürütücü, tek görev defteri, tek Saray kaynağı; yerel Python standart kütüphanesi, isteğe bağlı Ollama, HTML, SQLite, SHA. Hedef 1'de GitHub/ChatGPT canlı bağlantısı, yeni ücretli servis, Mac kurulum ve canlı Saray indeks yazımı bulunmaz.

**Korunan kaynaklar:** 13 Kasım V1 / V1.1 / V1.2 UstaMimar owner/sözleşme ve H00..H08 haritaları, V0.2 ZIP, 26/26 regresyon, 21/21 harita yapısal test, 12 H1 özgün kabul şartı, 18 UM, 32 WC muadil tasarım kıyası, 56 özgün 4H, W01..15, Hafıza Sarayı önceki gain_ID ve K03/K04 HOLD. Tarihsel testler yeni rolün kanıtı olarak yalnız tekrar çalıştırılıp kapsamına göre bağlanır.

## 3. Mühendislik beceri hiyerarşisi
- **Yetenek:** 12 atomik işlev `Y01..Y12`; her biri görev ve araç makbuzu ile ölçülür.
- **Yetkinlik:** 6 bütünleşik mühendislik alanı `KMP01..KMP06`; ilgili yetenekleri tek gerçek görevde birleştirir.
- **Yeterlilik:** 10 kalite ölçütü `Q01..Q10`; gözlenebilir sonuç, olumlu/olumsuz/kesinti ve ayrı doğrulama gerektirir. Bir örnekten genel uzmanlık ilan edilmez.

İlişki: `Y → KMP → Q → H00..H08 → H1-C01..12 → Ana Kabul Panosu`; yürütme sonucu aynı `task_id` ile kanıta bağlanır. Her becerinin `PASS_SCOPED`, `HOLD`, `NOT_TESTED` gibi gerçek durumu ayrı tutulur.

## 4. Ürünün beklenen mühendislik sonuçları
1. HTML'de kullanıcı gerçek görev verir, planı ve izni görür, aynı tarayıcı oturumunda onaylar.
2. Gerçek izinli dosya doğar; içerik, SHA ve görev kimliği aynı makbuzda tutarlıdır.
3. Python işi ayrı süreçte test edilir; HTML işi gerçek tarayıcı etkileşiminden geçer.
4. Hatalı kaynak için **önce başarısız test → teşhis → izinli yama → gerçek tekrar PASS → regresyon** kanıtı toplanır (henüz genel kabulü açık).
5. Tekrarlı çalışma yeni dış etki yaratmaz; kesinti ve kanıt bozulması güvenli `HOLD` durumuna gider.
6. HTML yenilendiğinde kayıt ve makbuz geri gelir; bağımsız doğrulayıcı dosya SHA'sını yeniden ölçer.
7. Ana Pano haritaları gösterir, yetki veya sahte PASS üretmez; gerçek kaynaklar gereksinim ID ve testlerin yanındadır.
8. Günlük kullanıcı hiçbir komut/prosedürle uğraşmadan işi tamamlar (mevcut prototipte ayrıca kanıt gerektirir).
9. Hafıza Sarayı kaydı eklemelidir: yeni kimlik eski kazanım bağlantılarını korur; K03/K04 açık kalır.
10. **Hedef 1** tüm on iki kontrol geçince `HTML_PROTOTYPE=PASS`; Hedef 2 owner kararıyla açılır.

## 5. Kabul merdiveni ve kalite hükmü
| Katman | Tamamlanma koşulu | Mevcut kapsam |
|---|---|---|
| Teori | Tek ürün, beceri hiyerarşisi, sınır, kaynak ve hedef/kapı 10/10 | Kendi rubriğinde 100/100 adayı |
| Tasarım | Dokuz harita, 12 Y, 6 KMP, 10 Q ve Ana Pano tüm ID bağları | Kendi rubriğinde 100/100 adayı |
| Zülfikar SIM1–SIM3 | Her haritada olumlu/karşıt/onarım; sahte yetki, SHA drift ve sahte PASS reddi | Gerçek sentetik testle ölçülür |
| Teknik regresyon | Önceki 26 H1 ve 21 harita testlerinin yeni sürümde çalışması | Gerçek test makbuzuyla karar |
| HTML ürün | `H1-C01..H1-C12` 12/12 gerçek tarayıcı, dosya, test, SHA, yenileme, negatif, bağımsız kabul | Açık, gerçek kanıt gerekir |
| Mac OSi | Yerel Mac saha, kurulum, restore ve owner kabulü | `PARKED` |

Tasarım 100/100 ile gerçek ürünün `PASS` hükmü ayrı değerlendirilir. Kendi hazırladığımız yapısal testler bağımsız DoneCheck™ değildir. Düzeltme döngüsü: **Hakikati gör → Değeri koru → Eksikleri bul → Gereken farkı üret → Test/Simülasyon → Onar → Tekrar test → Kanıtla → Kabul → Kazanımı koru.**

**Kalıcı ve sabit sonraki tek hareket:** gerçek tarayıcıda doğrudan HTML→HTTP API→gerçek dosya→gerçek test→HTML makbuzu aynı oturum testini tamamlamak. **Hedef 2 ASKIDA.**
