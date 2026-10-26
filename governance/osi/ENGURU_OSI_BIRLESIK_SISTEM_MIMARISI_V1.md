# ENGÜRÜ OSi Birleşik Sistem Mimarisi™ V1

> **2026-10-26 güncel GitHub uzlaştırması:** İlk kaynak gözleminden sonra Zülfikar PR #242 `main` üzerine birleşti. Güncel control main `28db999ba676e4764ae1b644950865674661d0b8`; ürün main `c6ef1555a48beeff94a85cab316c80b3fa60f9c5`; PiLive PR #241 çalışma HEAD'i `64afbf862a393fcb2972f1f2dcbeb98649885fb8`. Bu olayın ayrı kaydı [GITHUB_SOURCE_OBSERVATION_20261026_V1.json](GITHUB_SOURCE_OBSERVATION_20261026_V1.json). Aşağıdaki ilk tablo tarihsel gözlem olup bugünkü HEAD veya gerçek OSi okuması olarak kullanılmaz.

**Tarih:** 2026-10-26 · **STATE:** `ARCHITECTURE_REVIEW_CANDIDATE / OSI_LIVE_READBACK_HOLD`
**Karar:** Kullanıcı sistem adını ve GitHub ↔ Mac OSi **eşlenik ikiz** çalışma hedefini kabul etti. Bu belge proje/ürün yetkilerinin yerine geçmez.

## 1. Bütünleşik OSi fabrikası

| Katman | Tek rol | Mevcut kaynak / kabul ayrımı |
|---|---|---|
| **OSi Fabrika** | Yerel Mac gerçek çalışma, test, kurulum, recovery ve Evidence | Canlı Mac ölçümü gereken ayrı saha |
| **ENGÜRÜ Mac Engineer™** | Ana motor: yetkili mühendislik icrası, build/test, onarım | Ürün kaynak deposu `engurulabory/enguru-mac-engineer` |
| **ZEKÜ** | Ana pilot, hedef, yönlendirme, Second Look | `PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json` içindeki `leadPilot=ZEKU`; gerçek pilot handler saha doğrulaması ayrıdır |
| **Ana Cockpit** | Ana kullanıcı yönlendirme/çalışma yüzeyi | Ürün reposunda `runtime/cockpit_store.py` ve genel HTML modal altlığı var; yeni birleşik kabul ayrı |
| **PiLive™** | İlerleme, takip, uyarı, kanıt ve kaynak tazeliği | Mevcut tek Progress Core'a salt-okunur bağlı; ikinci sayaç/otorite yok |
| **Süzgeç + Zülfikar** | Hedef 100 → Tasarım 100 → Teori 100 → Teknik Altyapı 100 → GitHub 100 → gerçek saha → kullanıcı → FIN | Yöntem; mevcut canonical issuer ve Human Threshold korunur |
| **DoneCheck / Human Threshold** | Bağımsız kanıt ve resmî kabul | Ürünün özgün yetkili kapıları geçerlidir |

ZEKÜ uzman profil kümesi: ATLAS, FORGE, ASTRA, NEURON, SENTINEL, FORMA. Profil tanımı canlı native handler kabulü değildir.

## 2. PiLive: iki sunum, bir hakikat

```text
OSi FABRİKASI
  Ana Cockpit ⇄ ZEKÜ Ana Pilot → Mac Engineer Ana Motor
  Canonical Progress Core → Read-only / SHA-bound PiLive Data Contract
                                ├── PiLive bağımsız Mac uygulaması
                                └── Ana Cockpit açılır-kapanır PiLive modal
  Evidence → DoneCheck → Human Threshold → Yetkili kabul

GitHub Control Plane / Product Source ⇄ exact source SHA, CI, receipts ⇄ OSi gerçek Mac
```

**Tek source of truth:** PiLive standalone ve Cockpit modal aynı `projectId` kümesi, source revision, `projectionDigest`, teknik done/total/% ve resmî ayrı HOLD/acceptance tüketir. İki ekranın `uiRenderedAt` zamanları ayrı olabilir; kaynak revision/digest uyuşmazsa STALE/HOLD. İkinci keşif motoru, gölge sayaç, writer veya issuer üretilmez.

