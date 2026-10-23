# ENGÜRÜ Laboratuvar Yönetişim İcrası™ V1.0
STATE: DESIGN_CANDIDATE / THEORETICAL_REVIEW / AUTHORITY_HOLD
SCOPE: ENGÜRÜ Laboratuvarı genel yönetim ve yönetişim icrası; ürün bazlı uygulama icrasının üzerinde planlama ve kabul koordinasyonu.
SOURCE: AGENTS.md; Evrensel Kanıtlı Tamamlama Talimatı™ V3; ENGÜRÜ Süzgeci™ sekiz aşama.
Bu belge mevcut V3'ü, ürün canonical kabulünü veya Human Threshold™ yetkilerini değiştirmez.

## Hedef ve rol ayrımı
Yönetişim icrası WHAT / WHY / WHEN / EVIDENCE-GATE sorularını yönetir.
Mevcut uygulama icrası HOW / RUN / TEST / EVIDENCE işlerini kendi canonical yetkisiyle yürütür.
Yönetişim, uygulama motoruna yeni yetki vermez; ürün sahibinin kabul şartları önceliklidir.
Tek ana iş listesi ve özgün TASK_ID/CONTROL_ID korunur. Bloklar işlerin geçici yürütme gruplarıdır; yeni ana işler veya sayaç yaratmaz.

## Tekrarlanabilir yönetişim çalışma döngüsü
1. Kaynak hakikati, son kanıtlı ilerleme ve kalan özgün işleri topla; bağımlılıklarla uygulanabilir bloklara böl.
2. Önceden kilitli kabul ölçütleriyle bütünleşik uçtan uca masa başı simülasyonu ve puanlama yap.
3. Eksik, hata, ihtiyaç, gereksinim, risk, yetki ve bağımlılık farklarını görünür kıl.
4. Yönetişim kapsamındaki plan/sıra/kriter hatalarını düzelt; teknik farkları ilgili mevcut uygulama icrasına aynı ID ile aktar.
5. Yeniden puanla; tüm puanların ölçüt/kanıt dayanağını açıkça yaz.
6. Karşıt simülasyonda source drift, eksik grant, yanlış CI PASS, çift sayım, başarısız rollback ve bağımsız reviewer yokluğunu dene.
7. Kalan erişilebilir yönetişim farklarını tamamla; gerçek testin ve yetkinin yokluğunu HOLD kaydet.
8. Son kez puanla; tasarım 100/100 koşulunu karşılıyorsa gerçek icraya geçir. Sonraki bloğa yalnız gerekli kapılar PASS ise geç; diğer bağımsız hazırlıkları ilgili yetki sınırında paralel yürütebilirsin.

Bu sekiz çalışma hareketi ENGÜRÜ Süzgeci'nin canonical sekiz aşamasına hizalı alt yöntemdir; onun yerine yeni sekiz-aşamalı canonical motor kurulmaz.

## Üç kalite boyutu ve ölçülebilir 100/100 rubriği
A. Teorik bütünlük /100: ana hedef 20, 19/19 veya ilgili özgün iş kapsamı 20, bağımlılık ve yetki grafiği 20, kaynak/kanıt sözleşmesi 20, stop/finish ve geri dönüş 20.
B. Hata bulma/düzeltme disiplini /100: negatif vaka kapsamı 20, gerçek kök neden kanıtı 20, dar düzeltme 20, regresyon gerçek test koşulu 20, yeniden doğrulama ve audit 20.
C. Gerçek sonuca ilerletme kapasitesi /100: yürütülebilir blok 20, mevcut icra motoruna kabul edilebilir handoff 20, gerçek CI/test kanıtına bağlanma 20, bağımsız reviewer/owner/issuer kapısı 20, objektif kapanış ve sayaç 20.
Puan, her alt başlık için yalnız tanımlı mekanizma ve kontrol kanıtı varsa verilir. Teorik tasarım puanı, gerçek ürün kabulü değildir. Önerilen tasarımın tüm mekanizmaları tanımlanırsa SELF_ASSESSED_THEORETICAL_100_100; dış doğrulama ve gerçek saha için HOLD.

## Karar ve kanıt sözleşmesi
Girdi: OBJECTIVE, canonical SOURCE_REF+SHA, MAIN_WORKLIST, ACTIVE_BLOCK, BASELINE, ACCEPTANCE, AUTHORITY.
Çıktı: BLOCK_ID, INPUT_TASK_IDS, DEPENDENCIES, SIMULATION_1_SCORE, GAPS, FIXES, SIMULATION_2_SCORE, ADVERSARIAL_SCORE, REAL_EXECUTION_REF, TEST_RESULT, REVIEWER, GRANT, DELTA, DONE_TASK_IDS, NEXT_BLOCK, STATE.
Kararlar: ILERLE, GUVENLI_DUR, VERIFIED_FINISH, BITTI_DUR. Tam bitiş yalnız ürünün yetkili canonical kaynakları ve gerçek bağımsız kabul kanıtlarıyla.
Sayaç: DONE/ALL yalnız zorunlu gerçek kanıt + bağımsız kabul karşılanan özgün işler; PARTIAL ayrı raporlanır. Bir iş en çok bir kez sayılır. Simülasyon sonuçları gerçek sayaç artışına yol açmaz.

## Üç karşıt simülasyon örneği — mantıksal
T1: CI yeşil fakat entegrasyon test adımı skip → CI kapsamı yanlışsa HOLD_TEST; sayaca 0.
T2: Kaynak SHA sapması veya gizli özel kaynak checkout izni yok → HOLD_SOURCE/HOLD_AUTHORITY; ürün kodu yetkisiz yüzeye taşınmaz.
T3: 19/19 test iddiası var fakat reviewer veya issuer makbuzu yok → OFFICIAL_FINISH_HOLD; bağımsız kabul ve ledger kapıları korunur.
Bu testler birer tasarım karşıt sınamasıdır; repo/ci çalışma kanıtı değildir.

## İlk uygulama / EMÜS V1.1
MAIN_WORKLIST=19; GH01..04 / PR #210; P0→P1→P2→P3→P4 geçişleri.
Mac Engineer PR #17 ve DoneCheck PR #11 teknik yürütme kanıtları ayrı canonical depolarında kalır.
Kaynak, test ve yetkili kabul olmadan 19/19 resmî PASS yazılmaz.

## Kabul sınırı
Bu V1.0 taslak inceleme dalındadır. main, AGENTS.md, V3 SHA kilidi, mevcut ürün yetkileri ve Human Threshold™ korunur.
Yayın, canonical onay ve genel laboratuvar yönetimine bağlayıcı hâle getirme bağımsız insan incelemesiyle değerlendirilir.
