# ENGÜRÜ Ana Yöntem™ — Altı Üretim Alanı ve Kullanıcıyla Üç Turlu Simülasyon Disiplini V1

**Tarih:** 2026-10-24  
**Karar:** Önceden kabul edilen [Ana Terazi™ 5 × 100/100](ENGURU_ANA_TERAZI_5X100_V1.md) korunur. Bu belge onun altı üretim alanındaki uygulama adaptörüdür.  
**Kaynak:** [Altı alan sözleşmesi](ENGURU_ALTI_URETIM_ALANI_V1.json) · [Üç turlu sentetik onarım simülatörü](../../tools/enguru_alti_uretim_simulasyon_dongusu_v1.py).  
**Otorite:** Canonical [ENGÜRÜ Evrensel V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md), ürünün kendi kabul sözleşmesi, DoneCheck™ v1.2 ve gereken Human Threshold™.  
**STATE:** SIX_AREA_ADAPTER_SOURCE_MERGED_MAIN / REAL_USER_PRODUCT_FIELD_ACCEPTANCE_HOLD. Ana yöntem PR #221 ile `main`e birleşti; altı alanın gerçek ürün kurgu, semantik inceleme, saha pilotu ve nihai kabul kapıları ayrı kalır.

## I. Hizmet alanları — altı alan, tek ortak çalışma disiplini

| Alan | Ortak 12 kontrol üzerine özgün dört tasarım kontrolü | Kullanıcıya hizmet |
|---|---|---|
| **01 Çekirdek üretimi** (`CORE`) | API/ABI sözleşmesi ve sürüm, determinizm, migrasyon, canonical build provenance | Yeniden kullanılabilir, dayanıklı ve kaynak bütünlüğü korunmuş yazılım çekirdeği |
| **02 Motor üretimi** (`ENGINE`) | Kalıcı state/checkpoint, idempotent yan etki, runtime/kaynak bütçesi, failure recovery | Görev ve üretim işlerini güvenilir yürüten motor |
| **03 Agent üretimi** (`AGENT`) | Araç ve insan yetkisi, prompt-injection/gizli bilgi savunması, görev-sonuç eval'i, bağlam/bellek sürekliliği | Sınırları ve kanıtı belli ajan iş akışı |
| **04 Web üretimi** (`WEB`) | Erişilebilirlik/responsive, güvenlik, ihtiyaç bazlı SEO/performance, gerçek tarayıcı E2E | Güvenli, erişilebilir ve kullanılabilir web sitesi/servisi |
| **05 Uygulama/App üretimi** (`APP`) | Hedef OS/cihaz, veri yaşam döngüsü, kurulum/restart/update, platform signing/release | Çalışan native/hybrid masaüstü/mobil uygulama |
| **06 Ticari üretimler** (`COMMERCE`) | Talep/teklif, fiyat-ödeme ve finans sınırları, hukuk/veri/uyum uzman kapısı, teslim/destek/iade | Müşteriye değer sunup gerçek teslim ve uygun maliyet üretebilen ticari ürün veya hizmet |

**Tek çekirdek ve mevcut yönteme sadakat:** Bu altı alan yeni altı yönetişim motoru anlamına gelmez. Ortak `U01–U12` kontrol sözleşmesi her alana uygulanır. Her alana yalnız özgün dört adaptör kontrolü eklenir: **6 alan × (12 ortak + 4 özgün) = 96 bağlamsal kontrol uygulaması**. Genel ENGÜRÜ tasarım paydası [48 D01–D48](ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json) aynen korunur; 96 adaptör örneği o 48 şartın yerine geçmez. Her adaptörün kendi 16 ölçüt paydası sabittir.

## II. Kullanıcıyla ilk kurgu — gerçek hayattaki ilk zorunlu adım

Yeni bir işte ilk simülasyon, kullanıcının amaç, beklenti, gerçek fayda, sınırlama ve kabul koşullarıyla birlikte kurguladığı ürün **ilk taslağı** üzerinde başlar.

