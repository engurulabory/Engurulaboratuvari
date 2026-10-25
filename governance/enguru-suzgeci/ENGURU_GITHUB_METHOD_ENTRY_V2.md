# ENGÜRÜ — Tek GitHub Yöntem Girişi V2

**Konum:** `engurulabory/Engurulaboratuvari` → güncel `main`.
**Statü:** GitHub üzerindeki ana yöntem için giriş rehberi. **Yeni çekirdek, üretim motoru veya otorite içermez.**

## Kullanıcı tarafından kilitlenen kalıcı sekiz aşama

**İlk okuma:** [ENGÜRÜ Kalıcı Çalışma Disiplini™ V1](ENGURU_KALICI_CALISMA_DISIPLINI_V1.md) ve [SHA-256 kilit kaydı](ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json). Tam ifade: **Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla → Kanıtla → Sonraki ihtiyaçları belirle → İlerlet.**

**Pozitif tamamlanma dili:** Eksikleri tamamlanmış. Uçtan uca tam bitmiş. Bütün gerekli teknik kanıt ve yetkili kabulü tamamlanmış.

**PiLive güncel hedefi:** [PiLive Ürün Hedefi V4 — yeni yaratıcı kullanıcı deneyimi ve U01–U12](../plive/ENGURU_PILIVE_URUN_HEDEFI_V4.md). Kurulu eski V3.1 görünür yüzeyi başarısız bir deneme olarak değerlendirilir; yeni görsel kabul sıfırdan oluşur. Kaynak/progress/Swift teknik kazanımları bağımsız doğrulamayla yeniden kullanılır.

## Tek oturum başlangıcı

1. GitHub bağlantısını aç, `main` dalındaki **anlık HEAD** kimliğini kaydet.
2. [AGENTS.md](../../AGENTS.md) → [canonical V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) ve [kilidi](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) → ürünün özgün kabul sözleşmesini sırayla doğrula.
3. İşin türünü belirle: [Altı alan](ENGURU_ALTI_URETIM_ALANI_V1.json): CORE / ENGINE / AGENT / WEB / APP / COMMERCE. İş birden fazla alanı kapsarsa özgün şartları bir kez sayıp uygun adaptörleri birlikte uygula.
4. Kullanıcıyla ilk kurguda gerçek amaç, maliyet, risk, başarı ölçütü, karşıt örnek ve yetkiyi sabitle. [Ana Terazi](ENGURU_ANA_TERAZI_5X100_V1.md) teoriyi / tasarımı / üç farklı karşıt simülasyon ailesini ayrı değerlendirir.
5. [Dinamik tasarım döngüsü](../../tools/enguru_method_dynamic_loop_v2.py): **ilk kurgu → simüle et → puanla → eksik/ihtiyaç/gereksinim/hata/yanlış/kaynak hatasını teşhis et → kanıta bağlı düzelt → yeniden simüle et**. Temel üç tasarım turundan sonra kanıtlı açık için en çok iki ek tur; tam puan için gerçek kanıt, aksi hâlde gerekçeli HOLD.
6. [Dışarıdan karşıt senaryolar](../../tools/enguru_method_dynamic_adversarial_v2.py), özgün kabul paydası, sentetik/gerçek test ayrımı ve eylem yetkisi ayrı kontrol edilir.
7. Erişilebilir gerçek mühendislik ve GitHub CI çalıştırılır; somut kaynak, commit, job, çıktı ve SHA kaydedilir. DoneCheck™ v1.2 ve gereken Human Threshold™ yalnız canonical kabul zinciri üzerinden kullanılabilir.

## Nihai kullanıcı hedefi → GitHub → OSi devir hazırlığı → DUR sözleşmesi (25 Ekim 2026)

**Kullanıcı hedefi ve ürünün özgün kabul ID/paydasını başta sabitle.** ENGÜRÜ'nün sıralı çalışma sözleşmesi:

`KULLANICI HEDEFİ → TASARIM (3 temel, gerekirse +1/+2 kanıtlı tur, 100/100) → TEORİ (3+2, 100/100) → GITHUB KAYNAK VE TEST HAZIRLIĞI (3+2, beşli 100/100 ve exact-source CI PASS) → OSİ SALT-OKUNUR DEVİR HAZIRLIĞI (3+2, 100/100) → İNSAN KARARINDA DUR`.

**Aşama ilerlemesi:** Her aşama mevcut kaynağı puanlar, özgün eksik kontrol ID ve nedenini gösterir, yetkili yürütücü gerekli farkı üretir, gerçek yeni kanıtla yeniden puanlar. Tasarım → Teori → GitHub geçişi sıra zorunluluğudur. Teknik kaynak değişince önceki tasarım ve teori, **son GitHub kaynak SHA ile yeniden doğrulanır**. Bir tur yeni kanıt üretirse iz bırakır; dördüncü/beşinci tur özgün açık kontrolü gerçekten kapatır. En fazla beş turda açık varsa `HOLD + kesin sonraki kaynak/kanıt ihtiyacı`; otomatik 100 veya kabul kapsamı azaltması geçiş yolu değildir.

**GitHub finali:** Başarılı tasarım+teori, gerçek kod/CI ve **birbirinden farklı üç SIM1/SIM2/SIM3** kanıtlanır. GitHub PASS, OSi üzerine yazma/çalıştırma yetkisi doğurmaz. GitHub sonrasında OSi'ye geçiş **yalnız hazırlık** olarak, yerel güncel kaynak/dal, araç/disk bütçesi, korunmuş dirty worktree, taşıma kapsamı, geri alma/checkpoint, güven kökü ve tam insan karar kapsamı kontrol edilir; gerçek OSi yetkili salt-okunur fiili inceleme bu kapının zorunlu girdisidir. GitHub'ın sentetik OSi planı **gerçek native preflight değildir**.

**OSi hazırlık son kapısı:** Var olan `tools/enguru_method_three_phase_gate_v1.py` önceki üç aşama içindir. [Dördüncü bağlı politika denetleyicisi](../../tools/enguru_method_osi_handoff_gate_v1.py) onu bozmadan, exact-HEAD/CI için dış doğrulayıcı, son GitHub source hash üzerinde teori/tasarım revalidation, yerel **read-only** OSi gözlem makbuzu ve sekiz sabit devir kontrolünü üç-beş kanıtlı turda ister. Bu, uygulamayı kurmaz, dosya değiştirmez ve owner imzası üretmez. Salt politika testinin PASS'i gerçek GitHub CI veya OSi saha hazırlığı PASS'i değildir; ürünün kendi özgün doğrulayıcısı ve insanı kanıtları ayrıca onaylar.

**Son hükümler ayrı:** `GITHUB_PREPARED`, `OSI_HANDOFF_PREPARED`, `OSI_FIELD_READY`, `HUMAN_AUTHORIZED`, `VERIFIED_FINISH`. İlki gerçek exact CI ile, ikincisi gerçek read-only OSi saha reçetesiyle ve özgün geçiş kontrolleriyle, kalanları kendi gerçek yürütme/kabul yetkileriyle ilerler. Hedef sınır: **`OSI_HANDOFF_PREPARED=PASS → READY_FOR_OSI_TRANSFER_HUMAN_DECISION → DUR`**.

## Ürün ve proje için üç aşamalı 3+2 olgunlaştırma

**Çalışma sırası:** `TASARIM → TEORİ → GITHUB HAZIRLIĞI`. Her aşamada **ön değerlendirme → karşıt simülasyon/onarım → bağımsız yeniden değerlendirme**, toplam **3 tur**. Gerçek kanıt/onarım ilerlemesine bağlı **en çok 2 ek tur** ile **3–5 tur**. Her aşamanın 100/100 hedefi ayrı; eksik özgün kontrol varsa HOLD ve gerçek neden/sonraki hareket.

