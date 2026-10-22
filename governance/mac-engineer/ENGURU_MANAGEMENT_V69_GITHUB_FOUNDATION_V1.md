# ENGÜRÜ Yönetim V6.9 — GH69-BASE Bütünleşik Teorik Temel Sözleşmesi V2

**Durum:** `OWNER_APPROVED_GITHUB_REVIEW_BRANCH_CANDIDATE / CI_AND_REVIEW_HOLD`  
**Kaynak:** GH69-BASE V1 ve 22.10.2026 tarihli hizalama 87/100, teknik 82/100 denetimi  
**Görev:** `ENGURU-MGMT69-GH-FOUNDATION-01`  
**Kalıcı sabit hedef:** `TEORİK 100/100 → BAĞIMSIZ TASARIM KABULÜ → GERÇEK MÜHENDİSLİK → VERIFIED_FINISH → BITTI_DUR`

## 0 — Sınır, otorite ve kabul beyanı

Bu V2, GH69-BASE'in önceki 12 özgün kontrolünü koruyan **tek bütünleşik tasarım revizyonudur**. V1'de kanıtlanmış tasarım kararları korunur. Yedi açık (D01–D07) bu belge, veri sözleşmesi ve yerel testlerle kapatılacak biçimde ifade edilir. Bu belge **kanonik repo kaydı, resmi DoneCheck makbuzu, GitHub PR CI sonucu veya gerçek sistemde VERIFIED_FINISH değildir**. Kriterlerin teorik kapsam puanı ve gerçek mühendislik kabul puanı ayrı muhasebedir.

**Kaynak sırası:** Güncel, yetkili ve işlem-kapsamlı insan/issuer kararı + yürürlükteki canonical kaynak → exact `main` referansı → salt okunur PR önerisi → son doğrulanmış yerel Mac saha gözlemi. Kaynak çatışmasında `HOLD_SOURCE` ile mutabakat. Owner onayı başka role, süreye veya repoya otomatik taşınmaz. İmza ve güven kökü gerçek üretim sisteminden doğrulanır.

**Canonical temel:** ENGÜRÜ Süzgeci™ v2.4 sekiz aşama; GitHub canonical V3 SHA-256 `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`; Language Governance V1; mevcut DoneCheck Authority Model; inceleme dalında bulunan Toplu Kanıt → Toplu Kabul V2; mevcut Yönetim standardı. Hiçbiri yeni bir core/dokuzuncu aşama/ikinci canonical yetkiyle değiştirilmez.

**Kaynak gözlemi (22.10.2026):** Control `main` = `1f7dfd708d652764ac74df27dcbbd393779e2b3b`, control PR #191 = `de63a9e34a9b05b6474c847019d8c682b5360d50`; product `main` = `5432b9b135499cea18273c0e003877b864af92c6`, product PR #14 = `f806d3e0e5d68e6f06af96a5a24a83762b49f0ab`. GitHub mühendisliği öncesi bu kimlikler yeniden okunur. PR191 `27/100`, B01-09 HOLD; resmî H1/H2/H3 `0/12`. GH69 V2 bu sayaçlara otomatik ilerleme eklemez.

## 1 — D01: On iki özgün kontrol için eksiksiz V3 kabul matrisi

Kontrol kimlikleri `GH69-BASE-01` ... `GH69-BASE-12` sabittir; aşağıda sade okunur görünüm, JSON içinde **her kontrol için** `CONTROL_ID / REQUIREMENT / PASS_CONDITION / REQUIRED_EVIDENCE / VERIFIER / AUTHORITY / STATE` ve `DEPENDENCIES / SOURCE_PIN / RECENCY / GATE_TYPE / OWNER_ACTION` bulunur. İlk durumda tümü `HOLD_REAL_GITHUB_EXECUTION`; teorik sözleşmenin kabulü bunları gerçek GitHub PASS konumuna yükseltmez.

