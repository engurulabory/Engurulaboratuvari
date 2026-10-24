# ENGÜRÜ Mühendislik Kası™ — gerçek V4 komut yönlendirme regresyonu

**Tarih:** 2026-10-24. **Kapsam:** Korunmuş V4 ve V4.1 ZIP giriş kaynaklarında tarihsel sessiz aktivasyon hatasının kaynak ve çalıştırma testleriyle doğrulanması.

## Gerçek gözlem ve kaynaklar

Owner Mac Terminal çıktısında eski V4 `--activate` yalnız `PACKAGE_MANIFEST=PASS_SHA256` göstermiş; gerçekte kurulum yönlendiricisi çağrılmamıştır. İncelenen eski ZIP `__main__.py` dosyasında `from tools.enguru_mk_autopilot_v4 import main` vardır, arkasından `main()` çağrısı bulunmaz. V4.1 ZIP girişinde `main()` çağrısı mevcut; owner'ın V4.1 saha kanıtı `PASS_V4_LOCAL_ACTIVATION`, `FIELD_EXIT_CODE=0`, `V41_LAUNCHD=PASS_LOADED` gösterdi.

- Eski tam V4 ZIP SHA-256: `ee2f36a6d2b7032d180ab641d06c69b4202173685f567ea3be1cffd0c4a9edd0`.
- Eski giriş dosyası SHA-256: `ac9c058ad8b0e05c5702da61b6462b1353adee1b284656675f0699bd87476d98`.
- Onarılmış V4.1 tam ZIP SHA-256: `af033fbb7a5768b870f9c76aded36d5161026fd194d54503fdffa2da27e4bb4e`.
- Onarılmış giriş dosyası SHA-256: `d23588e0996d1e20ce1a17974d1c3fd4d1cd4b39333371f36de7cd456b19f0da`.

## Doğrulama yöntemi

Bu PR'daki iki kaynak kopyası SHA ile doğrulanır; `tests/test_mk_real_regression_case_v1.py` her birini **sentetik geçici ZIP** içine aynı manifest kontrolüyle yerleştirir. `--activate` çalıştırılırken Mac gerçek yürütücüsü yerine yazımsız sentinel kullanılır. Böylece geçerli SHA ve gerçek Python komut yönlendirmesi sınanır; ürün, Mac, GitHub ve canonical defter yazımı **0** kalır.

| Ölçü | V4 önce | V4.1 sonra |
|---|---:|---:|
| Manifest PASS | 1/1 | 1/1 |
| Komut gerçekten yönlendirildi | **0/1** | **1/1** |

Üç yerel test turu: **12/12 + 12/12 + 12/12 PASS**. GitHub üzerinde bağımsız exact-HEAD CI ayrıca kontrol edilecektir. Bu, yalnız **tek gerçek tarihsel hata ve onun düzeltmesi** için sınırlandırılmış kanıttır; çoklu vaka öğrenme performansı veya resmî yetki belgesi değildir.

## Korunan kabul

- `REGRESSION_FIX=PASS` ancak GitHub'ın aynı exact commit'te bağımsız test koşusu başarılı olduğunda.
- `V5_VERIFIED_LEARNING=HOLD`: gerçek yetkili bağımsız doğrulayıcı, güvenilir outcome ve zaman içinde çoklu vaka ölçümü ayrıca gereklidir.
- `GITHUB_EXACT_HEAD=HOLD` GitHub CI tamamlanıncaya kadar.
- `DONECHECK_HUMAN_THRESHOLD=HOLD`: canonical owner, DoneCheck™ ve Human Threshold™ ayrı çalışır.
- Köprü V5 kurulumu, `main`, Yönetim/İcra motorları, mevcut SQLite ve owner anahtarları korunur.

**Kalıcı sabit hedef:** `GERÇEK_VAKA_KANITI → BAĞIMSIZ_CI → YETKİLİ_ÖĞRENME_KANITI → OWNER/DONECHECK → VERIFIED_FINISH → BITTI_DUR`.
