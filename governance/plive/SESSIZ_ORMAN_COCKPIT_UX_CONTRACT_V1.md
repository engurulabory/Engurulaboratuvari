# ENGÜRÜ PiLive™ — Sessiz Orman Cockpit™ V1 / Yaratıcı Ekran ve Etkileşim Sözleşmesi

**Tarih:** 2026-10-26 · **State:** `G1.D02_DESIGN_REVIEW_CANDIDATE / OWNER_AESTHETIC_ACCEPTANCE_HOLD / REAL_SWIFTUI_HOLD`
**Yönetim kararı:** PiLive V4 bu oturumda aktif; OSi Birleşik Sistem Mimarisi™ V1 ayrı PR #244 / WORKLIST içinde `HOLD` olarak park edildi.
**Referanslar:** `governance/plive/ENGURU_PILIVE_URUN_HEDEFI_V4.md` (U01–U12); PiLive PR #241 exact HEAD `64afbf862a393fcb2972f1f2dcbeb98649885fb8`, `governance/pilive-learning/PORTFOLIO_DATA_CONTRACT_V1.md`, `NATIVE_PORTFOLIO_REVIEW_V1.json`. Kullanıcı onayı ayrı gerçek kapıdır; bu tasarım GitHub kodu veya macOS görünür deneyim kabulü değildir.

## 1. Kalıcı sabit ürün vaadi

**Tek pencere · Tek hakikat · Tek sonraki hareket.**

Sessiz Orman yönü: grafit/orman yeşili karanlık, az sayıda yeşim vurgu, geniş nefes alan boşluk, sakin San Francisco tipografisi, düşük uyarılma, üst düzey Mac hissi. **A · Sessiz Orman Cockpit** düzeni çalışma temeli; B · Orman Atlası'nın kategori haritası yalnız Projeler bölümünde kullanılır. Emin Baykuş yalnız sembol/rehberdir; kanıtsız yapay zekâ önermeleri üretmez.

## 2. Ekran mimarisi ve kanıtlı kullanıcı hikâyeleri

### 01 Genel Durum
İlk bakışta dört gerçek sinyal:
- **15 kaynakta gözlenen proje**, her satır ayrı source-bound `projectId`;
- **14/15 doğrulanmış teknik sayaç**; kalan **1 proje** `HOLD / N/A`;
- **resmî kabul ile teknik sayaç ayrı**; global portföy için sahte tamamlanma yüzde değeri veya farklı paydaların toplamı yok;
- **P02 0/12, %0; P02.S01.01**, proje içindeki aktif iş olarak gösterilir. Yetkili küresel tek odak kaynağı bulunana kadar `GLOBAL_ACTIVE_SELECTION=HOLD`; P02 otomatik küresel öncelik sayılmaz.

İkincil iki gerçek örnek:
- **Progress Core 44/44 (%100 teknik), finish=HOLD**: ilerleme ve yetkili bitiş eşanlamlı değildir.
- **Visual Cockpit 26 beyan/24 kanıt/2 açık**, proje ekran yüzdesi `N/A`, `progressIntegrity=HOLD`.

Başlıkta kaynak tazelik statüsü `FRESH/STALE/OFFLINE/HOLD`; kanıtlı `sourceReadAt` varsa göster, yoksa `BİLİNMİYOR`. `uiRenderedAt` yalnız gerçek UI çalışmasında verilir.

### 02 Şimdi
- Yetkili canonical global odak varsa **tek** iş göster. Çoklu/çelişik ya da henüz okunmamış küresel seçim `HOLD_CONFLICT / GLOBAL_PRIORITY_NOT_PROVEN`.
- P02 kartı proje içinde `P02.S01.01`, kaynak/paket `P02.S01`, tamamlanma `0/12`, yetkili `HOLD`, gereken kaynak/kanıt ve sonraki gerçek hareket ile sunulur.
- "Şimdi" ekranında Work mühendislik uygulaması için bir ilerleme sınırı bulunabilir; herhangi bir eylem butonu writer veya owner yetkisi doğurmaz. Gösterilen `nextAction` yalnız mevcut Core özetinden gelir.