| Özgün ID | Gereken gerçek kabul şartı | Kabul/verifier sahibi |
|---|---|---|
| `GH69-BASE-01` | AGENTS.md ve canonical V3, SHA-256 ve sekiz aşamanın tam kaynak eşliğini korur. | `SOURCE_AUDITOR` / `CANONICAL_OWNER` |
| `GH69-BASE-02` | Kontrol ve ürün depolarının main/PR/OSi kaynaklarını exact kimlikle ve tazelikle ayırır. | `SOURCE_AUDITOR` / `CANONICAL_OWNER` |
| `GH69-BASE-03` | Tek canonical ve mevcut core otoritesiyle uyumlu, değişiklik sınırı sabit mühendislik önerisi üretir. | `SECURITY_REVIEWER` / `CANONICAL_OWNER` |
| `GH69-BASE-04` | TASK_ID, PROJECT_ID, CONTROL_ID, acceptance revision ve scope kimliklerini birebir doğrular. | `SCHEMA_REVIEWER` / `TASK_OWNER` |
| `GH69-BASE-05` | Yönetim/İcra/owner/issuer/verifier/DoneCheck/Human Threshold rollerinin yetki ayrımını doğrular. | `SECURITY_REVIEWER` / `HUMAN_THRESHOLD` |
| `GH69-BASE-06` | Ham kanıt baytları, SHA-256, kaynak, süre ve iptal kontrolünün tamamını doğrular. | `EVIDENCE_REVIEWER` / `SOURCE_OWNER` |
| `GH69-BASE-07` | Tek kontrol PASS_EVIDENCE, toplu ID kabulü ve proje Verified Finish kararlarını ayırır. | `INDEPENDENT_REVIEWER` / `DONECHECK_V12` |
| `GH69-BASE-08` | PR/yerel kaynak ve main hakikatini uzlaştırır; kaynak yükseltmesini yetkili onayına bağlar. | `SOURCE_AUDITOR` / `CANONICAL_OWNER` |
| `GH69-BASE-09` | CAS, idempotency, olay günlüğü, checkpoint, restart/replay ve yan-etki tekilliği kanıtlarını tanımlar. | `RELIABILITY_REVIEWER` / `EXECUTION_OWNER` |
| `GH69-BASE-10` | Olumlu/olumsuz fixture, bağımsız oracle ve karşıt testleri deterministik yeniden üretir. | `INDEPENDENT_REVIEWER` / `TEST_OWNER` |
| `GH69-BASE-11` | CI, exact HEAD, değişiklik sınırı, gerçek test ve kaynak bütünlüğünü mutabık kılar. | `CI_REVIEWER` / `REPOSITORY_OWNER` |
| `GH69-BASE-12` | GH69-BASE tasarım/PR adayını ürün resmî bitişinden ayırır; yetki ve sayaçları korur. | `INDEPENDENT_REVIEWER` / `HUMAN_THRESHOLD` |

**Değişmez muhasebe:** GH69'ın 12 kendi tasarım kontrolü, Mac Engineer'ın 100 özgün `Bxx-yy` kriterinden ayrı ad uzayıdır. Ana sayaç `PASS_EVIDENCE` yalnız özgün kriter + gerçek kaynak + gerekli owner/verifier + yetkili ledger mutabakatıyla değişebilir. Aynı ham kanıt birden fazla özgün ID'ye kaynak olabilir, fakat her ID için bağımsız PASS şartı uygulanır.

## 2 — D02: Rol, gerçek güven adaptörü ve deterministik karar sınırı

`MANAGEMENT`: hedef, kapsam, öncelik ve karar önerisi. `EXECUTION`: yetkili mühendislik ve gerçek kanıt. `SOURCE_OWNER`: mevcut kaynak kapsamı ve kabul yetkisi. `INDEPENDENT_VERIFIER`: producer'dan ayrı kimlikle doğrulama. `DONECHECK_V12`: üretim makine doğrulaması ve kendi resmi kapısı. `HUMAN_THRESHOLD`: geri dönüşü zor ve nihai insan kararı. `GITHUB_ADMIN`: depo teknik izni; kendi başına signer, DoneCheck veya nihai insan yetkisi değildir.