**Stand-alone kapısı:** Genel Durum / Şimdi / Projeler / Kanıt çekmecesi; gerçek macOS U01–U12, kullanıcı estetik kabulü, erişilebilirlik ve performans. **Modal kapısı:** aynı veri sözleşmesi + focus/return, open/close, keyboard/VoiceOver, stale/reconnect, eş kaynak digest ve bağımsız saha testi. Bağımsız PiLive uygulaması ürün kabulü birinci aşamadır; özel modal ikinci aşamadır. Resmî P02 `12/12 + DoneCheck 4/4 + saha 7/7 + G3 + Human Threshold` her ikisinden ayrıca ayrıdır.

## 3. İki sistemli eşlenik ikiz ve yetki

**GitHub:** Kontrol deposu `engurulabory/Engurulaboratuvari`; Mac Engineer ürün deposu `engurulabory/enguru-mac-engineer`. AGENTS.md, canonical V3, kabul sözleşmesi ve ürün exact SHA kaynak otoritesidir.
**OSi:** `~/Enguru/Projects/Engurulaboratuvari`; `~/Enguru/Projects/enguru-mac-engineer`; `~/Enguru/Runtime/MacEngineer`; `~/Enguru/Evidence/MacEngineer`. Gerçek yerel source/runtime/kanıt eşliği ayrıca ölçülür.

**8 eşlik kapısı:** (1) repo/branch/HEAD/dirty, (2) her gerekli dosyanın SHA-256'sı, (3) toolchain ve dependency, (4) aynı komut/girdi→çıktı, (5) runtime/provenance, (6) security/authority, (7) restart/rollback, (8) original/desktop-copy receipt ve bağımsız reviewer.

**Çalışma sırası:** OSi read-only gerçek envanter → GitHub fark/dal/PR → 3 tur gerçek regresyon+karşıt test → exact HEAD CI+review → SHA-kilitli saha paketi → owner yetkisiyle yerel build/run → native Evidence → GitHub ile çift yönlü SHA uzlaştırma → DoneCheck + Human Threshold → Verified Finish.

**GÜVENLİ_DUR:** Kaynak/HEAD/dirty/iş kimliği/digest eşlik sorunu, çatışan yazıcı veya yetki eksikliği → son doğrulanmış iki yüzeyi koru; otomatik merge/overwrite/yetki genişlemesi yok. GitHub erişimi geçici kesildiğinde gerçek OSi yerel çalışma ve yerel Evidence kendi yetkisiyle devam edebilir; remote geri geldiğinde mutabakat yapılır. GitHub PASS native PASS sayılmaz.

## 4. Anlık kaynak hakikati (GitHub gözlemi, 26 Ekim)

| Kapsam | GitHub kaynak kanıtı | Bu oturumda doğrudan Mac readback |
|---|---|---|
| Control Plane `main` | `8947cb6c240a12950be1f8be9e186d0ecbfa3022` | `HOLD_LIVE_READBACK` |
| Mac Engineer product `main` | `c6ef1555a48beeff94a85cab316c80b3fa60f9c5` | `HOLD_LIVE_READBACK` |
| ZEKÜ Pilot Fabric | `leadPilot=ZEKU`; `CONTRACT_DEFINED` | `HOLD_NATIVE_HANDLER` |
| Ana Cockpit | Ürün source'da CockpitStore ve generic HTML modal | PiLive modal `HOLD` |
| PiLive PR #241 | `daee6cef9ad340acfdc2624c54b509addb55012d` / `218/218×3` Linux / `5/5` CI | Yeni 15 proje portföy native makbuzu bekleniyor |
| PiLive tarihsel native | Work raporu `203/203`, 15/15, P02 `0/12`; receipt `39c28d1c41777c14decc7a67d034d13c34f242a7b4c261c2a524fd766c54b808` | Bu turda yeniden okutulmadı |
| Zülfikar | PR #242 GitHub çalışma/CI, inceleme dalı | `OSI_FIELD_HOLD` |
| PiLive Standalone V4 + Cockpit modal | Hedef / tasarım sözleşmesi | İki gerçek yüzey kabulü `HOLD` |

