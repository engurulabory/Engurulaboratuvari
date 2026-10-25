# ENGÜRÜ Ana Terazi™ V1 — Teori / Tasarım / Üç Ayrı Simülasyon

**Tarih:** 2026-10-24  
**İş amacı:** Gerçek mühendislik icrasından önce ENGÜRÜ çalışma yöntemlerinin teorik temelini beş ayrı ölçümle 100/100 seviyesinde hazırlamak.  
**Sabit kaynak:** [AGENTS](../../AGENTS.md), [V3 canonical](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md), [V3 SHA lock](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json), [48 sabit kontrol](ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json).  
**İcra:** [ENGURU Ana Terazi doğrulayıcı](../../tools/enguru_ana_terazi_v1.py) ve [GitHub Design48 workflow](../../.github/workflows/enguru-design48-theoretical.yml).  
**Kanıt türü:** Gerçek GitHub'da çalıştırılan, sentetik tasarım karşıt sınamaları. Native Mac/saha/üretim doğrulaması değildir.

## Beş gözlü ana terazi

Her gözün puanı **ayrı veri, ayrı payda, ayrı gerekçeden hesaplanır**. Beş şartın hepsi tam puansa `THEORETICAL_PREPARATION_GATE=PASS`; her açık için gerekçeli `HOLD`.

| Göz | Kaynak / kabul sözleşmesi | Puan yöntemi | Başarı eşiği |
|---|---|---|---|
| **1. TEORI** | Kilitli V3 ve 10 temel sistem önermesi | 10 önerme × 10 puan; her birine 1 karşıt bozulma denemesi | **100/100** ve **10/10 bozulmayı yakalama** |
| **2. TASARIM** | Aynı D01–D48 ID'li 48 kontrol | 48 × 5 bağımsız kanıt kapısı: kimlik, sözleşme, olumlu oracle, karşıt oracle, muadil kaynak izleme | **240/240 = 100/100** |
| **3. SIMULASYON-1** | Gerçek uygulamadan ayrılmış sentetik tasarım oracle'ları | 48 × (olumlu + olumsuz + eksik giriş) | **144/144 = 100/100** |
| **4. SIMULASYON-2** | Aynı bağımsız puanlayıcıya karşı hasarlı kaynaklar | 48 × (olumlu fixture tahrifi + peer URI tahrifi + oracle binding tahrifi) | **144/144 = 100/100** |
| **5. SIMULASYON-3** | Metamorfik skor ve hakikat koruma sınamaları | 48 × (beyan puanı değişse de skor sabit + baz puan bozulursa skor azalır + sahte saha PASS skoru düşürür) | **144/144 = 100/100** |

**Zorunlu koşul:** `THEORY=100 AND DESIGN=100 AND SIM1=100 AND SIM2=100 AND SIM3=100`.

### Teori — 10 aksiyom

1. T01 — Canonical V3 gerçek SHA-256 ile kilitle eşleşir.
2. T02 — ENGÜRÜ Süzgeci™ sekiz aşaması aynı kaynakta korunur.
3. T03 — Tek ana hedef ve kabul şartları birlikte tanımlıdır.
4. T04 — Kabul paydası 12 alan × 4 kontrol = 48, başlangıç 211/240 sabittir.
5. T05 — Gerçek icra/kanıt/otorite muhasebesi üç ayrı alandır.
6. T06 — Bağımsız reviewer ile producer ayrımı fail-closed işletilir.
7. T07 — Simülasyon ile gerçek yürütme ve saha gözlemi ayrıdır.
8. T08 — Gizli bilgi ve maliyet riski `BLOCKED_RISK` üretir.
9. T09 — Teorik kararlar, 48 kaynak/oracle/peer bağına izlenebilir.
10. T10 — Human Threshold™, DoneCheck™ ve yetkili finiş teorik PASS'tan ayrı tutulur.

**Teori bozulma testi:** On aksiyomun her biri için bir *tekil* kritik müdahale yapılır. Yetkisiz kaynak kilidi, eksilen Süzgeç aşaması, yanlış ana hedef, bozulan payda, karışan icra muhasebesi, bağımsız reviewer atlaması, sahte saha PASS, güvenlik devresi, peer kayması, erken Verified Finish tek tek bulunmalıdır.

### Yöntem — tek giriş, beş çıktı, tek ilerleme kararı

