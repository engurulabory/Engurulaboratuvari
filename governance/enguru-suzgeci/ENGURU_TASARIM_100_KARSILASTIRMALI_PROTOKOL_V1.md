# ENGÜRÜ Çalışma Yöntemleri™ — Karşılaştırmalı Tasarım Güçlendirme Protokolü V1
**Tarih:** 2026-10-24  
**Kapsam:** Tasarımın 88/100 başlangıç değerlendirmesinden, dondurulmuş 48 ölçüt kapsamında teorik 100/100 adayına götürülmesi.  
**Durum:** DESIGN_REVIEW_CANDIDATE / INDEPENDENT_DESIGN_REVIEW=HOLD / FIELD_VERIFIED_FINISH=HOLD  
**Otorite:** [AGENTS](../../AGENTS.md) → [Kilitli Evrensel V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) + [V3 LOCK](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) → ürünün özgün canonical kabul sözleşmesi → DoneCheck™ v1.2 + gereken Human Threshold™.  
**Envanter:** [24 yöntem/yetenek atlası](ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md) ve [örnek simülasyon](ENGURU_YONTEM_UCTAN_UCA_SIMULASYON_V1.md).  
**Özgünlük:** Bu belge hiçbir mevcut çekirdeği, otoriteyi, ürün sayacını, kaynak kilidini veya zorunlu kabul koşulunu değiştirmez. Yalnız bunlara uygulanabilir tasarım gereklerini ekler.

## A. Ölçümün anlamı ve değiştirilemeyen sınırlar

1. Önceki **88/100**, 12 alanda 48 alt ölçütün yargısal/mimari başlangıç değerlendirmesidir; gerçek test verisi veya uluslararası sertifika değildir.
2. Bu protokolün **100/100 tasarım koşulu**, D01–D48'in tümünün uygulanabilir tasarım kuralı, gözlenebilir kabul çıktısı, reddedici karşıt durum ve kaynak ilişkisiyle **tam olarak tanımlanmasıdır** (48/48). Bir kritik kural tanımsızsa skor 100 değildir.
3. Puan **yalnız teorik kapsama** puanıdır. Kodun/uygulamanın gerçekten çalıştığı, 48 kapının sahada ispatlandığı, 100/100 operasyonel başarı veya uluslararası muadillere denk performans anlamına gelmez.
4. Rubrik bu sürümde dondurulur; puanı artırmak için payda düşürülmez, yinelenen test/PR yorumu ek puan üretmez; yeni ölçüt gerekiyorsa sonraki sürüm, fark kaydı ve yetkili inceleme kullanılır.
5. Kabul zinciri: **DESIGN_CANDIDATE_PASS → INDEPENDENT_DESIGN_REVIEW → GITHUB_EXACT_HEAD_EVIDENCE → GERÇEK_İCRA → GERÇEK_SAHA → DONECHECK → HUMAN_THRESHOLD (gerekiyorsa) → VERIFIED_FINISH**. Bu aşamadaki ana hareket ilk kapıdır.

## B. Uluslararası yöntemlerle karşılaştırma — hasat, kopya veya sertifikasyon değil

Dış belgelerin gerçek içeriği ile ENGÜRÜ'ye taşınan *yöntem ilkesi* ayrı gösterilir. Bunlar kıyas referanslarıdır; ENGÜRÜ'nün uluslararası bir kuruma akredite olduğu iddia edilmez.

