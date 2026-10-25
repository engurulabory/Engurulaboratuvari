# ENGÜRÜ Çalışma Yöntemleri™ — Birleşik Yöntem Atlası V1
**Envanter tarihi:** 2026-10-24  
**Kapsam:** ENGÜRÜ Labory kontrol düzleminin erişilebilir GitHub main kaynakları  
**Tarihsel başlangıç kaynak pini:** engurulabory/Engurulaboratuvari @ f5bd85da2c60db4c11bccd74067eef7fc3a6942f  
**Doğrulanmış PR #221 birleşme kimliği:** 9900f4ca7a17f99898521bdab1bfbe86784ecc07 (25 Ekim 2026); en güncel HEAD her oturumda GitHub üzerinden yeniden çözülür  
**Durum:** GITHUB_MAIN_SOURCE_DELIVERED / FIELD_ACCEPTANCE_HOLD / HISTORICAL_ATLAS_CONTENT  
**Rol:** Okunabilir ve bağlantılı envanter. Yeni core, yeni issuer, yeni yürütücü veya yeni kabul yetkisi oluşturmaz.

## 1. Merkez ve hiyerarşi

ENGÜRÜ Süzgeci™ sekiz aşamalı **ortak muhakeme ve çalışma disiplini**dir. Evrensel Kanıtlı Tamamlama Talimatı™ V3, Süzgeç içinde işin kanıtlı bitişini düzenler. Dil, planlama, simülasyon, test, icra, denetim, öğrenme ve yetkili kabul bu eksene bağlanır.

**Yetki sırası:** geçerli AGENTS.md → SHA-256 ile kilitli V3 → ilgili ürünün kendi canonical kabul sözleşmesi ve kaynak kimlikleri → gerçek DoneCheck™ mekanizması → gereken Human Threshold™. Ürüne özgü yetkili sözleşme üstünlüğü V3'te korunur.

**Ana düşünce hattı:** Niyet → Hakikati gör → Tek ana hedef / kabul matrisi → Kurgu ve bütünsel ön simülasyon → Bütünleşik icra → Gerçek test / karşıt değerlendirme → Kanıt / bağımsız doğrulama → DoneCheck™ → Yetkili karar → Verified Finish → Ölçülen etki / öğrenme.

**Üç farklı 100:** Teorik tasarım puanı, gerçekten çalıştırılmış test kapsamı ve resmî ürün bitişi birbirinden ayrıdır. Tasarımın 100/100 olması, sahanın 100/100 olması anlamına gelmez.

## 2. Sabit ENGÜRÜ Süzgeci™ — 8 aşama

| No | Korunan aşama | Operasyonel çıktı |
|---|---|---|
| 1 | Hakikati gör | Kaynak, sürüm, mevcut gerçek durum, yetki ve belirsizlik ayrımı |
| 2 | Değeri koru | Kullanıcı kararı, kaynak, kanıt, kilit ve geri dönüş sınırı |
| 3 | Eksikleri ve ihtiyaçları tespit et | Ölçülebilir açıklar, öncelikler, gerekli fark |
| 4 | Gerekli farkı üret | Uygulanabilir tasarım, gerçek mühendislik/araştırma işi |
| 5 | Eksikleri tamamla, ihtiyaçları karşıla | Doğrulanmış neden → gerekli onarım → yeniden test |
| 6 | Kanıtla | Kaynaklı iddia, test, bağımsız inceleme ve yetki kapıları |
| 7 | Bir sonraki ihtiyaçları belirle | Açık şartlar ve en yakın gerçek kapanış hareketi |
| 8 | İlerlet | Yetkili PASS ile devam; gerekli eşikte GÜVENLİ_DUR |

**V3 kabul kontrolleri:** K1 kabul sözleşmesi; K2 ön simülasyon; K3 gerçek icra; K4 eksik tamamlama; K5 bağımsız kanıt; K6 tamamlanma muhasebesi; K7 kanıt sürekliliği; K8 nihai kabul. K1–K8 ayrı Süzgeç aşamaları veya yeni bir core değildir.

