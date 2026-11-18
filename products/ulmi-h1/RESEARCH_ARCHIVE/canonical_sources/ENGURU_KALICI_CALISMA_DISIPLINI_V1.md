# ENGÜRÜ Kalıcı Çalışma Disiplini™ V1 — Sekiz Aşama

**Durum:** Kullanıcı tarafından belirlenen çalışma sırası; GitHub SHA-256 kilidi ve bağımsız CI denetimiyle korunan ortak yöntem metni.
**Kapsam:** Bütün ENGÜRÜ hedef, tasarım, teori, GitHub hazırlığı ve Mac OSi devir hazırlığı oturumları.
**Otorite:** Canonical V3 ve her ürünün özgün kabul sözleşmesi, DoneCheck™, Human Threshold™ ve resmî yetkili kararları önceliklidir. Bu kaynak yeni otorite veya ikinci Progress Core kurmaz.

## Kalıcı sekiz aşama — tam sıralı ifade

1. Hakikati gör
2. Değeri koru
3. Eksikleri ve ihtiyaçları tespit et
4. Gerekli farkı üret
5. Eksikleri tamamla
6. Kanıtla
7. Sonraki ihtiyaçları belirle
8. İlerlet

## Pozitif Dil Evreni ve tamamlanma hükmü

**Kalıcı sabit hedef:** Eksikleri tespit edilmiş, gereksinimleri karşılanmış, yanlışları düzeltilmiş, eksikleri tamamlanmış, gerçek testlerle kanıtlanmış ve uçtan uca tam bitmiş.

Her aşama özgün kabul kimlikleri, gerçek kaynak, gözlenebilir sonuç, kanıt ve gereken yetkili karar üzerinden yürütülür. Gerekli kaynak ve yetki mevcutsa **İLERLE**; gerçek açık kriter varsa **GÜVENLİ_DUR + açık ID + sonraki somut kanıt ihtiyacı**. Hazırlık düzeyindeki teorik puanlar, gerçek ürünün teknik veya saha PASS sonucu olarak gösterilmez.

## Kullanıcı hedefinden Mac devrine sıralı çalışma

**KULLANICI HEDEFİ → TASARIM 100/100 → TEORİ 100/100 → GITHUB HAZIRLIĞI 5×100/100 → OSİ DEVİR HAZIRLIĞI 100/100 → İNSAN KARARINDA DUR.**

Her olgunlaştırma kapısında üç temel değerlendirme, karşıt simülasyon ve onarım turu; yalnız kanıtlı ilerlemeyle bir veya iki tamamlayıcı tur uygulanır. Kontrol paydaları sabittir. Bağımsız final SIM1/SIM2/SIM3 gerçek GitHub kaynak/CI doğrulamasından ayrılmaz. OSi salt-okunur ön uçuş ve gerçek yazma/kurulum yetkisi ayrı sınırlar taşır.

**Doğrulama sınıfları:** `METHOD_POLICY_PASS` yalnız yöntem kuralı; `PROJECT_GITHUB_PREPARED_PASS` ilgili ürünün tam kaynak/CI kanıtı; `OSI_HANDOFF_PREPARED_PASS` gerçek yerel ön uçuş; `VERIFIED_FINISH` yalnız özgün ürünün bağımsız doğrulama ve yetkili kabulünün tamamlanması.

## Bütünlük ve sürüm denetimi

Bu dosyanın UTF-8 kaynak baytları `ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json` içindeki SHA-256 ile korunur. CI her PR ve main çalışmasında bayt özeti, sekiz aşamanın kimliği ve sırası, V3 canonical kilit kaydı ve AGENTS giriş bağlantısını denetler. Kaynak revizyonu ancak yeni onaylı sürüm ve yeniden kilitlenmiş SHA ile ilerletilir.
