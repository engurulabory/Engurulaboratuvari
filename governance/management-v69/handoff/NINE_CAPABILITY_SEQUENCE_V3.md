# ENGÜRÜ GitHub → OSi · Dokuz Yetenekli Sıralı Teorik Kabul V3

Sabit hedef: dokuz alanın her biri için 100/100 teorik tasarım kabulü; gerçek OSi saha ve G2–G6 yetkisi ayrı HOLD. Puanlar onaylanmış kanıt yokken artmaz.

| Sıra | Hedef | Önceki analitik puan | Kabul koşulu |
|---|---|---:|---|
| 01 | Mimarlık | 96 | T00–T12 grafiği, kaynak/ortam pinleri, bağımsız roller, tersine mimarlık ve son kapıların yürütülebilir karşıt testi |
| 02 | İş yapma yeteneği | 87 | Görevden kod/test/kanıta kadar gerçek yürütme ve hata onarım simülasyonu |
| 03 | Finiş yeteneği | 72 | Kanıt, reviewer, DoneCheck, owner ve saha ayrımının uçtan uca doğrulanması |
| 04 | Çalışma rahatlığı | 80 | Üç girdi; sade rapor; kurtarma, yönlendirme, tek insan eşiği |
| 05 | Akış kolaylığı | 89 | Bağımlılık grafiği, idempotent tekrar, güvenli devam ve drift |
| 06 | Güvenlik ve kanıt | 94 | Git hash, SHA256, provenance, yetki, path/symlink, audit, bağımsız inceleme |
| 07 | OSi kurulum hazırlığı | 78 | Gerçek envanter sınırı, paket, kurulum ön kontrol, atomik geçiş ve rollback |
| 08 | Mühendislik yeteneği | NOT_SCORED | Tasarım, kodlama, hata teşhisi, kök neden, test, build, mühendislik teslimi, kurtarma |
| 09 | İç işleyiş ve uyumlu çalışma | NOT_SCORED | Yönetim–Mühendis–kanıt–yetki bileşenlerinin birbiriyle çelişmeyen durumu, rollback ve süreklilik |

**Sıralama kuralı:** 01 kabulü olmadan 02 resmî teorik PASS alamaz; 02 sonrası 03…09. Her kategori için gerçek kaynaklara bağlanan kontroller, olumlu ve karşıt testler, üç yeniden çalıştırma, exact commit GitHub CI kanıtı ve bağımsız review gerekir. Metinsel öz değerlendirme tek başına 100/100 değildir.

**Mimarlık kabulünün sınırı:** tools/management_v69_architecture_acceptance.py yalnız şemanın grafiğini, rol ayrımını ve hash biçimini test eder. Gerçek kaynakta hash içeriği, canlı iki mühendislik motoru bağı ve tersine mimarlığın tamamı henüz HOLD'dur. Bu sebeple 01 mevcut puanı 96/100 referans olarak korunur.

Sıra 08 ve 09, önceki A–G 70 özgün kontrolün yerine geçmez; yeni H–I geliştirme kabul alanlarıdır. OSi mutation=0, Verified Finish=HOLD.
