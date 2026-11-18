# H03 — Yürütücü ve Araç Mimarisi · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Tek izole yürütücü ile dosya, kod, test, gerçek çalışma alanı ve SHA geri okumasını yürütür.

## Temel şema / teknik arayüz
**Tek gerçek yürütücü:** Python server.py → workspace/ → audit_outputs.py.

## Beklenen gözlenebilir sonuç
Yalnız onaylı alanda dosya yazılır, SHA geri okunur, gerçek test çalışır.

## Yetenek/yeterlilik bağları
Y04, Y05, Y06, Q05. Önceki gereksinim izleri: R03, R04, R08, R09, R10, R11, UM-04, UM-05, UM-06, UM-07, W03, W07, W08, W09.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Yalnız onaylı alanda dosya yazılır, SHA geri okunur, gerçek test çalışır.
- **SIM2 karşıt:** Sembolik bağ, path traversal, overwrite, serbest shell reddedilir.
- **SIM3 onarım/kurtarma:** Kesinti belirsiz dış etkiyi HOLD_RECONCILE ile bırakır.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
