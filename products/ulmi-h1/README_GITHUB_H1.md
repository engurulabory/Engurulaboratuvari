# ENGÜRÜ Mühendisi ULMi™ — H1 GitHub mühendisliği

**Emir:** `KAPTAN-ULMI-H1-BIRLESIK-01-TECH-01-11-20261118` · **H2:** PARKED.

Bu klasördeki `PRODUCT/` ve `TESTS/` dosyaları, 18 Kasım 2026 tarihli R2 teknik adayından korunarak aktarılmıştır. Özgün R2 paket SHA-256: `5c810fa9adf70e6b42525a49a8fe876694dab89d3a3c69d8b9b68fa5897cde2a`. Dosya içeriği kaynak bazında korunmuştur; teknik sonuçlar GitHub CI'da ayrıca ölçülür. Kaynakların public depoda bulunması, ürünün nihai kabul edildiği anlamına gelmez.

## Gerçek çalışma

```bash
cd products/ulmi-h1
python3 -m pip install 'requests>=2.31,<3'
python3 -B tools/verify_contracts.py
python3 -B tools/test_release_integrity.py
python3 -B TESTS/test_r2_project_chat_real_http.py
python3 -B TESTS/run_project_bound_e2e.py
python3 -B TESTS/run_generated_taskboard_e2e.py
python3 -B TESTS/run_final_e2e.py
python3 -B tools/build_release.py /tmp/ulmi-h1-technical.zip
bash START_H1.sh
```

Uygulama yalnız `127.0.0.1` üzerinde HTML + Python + SQLite olarak çalışır. Model erişimi isteğe bağlı ayrı yetki sınırındadır. Github Pages sadece statik önizleme için uygundur.

## Kanıt ve kabul

GitHub Actions `ulmi-h1.yml`, teknik testleri ve izinli Chromium tarayıcı testini birbirinden ayrı işler olarak çalıştırır. Runner üzerindeki test sonucu, gerçek Qwen yürütmesi, özgün Pilot A/B/C, bağımsız DoneCheck veya owner UAT sonucunun yerine geçmez.

Korunan başlangıç durumu: tarihsel 4/12 scoped; resmî V22 0/12 HOLD; Emir 01 özgün 11/11 technical full HOLD; H2 PARKED. Teknik kod ve test kazanımları SHA ve commit ile ilerletilir. `main` birleştirme/yayın için owner yetkisi esastır.

## CI başlatma ve paket bütünlüğü sınırı

GitHub Actions runner tahsisi başlamadan başarısız olduğunda, işin test adımları
çalışmış kabul edilmez. Olayı `HOLD_GITHUB_RUNNER_PRESTART` olarak kaydet;
aynı commit'in kaynak eşdeğerinde `tools/verify_contracts.py`,
`tools/test_release_integrity.py` ve gerçek HTTP/SQLite regresyonlarını ayrıca
çalıştır. Bu yerel sonuçları GitHub CI PASS'i yerine kullanma.

`tools/build_release.py`, yalnız kaynak dosyalarını, iç SHA-256 manifestini ve
çalışma yönergelerini teslim eder. `__pycache__`, `.pyc` ve benzeri geçici
dosyaları paket dışında tutar; dahil edilen alandaki sembolik bağlantıları
güvenli biçimde reddeder. İki üretim aynı baytlardan oluşur.

Gerçek tarayıcı testi GitHub runner üzerinde Playwright Chromium kullanır.
İzinli ve bağımsız yerel ortamda kurulu Chromium ile çalıştırılacaksa
`ULMI_CHROMIUM_EXECUTABLE=/usr/bin/chromium` tanımlanabilir; yönetilen tarayıcı
politikalarının sonucu kendi HOLD sınırında korunur. Gerçek Qwen, özgün
Pilot A/B/C yetkisi, bağımsız DoneCheck ve owner UAT ayrı kanıtlara bağlıdır.