`TASARIM=100` ⇒ TEORİ kapısı açılır. `TEORİ=100` ⇒ GITHUB TEKNİK hazırlık kapısı açılır. Son aşamada gerçek test/regresyon ve **üç ayrı final SIM1, SIM2, SIM3** zorunludur. Beş ayrı `100/100` + gerçek SHA ve exact commit CI doğrulanınca `GITHUB_PREPARED=PASS → READY_FOR_OSI_HANDOFF → DUR`. Kurulu Mac, gerçek kullanıcı ekranı, ayrı yetki ve canonical Verified Finish bu hükmün kapsamı dışındadır.

**Bağlayıcı araç:** [Üç aşama / 3+2 politika denetimi](../../tools/enguru_method_three_phase_gate_v1.py), [Ana Terazi](ENGURU_ANA_TERAZI_5X100_V1.md), [mevcut proje doğrulayıcı](../../tools/hybrid_handoff/validate_hybrid_handoff.py). Aşama politikası veri ve puan uydurmaz; gerçek kaynak-evidence oracle işlevi zorunlu, politika PASS gerçek GitHub CI PASS değildir. Ek turda kapanan özgün kontrol kanıtı aranır; kaynak ve kanıt aynıysa `GÜVENLİ_DUR`.

## Kalıcı yöntem kuralı — proje başına beş ayrı 100/100 (25 Ekim 2026)

**Bağlayıcı hazırlık eşiği:** Her yeni ENGÜRÜ projesi için **TEORİ=100/100; TASARIM=100/100; SİM-1=100/100; SİM-2=100/100; SİM-3=100/100** ayrı kaynak ve ayrı sabit payda ile gerçekten sınanır. Beş koşul birlikte PASS olunca `GITHUB_PREPARED=PASS` yalnız ilgili exact source ve başarılı GitHub CI üzerinde raporlanabilir. Tek bir koşulun açık kalması `GITHUB_PREPARED=HOLD` gerektirir. Kabul kapsamı bu hedefe uyacak diye küçültülmez; puanlar kullanıcı beyanıyla atanmaz.

- **Genel yöntem koruması:** [Ana Terazi 5×100](ENGURU_ANA_TERAZI_5X100_V1.md) mevcut bağımsız 10-aksiyom/48-kontrol/3×144 sentetik karşıt testleriyle kendi beş puanını üretir. Her projede bunların güncel gerçek sonuçları yeniden hesaplanır.
- **Proje düzeyi kanıt:** [Mevcut Hybrid Project doğrulayıcısı](../../tools/hybrid_handoff/validate_hybrid_handoff.py) tek projede sırasıyla kaynaklı teori bağı, 20×5 tasarım kontrolü, 20×5 olumlu hazırlık sınaması, 10×10 karşıt senaryo ve 4×25 bağımsız bütünlük/tekrar/koruma sınaması yapar. Birleşik puan her gözde **genel yöntem ve proje değerlendirmesinin asgari değeri**dir. Beşinin 100 olması zorunludur; herhangi bir çalıştırma ya da genel terazi ulaşılamazsa sonuç HOLD.
- **Geliştirme turları ayrı tarihtir:** T1→T2→T3 tasarım onarım puanları (ör. 65→90→96) yalnız o turlardaki gerçek durumu gösterir ve geçmişten silinmez. Bunlar birbirinden bağımsız SIM-1/2/3 kapılarının puanı yerine geçirilmez. Yeni kritik kusur ilgili onarıma geri döner; ardından bütün beş göz yeniden sınanır.
- **GitHub hazırlık sınırı:** Kanıtlı beş 100, sabit gerçek kaynak SHA, karşıt testler ve **exact-head/exact-main CI** ile `GITHUB_PREPARED=PASS` olur. Bu sonuç **OSi'ye taşımaya hazır** anlamındadır; `FIELD_READY`, `HUMAN_AUTHORIZED`, `VERIFIED_FINISH` kendi yetkili gerçek saha kapılarında HOLD kalır. **`READY_FOR_OSI_HANDOFF → DUR`**. Yerel Mac hazırlık incelemesi/gerçek aktarım ancak ayrıca açık insan kararıyla yürütülür.
- **Özgün otorite:** Süzgeç sekiz aşama, canonical V3 SHA kilidi, ayrı ürün Work Contract/DoneCheck/Human Threshold ve değer koruma geçerlidir. Yeni çekirdek, dokuzuncu aşama veya kendiliğinden üretici izni oluşturulmaz.

