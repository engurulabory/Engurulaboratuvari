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
- [x] Kasın GitHub V5 kaynakları PR #220 @ `74bc3741b876c064da48b44f16eaa9ccfc05a14d` üzerinden incelendi. `Enguru/Runtime/MacEngineer/state/mk-bridge`, V5 ZIP/LaunchAgent ve `ENGURU_MK_BRIDGE_PILOT_V1` görevi kaynakta görüldü. Yeni native makbuzda gerçek konum görüldü; dört V5 üye SHA'sı bu GitHub kaynağıyla eşleşti.

- [x] Yeni native makbuzun SHA ve paket manifest bağı doğrulandı; V5 LaunchAgent active/exit 0, eski V1/V4 launchctl sonucu 113 olarak ayrı korundu. Bu tek anlık gözlemdir.
- [x] İki tarihsel Python pini arşiv ve kurulu Resources'ta 4/4 içerik özetiyle bulundu; dört Swift piniyle birlikte tarihsel altı source pini içerik bazında eşleşti. Tam build bağı HOLD.
- [x] Yeni makbuzun üç önceki receipt çifti FileNotFoundError gözlemi kaydedildi; önceki 3/3 PASS kendi zamanında korundu. Taşınma/silinme nedeni kanıtlanmadı.

Bu işaretler yardımcı mühendislik hareketleridir; canonical P02 sayacı ve U01–U12 paydası yerine geçmez.

## Mevcut kanıt kimlikleri

| Kanıt | SHA / exact kaynak |
|---|---|
| Main | `8947cb6c240a12950be1f8be9e186d0ecbfa3022` |
| Native başarı makbuzu | `81cf6112ea6faf14ea02c750373a23ab08b5e7d28fd9cd950a060eb0a8c71a7a` |
| Native test edilen paket kaynağı | `9ac7f9555f0a7e265a650aca8b76533cb5952b2d` |
| Native başarı GitHub dönüşü | `3997fd61e1c208bdd73370d5629aaf9fd8a8c9f1` / 5/5 CI PASS |
| Yeni runtime makbuzu | `d91557b11abe20363f1a8ff89fb55267ec0549376c3c76839e2f80ea278349fa` |
| Native V5 ZIP | `060aaf6cbbaaac75fae1f79a2483bd141a1fc29a26b506110faed6a12e182f82` |
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

## Güncel kaynak incelemesi ve sonraki tek birleşik hareket

Native kasın gerçek kökü `~/Enguru/Runtime/MacEngineer/state/mk-bridge`, ZIP `pilot/enguru-mk-bridge-pilot-v5.zip`; SQLite yalnız stat ile görüldü, bağlantı açılmadı. ZIP'teki dört V5 üye SHA'sı PR #220 exact kaynağıyla eşleşti. Mevcut görev `ENGURU_MK_BRIDGE_PILOT_V1`; PiLive görevi ayrı kalır. Yönetim V6.9 varsayılanı korunur. Aktif ajan görüntüsü beş dakikalık süreklilik veya PiLive öğrenme trafiği kanıtı oluşturmaz.

`projection_v6.py` kurulu app Resources içinde bulunsa da snapshot'ı `~/Library/Application Support/ENGURU/LiveProgress/v4/snapshot_v52.py` yolundan çalıştırıyor. Bulunan bundle dosyasının SHA'sı, bu ayrı runtime dosyasının güncel SHA'sı yerine geçmez. `snapshot_v52.py` açık registry girişlerini dolaşıyor; native Core'un Work Contract ile dinamik keşfettiği P02 kümesiyle tam eşlik henüz ölçülmedi. Eski ürünün görünür yüzey kabulü sıfır kalır.

**Sonraki mühendislik hareketi:** Gerçek LiveProgress/v4 bağımlılık kapanımını ve güncel canonical pinlerini birlikte salt-okunur yakala; eski üç receipt'in exact konum/readback açığını ayrı kaydet. Kaynak→Core→adaptör proje kümesi ve sayım eşliği bu gerçek byte'lara karşı sınansın. Mevcut kası aktive etme, SQLite açma, eski binary'yi yeniden kurma veya canonical yazma gerekmez. Nihai dört ekran sözleşmesi geldiğinde yeni SwiftUI'ı bu doğrulanmış sınıra bağla; yeni build kendi source/toolchain/recipe/signing/binary manifestini üretir.

Tam kanıt zinciri, U01–U12, bağımsız GUI/işlevsel doğrulama ve yetkili kabul açık. Tasarım/teori/GitHub hazırlık puanları yeni kaynak gözlemiyle otomatik 100 yapılmaz. Ayrıntılı gizlisiz sonuç: `RUNTIME_SOURCE_REVIEW_V1.json`.

## Zülfikar V1.3 — 25 Ekim devam emri

V1.3 kaynağı PR #242 @ `5720cd0de67f959d44ea8ace42a3a716753077f1` üzerinden okundu. Açık inceleme dalı; main yayını ve PiLive ürün puanı olarak aktarılmıyor. Hedef / Teknik Altyapı / Başarı Kası / Tutarlılık Kası / FİN Verici uygulama kaydı: `ZULFIKAR_V13_APPLICATION_V1.json`. U01–U12 özgün paydası ve resmî P02 kabulü ayrı korunur.