**Üretim trust adapter arayüzü:** Sağlayıcı kimliği, kaynaklandırılmış kök sertifika/anahtar, kanonik bayt imzası, `TASK_ID + PROJECT_ID + CONTROL_ID + SOURCE_REPO + SOURCE_SHA + OPERATION + NONCE` kapsam bağı, UTC başlangıç/bitiş, iptal/rotasyon, principal ayrımı ve saldırı günlüğü. Model tarafından yazılmış bir alan, sentetik anahtar veya `verified=true`, üretim attestation yerine geçmez. Dış sağlayıcı kaydı eksikse `HOLD_EXTERNAL_BINDING`.

**Kabul geçiş tablosu:**

| Önce → Sonra | Zorunlu doğrulama | Yetkili merci |
|---|---|---|
| `PROPOSED → DESIGN_READY` | `SCHEMA_COMPLETE + SOURCE_SNAPSHOT_TYPED + DESIGN_TESTS_PASS` | `DESIGN_REVIEWER`, kapsam `THEORETICAL_ONLY` |
| `DESIGN_READY → FOUNDATION_ENGINEERING_PASS_CANDIDATE` | `REAL_GITHUB_PR + EXACT_HEAD_CI + EVIDENCE_SHA + REVIEW_RESULT` | `REPOSITORY_REVIEWER`, kapsam `GH69_BASE_ONLY` |
| `HOLD → CONTROL_ACCEPTED` | `ORIGINAL_CONTROL_REQUIREMENT + REAL_EVIDENCE + AUTHORIZED_OWNER + INDEPENDENT_VERIFICATION + LEDGER_CAS` | `CANONICAL_LEDGER_OWNER`, kapsam `SINGLE_ORIGINAL_ID` |
| `CONTROL_ACCEPTED → PROJECT_VERIFIED_FINISH` | `ALL_ORIGINAL_CONTROLS_ACCEPTED + CANONICAL_MAIN + AGGREGATE_LEDGER + DONECHECK_V12 + HUMAN_THRESHOLD + SIGNED_FINAL_RECEIPT` | `AUTHORIZED_FINALIZER`, kapsam `PROJECT_ONLY` |

**Kesin bitiş ilkesi:** `DESIGN_READY` yalnız tasarım/izole test sonucu; `FOUNDATION_ENGINEERING_PASS_CANDIDATE` yalnız gerçek inceleme dalı, exact HEAD CI, diff ve review kanıtıyla; `CONTROL_ACCEPTED` yalnız özgün ID ve gerçek otoriteyle; `PROJECT_VERIFIED_FINISH` yalnız resmî tam kontrol kümesi, exact-main, aggregate ledger, DoneCheck™ v1.2, Human Threshold™ ve finalizer receipt ile. Modelin tek taraflı karar yolu resmî PASS üretmez.

## 3 — D03: Ham kanıt, süre, iptal ve oturum devri

**EvidenceReceipt asgari tipli alanlar:** `RECEIPT_ID`, `TASK_ID`, `PROJECT_ID`, `CONTROL_ID`, `SOURCE_REPO`, `SOURCE_REF` (40 hex), `SOURCE_SHA256` (64 hex), `RAW_BYTES_LOCATOR`, `EVIDENCE_SHA256` (64 hex), `PRODUCER_ID`, `VERIFIER_ID` (ayrı), `ISSUED_AT`, `EXPIRES_AT`, `REVOCATION_STATUS`, `SCOPE`, `VALIDATOR_VERSION`, `AUTHORITY_RECEIPT`. `EXPIRES_AT > ISSUED_AT`; saat kayması sınırı ve iptal kaynağı üretim sağlayıcısından doğrulanır. SHA ancak özgün ham bayt yeniden hashlenip beklenen digest ile karşılaştırılırsa kanıt sayılır; yanlış SHA veya değiştirilmiş bayt `HOLD_EVIDENCE` üretir. Read-only kopya, asıl receipt'e bağlıdır.

