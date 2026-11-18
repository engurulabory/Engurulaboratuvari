# H08 — Kalite, Muadil Kıyas ve İki Aşamalı Kabul · ENGÜRÜ Mühendis OSi™ V2

**Ürün:** ENGÜRÜ Mühendis OSi™ · **Hedef 1:** AKTİF · **Hedef 2:** ASKIDA
**Kaynak mirası:** UstaMimar dokuz harita V1; eski harita ID, UM, WC, W ve 56 kabul sayacı korunur.

## Tek görev ve gerekçe
H1-C01..H1-C12 gerçek HTML kapılarıyla tasarım puanı ve ürün kabulünü birbirinden ayırır.

## Temel şema / teknik arayüz
**12 özgün H1 koşulu ve muadil kalite:** H1-C01..12 + Ana Pano + DoneCheck threshold.

## Beklenen gözlenebilir sonuç
12/12 gerçek zorunlu PASS ve bağımsız kabul ile HTML_PROTOTYPE=PASS.

## Yetenek/yeterlilik bağları
Y12, Q10. Önceki gereksinim izleri: R14, UM-11, UM-18, W01, W02, W06, W12, W13, W14, W15.

## Zülfikar V1.4.1 üçlü sınama
- **SIM1 olumlu:** 12/12 gerçek zorunlu PASS ve bağımsız kabul ile HTML_PROTOTYPE=PASS.
- **SIM2 karşıt:** 9 harita 100/100 tasarımı otomatik HTML ürün PASS yapmaz.
- **SIM3 onarım/kurtarma:** Eksik ID açık kayıt ve test→onarım→regresyon döngüsüyle tamamlanır.

## Kanıt ve kabul sınırı
Kaynak SHA, çıktı veya görev kimliği, gerçek test makbuzu ve negatif/kurtarma sonucu bu haritaya bağlanır. Kaynak ve arayüz tasarımı `PASS_SCOPED_DESIGN`; işlevsel runtime, kendi zorunlu H1 kontrolü ve bağımsız DoneCheck ile ayrıca kabul edilir. **Hedef 2:** PARKED.