## 3. Yöntem envanteri — ne iş yapıyor?

Aşağıdaki statüler **kaynak metinlerinin bildirdiği durumdur**. Bir dosyanın varlığı, anlık gerçek saha PASS'i olarak yorumlanmaz.

| No | Yöntem / yetenek | İşlev / mekanizma | Kanıt kaynağı ve sınırı |
|---|---|---|---|
| Y01 | **ENGÜRÜ Süzgeci™ v2.4 / sekiz aşama** | Her işi mevcut hakikat + gerekli fark yöntemiyle yönetir | [AGENTS.md](../../AGENTS.md); [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md); yaşayan kayıtta v2.4 referansı |
| Y02 | **Evrensel Kanıtlı Tamamlama™ V3** | K1–K8, tek hedef, kanıt kapıları, sınırlandırılmış deneme ve bitiş | [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md), [kilit](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) |
| Y03 | **ENGÜRÜ Pozitif Dil / Language Governance™** | STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT; yapıcı ve kanıta bağlı karar | [Dil sözleşmesi](../ENGURU_LANGUAGE_GOVERNANCE_V1.md); metninde CANDIDATE LOCK bildirimi |
| Y04 | **Tek ana hedef / tek proje / bütünleşik çalışma** | Bütünsel bağımlılık analizi, tek kabul matrisi, toplu kanıt | [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md), [Hybrid Contract](../mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_PRODUCT_ENGINEERING_CONTRACT_V1.md) |
| Y05 | **Kurgu / ön simülasyon / karşıt senaryo** | Mutlu yol, yanlış kanıt, yetki eksikliği, kaynak kayması, kesinti ve geri alma senaryosu | [Hybrid Contract](../mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_PRODUCT_ENGINEERING_CONTRACT_V1.md); [Steward preflight](../mac-engineer/ENGURU_STEWARD_V12_FULL_CHAIN_PREFLIGHT_AND_IMPLEMENTATION_PLAN_V1.md) |
| Y06 | **İki/üç turlu simülasyon ve puanlama** | Önce tasarım, eksik kapatma, tekrar sınama; özgün testleri koruma | [MK V3 kabul sözleşmesi](learning/ENGURU_MK_KALICI_AMAC_HEDEF_KABUL_V3.md), [V3 makbuz](learning/MK_V3_ACCEPTANCE_RECEIPT.json), [3x araç](../../tools/enguru_muhendislik_kasi_simulation_3x.py) |
| Y07 | **Systematic Debugging / TDD / Second Look** | Yeniden üret → kanıt → kök neden → hipotez → en küçük deney → başarısız regresyon → onar → doğrula | [Verified Production Discipline](../production/VERIFIED_PRODUCTION_DISCIPLINE_V1.md) |
| Y08 | **Golden / negatif / regresyon testleri** | Beklenen doğru davranış, hata kapılarının doğru HOLD'u, eski davranışın korunması | [MK V3 test runner](../../tools/enguru_mk_acceptance_v3.py); [Production Discipline](../production/VERIFIED_PRODUCTION_DISCIPLINE_V1.md) |
| Y09 | **Bağımsız inceleme / Quality & Red Team** | PR farkı + history/blame + kanıt + güven eşiği + bağımsız reviewer | [PR review contract](../quality/PR_REVIEW_CONTRACT_V1.md), exact-head CI gerekli aday |
| Y10 | **Sınırlı icra / Frozen scope / worktree** | İzinli dosya sınırı, yetki ve geri alma; riskli işte izole dal | [Verified Production Discipline](../production/VERIFIED_PRODUCTION_DISCIPLINE_V1.md) |
| Y11 | **REUSE → EXTEND → ADAPTER → NEW CORE** | Önce çalışan kabiliyeti koru, en küçük gerekli farkı uygula | [System 100 Hardening](../ENGURU_SYSTEM_100_HARDENING.md), [Selective Harvest](../quality/ECC_SELECTIVE_HARVEST_V1.md) |
| Y12 | **GitHub-first / Milestone-Mac / HYBRID** | GitHub kaynak, CI ve PR; Mac OSi gerçek çalışma ve native saha kanıtı | [GitHub-first](../mac-engineer/GITHUB_FIRST_MILESTONE_MAC_WORKING_MODEL_V1.md), [Hybrid](../mac-engineer/ENGURU_MAC_ENGINEER_HYBRID_PRODUCT_ENGINEERING_CONTRACT_V1.md) |
| Y13 | **ENGÜRÜ Yönetim / İcra rol ayrımı** | Yönetim hedef ve bağımlılık; İcra kaynak değişikliği; doğrulayıcı ikinci bakış | [Management V6.9](../management-v69/README.md), [Denetleyici](../controller/README.md) |
| Y14 | **ENGÜRÜ Denetleyici / beş dakikalık hedef** | Tek görev, sınırlandırılmış deneme, bağımsız yeniden doğrulama, kanıt makbuzu | [Controller](../controller/README.md); GitHub schedule best-effort, gerçek aralık kanıtı ayrı |
| Y15 | **ENGÜRÜ Mühendislik Kası™ / Verified Learning** | Gerçek olay → SHA/kapsam → tekilleştirme → karşıt test → insan incelemesi → doğrulanmış öğrenme | [Yaşayan kayıt](ENGURU_OSI_MUHENDISLIK_KASI_CANLI_KAYIT_V1.md), [V2](learning/ENGURU_MK_V2_README.md), [V3](learning/ENGURU_MK_KALICI_AMAC_HEDEF_KABUL_V3.md) |
| Y16 | **Üçlü tamamlanma muhasebesi** | Ayrı gerçek icra, gerçek kanıt, gereken yetkili kabul paydaları | [V3 bölüm 7](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) |
| Y17 | **DoneCheck™ / Human Threshold™** | Üretici makbuzu → tek gerçek makine otoritesi → yetkili insan kararı | [DoneCheck authority model](../mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md) |
| Y18 | **Oturumlar arası kanıt sürekliliği** | GOAL, VERSION, SOURCE_REF/SHA, ACCEPTED, OPEN, AUTHORITY_STATE, NEXT_ACTION | [V3 bölüm 8](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md), [session contract](../mac-engineer/SESSION_CONTINUITY_CONTRACT_V1.md) |
| Y19 | **Closed-Loop Production / Verified Agent Operating** | Task/Capability Contract → execute → observe → verify → correct → acceptance | [Closed Loop](../ENGURU_CLOSED_LOOP_PRODUCTION_CORE_V0_1.md) DESIGN LOCKED; [Agent Core](../ENGURU_VERIFIED_AGENT_OPERATING_CORE_V0_1.md) VISION LOCKED |
| Y20 | **Harvest / dış mekanizma seçici hasadı** | Yararlı kabiliyeti kanonik katmana taşıma, özgün yetkiyi koruma, regresyon | [ECC selective harvest](../quality/ECC_SELECTIVE_HARVEST_V1.md), implemented candidate / CI eşiği |
| Y21 | **Benchmark / kıyaslı deney** | Altın veri, karar uyumu, hatalı PASS, gecikme, maliyet, fallback | [JEV experiment](../quality/JEV_EXPERIMENT_CONTRACT_V1.md); deney HOLD, assessor yetkisi |
| Y22 | **Diff-aware release QA** | Fark → etki haritası → tarayıcı kanıtı → canary → benchmark → yayın kararı | [Release QA](../quality/RELEASE_QUALITY_ADAPTER_V1.md); aday / CI eşiği |
| Y23 | **Steward / envanter ve drift döngüsü** | Keşfet → kaydet → haritala → test → güvenlik → drift → onarım → rapor | [Steward Team](../../steward/STEWARD_TEAM_OPERATING_CONTRACT_V1.md) |
| Y24 | **ENGÜRÜ HİKMET CORE™ / Mizan** | Niyet, gerçeklik, sebat, mizan, sorumluluk, sonuç, ibret kapıları | [Hikmet v0.1](../ENGURU_HIKMET_CORE_V0_1.md): kavramsal yapı PASS, runtime HOLD |

