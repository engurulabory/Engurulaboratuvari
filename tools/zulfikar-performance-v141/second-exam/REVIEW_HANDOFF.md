# İkinci Gerçek İcra Sınavı — bağımsız inceleme devri

Korunan kabul: PR #247 / a83f6f428b6a4373be60029cd99e18e9ebca501b beş izole görev ve iki motor onarımı kendi kapsamlarında PASS. Bu sınav yeni, önceden tanımlanmış 12 görev ölçütüne sahiptir. Önceki 100 puanı bu görev grubuna taşınmaz.

## Gerçek işler

- S01: Mevcut P06 makbuz yazıcısı. NaN/Infinity girdileri standart JSON’a geçmez; makbuzun ve yeni dizinlerin kayıtları fsync edilir; dosya üzerine yazılmaz. Özgün native/Steward güvenlik regresyonları 11 test.
- S02: Mevcut V6.9 source adapter. Döngülü veya bozuk bağımlılıklar kontrollü HOLD; 1500 görevli geçerli zincir ve tekrarlı CLI korunur. Özgün regresyonlar 7 test.
- S03: Mevcut Yetenek Hasadı devir builder/inspector. Gerçek dokuz kaynakla paket üretilir; açılmış ZIP boyutu okunmadan sınırlandırılır; bozuk manifest ve kaynak satırı kontrollü HOLD. Özgün regresyonlar 7 test.

Kaynak commit ve tam SHA/Git blob kimlikleri UPSTREAM_SOURCES.json içindedir. Orijinal dosyalar upstream altında byte eşliğiyle korunur. Her görevde gerçek kaynak yaması patches/S01–S03.patch olarak üretilmiştir. Uygulama yalnız geçici, ayrı Git checkout içindedir. Diğer ürünlerin orijinal yollarında değişiklik yoktur. Ürünlere benimseme/merge/kurulum bu teslimle kendiliğinden gerçekleşmez.

## DÖM teknik onarımı

Kontrol noktası, canlı dosya yolu yanında ayrı SHA bağlı salt-okunur çıktı snapshot’ına bağlanır. Son doğrulama sonrası ve günlük yayımlanırken dosya değişimi karşıt sınanır; değişimde aday üretimi durur. Snapshot ve günlük dizin kayıtları fsync edilir. Tek yazar kilidi mevcut LocalJournal üzerinden korunur. Bu, ayrıcalıklı kötü niyetli bir yazara karşı işletim sistemi sandbox garantisi değildir; snapshot sonradan değiştirilirse replay hash denetimi HOLD verir.

Yeniden çalıştırmada yeni görev süreci yürütülmez. Yeni kayıt processObserved=false, exitCode=null ve CHECKPOINT_REVALIDATION_NO_NEW_TASK_PROCESS taşır; geçmiş gerçekten gözlenen süreç proof’u ayrı alandadır. Eksik tarihsel proof güvenli HOLD verir. Ayrı doğrulayıcı süreci görev icrası olarak sayılmaz.

## Yeniden denetleme

Kaynak checkout kökünde:

```bash
python3 -B tools/zulfikar-performance-v141/second-exam/test_engine_race.py
python3 -B tools/zulfikar-performance-v141/second-exam/run_real_work.py /tmp/zulfikar-review-fresh
python3 -B tools/zulfikar-performance-v141/second-exam/verify_package.py /tmp/zulfikar-review-fresh
```

run_real_work yeni ve boş bir çıktı dizini ister; özgün kaynakla başlangıç/arıza ölçer, aynı gerçek kaynak patch’ini mevcut DÖM üzerinden uygular, gerçek kodu ve özgün testleri çalıştırır; tekrar çalıştırmada görev icrası sayısının artmadığını kontrol eder. Uygulama/test süreçleri ve başlangıç/sonuçlar kalıcı makbuzlarda gözlenir. Git kimliği disposable@localhost yalnız izole test commit’idir; owner/issuer imzası sayılmaz.

GitHub kanıt ZIP’ini ayrı bir dizine açan reviewer, verify_package.py ile mevcut dosyaları salt-okunur denetleyebilir. BYTE_MANIFEST.json hash’lerini ve GitHub’ın bildirdiği ZIP hash’ini ayrıca karşılaştırmalıdır. Son commit HEAD’i, kaynak kimlikleri, 12 özgün ölçüt, açık işler, günlük zinciri ve snapshot’lar birbirine bağlanır. Farklı inceleme oturumunun kimliği ve kararı bu oturum tarafından üretilmez.

## Kabul sınırı

Teknik başlangıç 6/12; onarım sonrası 12/12. Bu kampanyada üç somut kaynak işi tamamlandığında yalnız teknik kapsam PASS olur. Genel operasyonel tek otorite özgün altı alanlı sözleşmedir. Mevcut owner kapsamı, gereken gerçek kullanıcı/saha kabulü, kimliği doğrulanmış farklı inceleme, DoneCheck ve Human Threshold ayrı değerlendirilir.

Eş görevli, eş bütçeli muadil araç/model yürütücüsüne bu oturumda doğrulanmış erişim ve yetki yoktur: PEER_BENCHMARK=HOLD. Önce/sonra ölçümü muadil performans deneyi olarak adlandırılmaz. GENERAL_VERIFIED_FINISH=HOLD.
