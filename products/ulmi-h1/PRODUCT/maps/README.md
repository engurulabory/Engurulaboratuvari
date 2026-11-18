# ENGÜRÜ UstaMimar OSi™ · 9 Harita + Ana Kabul Panosu

## Paket
- `haritalar/H00_HARITA.md` … `H08_HARITA.md`: dokuz ayrı kuram/tasarım/teknik hazırlık haritası; Mermaid şemaları.
- `USTAMIMAR_ANA_KABUL_PANOSU_MIMARI_V1.md`: tek kanıt/owner arayüzü sözleşmesi.
- `USTAMIMAR_ANA_KABUL_PANOSU_TASARIM_ONIZLEME.html`: salt okunur, internetsiz çalışan navigasyon; **iş yapan gerçek HTML Usta prototipi değildir**.
- `HARITALAR_V1_KAYNAK_MATRISI.json`: kaynak/pinler, R/W/UM/WC izleri, karar sınırları, 9 map ve çapraz bağlar.
- `SIMULASYON_KANIT.json`, `SIMULASYON_RAPORU.md`: üç aşamalı tasarım/şema simülasyonu.
- `test_design.py`: yapısal doğrulamalar ve fail-closed karşıt kontroller.
- `MANIFEST_SHA256.json`: paket bütünlük kayıtları.

**Aktif hedef:** Hedef 1 (gerçek çalışan HTML Usta prototipini inşa). **Askı:** Hedef 2 (Yerel Mac OSi geçişi).
**Owner yetkisi:** Bu talimat yalnız teori, tasarım, dosya üretme, simülasyon ve Saray'a append-only kayıt içindir. Mac kurulum ve canlı uygulama değişikliği yoktur.

## Yeniden doğrulama
`python3 test_design.py` → yapısal tasarım ve üç tur sentetik karşıt test.
`python3 -m http.server 8080 -d .` komutu burada gerekli değildir; `USTAMIMAR_ANA_KABUL_PANOSU_TASARIM_ONIZLEME.html` dosyası internetsiz açılır.

**Kabul ayrımı:** Tasarım rubriği 100/100 ancak öz-yazarlı yapısal kapsam içinde. Bu paket `HTML_PROTOTYPE_PASS`, `56/56`, `MAC_WORKING_PRODUCT` veya `VERIFIED_FINISH` değildir.

**H04 muadil eşleme:** `MUADIL_YETENEK_EK_H04.md` (Work/Claude Code/Codex/Aider, kaynak URL ve WC/UM ilişkisi).