Bu 24 satır **24 ayrı çekirdek** anlamına gelmez. Yöntem, operasyon, kalite kapısı, mevcut sistem mimarisi ve kavramsal/deneysel adaptörler aynı envanterde türü belirtilerek gösterilir.

## 4. İcra motoru: tek akış, farklı kapılar

~~~text
NİYET
  ↓
SÜZGEÇ 1-3 / GERÇEK KAYNAK + DEĞER + GEREKLİ FARK
  ↓
TEK HEDEF / SABİT KABUL MATRİSİ / KAYNAK SHA / YETKİ SINIRI
  ↓
KURGU + BAĞIMLILIK HARİTASI + ÖN SİMÜLASYON
  ├─ normal senaryo
  ├─ negatif/karşıt senaryo
  └─ eksik kanıt / kaynak drift / yetki ve kesinti senaryosu
  ↓
SİMÜLASYON RUBRİĞİ + GEREKİRSE 2.-3. TUR DÜZELTME
  ↓
YETKİLİ GERÇEK İCRA (GITHUB / OSI / HYBRID)
  ↓
GERÇEK TESTLER + CI + REGRESYON + GÜVENLİK
  ↓
KAYNAK VE ÇIKTI SHA / İZLENEBİLİR EVIDENCE
  ↓