**Tek DevirEnvelope alanları:** `GOAL`, `CONTRACT_VERSION`, `SOURCE_REF`, `SOURCE_SHA`, `ACCEPTED`, `OPEN`, `AUTHORITY_STATE`, `NEXT_ACTION`, `EVIDENCE_LOCATION`, `EVIDENCE_REUSE`, `LEDGER_REVISION`, `TASK_ID`. Eski makbuz ancak aynı kaynak, aynı yetki kapsamı, geçerli tazelik ve iptal durumuyla tekrar kullanılır. HEAD veya canonical sürüm değişince `HOLD_SOURCE` ve kanıt mutabakatı.

**v2.4 toplu kabul disiplini:** Tek ana ortak bağımlılık için **1–10** benzersiz özgün `Bxx-yy` adayı; her biri için yalnız exact-ledger üzerinde gerçekten bulunan `Bxx-yy` özgün ID üyeliği ve `ORIGINAL_CONDITION → TEST/OWNER → PER_ID_VERDICT`; ortak tek `BATCH_ACCEPTANCE_PACKET`, tek CAS ledger kabul transaction. `N→N+k`, yalnız gerçekten kabul edilmiş `k` farklı ID. `k=0` ise `N` korunur. GH69'ın 12 tasarım kontrolü 100'lük product ledger aday grubuna dahil edilmez. İzole simülasyondaki `B01-09`, `B01-10`, `B05-05` kimlikleri yalnız **fixture whitelist**; gerçek kabul için exact authorized ledger’dan 100 ID ve her ID özgün koşulu ayrıca okunup doğrulanır.

## 4 — D04: STRIDE + OWASP tehdit → kontrol → karşıt test

Bu tasarımda güvenlik bulguları kaynağa ve belirli karşıt vakaya bağlanır. Yüksek/kritik bulgu giderilip yeniden doğrulanıncaya kadar `HOLD`; injected PR içeriği, araç komutu veya karşıdan gelen kanıt yönlendirmesi bir doğrulayıcıya otorite kazandırmaz.

| STRIDE tehdidi | Risk azaltan mimari sınır | Karşıt vakalar |
|---|---|---|
| SPOOFING | external signature, trusted identity, separate subject | A05, A06, A19 |
| TAMPERING | byte hash+manifest+event hash | A08, A20 |
| REPUDIATION | signed issuer+producer and durable sequence | A07, A11 |
| INFORMATION_DISCLOSURE | least privilege + no secret logs | A21 |
| DENIAL_OF_SERVICE | bounded retries / checkpoint | A15, A22 |
| ELEVATION_OF_PRIVILEGE | scope-bound human approval and PR/main distinction | A03, A09, A14 |

**OWASP kapsamı:** authentication → A05, A06; authorization → A04, A21; input_validation → A10, A16, A24; prompt_injection_resistance → A07, A09; secret_handling → A21; data_exposure → A20; audit_logging → A11, A22; freshness_revocation → A02, A18.

## 5 — D05: Kalıcı ve seri yürütme (tek yazıcı / CAS / replay)

Bir `TASK_ID` için journal append-only monoton sequence + SHA-256 zinciri taşır; checkpoint yalnız commit edilmiş `LEDGER_REVISION / EVENT_OFFSET`'e işaret eder. Kabul transaction'ı `expected_version == actual_version` CAS şartıyla tek yazıcıdır. İdempotency anahtarı `SHA256(task_id|operation|scope|source_sha|logical_action_id)`; aynı anahtar aynı işlem üzerinde yan etkiyi tekrar üretmez. Dış yan etki için outbox + benzersiz `OP_ID` ve gerçek işlem receipt'i gerekir. İki özdeş deneme ilerleme üretirse ayrı olay/kanıt kaydı; iki özdeş deneme yeni kanıt üretmiyorsa yeni hipotez veya yöntem kararı. Kesinti sonrası yalnız zinciri doğrulanmış checkpoint ve kaynak pinlerinden resume.

