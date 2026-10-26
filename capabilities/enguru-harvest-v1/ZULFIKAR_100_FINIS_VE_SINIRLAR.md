# ENGÜRÜ Zülfikar V1.3.1 — 100/100 Hedef, Sert Kabul ve Sınırlar

**Tarih:** 26 Ekim 2026. **Tek sahip:** `engurulabory`. **Çalışma dalı:** PR #243 incelemesi.

## Karar matematiği: üç ayrı sayı

1. **Kabul tanımı / tasarım kapsaması:** GitHub **100/100** + OSi öncesi hazırlık **100/100**; her alan 10 adet 10 puanlık özgün kabul ölçütüyle tanımlı. Bu, kapsamın eksiksiz tanımlandığını kanıtlar.
2. **Gözlenen kanıt hazırlığı:** GitHub **65/100**, OSi öncesi **60/100**. Bu iki puan yalnız SHA, gerçek GitHub CI ve gözlenmiş kaynaklara göre verilir. Son exact-head CI başarıyla tamamlandığında geçerli olur.
3. **Resmî ürün Verified Finish:** GitHub **HOLD**, OSi **HOLD**. Sahte PASS veya sentetik simülasyon resmî karar üretemez.

**Mantıksal sınır:** Eski OSi 100 puan cetvelinde gerçek Mac uyumluluğu 15, Mac SQLite saha 10, owner saha yetkisi 10 puandır. OSi'ye geçiş yasak olduğu ve owner'ın ayrı saha yetkisi gelmediği sürece **gerçek puanın üst sınırı 65/100'dür**. Bu 35 puanı GitHub simülasyonlarıyla kazanılmış saymak yetki aşımıdır. GitHub içinde hazırlanabilen kısmın **tasarım tamamlığı 100/100** olabilir; gerçek puan farklıdır.

## GitHub Verified Finish — 35 puanlık son eksiklerin kapanışı

| Kapı | Kalan | Tam kabul kanıtı | Yetki/kısıt |
|---|---:|---|---|
| GH-A gerçek mühendislik faydası | 4 | Beş **farklı gerçek ürün görevi**, aynı kaynak HEAD'de eş koşullu baz ve aday, kalite gerilemesi 0, süre/CPU/RAM ve kaynak SHA makbuzu | GitHub mikro-benchmark tek başına kullanıcı etkisi değildir |
| GH-B dış yetenekler | 3 | P01–P12 her biri için gerçek, izinli görev sonucu, SHA'dan bağımsız test ve denetim | 9 gerçek teknik tool trial, 1 format; PROVEN hâlâ 0/12 |
| GH-C lisans/güvenlik | 6 | Seçilen kaynakların tam arşiv SHA-256, lisans kapsamı, güvenlik/bağımlılık kararı, sıfır zorunlu yeni API | 30 Git commit+README blob çifti yalnız köken kanıtıdır |
| GH-D kullanıcı faydası | 10 | Gerçek kullanıcının ihtiyaç duyduğu 5 farklı üretim görevi, çıktı kalitesi ve süre ölçümü, owner'ın kullanılabilirlik kabulü | Sentetik dummy/model skorları hariç |
| GH-E yetkili kapama | 12 | Mevcut canonical issuer/DoneCheck ve owner Human Threshold gerçek kaydı | Tek insan owner; ikinci peer reviewer zorunlu değil |
| **Toplam** | **35** | **35/35 gerçek kanıt** | `GITHUB_VERIFIED_FINISH=PASS` yalnız bu koşullarla |

## OSi öncesi hazırlık — 40 puanlık son eksiklerin kapanışı

| Kapı | Kalan | Tam kabul kanıtı | Yetki/kısıt |
|---|---:|---|---|
| OSI-A kaynak/hak aktarımı | 5 | İzinli kaynak ve SHA pinleri, yalnız yetkili dosyalar | GitHub tarafında tamamlanabilir |
| OSI-B gerçek Mac uyumluluğu | 15 | Kullanıcının gerçek Mac OSi'sinde izole, yetkili salt-okunur envanter, uyumluluk makbuzu | Şimdi `HOLD`; geçiş 0 |
| OSI-C SQLite saha pilotu | 10 | Gerçek Mac OSi'de izole DB, canary, restart/idempotency, SHA'lı makbuz | Şimdi `HOLD`; geçiş 0 |
| OSI-D owner saha girişi | 10 | Tek owner'ın ayrı OSi giriş ve yetki kaydı | Şimdi `HOLD`; geçiş 0 |
| **Toplam** | **40** | **40/40 gerçek kanıt** | `OSI_FIELD=PASS` yalnız gelecekteki yetkili saha sonucu |

## Sıralı kabul / güvenli duruş

**Aşama I (GitHub):** tam kaynak gözlemi ve commit+README pinleri → gerçek 5 görev → bağımsız teknik karşıt sınama → lisans/yetki → exact-head CI → tek-owner C04/C10 → gerçek DoneCheck → Verified Finish.

**Aşama II (yalnız OSi öncesi):** GitHub'da SHA-256'lı devir adayı ZIP ve manifest → ZIP içeriği ve rollback denetimi → yalnız GitHub CI üzerinden paket üretim testi → Mac OSi saha yetkisini ayrı bekleme.

**Hüküm:** `DESIGN_GITHUB=100/100`, `DESIGN_OSI_PREFIELD=100/100`, `GITHUB_EVIDENCE=65/100`, `OSI_EVIDENCE=60/100` ancak yeni exact-head CI PASS sonrasında; `GITHUB_VERIFIED_FINISH=HOLD`, `OSI_EXECUTION=0`, `MAIN_MERGE=0`.