```text
HAKİKAT / CANONICAL SHA
       ↓
TEORİ 10/10 + 10 karşıt aksiyom denemesi
       ↓
TASARIM 48 × 5 = 240/240
       ↓
SİM-1 144/144 → SİM-2 144/144 → SİM-3 144/144
       ↓
BİRLEŞİK TEORİK HÜKÜM (5 × 100/100 veya HOLD)
       ↓
AŞAMA 2: BAĞIMSIZ TASARIM İNCELEMESİ
       ↓
AŞAMA 3: GERÇEK GITHUB + OSi PİLOTU
       ↓
AŞAMA 4: KANITLI OLGUNLUK, YETKİLİ KABUL
       ↓
VERIFIED_FINISH → BITTI_DUR
```

### Kalıcı beşli 100/100 kuralının proje icrasına uygulanması (25 Ekim 2026)

**Her proje için hedef:** `TEORI=100/100 AND TASARIM=100/100 AND SIM1=100/100 AND SIM2=100/100 AND SIM3=100/100`. Birleşik beşli hazırlık geçişi **ancak her biri gerçekten hesaplanmış 100 puanda** mümkündür. Farklı ölçütlerin ortalaması, düşük puanı maskeleyerek geçiş sağlamaz.

Bu belgedeki beşli sentetik **ortak yöntem Ana Terazisi** ile ilgili projenin **özgün beşli hazırlık değerlendirmesi** birbirinden ayrı ölçülür. İlgili [Uçtan Uca Proje İcra Modu](../../tools/hybrid_handoff/validate_hybrid_handoff.py) genel beş puanı kaynakta yeniden çalıştırır, proje düzeyinde teori/şema bağı, gerçek Git snapshot, yapısal tasarım, olumlu senaryo, karşıt senaryolar, bağımsız arşiv ve replay kaynak kanıtlarını değerlendirir. Her göz için asgari puan kullanılır. Güncel kanıt yetersizse HOLD ve özgün eksik gösterilir.

**Üç düzeltici tur**, üç ayrı simülasyon ailesinin yerine geçmez: T1/T2/T3 tarihsel onarım ölçümleri başlangıç kanıtı olarak kalır. Düzeltme ardından **beş kapının tamamı yeniden** sınanır; kritik başarısızlıkta ilgili onarım turuna dönülür.

**GitHub hazırlığı 100:** Beş ayrı 100/100 + gerçek karşıt test + exact SHA + ilgili GitHub CI PASS → `GITHUB_PREPARED=PASS` ve **`READY_FOR_OSI_HANDOFF → DUR`**. Bu hüküm gerçek Mac kurulum, aktarım, insan yetkisi veya canonical Verified Finish değildir; o kapılar gerçek saha ve ayrı açık insan kararıyla ilerler.

### Dördüncü uygulama-koruma kapısı — OSi geçiş hazırlığı (25 Ekim 2026)

**Nihai yürütme sırası:** Kullanıcının özgün ürün hedefi → **TASARIM 100** (3+2 tur) → **TEORİ 100** (3+2 tur) → **GITHUB 5×100** (3+2 tur + üç ayrı final SIM oracle + exact CI) → **OSi geçiş hazırlığı 100** (3+2 tur) → **DUR**. Bu, Ana Terazi'nin beşli teorik ölçümünün üzerine **yeni puan türü ekleyen bir beşli terazi değildir**; OSi son adımı, mevcut kaynakları ve yetkileri koruyan **ayrı operasyonel devir planı kapısıdır**.

Gerçek read-only Mac envanteri, GitHub HEAD'den taşınacak exact içerik/SHA, değişmiş yerel dosyalar ve sahipliği, disk/araç, sağlam rollback/checkpoint, yetkili kapsam ve yerel güven önkoşulları **sekiz sabit OSi kontrolüne** bağlanır. Tüm kontroller 100 kanıtlanmadan `OSI_HANDOFF_PREPARED=HOLD`. GitHub PASS olsa dahi Mac aracı/güncel source gözlemi olmadığı sürece HOLD.

