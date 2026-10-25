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

### Gerçeklik/puan korunumu

- `THEORY=100` yalnız seçilmiş **10 mimari önermenin iç tutarlılığına** karşılık gelir; ampirik bilimsel teorinin doğrulanması anlamına gelmez.
- `DESIGN=100`, ilgili 48 sözleşmenin sentetik oracle ve kaynak izi yeterliliğidir; 48 ürün davranışının sahada başarılı olduğuna dair hüküm değildir.
- `SIM1/2/3=100`, sırasıyla üç **farklı sentetik test kümesinin** denetim çıktısıdır; modele veya gerçek kullanıcı ortamına karşı kör deney / bağımsız insan değerlendirmesi değildir.
- `GITHUB_CI=PASS`, gerçekte koşmuş tasarım simülasyonunu kanıtlar; aynı kapsamda `OSI_FIELD=HOLD` olabilir.
- `INDEPENDENT_DESIGN_REVIEW=HOLD`, `MAIN_MERGE=HOLD`, `DONECHECK=HOLD`, `HUMAN_THRESHOLD=HOLD`, `VERIFIED_FINISH=HOLD` ayrı gerçek kabul kapılarıdır.
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
