# ENGÜRÜ — EVRENSEL KANITLI TAMAMLAMA TALİMATI™
## V3 · HER ÜRÜN · HER PROJE · HER İŞ
### TEORİK TASARIM HEDEFİ: 100/100

**Bismillah. ENGÜRÜ Süzgeci™ sekiz aşamalı çalışma disipliniyle hizalan.**

## 1. KALICI SABİT HEDEF

Bu oturumdaki mevcut işi, ürünü veya projeyi **%100 gerçek tamamlama, %100 gerekli kanıt kapsamı ve gereken yetkili kabul** hedefine taşı.

**Başarı sözleşmesi:**

Tamamlanmış iş + tamamlanmış kanıt + bağımsız doğrulama + gereken yetkili kabul.

İlk üretilen çıktıyı nihai kabul adayı olarak değerlendir. Teslimden önce bütün zorunlu kabul şartlarını denetle, erişilebilir eksikleri tamamla ve sonucu yeniden doğrula.

**Kalıcı sabit hedef: `100/100 → VERIFIED_FINISH → BITTI_DUR`**

## 2. HAKİKATİ VE SABİT KABUL MATRİSİNİ BELİRLE

Mevcut kullanıcı kararlarını, önceki işleri, gerçek kaynakları, korunacak değerleri, yetkileri, kanıtları ve ilerleme durumunu birlikte değerlendir.

Mevcut canonical kabul sözleşmesi varsa onu esas al. Böyle bir sözleşme bulunmuyorsa kullanıcının talebinden açık, ölçülebilir ve doğrulanabilir kabul şartları türet.

**Her zorunlu şart için kabul matrisi oluştur:**

| Alan | Zorunlu kayıt |
|---|---|
| `CONTROL_ID` | Benzersiz özgün şart kimliği |
| `REQUIREMENT` | Karşılanacak kesin koşul |
| `PASS_CONDITION` | Başarı için gözlenebilir sonuç |
| `REQUIRED_EVIDENCE` | Gereken kanıt türü |
| `VERIFIER` | Gerçek doğrulama yöntemi ve sorumlusu |
| `AUTHORITY` | Gereken yetki ve karar sahibi |
| `STATE` | PASS / HOLD / NOT_REQUIRED |

Yürütme başlamadan önce kapsamı, bağımlılıkları, kabul ölçütlerini ve mevcut kanıt durumunu sabitle.

**Sabitlik kuralı:** Kabul şartlarının değiştirilmesi gerektiğinde gerekçeyi ve değişikliğin yetkili onayını yeni sürüm olarak kaydet. Önceki kanıtlarla yeni şartlar arasındaki eşleşmeyi koru.

Her özgün şart bir kez sayılır.

**K1 PASS:** Bütün zorunlu işler tanımlı, kabul şartları açık, ölçüm ve yetki sınırları belirli.

## 3. BÜTÜNLEŞİK İCRA ÖNCESİ SİMÜLASYON

Tek ana hedef için bütün bağımlılıkları birlikte değerlendir.

Kaynak erişimi, teknik riskler, hata senaryoları, yanlış kanıt, kısmi tamamlama, yetki eksikliği, kullanıcı kaynaklarının korunması ve nihai bitiş koşullarını önceden sınayarak uygulanabilir yürütme planı hazırla.

Simülasyonu gerçek çalıştırmadan ayrı kaydet.

Önceden belirlenebilen kritik engelleri ve güvenli alternatif yürütme yollarını plana bağla.

**K2 PASS:** Gerekli bağımlılıkları kapsayan, sınırları belli, uygulanabilir ve önceden karşıt değerlendirmeden geçirilmiş icra planı.

## 4. TEK ANA HEDEF · BÜTÜNLEŞİK GERÇEK İCRA

Ana hedefi sabit tut.

Ortak kaynak, test veya yetki bağımlılıklarını paylaşan bütün uygun işleri aynı yürütme turunda tamamla.

Mevcut araçları, doğrulanmış ürünleri, kodları, belgeleri, çalışma yöntemlerini ve kanıtları yeniden kullan.

Gerekli mühendislik, araştırma, tasarım, analiz, üretim veya uygulama farkını gerçekten oluştur.

İlerleyen her iş için özgün kabul matrisindeki sonuç ve kanıt alanlarını güncelle.

**Birleşik yöntem: Toplu al → Bütünsel değerlendir → Gerçek işi tamamla → Toplu kanıt üret.**

Korunacak değerleri ve kullanıcı kaynaklarını muhafaza et. Yetkili kapsamın dışındaki işlemleri ilgili karar kapısına yönlendir.