Mevcut [üç aşamalı denetim](../../tools/enguru_method_three_phase_gate_v1.py) korunur; [dördüncü OSi handoff denetimi](../../tools/enguru_method_osi_handoff_gate_v1.py) ona bağlanır. Araç yalnız kaynak/evidence callback sözleşmesini doğrular; gerçek teknik düzeltmeler özgün yürütücü ve testlerle yapılır. Final çıktısı OSi'de kod icrası/aktarımı, canonical state yazımı veya Human Threshold değildir. **Gerçek OSi ön uçuşu ve açık kapsamlı insan kararı** kendi kapısında kalır. `OSI_HANDOFF_PREPARED=PASS → İNSAN KARARINDA DUR`.

### Kalıcı üç aşamalı olgunlaştırma sırası — TASARIM → TEORİ → GITHUB (25 Ekim 2026)

**Yeni bağlayıcı sıra:** Başlangıçta ürünün özgün kullanıcı hedefi ve kabul paydası korunur. Üç ardışık **olgunlaştırma aşaması** ayrı yürütülür:

**AŞAMA 1 · TASARIM:** Ürün/proje taslağını hazırla; gerçek özgün kabul kriterlerine göre puanla; gözlemlenen eksik/yanlış/ihtiyacı tespit edip kaynaklı onar; üç amaçlı denetim turunda tasarımın bütünlüğünü yeniden simüle et ve yeniden puanla. Hedef `TASARIM=100/100`.

**AŞAMA 2 · TEORİ:** Tasarım kapısı kanıtlı tam puan olduğunda dayanak hipotezleri, canonical sözleşme, mimari/karar/bağımlılık ispatını ayrı karşıt kurallarla üç tur incele, onar, yeniden puanla. Hedef `TEORİ=100/100`. Teori bulgusu tasarımı etkiliyorsa tasarımın ilgili kapılarını yeniden değerlendir.

**AŞAMA 3 · GITHUB HAZIRLIĞI:** Kaynak/uygulama planı, entegrasyon, regresyon ve geri dönüşü üç amaçlı turda doğrula ve kanıtlı teknik farkı tamamla. Ardından **ayrı üç sabit simülasyon ailesini** `SIM1`, `SIM2`, `SIM3` özgün test/oracle ve sabit payda ile çalıştır. Teori ve tasarım da kaynak değişikliğinden sonra yeniden ölçülür. `TEORİ=100`, `TASARIM=100`, `SIM1=100`, `SIM2=100`, `SIM3=100` ve exact kaynak/CI başarıyla `GITHUB_PREPARED=PASS → READY_FOR_OSI_HANDOFF → DUR`.

**Tur kuralı:** Her aşamada **temel 3 tur**: (1) mevcut durumun ölçülmesi, (2) karşıt teşhis / kaynaklı onarım, (3) farklı oracle ile bağımsız uçtan uca göz. Tam puana ulaşılamazsa yalnız **gerçek yeni kanıt/onarım farkı** için tur 4 ve gerekirse tur 5 uygulanır. `MAX_ROUNDS=5`; beşinci turda kalan açık kaynak için `HOLD + eksik ID + kesin sonraki ihtiyaç`. Aynı kaynak ve aynı kanıtı yineleyip puan yükseltme, kapsam küçültme veya sonuç uydurma geçersizdir.

**Tur ≠ simülasyon ailesi:** Her aşamanın üç-beş **onarım/değerlendirme turu**, GitHub finalinin üç **bağımsız SIM1/2/3** ailesinin yerine geçmez. Final SIM3 yalnız ayrı kaynak–adaptör–çıktı/oracle ispatıyla 100 olur; TASARIM/TEORİ 100 olduğu için kendiliğinden 100 olmaz.

**Makine denetimi:** [Mevcut yönteme bağlı üç aşama / 3+2 tur kapısı](../../tools/enguru_method_three_phase_gate_v1.py) bağımsız evaluator sonuçlarının kontrol ID, SHA ve tur ilerlemesini denetler. Kendi sonucu **POLICY_REQUIRES_EXTERNAL_CI** seviyesindedir; gerçek özgün kaynak testini ve exact GitHub CI'ı yalnız onların özgün yetkili doğrulayıcıları kanıtlar. P01/P02/DoneCheck/Human Threshold ve gerçek Mac kurulum yetkisi ayrı kapılardadır.

### Gerçeklik/puan korunumu