## Altı alanda TRUE / deterministik karar sınırı

CORE, ENGINE, AGENT, WEB, APP ve COMMERCE için **12 ortak + 4 alan kontrolü** sabittir. Gerçek işin kabul sonucu; ilk kurguda sabitlenmiş başarı ölçütü, gerçek kaynak kimliği, bağımsız kanıt ve gerekli yetkili karar üzerinden hesaplanır. Aynı **dondurulmuş doğrulanmış girdi ve kanıt anlık görüntüsü** aynı sonuç/aynı makbuz SHA-256 üretir. GitHub CI, gerçek kaynak üzerinde çalışmış olsa da özgün altı ürünün tamamlanması anlamına gelmez.

- [Gerçek GitHub kaynak altı alan kapısı](../../tools/enguru_method_real_ci_gate_v2.py) gerçek GitHub REST commit/run verilerini okur; her alanda sabit 16 kontrolü muhafaza eder. [Mekanik regresyon ve karşıt testler](../../tests/test_enguru_method_real_ci_gate_v2.py), bozuk SHA, başka repo, başarısız/eski CI ve kendiliğinden ürün PASS'i için `HOLD` bekler.
- Kapı, mevcut V1 kabul kontrollerinin içerik özetini sabitler; özgün ID, key, required veya negative değişiminde `HOLD_FIXED_SCOPE` üretir. GitHub commit URL/repo ve tarihsel koşunun workflow kimliği ayrıca doğrulanır; bozuk girdi HOLD üretir.
- `pass_count_real_source=6`, aynı kaynak kontrolünün altı alana uygulanma sayısıdır. Özgün kanıt `unique_source_commits_verified=1` ve `unique_historical_ci_runs_verified=1` üzerinden sayılır. Tarihsel CI ayrı kayıttır; `current_commit_ci` için tamamlanmış exact-commit koşusu dışarıdan doğrulanır. Makbuz, kullanılan commit/run anlık görüntülerinin SHA-256 özetlerini taşır.
- Gerçek kullanıcının işe başlama/bitme zamanı, müdahale ve onarım sayısı, yürütme maliyeti ve hedefe ulaşma kanıtı ilgili **özgün görev kaydında** ölçülür.
- Önceden sabit üç tur sonuçları zorlama biçimde `100`e çıkarılmaz; sonuç `X/16` veya özgün kabul sözleşmesindeki gerçek paydadır. Kapsam dışı durumlarda `HOLD` ve kesin ihtiyaç verilir.
- Tek kaynaklı veya kendini onaylayan yazılım testi yalnız **makine denetimi** sayılır. Bağımsız insan / gerçek issuer / DoneCheck™ / Human Threshold™ gerektiren kararlar özgün kapılarında tutulur.
- Dış dünyadan gelen sonuçlar değişebilir; **aynı sabit girdinin ve doğrulanmış kanıtın hükmü deterministik**, yeni girdi/kanıtla yeniden hesaplama ve önceki makbuzun korunması esastır.

**Gerçek sonuç ölçüsü:** Kanıtlı olarak tamamlanan özgün görev/iş. Kontrol/test/belge adedi gerçek ürün ilerleme sayacı değildir.

## Tek çıktı sözleşmesi

```text
GOAL=<tek kabul hedefi>
DOMAIN=<CORE|ENGINE|AGENT|WEB|APP|COMMERCE|COMPOSITE>
SOURCE_MAIN=<anlık HEAD SHA>
ORIGINAL_CONTROLS=<tekilleştirilmiş ID ve sabit payda>
THEORY_DESIGN_SIM1_SIM2_SIM3=<her biri gerçek ölçülmüş puan>
THREE_REPAIR_ROUNDS=<başlangıç, değişim, sonuç, kalan HOLD>
REAL_GITHUB_TESTS=<işlem/job/commit/SHA>
INDEPENDENT_VALIDATION=<mekanizma + reviewer yetkisi ayrı>
REAL_FIELD_AND_AUTHORITY=<gerekli kendi PASS/HOLD>
NEXT_ACTION=<tek somut hareket>
VERDICT=<PASS veya delilli HOLD>
```

