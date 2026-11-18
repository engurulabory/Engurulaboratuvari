# H07 — Güvenlik, Hafıza ve Kurtarma · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Tek owner, izinli araç, köken, SQLite görev defteri, veri geri okuma, restore ve Hafıza Sarayı sürekliliğini korur.

## Temel şema / teknik arayüz
**Yetki, Hafıza ve kurtarma:** Host / Origin / CSRF token / workspace / HFS source lineage.

## Beklenen gözlenebilir sonuç
Yetkisiz değişiklik 0, önceki gain_id ler korunur.

## Yetenek/yeterlilik bağları
KMP06, Y11, Q08, Q09. Önceki gereksinim izleri: R03, R07, R13, R14, UM-11, UM-12, UM-13, UM-14, UM-15, UM-16, UM-17, W05, W10, W11.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Yetkisiz değişiklik 0, önceki gain_id ler korunur.
- **SIM2 karşıt:** Hafıza Sarayı K03/K04 açıkken FULL kabul veya izinsiz migrasyon yok.
- **SIM3 onarım/kurtarma:** Salt okunur doğrulama ve geri yükleme provası ayrı owner kapısında.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