| Referans | Dayanak mekanizma | ENGÜRÜ'de korunacak/mimarileştirilecek karşılığı | Eksik kapama ID |
|---|---|---|---|
| [NIST AI RMF / Playbook](https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook) | Govern, Map, Measure, Manage | Niyet/etki/risk kayıtları, insan etkisine göre risk eşiği ve izlenebilir karar | D02, D04, D39, D40 |
| [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) | Güvenli geliştirmeyi SDLC'ye yayma | Tehdit/gizli bilgi/yetki preflight'ı, test+rollback+gereken kontrol | D13, D32, D37, D38 |
| [DORA delivery metrics](https://dora.dev/guides/dora-metrics/) | Teslim akışı + hata/yeniden iş metrikleri | Kaynak commit'ten sonuç teslimine lead time, failure/rework, karşılaştırılabilir baz değer | D18, D46, D47 |
| [SLSA v1.2](https://slsa.dev/spec/v1.2/) | Artan tedarik zinciri güvenceleri ve provenance | Kaynak/commit/toolchain/artifact/üreten aktör bağlama; hash tek başına yeterli sayılmaz | D10, D27, D34 |
| [OpenSSF Scorecard](https://openssf.org/projects/scorecard/) | Otomatik güvenlik kontrol/puanlama | Kod kaynak/güvenlik ve izin açıklarını özgün kontrol ID'leriyle takip | D29, D37 |
| [LangGraph Persistence](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/persistence.mdx) | Checkpoint ile devam; store ile kalıcı bilgi ayrımı | TASK_ID + fingerprint + checkpoint + replay idempotency + yan etki koruması | D19, D42, D43 |
| [Anthropic Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) | Kod, model ve insan grader; görev sonucuna bağlı eval | Test oracle, golden/negative, false PASS, hold karşıt vakaları; grader bağımsızlığı | D23, D24, D31, D35 |
| [Google SRE / SLO](https://sre.google/workbook/implementing-slos/) | Hizmet seviyesi göstergesi/hedefi ve ölçüm döngüsü | Schedule güvenilirliği, recovery, insan sürtünmesi ve ölçülmüş kullanıcı hizmet kalitesi | D44, D46, D48 |

**Karşılaştırma hükmü:** Seçilmiş 8 kamuya açık uygulama ilkesi, ENGÜRÜ'nün 48 ölçütüne tasarım düzeyinde eşlenmiştir. Canlı performans ve standart uyum sertifikası bu kapsam dışında kalır.

## C. Önceki 88/100 durumunun 100/100 teorik adayına taşınması — 12 kapanış farkı

| GAP | Başlangıçta açık kalan tasarım boyutu | Yeni açık ve sınanabilir tasarım kuralı | İlgili D kontrolü |
|---|---|---|---|
| G01 | Faydanın yalnız hedef olarak kalması | Görev sözleşmesi kullanıcı değeri, başlangıç ölçümü, hedef etki, gözlem kaynağı ve ölçüm zamanı taşır | D04, D46–D48 |
| G02 | Dil/kuralın ürün yüzeyleri arasında kayması | Her adaptör canonical sürüm/ref/SHA/uygulama kapsamını bildirir; uyumsuzlukta HOLD_SOURCE_DRIFT | D08, D11, D14–D16 |
| G03 | Bütünleşik icrada kimlik/rol bulanıklığı | Control Plane, ürün kaynağı, GitHub CI, OSi saha ve DoneCheck yetkileri ayrı producer/verifier/owner alanları | D09–D12, D25–D28 |
| G04 | Kaynağın güncelliği ve izinler | HEAD, artifact, toolchain, actor, policy, privacy, egress ve costBound kilitli preflight; sapmada güvenli dur | D10, D13, D17, D37–D40 |
| G05 | Kurgu ve simülasyonun ölçüm oracle'ı | Her vaka sabit INPUT + EXPECTED_VERDICT + FORBIDDEN_CLAIM + verifier + negatif karşıt durumu içerir | D20–D24 |
| G06 | Tekrar puanla yöntemiyle hedefin kayması | 48 sabit ID; üç tur (baseline, düzeltme, adversarial); aynı deneme yeni kanıt üretmeyince yöntem değiştir | D19–D24 |
| G07 | Gerçek icranın salt PR yeşiline indirgenmesi | Gerçek kaynak/artefakt/saha/yan etki ayrı kapılar; kaynak SHA ve gerçek executor kimliği gerekir | D25–D28, D33 |
| G08 | Bağımsız doğrulama otoritesi | Producer ve reviewer ayrılığı; farklı mekanizma/kimlik ve kanıt güncelliği, mismatch → HOLD | D29–D36 |
| G09 | Güvenlik, maliyet ve insan eşiği | Fail-closed sınırlar, kalıcı yetki değil görev-kapsamlı izin, harcama limiti ve gizli bilgi dışarı akış kapısı | D37–D40 |
| G10 | Yarım kalmış işlem ve restart | İdempotency key, checkpoint, audit head, kesintiden sonra resume ve yan etki/çift-yazım kontrolü | D41–D44 |
| G11 | Kullanıcı yükü ve otomasyon hedefi | Otomasyon vs insan eşiği ayrımı; tek kullanıcıya özet durum + kesin sonraki düğme/değer | D45, D48 |
| G12 | Sonuç puanlamasının erken PASS riski | DESIGN_SCORE, EXECUTION, EVIDENCE, AUTHORITY, USER_IMPACT ayrı; son hüküm yalnız canonical DoneCheck | D03, D32–D36, D47 |

Bu kurallar **ileride kodla uygulanacak yeni görevler değil**, mevcut yöntemlerin birleşik tasarım sözleşmesine getirilen tanımlar ve doğrulama oracle'larıdır. Gerçek bağlama uygulama ve kanıt toplama sonraki aşamadır.

## D. Makine-okunur 48/48 tasarım matrisi

Yan belge [ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json](ENGURU_TASARIM_48_KONTROL_MATRISI_V1.json) D01–D48'i şu sabit şemayla tanımlar:

`id, area, statement, pass_design_condition, reject_case, implementation_scope, canonical_source, peer_refs, design_status`

12 alan × 4 özgün kontrol = 48 kontrol. **Her ölçüt için tek ID.** İlk puan tabanı 88/100 korunur; sonraki aday puan, tanımlı kontrollerden ayrıca türetilir.

## E. Simülasyon protokolü — üç tur, değiştirilmeyen test kümesi

**Tur 1 / BASELINE:** 48 kontrol ve 12 GAP sınıfını tarar, eksikleri `DESIGN_HOLD` olarak kaydeder. Başlangıç gösterimi 88/100 tarihsel uzman değerlendirmesidir; bu turda yeniden oluşturulmuş gerçek saha ölçümü değildir.

**Tur 2 / DESIGN_REPAIR:** GAP G01–G12'ye karşılık gelen açık şartlar matriste tam tanımlıysa, dondurulmuş payda 48/48 korunarak `THEORY_CANDIDATE_PASS` hesaplanır. İlgili durum ve kaynaklar her kontrolde yer almalıdır.

**Tur 3 / ADVERSARIAL:** Önceden tanımlı ve tekrar oynatılabilir **24 karşıt + olumlu test oracle'ı** sabit girişleriyle değerlendirilir. Negatif testlerde PASS üretimi yasaktır; geçerli olumlu durumda doğru sınırlı PASS, sahayı temsil etmeyen bir design PASS olabilir. Kritik yanlış PASS=0, yetki atlama=0, yinelenen ID=0 şartları.

Simülasyon tekrarları yeni puan üreten iş sayısı değildir. Bir testin varlığı otomatik çalıştırıldığı iddiası olmaz. Kaynak/PR/saha/otorite kapıları ayrıca raporlanır.

**Kritik ilkeler:** 
- Bir `design_status=SPECIFIED`, çalışır `implementation_status=PASS` oluşturmaz.
- Gerçekte uygulanmamış bağımsız review `NOT_EXECUTED` olur.
- Eşleşmeyen kaynak/HEAD/SHA `HOLD_SOURCE_DRIFT` olur.
- Başarılı simülasyon, kullanıcı üzerinde gözlenmiş faydaya dönüşmez.
- Reviewer, üreticiyle aynı kimlikteyse `INDEPENDENT_REVIEW=HOLD`; ayrı test mekanizması mümkünse kendi kapsamıyla kaydedilir.
- Aynı `CONTROL_ID` bir kez sayılır, skor paydası daima 48'dir.

## F. Tasarım 100/100 ilanı için geçiş kapısı

1. 48 özgün D kimliğinin tamamının yükümlülük + başarı şartı + negatif durum + kaynak bağı mevcut.
2. G01–G12 tasarım farkının her biri ilgili D kimliğiyle eşlenmiş.
3. 8 uluslararası muadilin doğrulanmış kamu kaynağına referans ve sınırlı ENGÜRÜ eşleştirmesi var.
4. 24 oracle senaryosunun üç turlu uygulama makbuzu üretilmiş; tüm negatif durumlar doğru HOLD/BLOCKED.
5. Eski canonical V3 ve ürün yetkileri aynı; skor yalnız `THEORETICAL_DESIGN_CANDIDATE_100` olabilir.
6. Gerçek repo CI / bağımsız inceleme ve ürün Mac OSi kanıtı ayrıca `HOLD` veya gerçekten doğrulanmış kendi alt düzeyinde gösterilir.

**Bitiş:** DESIGN=100 adayı → tasarım inceleme kapısı → **sonraki ayrı iş: kanıtlı olgunlaşma.** `VERIFIED_FINISH` bu protokol tarafından üretilemez.

## G. Kanıtlı olgunlaştırma için sonraki sabit sıra — bu turda icra dışı

1. Mevcut 48 tasarım şartını canonical ürünlerde kaynak/CI/test ile eşleştir; sahada gerçekten uygulanabilenleri işaretle.
2. Tek ürün/tek gerçek görev pilotunda GitHub→OSi ve gerçek veri akışı, restart/replay, geri dönüş, maliyet ve kullanıcı faydasını ölç.
3. Yetkili bağımsız reviewer → DoneCheck v1.2 → gereken Human Threshold → only then VERIFIED_FINISH.

**STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT**. Hedef: ölçütleri gevşeterek değil, onları test edilebilir kılarak 100/100 tasarım kapsamı.