- `THEORY=100` yalnız seçilmiş **10 mimari önermenin iç tutarlılığına** karşılık gelir; ampirik bilimsel teorinin doğrulanması anlamına gelmez.
- `DESIGN=100`, ilgili 48 sözleşmenin sentetik oracle ve kaynak izi yeterliliğidir; 48 ürün davranışının sahada başarılı olduğuna dair hüküm değildir.
- `SIM1/2/3=100`, sırasıyla üç **farklı sentetik test kümesinin** denetim çıktısıdır; modele veya gerçek kullanıcı ortamına karşı kör deney / bağımsız insan değerlendirmesi değildir.
- `GITHUB_CI=PASS`, gerçekte koşmuş tasarım simülasyonunu kanıtlar; aynı kapsamda `OSI_FIELD=HOLD` olabilir.
- `INDEPENDENT_DESIGN_REVIEW=HOLD`, `DONECHECK=HOLD`, `HUMAN_THRESHOLD=HOLD`, `VERIFIED_FINISH=HOLD` ayrı kabul kapılarıdır. Tarihsel PR #221 için `GITHUB_MAIN_MERGE=PASS_20261025`; sonraki her PR'nin merge durumu ayrı güncel GitHub kaynağından doğrulanır.
- Kaynak kilidi, V3, tüm ürün canonical sözleşmeleri ve özgün 48 kontrol ID'si korunur.
- Puanlayıcı `candidate_design_points` alanından puan almaz; puanı puanlayıcının doğrulanmış beş şartı belirler.
- Önceki 24'lü V1 karar simülasyonu ve V2 tasarım denetimi bu ana teraziye **ek olarak** CI'da yaşamaya devam eder.

### Başarısızlık halinde ileri hareket kuralı

Beş alandan herhangi biri **100'ün altındaysa** `THEORETICAL_PREPARATION_GATE=HOLD`: eksik aksiyom/ölçüt/scenario ID ile kaydedilir, mevcut kaynak en küçük doğrulanabilir farkla iyileştirilir, beş puan **yeniden** hesaplanır. Tekrarlanan aynı test, kanıt değeri olmayan bir puan artışı üretmez.

**Sabit bitiş iddiası:** Teorik PASS, gerçek iş/kanıt/otorite tamamlanmasına dönüştürülerek resmî kabul üretir. Bu belgenin tek başına `VERIFIED_FINISH` veya imza verme yetkisi bulunmaz.


## VI. Kalıcı kullanım alanları ve simülasyon onarım döngüsü — 24 Ekim 2026

Kullanıcı tarafından kapsamı sabitlenen hizmet alanları: **Çekirdek üretimi, Motor üretimi, Agent üretimi, Web üretimi, Uygulama/App üretimi ve Ticari üretimler**. Bunlara yönelik ortak yöntem ve özgün tasarım adaptörleri [Altı Üretim Alanı V1](ENGURU_ALTI_URETIM_UYARLAMA_V1.md) ile [makine-okunur altı alan sözleşmesinde](ENGURU_ALTI_URETIM_ALANI_V1.json) kayıtlıdır.

**Kullanıcıyla ilk kurgu esastır:** gerçek işin ilk tasarım/simülasyonuna kullanıcı ihtiyacı ve kabul sınırlarıyla başlanır. **Simülasyon döngüsü** şu sırayla işler:
`KULLANICIYLA İLK KURGU → SİMÜLASYON 1 → PUANLA → EKSİK/İHTİYAÇ/GEREKSİNİM/HATA/YANLIŞ TESPİTİ → ONARIM → SİMÜLASYON 2 → YENİDEN PUANLA/ONAR → SİMÜLASYON 3 → 100/100 VE KARŞIT DOĞRULAMA → TEORİK KAPI`.

Bu üç döngü **ardışık düzeltici tasarım turlarıdır**. Yukarıdaki beşli Ana Terazi'deki üç **ayrı simülasyon test ailesi** ise sabit hazırlık güvencesi oluşturur; amaçları farklıdır ve her iki kanıt türü ayrı makbuzda sayılır.

Her turda yalnız gerçekten kapanan özgün kontrol ID'leri puanı artırır. Üçüncü turun sonucu 100 altındaysa `HOLD` ve kesin eksik/onarım kanıtı verilir; sonraki hakiki müdahale yetkili çalışma planına alınır. Sentetik kullanıcı ilk kurgusu gerçek onay oluşturmaz; kullanıcı kararı/bağımsız inceleme/OSi/DoneCheck/Human Threshold ayrı kapılarda kalır. Mevcut canonical V3 ve 48 kontrolün paydası korunmuştur.