### 03 Projeler
- Başlıkta her zaman **Motor / Çekirdek / Web / App / Agent** beş üretim alanı.
- Ticari/COMMERCE ayrı kategori ve ikinci sayaç değildir; kaynaklı facet/etikettir.
- Kaynaklı `productionArea` yoksa proje **Kaynak eşlemesi bekleniyor** grubunda görünür. Kategori sayacına `0` yerine `N/A`; hiçbir proje gizlenmez.
- İster liste ister B'den esinli alan atlası, ikisi de aynı 15 kaynak projeyi, canonical key/ID teklik ve gerçek `done/total/%` ile gösterir. `HOLD` projede teknik oran `N/A`; 26 beyan/24 kanıt bilgisi kanıt ayrıntısında ayrı okunur.
- Liste arama/filtresi gerçek projeyi değiştirmez ve id/percent eşliğini bozmaz.

### 04 Kanıt çekmecesi (üstten tek hareket)
- Yerel/gerçek snapshot için: `projectId`, `activeItem`, `sourceRevision`, 8/8 Core pin, 48/48 kaynak SHA braketleri, `projectionDigest`, 218/218 native test receipt, 221/221×3 izole regresyon, exact-HEAD CI 5/5 ve asıl test zaman/ortam kapsamı.
- Kurulu **eski** V3.1 binary'nin `codesign --verify --strict` dönüş kodu `1` = **HOLD**. Güncel Swift 6.4 yalnız mevcut toolchain gözlemidir; tarihsel Swift→binary bağı `HOLD`.
- `sourceReadAt`, `adapterBuiltAt`, `uiRenderedAt` ayrı; `null` bilgi `Bilinmiyor`.
- Kapalı çekmeceden açılma ≤1 etkileşim; Escape ile kapanır, odağı açan kontrole döner, klavye ve VoiceOver uyumlu.

## 3. Görsel tasarım sistemi

| Token | Önerilen değer | Rol |
|---|---|---|
| `canvas` | `#0B1513` | Ana arka plan |
| `sidebar` | `#101D19` | Ana gezinme yüzeyi |
| `surface` | `#14241F` | İçerik kartı |
| `surfaceRaised` | `#1B2D26` | Üzerine çıkılan yüzey |
| `line` | `#30443A` | Düşük kontrast sınır |
| `textPrimary` | `#EEF4EE` | Ana metin |
| `textMuted` | `#A6B7AC` | Yardımcı metin (AA testi gerekir) |
| `jade` | `#91D4AD` | İlerleme vurgusu |
| `warning` | `#E9C78A` | HOLD/kanıt bekleme |
| `danger` | `#E59E9B` | Kaynak kopması/arıza |

**Typography:** SF Pro / platform system stack. Başlıklar 28–34 pt; ana sayaç 31–40 pt; satır metni 13–15 pt, ayrıntı 11–12 pt ve Dynamic Type büyümeye uygun. Grid 8 pt, iç kenar 20–28 pt, minimum tıklanabilir hedef 44×44 pt. Görsel yoğunluk kontrollü; grafik/animasyon süs için hakikat saklamaz. Koyu tema varsayılan; Reduce Motion ile animasyonlar kapanır; VoiceOver için her durum metni ve ikonun adı vardır. Kontrast ölçümleri gerçek native U08 kapısındadır.

**Pencere:** bağımsız Mac minimum hedef `980×640`, önerilen `1280×820`; dar pencerede sidebar daralır, kartlar dikeyleşir. Bu bir tasarım hedefidir; gerçek SwiftUI layout testi U06/U08'de yapılacaktır.

## 4. Ekran durum matrisi

| Durum | Görünür davranış |
|---|---|
| `FRESH` | Kaynak gözlem zamanı açık; yalnız kanıtlı proje sayaçları |
| `STALE` | Yaş ve son başarılı gözlem, ekran üstünde yazılı uyarı; eski değer güncel diye sunulmaz |
| `OFFLINE` | Son bilinen snapshot varsa belirgin cache etiketi, yoksa N/A |
| `PARTIAL_PROJECT_HOLD` | Bir proje N/A, diğer 14 geçerli |
| `GLOBAL_DRIFT` | Tüm model HOLD, önceki değerler güncel kabul edilmez |
| `KEY/ID_COLLISION` | Tüm model HOLD, ayrıntı çekmecesinde kaynak ID |
| `COUNTER_MISMATCH` | İlgili satır HOLD/N/A, küresel geçerli satırlar korunur |
| `MULTIPLE_GLOBAL_ACTIVE` | Şimdi ekranı `HOLD_CONFLICT`; P02 proje-içi iş gösterilebilir |
| `PERMISSION/UNREADABLE` | Açık kaynak eksikliği, veri yoksa N/A |
| `SIGNATURE_VERIFY_RC1` | Tarihsel binary **İmza HOLD**, sahte doğrulama PASS yok |