**Kaynak referansları:** `governance/mac-engineer/OPERATING_MODEL_V1.md`, `governance/mac-engineer/PRODUCT_OPERATOR_V12_PILOT_FABRIC_CONTRACT_V1.json`, `governance/plive/ENGURU_PILIVE_URUN_HEDEFI_V4.md`, PR #241 `governance/pilive-learning/PORTFOLIO_DATA_CONTRACT_V1.md`, Mac Engineer product source `runtime/cockpit_store.py`.

## 5. Tüm oturumlar için ortak disiplin

1. Güncel `main` + `AGENTS.md` + bu mimari + canonical V3 SHA kilidi + özgün ürün sözleşmesi ve kaynak/iş listesini oku.
2. GÖZLEM kimlikleri ayrı: `GITHUB_OBSERVED`, `OSI_LIVE_OBSERVED`, `HISTORICAL_RECEIPT`. Native saha ve GitHub sonuçları birbirinin yerine geçmez.
3. Yönetim hedef/öncelik/tasarım; Work kaynak/kod/test/native Evidence. Tek aktif yazıcı, tek ana iş listesi ve özgün ID'ler.
4. ✅ yalnız tam kanıtlanan özgün alt işe; product U01–U12 ve official P02/Human Threshold ayrı.
5. **Work yanıt sırası kilitli:** önce icra, kod, test ve kanıt, sonra varsa tek Terminal hareketi; **EN SON ≤8 satır MİNİ YÖNETİCİ RAPORU** (HEDEF; KANITLANAN KAZANIM; PUAN/PASS-HOLD; AÇIK EKSİK; GEREKEN KARAR/YARDIM; SONRAKİ TEK HAREKET). Raporun ardından ek yok.
6. Mevcut açık ChatGPT oturumları GitHub dosyasını kendiliğinden yeniden okumaz; kaynak/HEAD bağlantılı bir defalık hizalama talimatı aktarılır.

## 6. Saha hakikati ve geçici GitHub çalışma bağımlılığının kaldırılması

Canlı Mac gözlemi için `tools/enguru_osi_twin_probe_v1.py` (hazırlık adayı) yalnız açık owner Terminal çağrısında kullanılır. Git checkout HEAD/dirty sayıları, allowlisted dosya SHA ve kurulu app binary kimlikleri read-only okunur; orijinal `Desktop/AudiV13`, masaüstü SHA eş kopya. Yeni bir real task çalıştırmaz, uygulama açmaz, GitHub'a veri göndermez. Bu gözlem tek başına ürün kabulü değildir.

**Final sonrası GitHub'dan kaldırma kararı:** Native reel test, reel çalıştırma, bağımsız kabul, Verified Finish ve rollback kanıtından sonra **GitHub'ın günlük yerel yürütme için zorunlu bağımlılığı** kaldırılabilir. `ACTIVE_WORKING_PATH.md` benzeri geçici çalışma belgeleri, geçici inceleme dalları ve paketleri ayrı ve owner onaylı cleanup listesine girer. Canonical kaynak, sürüm ve audit tarihi ile geri dönüş/yeniden inşa yolu kalır. GitHub kaynaklarının bütünü için silme bu sözleşmenin otomatik eylemi değildir. **Şimdilik GitHub deletion=0; OSi mutation=0.**

**Kapı zinciri:** GITHUB_REVIEW → REAL_OSI_TWIN_PARITY → REAL_BUILD_RUN → STANDALONE_U01_U12 → COCKPIT_MODAL_FIELD → INDEPENDENT_ACCEPTANCE → DONECHECK/HUMAN_THRESHOLD → VERIFIED_FINISH → AUTHORIZED_TEMP_CLEANUP.

**STATE:** `ARCH_V1_GITHUB_REVIEW / OSI_LIVE_READBACK_HOLD / TWIN_PARITY_HOLD / REAL_FIELD_HOLD`.
