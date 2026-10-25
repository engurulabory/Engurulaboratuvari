# PiLive V4 — Zülfikar V1.2 yönetim kararına bağlı mühendislik iş listesi

25 Ekim 2026. Tek ana hedef: canonical veriye bağlı, güvenilir ve güzel gerçek Mac uygulaması.

**Kilitli yaratıcı karar:** A — Sessiz Orman Cockpit™; B'nin beş alan yaklaşımı Projeler ekranında. Yönetim özgün dört ekranı ve yaratıcı deneyimi hazırlıyor. Work'ün mevcut odağı altyapı/kanıt; SwiftUI bağlantısı nihai ekran sözleşmesinden sonra. Önceki A/B yön seçimi eşiği bu açık kararla kapandı; native estetik ve U07 kabulü kendi aşamasında.

## Tamamlanan gerçek mühendislik hareketleri

- [x] Güncel main AGENTS/V3 ve SHA-256 kilitli sekiz aşama okundu; korunmuş kaynaklar sabitlendi.
- [x] Yedi canonical içerik ve V2→V3 makbuz parent/SHA bağı doğrulandı; 116 içerik SHA'sı eşleşti.
- [x] Gerçek Mac'te 137/137 test; native Core verify; 8/8 kaynak pini önce/sonra aynı; 3/3 önceki receipt kopya eşliği PASS.
- [x] Native fixture hatası gerçek izden yeniden üretildi, koruma korunarak onarıldı ve gerçek Mac'te tekrar geçti.
- [x] Hata/onarım/başarı gizlisiz adayları mevcut GitHub kasına PR #241 üzerinden geri bağlandı; Yönetim V6.9 varsayılan görevi korunuyor.
- [x] A yaratıcı yönü ve B'nin beş alan yaklaşımının Projeler'e alınması kullanıcı kararıyla sabitlendi.
- [x] Zülfikar V1.2 kaynakları PR #242 @ `5b189e04b91dab4eb8099891188ca908f67bc816` üzerinden okundu; main'de yayımlanmış olduğu beyanı kurulmadı. Kullanıcının açık talimatıyla yardımcı inceleme çerçevesi olarak uygulanıyor.
- [x] Kasın GitHub V5 kaynakları PR #220 @ `74bc3741b876c064da48b44f16eaa9ccfc05a14d` üzerinden incelendi. `Enguru/Runtime/MacEngineer/state/mk-bridge`, V5 ZIP/LaunchAgent ve `ENGURU_MK_BRIDGE_PILOT_V1` görevi kaynakta görüldü. Mac'te gerçek eşliği sonraki probe'da ölçülecek.

Bu işaretler yardımcı mühendislik hareketleridir; canonical P02 sayacı ve U01–U12 paydası yerine geçmez.

## Mevcut kanıt kimlikleri

| Kanıt | SHA / exact kaynak |
|---|---|
| Main | `8947cb6c240a12950be1f8be9e186d0ecbfa3022` |
| Native başarı makbuzu | `81cf6112ea6faf14ea02c750373a23ab08b5e7d28fd9cd950a060eb0a8c71a7a` |
| Native test edilen paket kaynağı | `9ac7f9555f0a7e265a650aca8b76533cb5952b2d` |
| Native başarı GitHub dönüşü | `3997fd61e1c208bdd73370d5629aaf9fd8a8c9f1` / 5/5 CI PASS |
| Native Core | `f3e2610c6e325f6fd620baa84ec412437a015109dde88ac38cab7f08b2a365b4` |
| P02 Work Contract | `1dc9b0bae00a13672a142fb91f6b1fe603f151bcebaa64482e297029deda7512` |
| P02 State | `ad29d034c8a97be75d69d972fca1c6e7ee207e7f7f1339e79b74e1ce6c40f432` |
| P02 Worklist | `4021dc7486363bc7baf503860969ea23324eabcbd4e3551930a20d79784532d2` |

## Açık U01–U12 özgün şartları

