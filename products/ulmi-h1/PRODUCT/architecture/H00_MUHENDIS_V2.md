# H00 — Ana Sistem ve Yerleşim · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
Tek yazılım ve sistem mühendisliği ürününün rolünü, çalışan altyapısını, izinlerini ve bağımlılıklarını gösterir.

## Temel şema / teknik arayüz
**Tek sürecin sınırı:** HTML + API + SQLite + izinli araç + Qwen opsiyonu.

## Beklenen gözlenebilir sonuç
Yeni mühendis adı tek kaynakta; önceki kazanımlar korunur.

## Yetenek/yeterlilik bağları
Q01, Q02. Önceki gereksinim izleri: R01, R07, R09, R10, UM-05, UM-10, W01, W03, W04.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** Yeni mühendis adı tek kaynakta; önceki kazanımlar korunur.
- **SIM2 karşıt:** İkinci yürütücü açma talebi reddedilir.
- **SIM3 onarım/kurtarma:** Eski ürün kimliği alias olarak çözülür; runtime kimliği yeni ID ile sabitlenir.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