BAĞIMSIZ DOĞRULAYICI / SECOND LOOK
  ↓
DONECHECK v1.2 + GEREKEN HUMAN THRESHOLD
  ├─ tüm özgün kapılar PASS → VERIFIED_FINISH → BITTI_DUR
  └─ eksik/engel → GÜVENLİ_DUR → KESİN EKSİK → NEXT ACTION
                                       ↓
                         GERÇEK SONUÇ / ÖĞRENME KAYDI
~~~

Yöntem bütünleşik; **yetki ve kanıt hükümleri ayrık**. Bir teorik PASS, gerçek icranın; bir CI PASS, Mac sahasının; bir üretici JSON PASS, resmî DoneCheck'in; bir sohbet onayı, yetkili imzanın yerine geçmez.

## 5. Ölçüm, test, puan ve makbuz

| Ölçüm | Ölçtüğü şey | Kabul için gerekli ayrım |
|---|---|---|
| Tasarım puanı / 100 | Belirlenmiş rubriğin teorik kapsanması | Gerçek başarı veya resmî otorite üretmez |
| Simülasyon turu | Senaryoların/izole testlerin geçişi | Hangi kaynak/ortamda koşturulduğu gerekir |
| Gerçek test sayısı | Çalıştırılmış benzersiz senaryo | Test kümesi ve çıktı/CI kimliği gerekir |
| İcra kapsamı | Karşılanan özgün iş ID sayısı | Tekrar eden test/yazışma ilerleme sayılmaz |
| Kanıt kapsamı | Kanıtı karşılanan özgün şartlar | SHA/provenance ve güncellik gerekir |
| Yetkili kabul | Gereken owner/reviewer/issuer kapıları | Gerçek imzalı karar ve canonical doğrulama |
| Verified Finish | Bütün zorunlu şartların gerçek bitişi | DoneCheck + gerekli Human Threshold |

**Kaynakta bulunan örnek makbuz:** [MK V3 acceptance receipt](learning/MK_V3_ACCEPTANCE_RECEIPT.json) iki turda 104 benzersiz senaryo/tur, 25/25 tasarım kapısı/tur ve 100 teorik ağırlıklı puan bildirir. Aynı makbuzda real_schedule=HOLD_NOT_OBSERVED, mac_osi_human_review=HOLD_NOT_SIGNED, official_verified_finish=HOLD yazılıdır. Bu atlas o testleri yeniden çalıştırmış sayılmaz.

