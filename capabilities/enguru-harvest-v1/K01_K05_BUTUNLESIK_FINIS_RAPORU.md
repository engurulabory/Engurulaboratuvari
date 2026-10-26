# ENGÜRÜ Yetenek Hasadı™ — Zülfikar V1.3.1 K01–K05 Finiş Paketi

**Kalıcı sabit hedef:** kaynak yetkileri korunmuş, ücretsiz API zorunluluğu 0, gerçek GitHub teknik başarı ve ileride yetkili Mac OSi saha. Tek aktif mühendislik hedefi PR #243 ve yalıtılmış inceleme dalıdır.

## K01 — Gerçek mühendislik farkı
- Eski ENGÜRÜ `duplicate-check` fonksiyonunun `ids.count` tabanlı karesel taraması, `seen/repeated` tabanlı doğrusal taramaya dönüştürüldü.
- `run_k01_real_benchmark.py`: GitHub runner'ında 5 eş koşullu, ayrı düzenlenmiş 3.304 kimlikli veri kümesi; gerçek duvar saati ölçüsü, 100/100 çıkış eşliği ve SHA-256 makbuzu.
- Bu kanıt **mühendislik algoritma verimi** içindir. Müşteri/owner günlük kullanımında yeni kapasite artışı ayrı deneydir.

## K02 — Kaynak ve lisans güvenlik sınırı
- 30 kaynak README gözlemi, 29 kök lisans gözlemi ve Anthropic per-skill şartları ayrıştırılmıştır.
- `k02_source_policy.py`: 30/30 kaynak için fail-closed `OBSERVED_QUARANTINE`, yetkisiz terfi 0, ücretli API yetkisi doğrulaması 0.
- Harici kaynak byte arşiv kimliği, güvenlik incelemesi, hukukî yeniden kullanım ve sürüm kilidi gerçek kayıtla açılır.

## K03 — Codex / Claude Code yetenek uyumu
- İki sağlayıcı için ortak `SKILL.md` biçimi, Agent Skills upstream doğrulaması üzerinden PASS.
- GitHub'da ücretli API çağrısı olmadan CLI sürüm sorgusu ve npm yükleme kökeni ayrı makbuza alınır.
- **Sürüm sorgusu, gerçek oturum ve ücretli kullanıcı yetkisi ayrı kapılar.** Claude Code'un npm kurulum yolu üretici tarafından artık önerilmediği için native yol ileride ayrıca değerlendirilir; hiçbir installer Mac OSi üzerinde çalıştırılmadı.
- İki gerçek ücretli ajanı zorunlu kullanıcı bağımlılığına dönüştürme kararı mevcut **sıfır yeni ücretli abonelik** hedefine bağlıdır. Sahip erişimi varsa kullanım olabilir, yoksa kamuya açık beceri biçimi ve yerel ücretsiz alternatif geçerlidir.

## K04 — Üç Zülfikar simülasyonu ve exact-head CI
- `SIM1` hedef/10 kapı, `SIM2` karşıt/hata, `SIM3` bütünleşik sentetik alan korunur. Yalnız **mantıksal PASS** statüsünde kalır.
- GitHub üzerinde gerçek K01 benchmark, K02 karantina, K03 sürüm gözlemi, P03–P12 gerçek çalışma makbuzları ve exact HEAD canonical V3 SHA bağımsız teknik izdir.
- Son commit için **bütün** zorunlu workflow ve job sonuçları SUCCESS olmadan teknik PASS açıklanmaz.

## K05 — Tek sahipli GitHub karar ve OSi devir
- Zülfikar V1.3.1 kaynak kararına göre GitHub **teknik hazırlık** kapsamında ikinci insan peer reviewer gerekli değildir: C01–C03/C05–C09 makine CI, C04/C10 tek sahipli `Human Threshold`.
- Bu, bir bağımsız denetçi veya ikinci GitHub kullanıcısı yaratılacağı anlamına gelmez.
- `GITHUB_TECHNICAL_PREPARED` yalnız exact HEAD teknik CI + kaynak eşliği + geçerli owner kararına bağlıdır; `GITHUB_VERIFIED_FINISH` ve Mac OSi saha ayrı kabul sınırındadır.
- PR taslak; merge ve `main` değişikliği 0. Mac OSi kurulum, transfer, test icrası 0.

## Resmî ayrım

| Karar | Kanıt | Hüküm |
|---|---|---|
| K01/K02 teknik | CI, makbuz ve negatif test | Exact HEAD'e bağlı |
| K03 iki CLI gerçek ajan oturumu | Yetkili canlı CLI görev izi | HOLD |
| K04 GitHub teknik | Bütün iş akışları + özgün kaynak | Exact HEAD'e bağlı |
| K05 owner yetki | Kullanıcının mevcut repository owner onayı ve özgün canonical karar | HOLD |
| Resmî beceri PROVEN 12/12 | Kaynak/lisans, 5 tekrar eş değer, özgün yetki | 0/12 |
| OSi geçiş | GITHUB kapısı + ayrı Mac kabulü | HOLD |

**Hüküm:** `PASS_GITHUB_ENGINEERING` ile `GITHUB_VERIFIED_FINISH` ayrı. Kullanıcıya yeni prosedür yüklemektense tek inceleme dalı, tek owner ve SHA kanıtları kullanılır.