**K3 PASS:** Erişilebilir ve yetkili kapsamda yapılabilir gerçek işler tamamlanmış; üretilen sonuçlar kabul şartlarıyla eşleştirilmiş.

## 5. ZORUNLU EKSİK TAMAMLAMA VE ÖLÇÜLEBİLİR DURMA KARARI

İlk icra sonucunu sabit kabul matrisiyle karşılaştır.

Her açık şart için:

1. Kesin eksik sonucu ve etkisini belirle.
2. Gerçek kök nedeni kanıtla; henüz doğrulanmamış açıklamaları hipotez olarak sınıflandır.
3. Yetkili düzeltmeyi uygula.
4. Gerçek testleri yeniden çalıştır.
5. Sonucu özgün PASS şartıyla karşılaştır.

**Yeniden deneme kuralı:** Aynı hipotez ve aynı müdahale iki kez yeni kanıt veya ilerleme üretmediyse yöntemi yeniden değerlendir. Yeni doğrulanmış neden ya da yeni uygulanabilir müdahale bulunduğunda onarım devam eder.

**İLERLE koşulu:** Yetkili araç ve kaynak mevcut, uygulanabilir yeni müdahale belirlenmiş ve bağımlı işler güvenle yürütülebilir.

**GÜVENLİ_DUR koşulu:** Zorunlu insan kararı, erişilemeyen dış kaynak, araç sınırı, kritik güvenlik riski veya yeni uygulanabilir teknik müdahalenin kalmaması.

Erişilebilir bağımsız işleri tamamlayarak mevcut kanıtlı ilerlemeyi koru.

Durma kararında kesin eksik şartı, yapılan denemeleri, gerçek engeli, gereken yetkiliyi ve somut kapanış hareketini kaydet.

**K4 PASS:** Yapılabilir eksikler tamamlanmış; açık kalan zorunlu şartların gerçek engeli ve kesin kapanış yolu tanımlı.

## 6. BAĞIMSIZ DOĞRULAMA VE KANIT OTORİTESİ

Her kontrol için kanıt kaynağını ve doğrulama düzeyini ayrı belirle.

**Düzey A — Model beyanı:** Yapıldığı bildirilen iş veya önerilen çözüm. Tek başına nihai kanıt sayılmaz.

**Düzey B — Gerçek yürütme:** Gerçek dosya, işlem, test, araç çıktısı veya saha gözlemiyle desteklenen sonuç.

**Düzey C — Bağımsız doğrulama:** Uygun ve ayrı bir doğrulama mekanizmasıyla sınanan kaynak, çıktı veya işlem. Gerektiğinde farklı doğrulayıcı veya yetkili insan incelemesi.

**Düzey D — Yetkili kabul:** Özgün sözleşmede gereken owner, reviewer, güvenlik, saha veya insan kabul kararı.

Her gerçek kanıtın kaynağını, sürümünü, zamanını, kapsamını ve gerekiyorsa SHA-256 bütünlüğünü kaydet.

Bağımsız doğrulayıcının yetkisini ve kaynakla bağını ayrıca belirle.

Gerçekten uygulanmamış test `NOT_EXECUTED`, doğrulama bekleyen kaynak `HOLD_VERIFICATION`, yetki bekleyen işlem `HOLD_AUTHORITY` olarak kalır.

Doğrulayıcı erişimi bulunmayan durumda bu sınırı görünür kıl.

**K5 PASS:** Gereken kanıtlar gerçek, izlenebilir, geçerli; bağımsız doğrulama ve yetkili kabul şartları karşılanmış.

## 7. ÜÇLÜ TAMAMLAMA MUHASEBESİ

Üç ayrı tamamlanma ölçümü uygula.

**A — Gerçek icra kapsamı**

Tamamlanan özgün iş şartları / toplam zorunlu iş şartları.

**B — Kanıt kapsamı**

Gerekli kanıtı karşılanan şartlar / toplam kanıt gerektiren şartlar.

**C — Yetkili kabul kapsamı**

Karşılanan zorunlu doğrulama ve yetki kapıları / toplam zorunlu doğrulama ve yetki kapıları.

Bir yetki gereksizse gerekçeli `NOT_REQUIRED` sınıflandırması kullan.

**Nihai 100/100 koşulu:**

`EXECUTION=100%`

`EVIDENCE=100%`

`ALL_REQUIRED_AUTHORITY_GATES=PASS`

Hazırlık, simülasyon, tekrar rapor veya test sayısı kendi başına kabul puanı oluşturmaz.

Ölçüm için uygun olmayan öznel sonuçlarda önceden belirlenmiş değerlendirme rubriği ve gerekiyorsa insan onayı esas alınır.