**Test oraklı:** Gerçek SQLite dosyası üzerinde bağımsız yeniden açma; bir işlem uygulanır, ikinci çağrı `REPLAY_NO_EFFECT` verir; eski CAS `HOLD_CAS_CONFLICT`; yeniden açılmış süreç doğru `version,count` ile devam eder. Bu test **yerel izole fixture**'dır: üretim dış işlem tekilliğini veya gerçek OSi replay'ini kanıtlamaz.

## 6 — D06: ENGÜRÜ pozitif dil ve karar bütünlüğü

Her karar aynı sırada sunulur: `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT`. Örnek:

`STATE=HOLD_AUTHORITY` · `CLAIM=Kaynak ve kanıt tasarım düzeyinde hazır` · `EVIDENCE=PR exact HEAD / gözlemlenen makbuz` · `NEXT_ACTION=Owner scope+expiry imzasını gerçek kaynaktan doğrula` · `VERDICT=HOLD`.

`STATE=DESIGN_READY` · `CLAIM=GH69 temel şeması ve izole test kapsamı tamamlandı` · `EVIDENCE=12/12 sözleşme + A01–A24 oracle` · `NEXT_ACTION=GH69 GitHub inceleme dalı için açık yetkili kapsam kararı` · `VERDICT=DESIGN_PASS_ONLY`.

Negatif gerçek durum bilgisi (`HOLD`, `BLOCKED`) doğruluk için korunur; yapılacak hareket yapıcı fiillerle anlatılır. Gerçek kök neden yalnız kanıtla adlandırılır. Sekiz aşama ürün akışını yönetir; GH69, v2.4 veya V3 üzerine yeni aşama eklemez.

## 7 — D07: Karşıt sınama, gerçek benchmark ve üretim CI kabulü

**Asgari karşıt matris:** A01–A24'ün tamamı ayrı sabit beklentiye bağlanmıştır (özgün A01–A14 korunmuş, A15–A24 genişletilmiş). Hatalı SHA, stale main, sahte owner/issuer, rol çakışması, bozuk tip, negatif sayaç, tekrarlı effect, eksik handoff/receipt, süre aşımı ve sentetik finish tespit edilir. Pozitif sentetik A13/A23 yalnız `DESIGN_READY`; gerçek dış sağlayıcı izni A14'te bulunmadığından `HOLD_EXTERNAL_BINDING`.

**Kesin GitHub değişiklik izin listesi (4 dosya):** `governance/mac-engineer/ENGURU_MANAGEMENT_V69_GITHUB_FOUNDATION_V1.md`, `governance/mac-engineer/ENGURU_MANAGEMENT_V69_FOUNDATION_ACCEPTANCE_V1.json`, `tests/test_enguru_management_v69_foundation.py`, `evidence/ENGURU_MANAGEMENT_V69_FOUNDATION_REVIEW_V1.json`. Yeni core sayısı: `0`; yeni canonical yetki sayısı: `0`; mevcut dosyalar korunur. 22.10.2026 tarihinde kullanıcı dört izinli GH69-BASE dosyası için ayrı GitHub inceleme dalında gerçek mühendisliğe açıkça izin verdi. Yetki yalnız bu dar dal/iş/kapsama uygulanır; main merge, PR191/PR14 değişikliği, canonical ledger, signer, OSi veya Verified Finish bu kapsamın dışındadır. Dört dosyanın her biri inceleme kaydıdır; ek workflow gerektiğinde yeni yetkili diff kararı alınır.

**Gerçek CI kabulü:** Yetkili yazım kararından sonra `main` anlık tekrar oku → mevcut canonical dosyalar/araçlar taransın → izole review branch üzerinde 4 dosyalık allowlist (`governance/mac-engineer/*.md`, `governance/mac-engineer/*.json`, `tests/*.py`, `evidence/*.json`) ancak ismen GH69'a ait path'lerle → lint/type/schema/24 karşıt test → GitHub run ID/status → branch HEAD tekrar oku → SHA-256 manifest/diff → bağımsız reviewer → yalnız `FOUNDATION_ENGINEERING_PASS_CANDIDATE`. Mevcut `AGENTS.md`, canonical V3, 100'lük ledger, DoneCheck, P01/PLive, PR191 ve Mac worktree koruma kapsamındadır.

