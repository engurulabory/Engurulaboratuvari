# ENGÜRÜ — Masa Başı Mühendislik Denetimi V2

**Kapsam:** Gerçek Mac OSi saha kanıtı ve altı gerçek ürünün üretim kabulü hariç. Bu belge kullanıcıya özgü mühendislik değerlendirmesidir; canonical V3 ve 48 özgün kontrolün yerini almaz.

## Sabit kalan değerler

- ENGÜRÜ Süzgeci™ sekiz aşama, V3 SHA-256, DoneCheck™ v1.2 ve gereken Human Threshold™ korunur.
- 5 × 100/100 teorik Ana Terazi, kendi sabit 48 D kontrolünü ve farklı SIM1/SIM2/SIM3 test ailelerini korur.
- Altı üretim alanı, 12 ortak + 4 özgün kontrol adaptörüdür; **96 uygulama** yeni 96 evrensel kanıt maddesi sayılmaz.
- Orijinal sentetik örnek `62,5 → 87,5 → 100` **eğitim amaçlı korunur**; farklı tasarım problemlerinin doğal sonuçları için evrensel oracle olmaz.

## Kesin masa başı bulgular ve düzeltmeler

| Bulgular | Kök neden / kapsam | Yeni çözüm | Son gerçek hüküm |
|---|---|---|---|
| Atlas tarihsel REVIEW_CANDIDATE / kapanış aracı PR221 unmerged yazıyordu | Statik tarihsel durum; merge sonrasına otomatik taşınmış | Tarihsel pin ayrıldı, canlı `main` okunur; statik receipt merge kararını kendi başına üretmez | Yeni GitHub CI ve exact-main kanıtına bağlı |
| Üç turlu adaptör testi bütün alanlarda aynı puan dizisini hedefliyordu | Hazırlanmış tek sentetik kurgunun yanlış genellenme riski | V2 24 farklı başlangıç, 6 alan, değişken kısıt/bütçe ve hedeflenen HOLD | Tasarım CI ve karşıt kontrole bağlı |
| Beş teşhis sınıfı sıra numarasıyla dağıtılıyordu | Kaynak gözlemine dayalı sınıflama eksikliği | V2 hata biçiminden `missing/need/requirement/error/incorrectness/provenance` tanısı verir | Kapsam sentetik gözlemdir, gerçek iş kök nedeni değildir |
| Gerçek ana yöntem CI yalnız PR olayında tetikleniyordu | `push: main` kapsamı tanımlanmamış | Yöntem kaynakları değiştiğinde main push üzerinde aynı CI | Exact-main sonrası çalıştırılmış job kanıtı gerekir |
| Yeni oturum başlatma çoklu dosya ve elle yönlendirme gerektiriyordu | Giriş noktası dağınık | [Tek Giriş V2](ENGURU_GITHUB_METHOD_ENTRY_V2.md), dinamik anlık HEAD kuralı | İlk gerçek oturum kullanımı ayrıca ölçülür |

## Karşıt denetim ve puanlama politikası

- **V2 dinamik tasarım yürütücüsü:** `tools/enguru_method_dynamic_loop_v2.py`. Sözleşmeden çıkan gözlemler üç turda yeniden ölçülür. **12 başarı + 12 gerekçeli HOLD** örnek seti bilinçli olarak karışıktır. 100/100, yalnız sıfır açık durumunda çıkar.
- **İkinci makine kontrolü:** `tools/enguru_method_dynamic_adversarial_v2.py`, **576** ayrı alan/kontrol/bozulma ve **52** senaryo/sahte puan/değişken bütçe sınamasını uygular. Testin kendi kodunun aynı depoda olması bağımsız insan incelemesi anlamına gelmez.
- **Hedeflenen mühendislik puanı:** Eski öznel değer `92/100`; görev sonrası `98/100` ancak gerçek kaynak tutarlılığı, her iki test, exact-main CI ve açık kalan semantik sınırlar ayrı açıklanınca *değerlendirme* olarak verilebilir. `98`, evrensel kabul makbuzu/alan ürün tamamlanması veya saha kanıtı değildir.
- **Bilinen masa başı sınır:** 48 kontrolün dış muadil kaynak URL/provenance eşleşmesi otomatik denetlenir; her bağlantının tasarım ölçütünü *anlamsal* olarak desteklediği bütün olgular için ikinci bir bağımsız insan akademik denetimi yapılmış değildir.
- **Saha sınırı:** OSi kullanıcı kurulumları, gerçek ticari satış, agent gerçek araç eylemleri, app imzalama ve DoneCheck™ gerçek yetki kabulü ayrı HOLD olarak kalır.

**İLERLE:** Gerçek test kanıtını kaydet, yeni yöntem çekirdeği açmadan kalan ürün çalışmalarında kullan. **GÜVENLİ_DUR:** Doğrulanmamış semantik iddia, farklı kaynak yetkisi veya resmî saha kabulü gerektiren hükmü kendi kanıt kapısına yönlendir.
