# PiLive — Şimdi → Projeler → Projenin Kanıtı saha sözleşmesi

Korunan kabul: PASS_SOURCE_TO_VISIBLE_FRAME_ONLY; gerçek OSi receipt SHA e5e53e1a3a65f0c6ca0fde1884c76b2f2868efa656f4dff9e9ebbbd457b615a9, binary be6260459172e3b46398e24b293379f86f1c66319b0e8a568e4fc987918271c3. 17 kaynak pini / 48 kaynak SHA / 8 Core pini / 15 kimlik / 14 qualified / native Swift14 önceki kapsamda korunur. V2 başlamadan mevcut original receipt ve eski candidate binary salt-okunur doğrulanır; yeni build ayrı session'dadır.

## Görevler ve ölçülebilir kabul

| Yardımcı görev | Kullanıcı hareketi | Kaynak ve kabul kanıtı | Özgün kapsam |
|---|---|---|---|
| FJ.NOW | Saha görevi → P02 0/12, aktif iş ve küresel HOLD bilgisini oku → doğrula | Aynı reader packet/source SHA; proje ENGURU_PLIVE_P02_USER_SCREEN; gerçek kendi pencere içerik PNG'si | U03/U04/U09 alt sınama |
| FJ.PROJECTS | progress-core ara → projeyi seç → gerçek 44/44 teknik / finish HOLD ayrımını doğrula | Seçilen ID ENGURU_PROGRESS_CORE; kaynaklı sayaç; diğer projenin kartıyla karışma sıfır; kendi sheet PNG'si | U03/U05/U06 alt sınama |
| FJ.EVIDENCE | Bu projenin kanıtı → aynı ID, sourceRevision/digest ve o projenin State/Worklist SHA'larını oku → doğrula | Projeden kanıta 1 eylem; tam iki proje kaynak pini; Core/P02 kanıtı karışmaz; aynı kaynak kimliği; PNG | U01/U02/U09/U12 alt sınama |
| FJ.RETURN | Escape → açan proje satırına odak dönüşünü gözle → kaydı tamamla | Escape handler + FocusState hedefi + açık kullanıcı görev onayı | U08 alt sınama |

Bir proje en fazla iki seçim eyleminde bulunur; arama metni girişi ayrıca kaydedilen görev adımıdır. Native kullanıcı/keyboard süreci kontrol edilir; CI state testleri gerçek VoiceOver veya piksel kabulü sayılmaz. PNG'ler yalnız uygulamanın kendi NSView içeriklerinden üretilir; masaüstü veya başka uygulama yakalanmaz. PNG cache görüntüsünün görünür metinleri ve boş/eksik render olasılığı Work tarafından ayrıca incelenmeden görsel PASS verilmez.

## Bu tur tespit edilen ve onarılan farklar

1. Proje ayrıntısı → proje kanıtı doğrudan bağlantısı eksikti. Kaynaklı ProjectEvidence ve tek sheet içi geçiş eklendi; genel portföy pinleri seçili projenin pinleri gibi gösterilmez.
2. Ayrıntı kartı eski ProjectRow değerini tutabiliyordu. Canonical ID üzerinden güncel modelden okunur; digest değişiminde açık HOLD ve yeniden seçim gerekir.
3. uiRenderedAt ilk frame'de kalıyordu. Her yeni kaynak okumasının görünür modeline ayrı render zamanı bağlanır; eski ilk makbuz korunur.
4. Native etkileşim olayları/PNG/görev kimliği yoktu. Açık kullanıcı düğmeleriyle üç olay ve Escape/focus dönüşü kaydedilir. Kaynak drift'i karışık yolculuğu reddeder; kısmi kayıt korunarak yeniden başlatılabilir.

## Bağımsız veri sınaması ve kesin sınırlar

`tools/pilive_field_journey_v1.py` raw reader packet/wire SHA, Core8 pin, before/after source bracket, Core facts→existing adapter replay, proje ID/sayaç/State/Worklist pin eşliğini ve dört timestamp sırasını ayrı Python koduyla sınar. Üç görev aynı revision/digest'te; olay kaynak yaşı ≤60sn; görev sırası tam ve tekildir. PNG dosya SHA/header/boyutu, path escape/symlink ve yanlış otorite karşıt sınanır. Numeric JSON normalization yüzde anlamını değiştirmez; bool sayaç kabul edilmez.

PASS_TASK_DATA_AND_IMAGE_INTEGRITY_ONLY sadece veri ve dosya bütünlüğüdür. Native own-app PNG/event + kullanıcı onayı saha girdisidir; bağımsız piksel incelemesi ve görev kabulü ayrıca gerekir. captureDurationMs ekran kanıtı üretim maliyeti; elapsedSeconds kullanıcı yolculuk süresidir. Bunlar U11 100 proje / 30 açılış / 100 yenileme benchmark'ı değildir.

Native `--field-journey` kaynak/test/build/signature/ilk-frame adımlarından sonra uygulamada kullanıcı görevini bekler (en fazla10dk). AudiV13 orijinal JSON+kanıt ZIP'i ve SHA eş Masaüstü kopyası korunur. Son kullanıcı yalnız FIELD_BUNDLE ZIP'ini Work'e getirir; raw canonical Python/özel anahtar/başka uygulama görüntüsü yayımlanmaz. Kurulu app/canonical/kas yazımı0; owner/issuer/DoneCheck/HT üretilmez. U01–U12 ve ayrı P02 kendi tam şartlarında HOLD.

Zülfikar V1.4.1 ve mevcut DÖM kapsamı korunur. Üç tur: kaynak/kimlik doğruluğu → hata/klavye/erişilebilir ad → kaynak drift'i/geri dönüş/kanıt bütünlüğü. Bu saha görevlerinin100/100'ü ancak tüm görev şartları gerçek Mac kanıtı ve bağımsız incelemeyle kapanır. Önceden kazanılmış P01/P02 ve CI başarısı yeni saha PASS'ine dönüştürülmez.