| ID | Kanıtlanan alt kapsam | Kesin açık / kapanış ihtiyacı |
|---|---|---|
| U01 | Canonical içerikler, native kimlik ve kaynak pinleri | Swift→kurulu binary tam build kökeni; HOLD |
| U02 | Mevcut tek Core'un gerçek native verify çıktısı | Gerçek adaptör→atomic UI snapshot eşliği; HOLD |
| U03 | P02 countedPass=0 / total=12, finish HOLD | Teknik toplam ve ayrı resmî kabulün gerçek ekran eşliği; HOLD |
| U04 | P02 aktif iş kimliği S01.01 kaynakta mevcut | Gerçek ekran odağı, çelişki/unknown/cycle etkileşim sınamaları; HOLD |
| U05 | Beş alan ve Ticari facet kuralı sabit | Kaynaklı proje sınıflaması, unclassified ve tek sayım; HOLD |
| U06 | Yön kararı A + B Projeler yaklaşımı | Yönetimin dört ekran sözleşmesi ve gerçek SwiftUI; HOLD |
| U07 | Yaratıcı yön seçimi kabul edildi | Nihai görsel sözleşme ve gerçek Mac kullanıcı estetik kabulü; HOLD |
| U08 | Tasarımda klavye/kontrast/büyütme şartları tanımlı | Gerçek görev testi, VoiceOver, AA, büyütülmüş metin ve Reduce Motion; HOLD |
| U09 | Kaynak ve UI zamanı ayrımı korunuyor | Üç gerçek timestamp, stale/cache yaşı ve hata yüzeyi; HOLD |
| U10 | İzole source/receipt/malformed/path regresyonları mevcut | Gerçek native source-revision→UI determinismi ve dayanıklılık; HOLD |
| U11 | Saha araçları ve native Python test yolu mevcut | Finder/crash/restart/rollback ve 100 projede 30 açılış/100 yenileme ham ölçümleri; HOLD |
| U12 | Kaynak, test, GitHub ve receipt SHA izleri korunuyor | Tam UI zinciri, bağımsız GUI/işlevsel inceleme ve yetkili kabul; HOLD |

Resmî P02: 0/12 counted PASS, 0/4 DoneCheck; 7 saha şartı/G3/Human Threshold/Verified Finish kendi kaynaklarında HOLD. P01 ve P06 yetkileri ayrı korunur.

## Zülfikar V1.2 uygulama durumu

| Özgün kontrol | Bu oturumun kanıtı ve sınırı |
|---|---|
| Z02_EVENT | Native FAILURE→RECOVERED/SUCCESS olayları ayrı SHA ile kayıtlı; kaynak incelemesi PASS |
| Z03_TRANSFER | Bir onarım vakası mevcut; üç donmuş karşılaştırılabilir görevde ölçülmüş aktarım/efor kanıtı açık; HOLD |
| Z04_LINEAGE | Canonical→Core→test→receipt→GitHub izi var; kullanıcı ekranı/sonuç/yetki halkaları açık; HOLD |
| Z05_BENCHMARK | Yeni gerçek muadil eş denemesi yürütülmedi; NOT_MEASURED |
| Z08_IMPACT | Gerçek kullanıcı önce/sonra ölçümü henüz oluşmadı; HOLD |
| Z10_CONCURRENCY | Yalnız PR #241 inceleme dalı; expected-head lease; Mac canonical/kas writer sayısı 0. Ürün writer yetkisi kendi kapısında |
| Z10_SAFE_FIN | Ürün bitişi HOLD; hazırlık/test PASS resmî kabule aktarılmıyor |

## Sonraki tek birleşik hareket

`pilive_runtime_lineage_observer_v1.py`: runtime V5 LaunchAgent plist'lerinden yalnız izinli metadata, ZIP manifest/SHA ve AST görev sabitlerini; SQLite dosyasının yalnız stat bilgisini; kurulu V3.1 binary kimliğini ve iki eski Python source pininin sınırlı kapsamda eşleşmesini toplar. Yerel native kodu import/execute, cycle/status/activate, SQLite bağlantısı, ağ, Keychain ve ürün/kas yazımı 0. Launchctl print'in tüm çıktısı kaydedilmez; yalnız state/pid/exit alanları alınır. Eski pilot görevi PiLive'a çevrilmez. Görev uyumu görülünce gerekli PiLive adaptörü ayrı sözleşmeyle değerlendirilir.

Arama kapsamı: bilinen V3.1 arşivi ve kurulu app Resources, ayrıca yalnız owner UID'sine ait isim filtresiyle `/private/tmp` üst seviyesi. Limitler ve eksik dizinler raporlanır; kaynak bulunmaması genel yokluk veya build kökeni PASS'i oluşturmaz. Kanıt tamamlanamazsa eski binary korunur; yeni SwiftUI ürününün kendi source/build/binary manifesti nihai ekran sözleşmesine bağlanır.