## 5. Gerçek kaynaktan doğrulanan, demo için referans olgular

```
projectRows=15, qualifiedCounters=14, sourceBoundObservations=15
P02: projectId ENGURU_PLIVE_P02_USER_SCREEN, done=0, total=12,
  percent=0, activeItem=P02.S01.01, officialAcceptance=HOLD
Progress Core: done=44, total=44, percent=100, finish=HOLD
Visual Cockpit: declared=26, evidenced=24, unverified=2,
  done=null, total=null, percent=null, status=HOLD
CorePins=8/8; sourceBrackets=48/48; replayDigest=
  b051e49b654bc606af40c884c70185972a484573d0b291ec72438a6812498632
Native=218/218 (Mac); Post-review regression=221/221 ×3 (isolated);
GitHub PR #241 exact HEAD=64afbf862a393fcb2972f1f2dcbeb98649885fb8, CI=5/5
Installed V3.1 binary codeSignStrict returnCode=1 -> HOLD
```

Bunlar **tarihsel native receipt ve GitHub kaynak gözlemi**; statik tasarım/demo gerçek zamanlı telemetri veya `uiRenderedAt` kanıtı değildir. Bu sözleşme statik UI önizleme verisinin doğruluğuna ilişkindir, yayımlanmış UI olgusu değildir.

## 6. İki biçim ve kabul kapıları

**Öncelik 1:** PiLive kendi bağımsız macOS SwiftUI uygulaması. Onaylı görsel sonrası Work, mevcut salt-okunur adapter ve Progress Core'u gerçek ekranla bağlar, yeni build için exact Swift→binary provenance oluşturur, U01–U12 ve 12/12 gerçek saha kabulünü kanıtlar.

**Öncelik 2 (fabrika backlog HOLD):** Ana Cockpit'te açılıp kapanan PiLive modal. Aynı proje kümesi/revizyon/digest; ekran zamanı farklı olabilir; klavye/focus trap, VoiceOver, pencere yaşam döngüsü ve bağımsız saha onayı. Ana Cockpit'in mevcut genel modal CSS/HTML varlığı, özel PiLive modal PASS değildir.

**Ayrı resmî kapı:** P02 `12/12` + DoneCheck `4/4` + saha `7/7` + G3 gerçek owner/issuer/grant/writer + Human Threshold → native Verified Finish. Teknik P02 `0/12`; bağımsız GUI ve ürün onayı HOLD.

## 7. Üç tur yaratıcı karşıt sınama (tasarım kontrol matrisi, saha testi değildir)

1. **Hikâye/boş durum:** Kullanıcı 15 projeyi, 14 kaynağa bağlı sayacı, bir HOLD projesini, P02'yi ve belge açmadan sonraki hareketin kaynağını anlar. Eksik global öncelik ayrıca HOLD.
2. **Kötü veri/otorite:** Visual Cockpit 24/26 beyanına sahte `92%` üretilmez; `progress-core 100%` resmî bitiş diye sunulmaz; P02 `0/12` ve resmi HOLD ayrıdır.
3. **macOS/erişilebilirlik:** En fazla 2 etkileşimde proje, en fazla 1 etkileşimde kanıt; Escape, VoiceOver, AA contrast, Dynamic Type, Reduce Motion, pencere boyutu testleri gerçek SwiftUI uygulamasında ayrı PASS gerektirir.

**G1.D02 tasarım metni hazırlanmıştır.** **G1.D03 karşıt UX tasarım incelemesi adayıdır. G1.D04 kullanıcı estetik kabulü HOLD.** Bu doküman kendi varlığıyla `DESIGN_100` veya U07 PASS üretmez.

## 8. Work'e tasarım-uygulama devir sınırı

Work bu **ayrı tasarım PR'ını** kaynak olarak okur; teknik PR #241 tek mühendislik yazıcısı olarak korunur. Görsel owner kabulü gelmeden gerçek SwiftUI ürün estetiğinin nihai seçildiği varsayılmaz. Work erişilebilir hazırlık olarak durum modelleri, display-status mapping, icon/contrast test planı ve source-bound SwiftUI adapter skeleton tasarlayabilir.

Work yanıtı **önce icra, sonra teknik kanıt/Terminal**, **en sonda ≤8 satır MİNİ YÖNETİCİ RAPORU**. GitHub UI testleri native saha kabulü yerine geçmez.