- [x] Captured Core ve snapshot kaynak SHA'larıyla sınırlı replay: Core registry + P02 Work Contract = 8 proje; eski snapshot assemble = 7 proje; P02 yok. Eski isim filtresi P02 `WORKLIST_V1.json` dosyasını da keşfetmiyor. Bu sonuç gerçek güncel Mac ekranı gözlemi değildir.
- [x] Exact proje-ID kümesi karşılaştırması eklendi: eksik, fazladan, çift veya boş canonical küme HOLD; aynı küme yalnız verilen ID'lerin eşliğini kanıtlar. Yeni keşif veya sayım çekirdeği kurulmadı.
- [x] Sekiz yeni regresyonla PiLive izole testleri 65/65; üç temel turda PASS. Önceki 137/137 Mac kazanımı kendi kaynak sürümünde korunur; yeni testlerin Mac çalışması NOT_EXECUTED.
- [x] Yeni gizlisiz olay mevcut öğrenme kaydına REVIEW_REQUIRED adayı olarak bağlandı. Mevcut pilot ve Yönetim V6.9 görevleri korunur.
- [ ] `enguru.pilive.runtime-dependency-observation/v1` yeni gerçek makbuzu henüz teslim edilmedi. Önceki Terminal devri geçerlidir; aynı gözlem komutunu tekrar çalıştırmaya gerek yok, üretilmişse ORIGINAL JSON yeterlidir.

**Özgün kabul etkisi:** U02 proje kümesi açığı yeniden üretildi; U05 eksik/çift proje görünürlüğü sınırına koruma eklendi; U10 karşıt regresyonu ve U12 kaynak izi genişledi. Bu alt kanıtlar U01–U12'nin tam PASS'i değildir. Sonraki tek hareket, gerçek runtime makbuzunu okuyup kaynak içeriklerini ve sekiz pini aynı gözlem kapsamında uzlaştırmaktır. Güncel pin eşliği ve eski makbuz konumları yeni veri gelene kadar HOLD kalır.

## Gerçek runtime makbuzu ve adaptör onarımı — 18:49Z

- [x] Makbuz `150c772bbec5d536f884888e84f1e9ee47bb6b6b870cbfe7ec4263df1b6c88b7` upload byte'ları Terminal SHA ile aynı; parent `d91557b11abe20363f1a8ff89fb55267ec0549376c3c76839e2f80ea278349fa`.
- [x] Dört runtime/bundle Python içeriği SHA ve byte boyuyla doğrulandı; sekiz Core/canonical pininin dört gözlem listesi birebir aynı ve beklenen pinlerle eş.
- [x] Üç önceki orijinal AudiV13 altında gerçek SHA ile bulundu. Eski Desktop kopyaları exact üst seviyede gözlenmedi. Önceki pair HOLD sonucu orijinalin kaybolduğu anlamına taşınmıyor. Arama ValueError limiti genel yokluk üretmez.
- [x] LiveProgress/v4 altında bulunmayan `projection_v6.py` tahminî bir yoldu; kurulu `plive_v3_base_projection.py` doğrudan runtime `snapshot_v52.py` çağırır. Eksik yol bu aşamada gerekli bağımlılık sayılmaz. Gerçek `snapshot.py` iki ek dosyaya bağlıdır: `bridge.py`, `legacy_snapshot.py`.
- [x] Saf adaptör mevcut Core `registry()` çıktısını tüketir; Work Contract ile bulunan P02 dahil her proje bir kez görünür. Yeni keşif veya sayaç kurulmadı. Core summary/verify olguları aynı project ID ve state/worklist digest'lerine bağlanır. Eksik olgulu projeler görünür HOLD kalır.
- [x] Exact kaynak kopyalarıyla sınırlı Linux Core API tekrarında 8→8, P02 tekil 0/12, aktif P02.S01.01, resmî HOLD. Test fixture Git HEAD sabiti kullanıldı; gerçek Mac/revizyon sonucu olarak aktarılmaz.
- [x] Yirmi yeni karşıt kontrol dahil 85/85 PiLive testi üç tur PASS. Önceki gerçek Mac 137/137 korunur; yeni native paket sınaması bekler.
- [ ] Sonraki tek paket: Mac'te tüm paket testleri + pin kontrollü mevcut Core API üzerinden P02 adaptör dry-run + adı kaynaktan çıkan iki runtime dosyası ve bundle projection_v6 içeriği. Uygulama/LaunchAgent aktivasyonu, canonical/kas/kurulu app yazımı, ağ, SQLite ve Keychain 0; yalnız owned temp test alanı ve yeni receipt/kopya.

U01 kaynak bağı alt kanıtı ilerledi; exact Swift/build/toolchain/signing/binary zinciri HOLD. U02/U05 proje kümesi onarımı kod ve sınırlı replay kapsamıyla PASS; gerçek Mac dry-run ve UI eşliği açık. U09 üç zaman ayrımı/deterministik digest, U10 yirmi regresyon, U12 gizlisiz kanıt izi ilerledi. U01–U12 tam kabulü ve P02 resmî bitişi kendi kapısında HOLD. Nihai dört ekran sözleşmesi beklenir.
