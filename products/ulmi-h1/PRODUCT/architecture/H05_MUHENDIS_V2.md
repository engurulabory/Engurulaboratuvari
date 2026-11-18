# H05 — Yeterlilik Haritası · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Mühendislik yetkinlikleri ile kanıtlanmış yeterlilik seviyesini ayrı ölçütlerde yönetir.

## Temel şema / teknik arayüz
**6 yetkinlik + 10 yeterlilik ölçütü:** KMP01..06, Q01..10.

## Beklenen gözlenebilir sonuç
Yetenek/Yetkinlik/Yeterlilik birbirine karıştırılmadan sayılır.

## Yetenek/yeterlilik bağları
KMP02, KMP03, KMP04, Q06. Önceki gereksinim izleri: R11, R12, R14, UM-06, UM-08, UM-09, UM-11, UM-18, W09, W12, W13.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Yetenek/Yetkinlik/Yeterlilik birbirine karıştırılmadan sayılır.
- **SIM2 karşıt:** Şablon Python PASS genel kod onarma yeterliliği sayılmaz.
- **SIM3 onarım/kurtarma:** Fail→yama→regresyon ve gerçek tekrar sonrası yetkinlik yükselir.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
