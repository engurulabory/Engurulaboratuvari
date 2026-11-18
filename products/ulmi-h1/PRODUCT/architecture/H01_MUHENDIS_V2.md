# H01 — HTML Ekranı ve Kullanıcı Deneyimi · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
HTML ekranında gerçek görevi alma, plan/onay, çıktı, test ve yeniden açma akışını gösterir.

## Temel şema / teknik arayüz
**Gerçek HTML kullanıcı akışı:** GET /, GET /app.js, POST /api/scaffold, POST /api/execute, GET /api/task.

## Beklenen gözlenebilir sonuç
Gerçek tarayıcı aynı oturumda görev oluşturup makbuzu gösterir.

## Yetenek/yeterlilik bağları
Y01, Y02, Q03. Önceki gereksinim izleri: R01, R02, UM-02, UM-18, W07, W09, W15.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Gerçek tarayıcı aynı oturumda görev oluşturup makbuzu gösterir.
- **SIM2 karşıt:** DOM mock veya Python HTTP sonucu tarayıcı PASS ilan edemez.
- **SIM3 onarım/kurtarma:** Reload sonrası task_id ile aynı makbuza dönülür.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
