# FETİH CORE v0.1

Kaynağa bağlı deterministik kavram adayı çıkarımı ve salt okunur yerel API. Python **3.10+**; standart kütüphane; çalışma anında ağ ve ücretli API bağımlılığı sıfır.

## Tek kurulum ve sınama

ZIP'i açın. Terminal'de bu klasöre geçtikten sonra:

```bash
python3 install_and_test.py --target "$HOME/FETIH_CORE_V01_$(date +%Y%m%d_%H%M%S)"
```

Bu komut kaynak bütünlüğünü kontrol eder, yeni ve yalıtılmış hedef oluşturur, pip/indirme gerektirmeyen venv kurar, çekirdeği kopyalar, testleri çalıştırır, JSON üretir ve ayrı süreçteki gerçek HTTP API'yi sorgular. Hedef klasörün önceden bulunması durumunda durur. Eski Ulak, PiLive, SQLite veya projelere erişmez. Çıktıdaki `receipt`, `RUNTIME_RECEIPT.json` yoludur. `serve` dizisini Terminal komutu olarak çalıştırınca API sürekli açılır. Varsayılan port 8765; meşgulse `--port 8766` ekleyin. Durdurma: Ctrl-C. Otomatik başlatma veya sistem kurulumu içermez.

**Mac OSi saha durumu:** Bu teslimde Linux üzerinde yalıtılmış kurulum yürütülmüştür. Mac çalışması makbuzu henüz yoktur. Mac kurulum hareketi owner'ın kararıyla başlatılır. Önceden sistemde Python 3.10+ bulunmalıdır; kurucu Python indirmez veya sistem ayarlarını değiştirmez.

Geri alma: Üretilen kanıtları koruduktan sonra yalnız bu komutun oluşturduğu yeni hedef klasörünü kaldırın. Kaynak ZIP ve önceki ürünler korunur.

## Kullanım

Kurulum sonucundaki Python yolu için örnek:

```bash
/YENI_HEDEF/venv/bin/python -I -B -m fetih_core verify
/YENI_HEDEF/venv/bin/python -I -B -m fetih_core export --output /YENI_HEDEF/yeni_cikti.json
/YENI_HEDEF/venv/bin/python -I -B -m fetih_core serve --port 8765
curl 'http://127.0.0.1:8765/verses?id=48%3A25'
curl 'http://127.0.0.1:8765/graph?concept=bilgi%20s%C4%B1n%C4%B1r%C4%B1'
```

Dışa aktarım mevcut dosyanın üzerine yazmaz. API salt okunurdur; onay veya kullanıcı verisi yazan uç nokta bulunmaz. İnsan incelemesi `review-queue` çıktısı üzerinden yapılır; bu sürümde inceleme kararı otomatik statü yükseltmez. `Origin` başlığı olan tarayıcı çağrıları ve beklenmeyen Host reddedilir. Bu API çok kullanıcılı kimlik doğrulama servisi değildir.

| Uç nokta | İşlev |
|---|---|
| `/health` | Kaynak yüklenmesi ve sürüm |
| `/verses`, `/verses?id=48:25` | 29 ayet veya tek ayet |
| `/sources` | Kaynak ve meal/tefsir kimlikleri |
| `/concepts`, `/review-queue` | İnsan incelemesi bekleyen adaylar |
| `/graph?concept=...` | Kaynaklı komşu ilişkiler |
| `/models` | Açık K4 süreç/koşul/eylem/sonuç modeli |
| `/hypotheses` | Deneysel H01 hipotezi |
| `/export` | Birleşik JSON |

## Veri ve anlam sınırları

Arapça metin: [Tanzil Project](https://tanzil.net), Uthmani 1.1; 29 ayetlik özgün dizeler korunur. Yayıncının ilk ayet dışa aktarımı besmeleyi içerir. Lisans ve telif bildirimi veri klasöründe bulunur. Ayrı AlQuran Cloud yayın kanalıyla temel harf dizisi 29/29 karşılaştırılır; durak/hareke farkları orijinalde korunur. Bu iki kanalın editoryal bağımsızlığı kanıtlanmış değildir.

Diyanet tefsirinin 48. sure kayıt kimlikleri ve ayet aralıkları okunmuştur. Telifli tefsir ve meal metinleri bütünüyle dağıtılmaz. Meal kaynak kataloğu kimlikleri saklanır; meal metni bu sürümde çıkarım girdisi değildir. `source_reference`, metnin doğru aktarıldığına ve ilgili tefsir aralığına bağdır; insanın ilişkiyi onayladığı anlamına gelmez.

**K1:** Arapça ayet. **K2:** Diyanet tefsir kimliği ve okunmuş bağlam. **K3:** Yedi dar sözlük kuralıyla üretilen insan incelemesine açık kavram/ilişki adayları. **K4:** Ayrı mühendislik modeli ve kısa-iş-önce hipotezi. Tüm 29 ayet yüklenir; 7 ayette aday anotasyon vardır. Genel Arapça anlambilim veya bütün sureyi eksiksiz yorumlama iddiası yoktur. Doğrulanamayan adaylar `PENDING_HUMAN_REVIEW` kalır.

`confidence=0.5`, sabit aday öncelik işaretidir; kalibre edilmiş olasılık, kaynak doğruluğu veya dinî kesinlik değildir. Kaynak metin bütünlüğü ve yorum kabulü ayrı alanlardır. SHA sabitleri yerel değişimi yakalar; kod ve sabitlerin birlikte değiştirilmesini önleyen imzalı haricî güven kökü değildir.

## Test ve deney

Kaynak klasöründe `python3 -B -m unittest discover -s tests -v`. Kurucu aynı testleri kurulu kopya üzerinde `-I` ile çalıştırır. Birim, gerçek HTTP bütünleşme, kaynak değişimi/silme/symlink, sahte yorum, ayet sınırı, bozuk tür, NaN, yinelenen JSON anahtarı ve yazma girişimi testleri vardır.

`python3 experiment/run.py` tek ön kayıtlı **sentetik** A/B ön sınamayı tekrarlar. Beş vaka aynı girdi/bütçeyi paylaşır. İşlerin süreleri sentetik girdidir; API/algoritma hesap süresi gerçek ölçümdür; insan emeği ve gerçek uygulama süresi ölçülmemiştir. Her iki yöntem de bağımlılık/bütçe denetimi yapar; B yalnız uygun işler arasındaki sıralamayı değiştirir. Olumsuz karşıt örnekler korunur. Sonuç evrensel üstünlüğü desteklemez. Gerçek insan faydası `NOT_TESTED`.

## Kaynak lisansı

Python kaynak kodu ve özgün belgeler ENGÜRÜ teslimidir; üçüncü taraflara otomatik lisans verme amacı taşımaz. Tanzil metni kendi CC BY 3.0 ve değiştirmeden dağıtım koşullarına tabidir; `fetih_core/data/TANZIL_LICENSE.txt` içindeki bildirimi koruyun. İkinci Arapça kanal, zaten Tanzil ile karşılaştırılan kutsal metnin kontrol kopyasıdır. Meal/tefsir kaynak adları, kayıt kimlikleri ve kısa özgün özetler kaynak izlenebilirliği içindir.
