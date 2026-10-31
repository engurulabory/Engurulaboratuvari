# ENGÜRÜ OSi Üçlü Yerel Zekâ™ — V015

İki zekâ · Bir ortak deterministik çekirdek · Bir Ulak.

Bu sürüm, gerçek SQLite defteri, typed rol önerileri, özel yerel yetki,
kapalı araç geçidi, bağımsız test doğrulaması ve read-only projeksiyonla
bütünleşmiş **ürün adayıdır**. Uçtan uca ürün kabulü HOLD.

## Gerçek çalışan kapsam

Türkçe `unique_jobs` sıra koruma görevi: Yönetici/İcracı typed öneri → kaynak ve
kapsam/yetki denetimi → özel çalışma alanında sabit bozuk kaynak → gerçek kırmızı
test → incelenmiş deterministik patch → gerçek yeşil test → bağımsız tekrar test
→ imzalı işlem makbuzu → verified kayıt → kanıtlı görev yüzdesi → Ulak snapshot.

Kuyruk SQLite WAL üzerinde kalır. Aynı kimlik ve aynı istek kararlı mevcut sonucu
döndürür; çelişki eskisini koruyarak reddedilir. Çift aktif iş indeksi, nonce,
flock ve transactional claim vardır. Çöken RUNNING görev salt-okunur uzlaştırma
için HOLD olur; yeniden etki otomatik uygulanmaz.

**Kapsam sınırı:** keyfi yazılım/dosya/GitHub görevleri henüz desteklenmez ve HOLD
olur. Bu araç geçidi keyfi Python için sandbox değildir. Serbest model kodunu
çalıştıran bir yol yoktur; yalnız release-pinned incelenmiş fixture/harness
çalışır. Modelin kodunu uygulayıp mesleki başarısını ölçtüğü iddia edilmez.

## Güven ve kaynak

Yerel owner UI/CLI bridge yalnız özel pilot için HMAC yetkisi üretir. Bu süreç
model JSON'undan grant almaz. Sahte/expired/yanlış task/plan/source/scope/resource
grant reddedilir. Anahtar özel profile'da0600; sistemde aynı owner UID altında
çalışan kötü niyetli süreçlere karşı tam OS sandbox/secure enclave iddiası yok.
Üretim kapsamının genel araçlara genişlemesi ayrıca güvenlik kabulü gerektirir.

İki rol localhost Ollama qwen3:14b aynı pinned digest üzerinde ayrı system
bağlamları kullanır. Dördüncü model, ücretli API ve model indirmesi yok. Canlı
model erişimi veya typed öneri başarısız olursa HOLD; test sağlayıcısına otomatik
geçiş yok. Linux regresyonda stublar açıkça etiketlenir.

## Mac adayı ve korunma

Native SwiftUI kaynağı tek sohbet, kanıtlı yüzde, açılır kuyruk/kanıt, uyku
activity token ve yerel IPC bridge içerir. V0.6 referans PNG'leri orijinal SHA ile
korunur. Canlı görünümün karakter/yerleşim eşdeğerliği, VoiceOver/kontrast,
gerçek build ve görsel owner kabulü HOLD; referans resmi canlı ekran değildir.
Ana Cockpit/PiLive portföy modalı bu ilk adayda uygulanmadı; eski uygulama/veri
kaynağına erişilmez. Genel görev becerisi ve günlük kullanım kabulü açık.

Mac akışı mevcut Python3.10+ ve mevcut Xcode araçları gerektirir; bağımlılık
indirmez. Paket doğrulamasından sonra yalnız AudiV13 altında yeni alanda ayrı
bir .app oluşturur. /Applications, eski Ulak, PiLive ve eski SQLite/yedeklere
dokunmaz. Geri alma: yeni uygulamayı kapatıp korunmuş önceki uygulamayı açmak;
silme/DBrestore yapılmaz. Kurulum receipt'i ve canlı yerel rol pilotu makbuzu
üretir. Bütün Mac sonuçları gerçek makbuz gelene kadar NOT_TESTED/HOLD.

## Kabul ve kararlar

contracts içindeki onaylı metinler değişmeden saklanır. Bu metinlerdeki eski
taslak statüsünü owner39 mimari onayı ve owner40 bütünleşik teslim kaydı ayrı
olarak sürümler; eski baytlar değiştirilmez.34 karar eşleme taslağı signed owner
registry değildir; authority-review kaydı bu ayrımı korur. Bu durum owner39/40
yetkisinin tekrar istenmesi anlamına gelmez.

75 özgün koşulun metni/ID/alanı birebir doğrulanır; kısmi testler otomatik75PASS
üretmez.9 kapı kendi kapsam kanıtıyla değerlendirilir. Pilot100%,
PASS_SCOPED_PILOT; ürün Verified Finish HOLD. ZülfikarV1.4.1 yöntem hizası
uygulanır; gerçek motor yürütmesi iddia edilmez.
