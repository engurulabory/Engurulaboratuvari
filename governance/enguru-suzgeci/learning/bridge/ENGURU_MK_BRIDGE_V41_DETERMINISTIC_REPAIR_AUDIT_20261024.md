# ENGÜRÜ Çift Yönlü Öğrenme Köprüsü™ — V4.1 Deterministik Komut ve Saha Onarım Kaydı

**Tarih:** 2026-10-24. **Kapsam:** PR #215 üzerinde geliştirilen karşılıklı öneri pilotunun Mac ZIP uygulama giriş noktası. **Durum:** THEORETICAL_100_100 / LOCAL_SIMULATION_378_378_PASS / MAC_FIELD_HOLD / OFFICIAL_FINISH_HOLD.

## Gerçek gözlem ve doğrulanmış kök neden
Mac çıktısında V4 paketinin `--self-test` çalışması 107/107 ×3 PASS; `--activate && --status` yalnız `PACKAGE_MANIFEST=PASS_SHA256` gösterdi. Doğrulanmış kaynak nedeni: V4 ZIP `__main__.py` içinde `from tools.enguru_mk_autopilot_v4 import main` satırından sonra `main()` çağrısı bulunmuyordu. Python modülü tanımı içe alınmış, operatör komutları yürütülmemişti; yanlışlıkla çıkış kodu 0 görüldü. V3 gerçek kurulumu korunmuş varsayılmalıdır; Mac V4 aktivasyonu PASS olarak yorumlanmaz.

## V4.1 bütünleşik onarım
1. ZIP girişindeki `--activate / --cycle / --status` gerçek `main()` çağrısına bağlı. Başarıda JSON durum kaydı, hata durumunda açık HOLD ve çıkış kodu 50.
2. `--status`, `mode=ro` SQLite bağlantısı kullanır. Eksik, sembolik bağ veya bozuk yerel depo durumunda veri oluşturmadan HOLD.
3. AudiV13 yedeğinde mikro saniye çözünürlüklü farklı ad ve `O_EXCL` rezervasyonu; tekrar denemelerde mevcut yedekler korunur. SQLite backup bağlantısı kapatılır, quick_check uygulanır.
4. Kaynak listesi, ZIP metadata ve dosya sırası sabittir (`ZIP_STORED`, sabit tarih). Aynı kaynaklardan iki ayrı yapımda tüm ZIP baytları ve SHA-256 eşit.
5. Eski V3 pilot ve SQLite korunur; V4 aktivasyon reddi veya başarısız başlatma güvenli HOLD. Önerilerin `SUGGESTION_ONLY` hükmü ve salt-okunur icra sınırı korunur.

## Simülasyon ve puanlama
- Önceki kör nokta: ZIP giriş komutlarını gerçekten başlatan uçtan uca test bulunmuyordu.
- Ek regresyon kapsamı: gerçek `python -B <ZIP> --activate/--cycle/--status`; Mac aktivasyon taklidi; mevcut paketle yeniden deneme; beklenen launchd geri dönüşü; yedek çakışması ve SQLite kapatma; yeniden üretilebilir ZIP.
- **126 özgün test × 3 ayrı subprocess turu = 378/378 PASS.**
- **Teorik deterministik rubrik 100/100**: CLI yönlendirme 20, hatada kesin HOLD 20, salt-okunur sorgu 20, yedek/rollback 20, bayt düzeyinde yeniden üretim 20.
- Paket SHA-256: `af033fbb7a5768b870f9c76aded36d5161026fd194d54503fdffa2da27e4bb4e`.
- Kanıt makbuzu SHA-256: `c7370b4f146b3ca76877302b38129da2907b3fe4069ef66b8dcc4227c097ad25`.

## Bağımsız saha kabul sınırı
- GitHub kaynak ZIP CI exact SHA, gerçek Mac V4.1 aktivasyonu, `launchd` yeni agent, SQLite inbox/ack ve iki yönlü öneri+nextStep uygulaması ayrıca gerçek kanıt ister.
- Ana ürün GitHub `main`, Yönetim/İcra dalları ve mevcut Human Threshold / DoneCheck mutasyonu bu kayıt kapsamında **0**.
- `VERIFIED_FINISH` yalnız canonical yetkili DoneCheck/owner kabulü ile oluşur.

**Son mühendislik hükmü:** `PASS_THEORETICAL_CLI_DETERMINISM / HOLD_GITHUB_PACKAGE_CI / HOLD_MAC_FIELD / HOLD_OFFICIAL_VERIFIED_FINISH`.