**İleri muadil benchmark tasarımı:** Temporal, LangGraph ve Microsoft Agent Framework için aynı görev verisi, donanım, fixture SHA, seed, ağ ve fail injection; senaryo başına ≥30 gerçek tekrar. Ölçümler `false_verified_finish, false_hold, valid_completion_rate, duplicate_side_effects, crash_recovery_rate, p50/p95, cost, handoff_count, evidence_loss_count`. Sert güvenlik eşiği: yanlış resmî bitiş 0, çift yan etki 0, kanıt kaybı 0; geçerli pozitifte dış yetki doğrulama zorunlu. p50/p95 sayısal eşikleri baseline ölçümünden sonra yetkili kabul şartı olarak sabitlenir; karşılaştırmalı runtime sonuçları bu taslakta `NOT_MEASURED`.

## 8 — İki ayrı 100/100 puanının anlamı ve sonraki kapı

- **Standart hizası teorik 100/100:** Önceki 10 adet 10 puanlık rubriğin tüm kesin şartları, sabit matriste ve bağımsız testlerde karşılanmışsa.
- **Kendi teknik teorik kalitesi 100/100:** Ayrı 10 adet 10 puanlık rubriğin tüm kesin şartları, test oraklı ve karşıt taramayla karşılanmışsa.
- Bu iki puan **tasarım sözleşmesinin tanımlı kapsam iç uygunluk puanları**dır. Gerçek CI, canlı benchmark, gerçek signer, bağımsız yetkili reviewer ve Verified Finish kendi kapılarına sahiptir.

**İlerleme:** `THEORETICAL_DESIGN_ACCEPTANCE` (kanıtlıysa) → `OWNER_APPROVED_GITHUB_REVIEW_BRANCH` → `REAL_GITHUB_CI_AND_REVIEW` → `AUTHORIZED_LEDGER_DONECHECK` → `OSI_FIELD_ACCEPTANCE` → `VERIFIED_FINISH → BITTI_DUR`.

**Özgün teorik kanıt paketindeki GitHub/OSi yazımı = 0**. 22.10.2026 tarihli kullanıcı kararıyla dört dosyanın izole GitHub inceleme dalına geçirilmesi yetkilidir. Bu belgenin GitHub kaydı ürün kabulü veya merge onayı anlamına gelmez; `GH69-BASE-11` exact-head GH69 CI ve reviewer tamamlanana kadar HOLD kalır.

## 9 — 22.10.2026 GH69-BASE ilk GitHub aktivasyon kaydı

**Owner instruction:** “Teorik temeli kapatalım. GitHub'a geçelim.” İzin kapsamı **yalnız 4 yeni GH69-BASE dosyasının ayrı inceleme dalında oluşturulması**, gerçek testlerin ve mevcut GitHub CI durumunun okunması, bağımsız PR incelemesine sunulmasıdır.

**Üretim güvenliği:** PR #191'in inceleme dalındaki 27/100 kabul sayaçları, `B01-09=HOLD`, resmî H1/H2/H3 `0/12` olarak korunur. Kontrol `main` v0.6 canonical sürümünü ve yerel Mac gözlemi v0.8 kapsam ayrımını koru.

**GH69-BASE-11 kalite eşiği:** Repo üzerindeki genel Labory Final Gate, PR için çalışsa bile GH69 özel `test_enguru_management_v69_foundation.py` testini doğrudan çağırmıyor. Bu sebeple GitHub exact-head özel test zorunluluğu **GH69 özel GitHub CI bağlanıncaya ve ilgili workflow run PASS oluncaya kadar HOLD** kalır. İzole/test çıktısı `PASS_LOCAL` olarak ayrı kaydedilir; kullanıcıya PR/CI ile eşdeğer gibi sunulmaz. Bu ikinci mühendislik hareketi yalnız gerekli yetkili kapsam kararıyla yapılacaktır.
