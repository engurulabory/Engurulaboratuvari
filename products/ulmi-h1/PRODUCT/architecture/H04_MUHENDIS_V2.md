# H04 — Yetenek Haritası · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Yazılım ve sistem mühendisinin atomik yeteneklerini ve gerçek test durumlarını ayrıştırır.

## Temel şema / teknik arayüz
**12 atomik mühendislik yeteneği:** Y01..Y12 / linked 18 UM, 32 WC.

## Beklenen gözlenebilir sonuç
Her yetenek ayrı gerçek sonuç ve runtime state taşır.

## Yetenek/yeterlilik bağları
Y07, Y08, KMP02. Önceki gereksinim izleri: R01, R11, UM-01, UM-03, UM-04, UM-06, UM-08, UM-12, UM-18, W02, W05, W09.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Her yetenek ayrı gerçek sonuç ve runtime state taşır.
- **SIM2 karşıt:** Tasarımsal WC karşılaştırması canlı muadil eşdeğerliği sayılmaz.
- **SIM3 onarım/kurtarma:** Yetenek eksikse ilgili görev HOLD ve telafi ihtiyacı görünür.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