**Yalnız GitHub ile başlayan kullanımda OSi saha testleri** `HOLD_NOT_EXECUTED` olarak tutulur. **Gerçek kullanıcı kurgusu**, örnek simülatördeki sentetik kullanıcı girdisinden ayrıdır. GitHub ana yöntemin kod başarısı, altı alanın gerçek ürün kabulü anlamına gelmez.

## Önceki kayıt ve güncellik

- PR #221 birleşmesi: `9900f4ca7a17f99898521bdab1bfbe86784ecc07` — **tarihsel kesin kaynak**.
- Bu belgede sabitlenen SHA, sonsuza kadar güncel HEAD kabul edilmez. Güncel kaynak GitHub `main` üzerinden okunur.
- [Atlas](ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md), [Altı Alan V1](ENGURU_ALTI_URETIM_UYARLAMA_V1.md), [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) ve ürün özgün sözleşmeleri içerik otoritesidir. Bu giriş yalnız çalışma sırasıdır.

**Bitiş:** `GERÇEK HAKİKAT → 3 TUR KANITLI TASARIM → YETKİLİ GERÇEK İCRA → BAĞIMSIZ KANIT → GEREKEN KABUL → İLERLE`.

## Uçtan Uca Proje İcra Modu™ V1

Mevcut [Hybrid Contract](../mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_PRODUCT_ENGINEERING_CONTRACT_V1.md) ve [handoff doğrulayıcısı](../../tools/hybrid_handoff/validate_hybrid_handoff.py) farklı proje türleri için yeniden kullanılır. Bu mod mevcut sekiz aşama içinde hazırlık/karşıt test/devir sağlar; çalışma alanı veya ürün kabul sayacı oluşturmaz.

**T1 — Bütünsel hazırlık:** Handoff kaydına `projectPlan` ekle: version `1`, tek goal/owner, V3'ün özgün CONTROL_ID/REQUIREMENT/PASS_CONDITION/REQUIRED_EVIDENCE/VERIFIER/AUTHORITY/STATE matrisi, dependencies DAG, tools ve sürüm/probe gereksinimleri, sıfır purchasedCredits/paidApi/purchases bütçesi, Actions kanıt sınırı, inventory, target, steps, risks, humanDecisionScope ve kapsamı/verifikasyonu açık rollback. Kaynak root'u temiz, tam ancestry içeren Git çalışma ağacıdır. HEAD/origin, gerçek izlenen dosyaların SHA-256 manifesti ve gözlenen yerel refs özeti kayda bağlanır. Plan ve kabul matrisi ayrı digest ile devirde sabitlenir; değişiklikte yeniden inceleme gerekir.

**T2 — Karşıt değerlendirme ve onarım:** `project` modu normal yol ve on mutasyonla kesinti/replay/çakışma/yanlış kaynak/eksik yetki/drift/disk/araç/kısmi sonuç/rollback hazırlık eksiklerini sınar. Bunlar hazırlık girdisi mutasyonlarıdır. Ayrı regresyon testi gerçek geçici Git clone, SIGKILL, yeniden doğrulama, mevcut hedef çakışması ve yalnız test-owned staging geri alımını çalıştırır. Kaynak dışı Mac işlemi yürütülmüş sayılmaz. Kanıtlanan eksik giderilince aynı özgün şartlar yeniden sınanır. İki aynı hypothesis/intervention/evidenceDigest kaydı `GÜVENLİ_DUR_REDIAGNOSE` üretir; yeni teşhis/kanıtla ilerlenir. CLI install/fetch/checkout/publish/cleanup yürütmez.

**T3 — Bağımsız uçtan uca denetim:** Çalışma dosyalarından hesaplanan SHA-256 manifestini ayrı `git archive HEAD` mekanizmasıyla karşılaştır; bütün hazırlığı yeniden oku, değişmeyen replay sonucunu doğrula. Exact-head/exact-main CI ve gereken ayrı kimlikli reviewer kabulü kendi kanıtlarıyla değerlendirilir. Arşiv dışında kalan özel dosya, symlink/submodule veya okunamayan kaynak HOLD üretir. Kritik kusur ilgili onarım turuna geri döner.