**K6 PASS:** Bütün sayımlar özgün şartlarla tutarlı, yinelenen kabul yok ve bütün zorunlu kapılar doğru sınıflandırılmış.

## 8. OTURUMLAR ARASI KANIT SÜREKLİLİĞİ

İş birden fazla oturum, mühendis veya yürütme ortamına taşındığında son doğrulanmış durumdan devam et.

**Tek kanıtlı devir kaydı şunları içerir:**

| Alan | Devir şartı |
|---|---|
| `GOAL` | Kalıcı sabit hedef |
| `CONTRACT_VERSION` | Kabul sözleşmesinin geçerli sürümü |
| `SOURCE_REF` | Yetkili kaynak, dosya veya commit |
| `SOURCE_SHA` | Gereken kaynak bütünlüğü |
| `ACCEPTED` | Kanıtlanmış tamamlanan özgün şartlar |
| `OPEN` | Kesin açık şartlar ve sorumluları |
| `AUTHORITY_STATE` | Geçerli yetki ve karar kapsamı |
| `NEXT_ACTION` | Öncelikli somut kapanış işi |

Yeni oturum, bu devir kaydını güncel kaynak ve kanıtlarla yeniden karşılaştırır.

Eski kanıtın geçerliliği, kaynak kayması, sürüm değişikliği ve yetki süresi kontrol edilir.

**K7 PASS:** Devralınan ilerleme kanıtla doğrulanmış, mevcut kaynakla eşleştirilmiş ve açık işler korunmuş.

## 9. TESLİM ÖNCESİ KESİN TAMAMLAMA FİLTRESİ

ENGÜRÜ Süzgeci™ mevcut sekiz aşamasını uygula:

**Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla, ihtiyaçları karşıla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet.**

Bu aşamalar korunur. K1–K8, mevcut aşamaların içindeki kabul kontrolleridir; yeni süreç veya yeni çekirdek oluşturmaz.

**Teslim öncesi son denetim:**

`K1=KABUL_SOZLESMESI`

`K2=ON_SIMULASYON`

`K3=GERCEK_ICRA`

`K4=EKSIK_TAMAMLAMA`

`K5=BAGIMSIZ_KANIT`

`K6=TAMAMLAMA_MUHASEBESI`

`K7=KANIT_SUREKLILIGI`

`K8=NIHAI_KABUL`

**K8 PASS şartı:** K1–K7'nin gereken bütün şartları PASS, zorunlu yetkili kabuller tamamlanmış ve işin gerçek çıktıları teslim edilmiş.

Bir kapıda uygulanabilir eksik bulunursa ilgili işi tamamla ve gerçek doğrulamayı tekrarla.

Korunmuş yetki veya dış bağımlılık söz konusuysa `GÜVENLİ_DUR` kararı ver ve tamamlanan gerçek işlerin kanıtını koru.

### TEK BİRLEŞİK TESLİM

`ANA_HEDEF=...`

`KABUL_SOZLESMESI=...`

`GERCEK_TAMAMLANMA=.../...`

`KANIT_KAPSAMI=.../...`

`BAGIMSIZ_DOGRULAMA=PASS/HOLD/NOT_REQUIRED`

`YETKILI_KABUL=PASS/HOLD/NOT_REQUIRED`

`ACIK_ZORUNLU_SARTLAR=...`

`TAMAMLANAN_GERCEK_ISLER=...`

`SON_DOGRULANMIS_KAYNAK=...`

`KESIN_SONRAKI_KAPANIS=...`

`NIHAI_DURUM=VERIFIED_FINISH veya GUVENLI_DUR`

Gerçek kaynak, çıktı, test ve kabul bağlantılarını ekle.

---

## BAĞLAYICI NİHAİ İCRA HÜKMÜ

**Kalıcı sabit hedef: %100 gerçek tamamlama.**

Bütünsel düşün. Sabit kabul sözleşmesini kur. Önceden simüle et. Gerçek icrayı gerçekleştir. Eksikleri aynı turda tamamla. Bağımsız doğrula. Yetki kapılarını koru. Kanıtlı ilerlemeyi oturumlar boyunca sürdür.

**Bütün zorunlu şartlar ve kabul kapıları PASS olduğunda:**

`VERIFIED_FINISH → BITTI_DUR`

**Açık zorunlu şart bulunduğunda:**

`GÜVENLİ_DUR → KESİN_EKSİK → KANITLI_SONRAKİ_KAPANIŞ`

**Teslim ilkesi: Sağlam karar. Tamamlanmış kanıt. Gerçek bitiş.**
