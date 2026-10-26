# ENGÜRÜ PiLive™ — Mevcut Mühendislik Kası™ öğrenme adaptörü V1

25 Ekim 2026. `REVIEW_CANDIDATE / PRODUCT_ACCEPTANCE_HOLD`.

## Görev ve izinli kapsam

Mevcut kasın varsayılan `ENGURU_MANAGEMENT_V69_PR_203` görevi, watcher hedefleri, owner-comment allowlist'i ve Yönetim V6.9 bitiş hedefi korunur. PiLive için kaynak Work Contract'taki gerçek `ENGURU_PLIVE_P02_USER_SCREEN` kimliği yalnız açık öğrenme adaptörü çağrısında seçilir. Varsayılan parser, CLI ve watcher PiLive event'ini kabul etmez. PiLive adaptörü Yönetim event'ini kabul etmez. Etkinlik gövdesi görev kapsamını kendi başına seçemez.

İzinli fark: mevcut parser/process'in sabit ve açık görev parametresi, ayrı PiLive öğrenme adaptörü, regresyonlar, salt inceleme kanıtı ve aynı yaşayan kayıtta gizlisiz öğrenme adayları. Yeni Progress Core, ürün sayacı, signer, scheduler, writer veya resmî kabul yetkisi oluşmaz. Otomatik PiLive watcher aktivasyonu bu değişiklikte bulunmaz.

## Gerçek kanıt ve gizlilik

V2 makbuz SHA-256 `0dac03bf15579f28bccd3da5fc3daa36fb81c5d368b209216a0c32769d6327a8`.
V3 makbuz SHA-256 `bd64da51f2b708d55c358cf4307f2e746d8ddd33f5814690ed0ff3791652e1ed`.
V3 gözlem aracının SHA-256 değeri `cbf8fe07a71466f3907d5553495be393b4102d72065446c69f1ccef16403587e`.

V2→V3 parent bağı, 7 canonical içeriğin eşliği ve 116 içerik kaydının UTF-8 bayt/SHA eşliği doğrulandı. V3'te 97 PiLive Swift aday dosyası, 54 benzersiz PiLive Swift içeriği bulunuyor. Ek Swift envanterindeki bir dosya PiLive yol bağlamı dışında; ham içerik aktarımına alınmamış. Tarihsel V3.1 kaydında dört Swift source pini yakalanan içeriklerle eşleşiyor; iki Python kaynak pini ve kurulu binary'ye kadar tam build kaydı açık. Kod/binary kimliği ve uçtan uca build kökeni ayrı kanıtlardır.

Ham native dosyalar, Swift içerikleri, yerel kullanıcı yolları ve özel depo metaverileri bu PR'a eklenmedi. Yerel özel-bilgi desen taramasında private key/token/parola ataması eşleşmesi 0 gözlendi; ham kaynaklarda kişisel yollar bulunduğu için ham içerik yerelde tutuldu. Desen taraması tam gizlilik kanıtı sayılmaz. Kamusal adaylar sabit sözlükteki gözlemler ve SHA işaretçileriyle sınırlı, A düzeyinde ve REVIEW_REQUIRED durumundadır. Kaynak SHA işaretçisi tek başına bağımsız ürün kabulü oluşturmaz.

## Gerçek kaynak tekrarı

Yakalanan orijinal Progress Core, adapter, intelligence ve P02 canonical baytları dar bir Linux kaynak tekrar ağacında çalıştırıldı. P02 `countedPass=0`, `total=12`, `progressIntegrity=PASS`, `finishState=HOLD`; dependency/criticalPath `NOT_DECLARED`. Bu dar tekrar ağacı tam Mac registry ortamı veya native saha verify yerine geçmez. Diğer keşfedilmiş projelerin eksik dosyaları bu tekrar ağacına eklenmedi; sonuç yalnız P02'nin yakalanan kaynak semantiği kapsamındadır. Kaynak paydası ve resmî kabul sınırı korunur.

## Çift yönlü öğrenme

**OSi → GitHub:** Dar tracked sorguda sıfır Swift sonucundan genel yokluk çıkarımı, tarihsel pin ile build kökeninin ayrımı ve arşiv Swift bridge'indeki sayı dönüştürme davranışı üç ayrı öğrenme adayı olarak mevcut yaşayan kayda bağlandı. Kaynak gözlemi, doğrulanmış kök neden ve ürün kabulü ayrı tutuldu.

