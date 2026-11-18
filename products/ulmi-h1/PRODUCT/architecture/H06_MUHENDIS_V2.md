# H06 — Görev, Süreklilik ve Finiş · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Görev→teşhis→onay→değişiklik→regresyon→SHA→finiş zincirini kesintiye dayanıklı kurar.

## Temel şema / teknik arayüz
**Görev/onarım ve finiş:** task_id / status / idempotency / SHA / regression.

## Beklenen gözlenebilir sonuç
Aynı görev tek makbuz, olumlu test, yenilenince devam üretir.

## Yetenek/yeterlilik bağları
KMP05, Y09, Y10, Q07. Önceki gereksinim izleri: R02, R05, R12, UM-01, UM-09, UM-10, UM-18, W07, W10, W12, W14.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Aynı görev tek makbuz, olumlu test, yenilenince devam üretir.
- **SIM2 karşıt:** Kesilmiş görevde belirsiz etki otomatik tekrar yazılmaz.
- **SIM3 onarım/kurtarma:** Checkpoint, fail test ve tekrar ölçüm sonucu güvenli devam.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