**Sabit 5×20 rubrik:** scope, feasibility, resilience, authoritySafety, provability; her birinde dört gözlenebilir hazırlık kontrolü ×5. Çıktıdaki `preparationChecklistScore` yalnız yapısal hazırlık kapsamasıdır. Gerçek proje semantiği, saha, insan yetkisi ve teorik 100/100 kararı ayrı kaynaklı değerlendirme ister. Hazırlık puanı ürün kabulüne çevrilmez. Her tur aynı ölçütler ve gerekçeli açıklarla raporlanır.

| Kapı | Bu aracın kanıtı / kalan yetki |
|---|---|
| PREPARED | Planın gerekli yapısı, gerçek kaynak snapshot'ı ve sınırlı karşıt hazırlık testleri; kapsamlı semantik inceleme ayrıca raporlanır |
| FIELD_READY | Gerçek hedef araç/disk/izin/dizin/korunacak dosya gözlemi: yetkili yerel yürütücü bekleyen HOLD |
| HUMAN_AUTHORIZED | Tam repo/HEAD/hedef/işlem/rollback kapsamlı gerçek insan kararı: canonical doğrulama bekleyen HOLD |
| VERIFIED_FINISH | Gerçek icra + özgün test + bağımsız kontrol + canonical DoneCheck + gereken Human Threshold: yetkili zincirde HOLD |

GitHub aracı son üç kapıyı kendi JSON girdisinden PASS'e yükseltmez; ilgili kanıtlar mevcut canonical mekanizmada doğrulanır. `handoff/template` çıktısı `PASS_HANDOFF_SHAPE / PREPARED=NOT_ASSESSED` biçim doğrulamasıdır. `project` modu eksikte exit 2, sınırlı hazırlık testleri geçtiğinde exit 0 üretir; exit 0 saha finişi anlamına gelmez.

### Gerçek kaynaklı Mac OSi hazırlık örneği

[Labory örnek planı](../../tools/hybrid_handoff/labory-osi-project.example.json) frozen `c1b6281163d2a52e7cb1ae4af0d50ae9a83a22c2` kaynağı içindir. `/Users/abdal/ENGURU/Engurulaboratuvari` yalnız önerilen hedeftir; gerçek hedef, yerel envanter ve uygulama kararı HOLD. Örneğin refsDigest'i hazırlık ortamında gözlenen yerel refs kapsamıdır; başka clone'da güncel refs/source manifesti yeniden gözlenip plan yeniden incelenir. Tarihsel pin sonsuza kadar güncel main kabul edilmez.

Git ancestry, izlenen dosyalar, gözlenen yerel refs ve remote heads/tags uygulama kapsamı ayrı belirtilir. GitHub issues/PR yorumları/Actions log ve artefaktları Git clone'a dahil kayıtlar değildir; gereken scoped metadata/export ayrı envanterlenir. GitHub kayıtlarına ait URL/HEAD/CI gerçek API üzerinden ayrıca okunur. Yerel dirty/untracked/ignored dosyalar, .env, Keychain ve tarihsel imzalı makbuzlar korunur. Ayrı yeni staging ve doğrulanmış sahiplik/kapsam geri dönüşü esas alınır.

Doğrulanmış kaynak snapshot'ı ve incelenmiş plan için:

```bash
python3 -B tools/hybrid_handoff/validate_hybrid_handoff.py tools/hybrid_handoff/labory-osi-project.example.json --mode project --source-root /path/to/verified-source-snapshot
python3 -B -m unittest discover -s tools/hybrid_handoff -p 'test_*.py' -v
```

Saha emri, ancak tam kapsamlı insan kararı ve yerel yürütücü preflight kanıtından sonra mevcut Hybrid handoff ile devredilir. Aynı yöntem PiLive'ın kendi canonical kaynak/matris/owner/finalizer bağlarıyla uygulanabilir; P02 resmî kabul sayacı ayrı kalır.