**GitHub → OSi:** Exact kaynak manifestiyle aynı parser, PiLive adaptörü ve regresyon testleri ayrı geçici test alanında çalıştırılacak. Yerel kas dosyalarının varlık/SHA ve görev kapsamı salt okunur gözlenecek. Orijinal Mac kaynakları korunur; kalıcı kasa yazım için mevcut öğrenme yolu ve gerçek kapsam eşliği ayrıca doğrulanır. GitHub paketinin Mac'te test edilmesi, eski yerel kasın güncellendiği beyanını oluşturmaz.

Öğrenmenin tekrar testi: aynı event idempotent; aynı ID'de farklı içerik HOLD; yanlış görev, ham metin/gizli içerik, parent/SHA drift, duplicate kaynak eşlemesi, boole/ondalıklı sayaç, yanlış run türü ve geniş schedule aralığı karşıt testleri.

## Beş dakikalık gözlem

Gerçek `event=schedule` GitHub run verileri okundu. Kas workflow'u `393938055` için son dört tamamlanmış run aralıkları 19355 / 18751 / 7086 saniye; controller `392178296` için 11969 / 19653 / 17880 saniye. Run kimlikleri `SOURCE_REVIEW_V1.json` içinde. 420 saniyelik sınıra göre iki gözlem de `HOLD_SCHEDULE_CONTINUITY`; ayrıca dört run'ın tamamı güncel main kaynağında bulunmuyor. Cron ifadesi ve yeşil çalışma sonucu gerçek beş dakika sürekliliğini tek başına kanıtlamaz. Bu küçük örnekten genel hizmet SLA'sı çıkarılmadı. Mevcut schedule yapılandırması korundu.

## Test ve ürün sınırı

Mevcut kas sözleşmesi: 104 test × iki temiz subprocess turu, 25/25 amaç kapısı PASS. Ek PiLive adaptörü: 26 bağımsız test; scope/kanıt/display-schedule aileleri. Bu testlerin sonucu kasın yardımcı mühendislik kapsamına aittir. PiLive TASARIM/TEORİ/GitHub 5×100 veya U01–U12 kabulüne puan aktarmaz.

`TASARIM=87/100` A ve `85/100` B önceki öz değerlendirmesi korunuyor; bağımsız görsel doğrulama ve yaratıcı kullanıcı kabulü açık. PiLive U01–U12, P02 12/4/7, G3, P01/P06 ve native Verified Finish kendi kaynak/kanıt/yetki kapılarında kalır. Mac kaynak makbuzunun AudiV13 orijinali ile Masaüstü kopyasının güncel yerel readback karşılaştırması ayrıca yürütülecek; yüklenen tek kopya bu eşliği tek başına kanıtlamaz.

**Sonraki somut hareket:** Aynı exact GitHub kaynak paketini Mac'te ayrı geçici test alanında sınamak, mevcut yerel kas dosyalarının kapsam/SHA eşliğini okumak ve sonuç makbuzunu mevcut PiLive öğrenme adaptörüne geri bağlamak.

## Native tekrar probu

`tools/pilive_native_learning_probe_v1.py` yalnız Darwin CLI girişinde, manifestte SHA'sı sabitlenmiş GitHub testlerini sahipliği belli geçici dizinde çalıştırır: mevcut 104 + PiLive adaptörü 26 + probe sınırları 6 = 136 özgün test. Kurulu yerel kası içe aktarmadan iki bilinen repo kökünde yedi exact kaynak yolunun içerik/SHA/görev sabitlerini okur; bulunmayan dosya `MISSING_IN_EXACT_SCOPE` olarak raporlanır. Bu sınırlı kapsam bütün Mac'te yokluk hükmü oluşturmaz.

Sekiz native Core/canonical kaynak SHA'sı eşleşirse mevcut `enguru_progress.py plive-p02-user-screen --verify`, `-B -S` ile ve PYTHONPATH kaldırılarak çalıştırılır. Önce/sonra source SHA eşliği ve gerçek verify alanları kaydedilir. Uygulama açılışı, Keychain, ağ, canonical yazım ve yerel kas yazımı 0. Testlerin kendi fixture/checkpoint yazımları yalnız yeni geçici test alanındadır. İki önceki makbuzun AudiV13 orijinali ve Masaüstü kopyası aynı exact pinlerle yeniden okunur. Yeni sonuç orijinali ve SHA eş kopyası benzersiz adla kaydedilir.