**Kaynak kilidi:** [V3 lock](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) beklenen SHA-256 değerini 11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc olarak verir. Canlı doğrulama yöntemi [verify_enguru_universal_v3_lock.py](../../tools/verify_enguru_universal_v3_lock.py) ve [lock workflow](../../.github/workflows/enguru-universal-v3-lock.yml) içindedir.

## 6. İşletim yerleri ve yetki sınırı

| Yer | Gerçek görevi | Doğrulanacak kanıt |
|---|---|---|
| ChatGPT/Yönetim | Amaç, sıralama, kapsam, kabul matrisini kurma | Doğru kaynak atfı / gerçek kanıta dayalı iddia |
| GitHub | Canonical kaynak, izole dal, PR, CI, review ve exact-main | Commit SHA, job/run, test artefaktı, PR/merge |
| Mühendislik / İcra | Yetkili kod, araç, tasarım ve onarım farkı | Değiştirilen dosya, test ve çıktılar |
| Mac OSi | Native çalışan uygulama, Keychain, runtime, kurulum, saha | Gerçek Mac gözlemi, SHA, test, restart/recovery |
| Bağımsız doğrulayıcı | Kapsam, SHA, kaynak ve sonucu yeniden ölçme | Ayrı mekanizma veya yetkili reviewer kimliği |
| DoneCheck™ v1.2 | Makine doğrulaması, audit, resmî receipt | Geçerli canonical makbuz ve provenance |
| Human Threshold™ | Geri dönüşü zor, gerçek kişi/kurum adına veya resmî kabul | Yetkili özgün karar |

## 7. Mevcut doğrulanabilir kapsam ve açık eşikler

- **SOURCE_INDEXED:** Yukarıdaki dosyalar 2026-10-24 tarihinde GitHub main üzerinden okunarak eşleştirildi; başlangıç HEAD pini bu belgede kayıtlı.
- **HISTORICAL_SIMULATION_EVIDENCE:** MK V3 makbuzunda iki × 104 izole vaka PASS bildiriliyor; yeni dal için yeniden test ve CI sonucu ayrıca gerekir.
- **SOURCE/STATUS_BOUNDARIES:** Bazı metinler CANONICAL, bazıları CANDIDATE, bazıları DESIGN/VISION LOCKED veya EXPERIMENT HOLD durumunda. Tablo bunları tek üretim PASS'ine dönüştürmez.
- **OPEN:** Bu atlasın PR #221 GitHub birleşmesi ve exact-main 3/3 CI başarıyla kapandı; alanların gerçek kullanıcı, semantik reviewer ve saha kabulü kendi kapılarında izlenir.
- **OUT_OF_SCOPE:** Mac OSi kurulumu, signer yetkisi, canlı schedule, ürün PR birleştirmesi, resmî Verified Finish; bu derlemenin işi yalnız mevcut yöntemi görünür kılmaktır.
- **ENVANTER SINIRI:** Bu sürüm merkezi Labory main üzerindeki doğrulanmış yöntemleri toplar. Diğer ürün depolarının bütün özel sözleşmeleri ayrı kapsamlı tam envanter olarak incelenmiş sayılmaz.

## 8. Birlikte kullanım: pratik okuma sırası

1. Önce [AGENTS.md](../../AGENTS.md) ve [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) ile kaynağı ve görevi sabitle.
2. Tasarım/puanlama, hata/karşıt simülasyon ve gerçek icra ayrımını [Uçtan Uca Kılavuz](ENGURU_YONTEM_UCTAN_UCA_SIMULASYON_V1.md) ile uygula.
3. Gerçek test, bağımsız kanıt, yetki ve kapanışta ürüne özgü canonical sözleşmeyi esas al.

**Nihai atlas hükmü:** GITHUB_SOURCE_INTEGRATED / PR_221_MERGED / REAL_PRODUCT_ACCEPTANCE_HOLD. Kaynakların haritalanması yeni bir ürün kabulü değildir.