**İlk ortak kurgu kaydı:**
`PRODUCT_AREA; GOAL; USER_NEED; DESIGN_SCOPE; HARD_REQUIREMENTS; ACCEPTANCE_IDs; RISKS; DATA_PRIVACY; CAPABILITY_BUDGET; SOURCE_VERSION; NEGATIVE_CASES; USER_SCOPE_DECISION; DATE; NEXT_ACTION`.

Kullanıcı ilk kurguyu kabul ederse `USER_DESIGN_CONSENSUS=PASS` ancak **gerçek kullanıcı kararı kanıtı** ile atanır. Kullanıcı girdisi henüz edinilmemiş örnek çalışmalarda `USER_DESIGN_CONSENSUS=HOLD_PENDING` görünür. Modelin ürettiği taslak veya sentetik kullanıcı, gerçek insan kararı olamaz.

## III. Düzeltici üç turlu döngü — gerçek fark üreten yöntem

### Tur 1 — İlk tasarım ve simülasyon
Kullanıcıyla ilk kurgunun sabit kabul koşullarını oluştur → mutlu/olumsuz/eksik veri, yetki ve bağımlılık senaryolarını sınar → **gerçek puanı** hesaplar → açık ID'leri eksik, ihtiyaç, gereksinim, hata, yanlış sınıflarına ayırır → kök neden için gözlenen kanıt ile hipotezi ayrı kaydeder. Çıktı: `S1_SCORE; S1_GAPS; CAUSE_EVIDENCE; FIX_PLAN`.

### Tur 2 — İlk onarımlardan sonra yeniden simülasyon
S1'de belirlenen ve yetki açısından yapılabilir iyileştirmeleri uygula → değişimin gerçek kaynak/kanıt ID'sini kaydet → **aynı** özgün kabul matrisini ve karşıt testleri kullanarak yeniden simüle et → yeni puan ve açık gereksinimleri belirle. Çıktı: `S2_SCORE; RESOLVED_GAP_IDS; REMAINING_GAPS; REPAIR_PROOF`.

### Tur 3 — Son bütünleşik onarım ve bağımsız karşıt sınama
Kalan somut eksikleri gider → bağımsız/orijinal test oracle'ları ve yeni risk karşıt vakalarıyla yeniden simüle et → `S3_SCORE` hesapla → beşli Ana Terazi'nin Teori/Tasarım/Sim1/Sim2/Sim3 koşullarını, özgün sabit payda ve ayrı makbuzlarıyla değerlendir. Çıktı: `S3_SCORE; FALSE_PASS_COUNT; DIFFERENCE_FROM_S2; FINAL_THEORETICAL_GATE`.

**İlerleme hükmü:** Üç tur sonunda hedef `100/100`. Bir turda erken 100 bulunduğunda kalan turlar güçlü karşıt/bozma/regresyon testleri için kullanılır; tekrarlı aynı PASS gerçek yeni ilerleme sayılmaz. Üç tur sonunda 100'e ulaşılamazsa `HOLD_DESIGN_GAPS` ve kesin sonraki onarım aktarılır; 100 puanı zorla üretilmez. Yeni kanıtlı kök neden veya yeni uygulanabilir müdahale ortaya çıktığında aynı korunmuş kabul kaydı üzerinden sonraki plan yetkiyle belirlenir.

**Simülasyon kalitesi ölçüleri:** İlk kullanıcı kurgusunun hakikati; özgün kabul ölçütü kapsaması; olumlu ve negatif test oracle'ı; hata ve kök neden ayrımı; müdahalenin puan artışını gerçekten üretmesi; sabit payda; regressions ve güvenli durma; bağımsız doğrulama; güvenlik/maliyet/insan yetkileri; gerçek uygulamadan ayrılmış doğruluk beyanı.

## IV. GitHub'daki teorik prova — gerçek kullanıcı icrası sayılmaz

[Test simülatörü](../../tools/enguru_alti_uretim_simulasyon_dongusu_v1.py), altı alanın her birinde 16 özgün adaptör kontrolünün sabit paydasına karşı şu **sentetik tasarım eğitim senaryosunu** yürütür:

| Tur | Planlanan yapısal kapsam | Aranan iyileştirme |
|---|---|---|
| **1 — İlk taslak** | 10/16 → **62,5/100** | 6 eksik kontrol kimliğini tespit |
| **2 — Düzeltme 1** | 14/16 → **87,5/100** | 4 ayrı farkın giderildiğine dair before/after kanıt |
| **3 — Düzeltme 2** | 16/16 → **100/100** | Son 2 farkı kapat; 48 ayrı kontrol bozma denemesini yakala |

Altı alanda toplam **18 ayrı simülasyon turu**, **12 tanımlı onarım olayı** ve **288 karşıt bozma denemesi** oluşur. Bunlar yalnız makine tarafından çalıştırılırsa kanıt sayılır; gösterilen örnek puanlar önce bir tasarım beklentisidir. Gerçek kullanıcı ortak tasarım onayı veya 6 üretim alanının saha başarısı olarak sunulmaz.

### Genel ana terazi ile iki farklı ölçeğin korunması

**A — Evrensel hazırlık:** `THEORY=100/100; DESIGN=100/100; SIM1=100/100; SIM2=100/100; SIM3=100/100` ana kaynağının kendi makbuzuyla ispatlanır.

**B — Alan uyarlaması:** Her alanda `S1 < S2 < S3=100`, gerçek açıklar tanımlı ve onarımlar izlenebilir, negatif testler PASS. Bu, evrensel beşli teraziyi ikinci kez saymaz.

**C — Gerçek ürün başlangıcı:** Kullanıcıyla fiilî ortak ilk kurgu + ürünün özgün canonical kabulü, gerçek iş yürütmesi, test, bağımsız doğrulama, gereken imza ve saha kanıtı kendi kapılarından geçer.

## V. Aşama 2–4 korunmuş geçiş planı

- **Aşama 2, bağımsız tasarım incelemesi:** Ana Terazi ve altı adaptörün kaynak, test kalitesi, bağımsız scorer, insan katılımı ve kapsam farkları gerçek reviewer tarafından incelenir. Bu karar ancak gereken yetkili mekanizma ile verilir.
- **Aşama 3, gerçek GitHub + OSi pilotu:** Kullanıcı tarafından seçilen bir gerçek üretim vakasında doğru alan adaptörü kullanılır; kayıtlı user design consensus ve GitHub/OSi icra, test, restart, kanıt zinciri gözlenir. Ürün sözleşmesine göre makine yetkisi sağlanır.
- **Aşama 4, kanıtlı olgunluk ve resmî kapanış:** Altı alan hedefi üzerinde gerçek kullanıcı işi ve geçerli kanıt kapsamı ölçülür. Gerekli bağımsız doğrulayıcı, DoneCheck v1.2, Human Threshold ve yetkili nihai kabul ile `VERIFIED_FINISH → BITTI_DUR` yürütülür.

**Kalıcı sabit hedef:** Teori ve tasarımda sağlam karar, gerçek icrada tamamlanmış kanıt, saha üzerinde yetkili gerçek bitiş. `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT`.


### Simülasyon teşhis kalitesi — makbuz sözleşmesi

Üç turlu teorik prova, tespit edilen açıklar için `diagnostic` içinde `CONTROL_ID`, `classification`, `observation`, `root_cause_status`, `required_change` kaydeder. **Beş sınıf birlikte aranır:** `missing` (eksik), `need` (ihtiyaç), `requirement` (gereksinim), `error` (hata), `incorrectness` (yanlış). Her uygulanmış tasarım onarımına `before/after`, kaynak ve kontrol kimliği bağlanır.

Örnek kurgunun eksik veri sınıflaması sentetik fixture'larda deterministik bir varsayımdır; sahada gerçek kök neden tespiti için gerçek gözlem ve ayrı doğrulama gerekir. Onarımın puana etkisi her turda sabit 16 kontrol paydasına karşı yeniden hesaplanır.