Probe'un Linux test kancası yalnız izole paket sınaması içindir; CLI Darwin kapısını korur. Native başarı ancak gerçek Mac sonuç makbuzuyla verilir. Bu probun PASS'i kullanıcı ekranı, owner estetik kabulü, resmî P02 veya Verified Finish yerine geçmez.

## Gerçek native tekrar ve fixture onarımı

Native makbuz SHA-256: `8485dbab50bd10e626db07ff6245feabe07d35f09faa7287b4f9809c026b22a8`.
GitHub kaynağı `52feb13810b8a7166f92c3a06521ee7ca7d0ee13`, paket manifest SHA-256 `9b0eafd9bbb1bda80ac77520db79e9c6fd92f32549a73cfe7b976c393d6cfb29`.

Gerçek Mac'te ilk 130 test ve probe'un 2 testi geçti; kalan 4 probe testi geçici test kökünde hata verdi: 2 failure + 2 error. Gerçek native Core verify PASS; 8/8 kaynak pini önce/sonra aynı, P02 countedPass=0, stateDrift=NONE ve finishState=HOLD. V2/V3 makbuzlarının AudiV13 orijinal ve Masaüstü kopyaları exact SHA ile 2/2 PASS. İki bilinen repo kökünde sorgulanan 14 exact kas yolu bulunmadı; bu bulgu bütün OSi üzerinde kas yokluğu hükmü oluşturmaz. Yerel kasın gerçek konumu ve görev kapsamı açık.

Hata kaynağı: test fixture'ının geçici dizin yolu, üretim okuyucusunun her bileşende uyguladığı O_NOFOLLOW sınırına ulaşıyor. Symlink içeren TMPDIR ile aynı 2 failure + 2 error Linux'ta yeniden üretildi. Onarım yalnız sahipliği belli fixture köklerini `resolve(strict=True)` ile hazırlıyor; üretim `directory_fd` ve `read_file` gövdeleri korunuyor. Yeni karşıt test, alias kökünün üretim okuyucusunda reddedildiğini, çözümlenmiş fixture kökünün okunduğunu ve leaf symlink'in yine reddedildiğini birlikte sınar.

Yeni probe test sayısı 7; toplam aktarım 137 özgün test. 33 yeni test, normal ve alias TMPDIR altında üçer tur PASS; mevcut 104 test iki temiz tur PASS. Native yeni tekrar kendi gerçek makbuzunu bekler. Önceki 136 testlik makbuz tarihsel kanıt olarak korunur. Yeni paket önceki native makbuzun orijinal/kopya eşliğini de okur. Bu onarım aynı yaşayan kayda ayrı PiLive öğrenme adayı olarak bağlandı.

## Native onarımın gerçek tekrar kanıtı

25 Ekim 2026 19:03:40 Türkiye saati. Yeni makbuz SHA-256 `81cf6112ea6faf14ea02c750373a23ab08b5e7d28fd9cd950a060eb0a8c71a7a`.
Exact paket kaynağı `9ac7f9555f0a7e265a650aca8b76533cb5952b2d`; manifest SHA-256 `d8318496adda0331340ab9168022b69e4527a094266cead7cb2e29b7a20dad44`. Makbuzdaki iki değer, teslim edilen V2 paketin gerçek manifest baytlarıyla eşleştirildi.

**Gerçek Mac: 137/137 test PASS.** Suite sayıları 33 + 46 + 25 + 26 + 7. Native Core verify yeniden PASS, sekiz kaynak pini önce/sonra aynı. Üç önceki makbuzun orijinal/kopya/pin eşliği 3/3 PASS. P02 countedPass=0, finishState=HOLD. Canonical, yerel kas, Keychain, ağ ve uygulama açılışı sayıları 0.

Native onarım başarılıdır; özgün ürün kabulleri ayrı kalır. İki bilinen repo kökünde incelenen 14 exact kas yolu yine bulunmadı; gerçek yerel kas konumu ve görev kapsamı HOLD. GitHub paketinin Mac'te geçici test edilmesi, kurulu yerel kasın değiştirildiği anlamına gelmez. Aynı yaşayan kayda gizlisiz SUCCESS inceleme adayı eklendi; ham kaynaklar taşınmadı.
