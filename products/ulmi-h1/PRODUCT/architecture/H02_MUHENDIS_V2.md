# H02 — Beyin ve Karar Mimarisi · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Yerel model önerisini mühendislik görevi, kaynak, sınır ve izin açısından değerlendirir.

## Temel şema / teknik arayüz
**Güvenli yerel model ve karar:** Ollama loopback /api/chat → JSON plan → syntax check → izin kapısı.

## Beklenen gözlenebilir sonuç
Kaynağı doğrulanmış model geçerli tek dosya planı üretir.

## Yetenek/yeterlilik bağları
Y03, KMP01, Q04. Önceki gereksinim izleri: R02, R06, R08, R12, UM-03, UM-10, UM-12, W02, W08.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Kaynağı doğrulanmış model geçerli tek dosya planı üretir.
- **SIM2 karşıt:** Model komut, dış yetki veya owner taklidi ile işe başlamaz.
- **SIM3 onarım/kurtarma:** Model yanıtı bozulursa HOLD; deterministik örnek göreve dönüş.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
