# ⚔️ ULMi H1 · Emir 01 / R2 — Gerçek HTML sohbet bağlantısı

**Mevcut emir kimliği:** `KAPTAN-ULMI-H1-BIRLESIK-01-TECH-01-11-20261118`.

Bu paket, özgün R1 ürünündeki HTML/HTTP/SQLite mimarisini korur. Ana çalışma masasına daha önce sunucuda bulunan **proje-SHA bağlı Emin–Maya sohbetini** görünür olarak ekler. Yeni bir mühendislik motoru, ücretli API veya Mac OSi H2 kurulumu içermez.

## Açma

ZIP'i ayrı bir klasöre çıkar. `python3 TESTS/verify_h1_r2_candidate.py <bu zip dosyası>` komutunu ZIP yanında çalıştırarak kaynak SHA manifestini doğrula. Çıkarılan klasörde `bash START_H1.sh` komutuyla yalnız yerel `127.0.0.1` H1 sunucusunu başlat. Tarayıcıda çıktıda gösterilen yerel adresi aç; SQLite proje kaydet; Emin–Maya bölümünden aynı projeyi seçip kaynaklı öneri iste. Gerçek Qwen/Shared AI ve SHA-kilitli canonical kaynak erişimi yoksa arayüz nedenini HOLD olarak gösterir.

**Kritik yetki sınırı:** Sohbet önerileri salt okunur. Gerçek model erişimi ve owner yetkisi ayrıca kanıtlanır. Üretilen görevler ayrıca açık izin gerektirir. Bu paket gerçek Safari/Chromium UAT, gerçek Qwen, Pilot A/B/C, bağımsız DoneCheck veya owner kabulü değildir.

## Özgün sözleşme

V22 sabit 12 iş, 10 hazırlık kapısı ve HTML-01–05 ölçütleri aynen korunur. İş 01–04 tarihsel scoped; 01–11 tam teknik kabulü halen `NOT_ESTABLISHED`; resmî 12/12 `0/12_HOLD`.

**R2 yeni kanıt:** Gerçek HTTP/SQLite + sentetik kaynak sağlayıcılı proje sohbeti 13/13 PASS. Gerçek HTTP/SQLite 49/49, üretilen uygulama 44/44, üç senaryo 49/49, model rota 25/25, sentetik Shared AI 18/18, W07/W08 23/23, 10.001 saldırı reddi ve W08 atomik okuma PASS. İlgili ham test günlükleri `EVIDENCE/R2_RUN_LOGS` içindedir. Chromium yönetim politikası `ERR_BLOCKED_BY_ADMINISTRATOR`; teknik tarayıcı UAT HOLD.

**İnsan kabulü:** Owner UAT ve H1 Verified Finish daha sonra. H2 PARKED.
