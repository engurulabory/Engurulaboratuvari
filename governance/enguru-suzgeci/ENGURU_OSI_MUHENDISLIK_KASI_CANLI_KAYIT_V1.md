# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™
## Yaşayan Hakikat, Fark, Hata ve Önleyici Kontrol Kaydı · V1.0

**Kayıt tarihi:** 2026-10-23  
**Durum:** `ACTIVE_LEARNING_RECORD / OFFICIAL_PRODUCT_FINISH_HOLD`  
**Kapsam:** ENGÜRÜ Yönetim V6.9 / PR #203 gerçek GitHub ve Mac OSi çalışması. ENGÜRÜ Süzgeci™ v2.4'ün sekiz aşamasının içinde çalışan **yardımcı öğrenme kaydıdır**; yeni çekirdek, yeni karar otoritesi veya ayrı ürün değildir.  
**Kaynak yönetimi:** Bu belge ayrı GitHub **inceleme dalında** sürümlenir; `main` üzerindeki V3, kaynak kilitleri, mevcut PR #203 ve Mac OSi canonical kayıtları korunur.  
**Kalıcı sabit ürün hedefi:** `ENGURU_MANAGEMENT_V69_PR_203 → VERIFIED_FINISH → BITTI_DUR`.  
**Öğrenme hedefi:** Tekrarlayan hata sınıflarını kanıta dayalı olarak azaltmak, tekrar denemelerin verimini artırmak, yeni durumda doğru kanıt/karar ayrımını korumak. **Sıfır hata hedefi yön tayinidir; henüz kanıtlanmış sıfır hata beyanı değildir.**

### 1. Değişmeyen çalışma bağlamı ve mevcut hakikat

| Kaynak / kapı | Son kanıtlı durum | Referans |
|---|---|---|
| Yönetim PR | `OPEN`, `merged=false`, `HEAD=63fe22e7c1ce73adf94b0cbdd40924511e8211cd`; base `main=1f7dfd708d652764ac74df27dcbbd393779e2b3b` | [PR #203](https://github.com/engurulabory/Engurulaboratuvari/pull/203); 2026-10-23 bağlantılı kontrol |
| Gerçek GitHub CI / DoneCheck `verifyTask` | `4/4 PASS_TECHNICAL_ONLY`, run `39852715540`, exact `MGMT69_VR_GITHUB_RUN_39852715540` | Artifact `12457199441`; ZIP SHA-256 `e42924718577aa2ff8130a405e9b3123f7bdd7789df6327fe805da43719d0502` |
| Mac saha kaynağı | `SOURCE_PINS=5/5 PASS`; mevcut bridge `private_key_pem` ister | [Saha sonucu](https://github.com/engurulabory/Engurulaboratuvari/pull/203#issuecomment-6362066351); Mac rapor SHA-256 `60708f1d2bf5165832899da76075e4d2ac6fb34b9d60cbdfbc167a6fb92b3f9c` |
| Mac signer kaynak araması | 561 kaynak dosyası / 18 dizin; signer üretim girişi kesinleştirilemedi; varsayılan Keychain 0/3 eşleşme | [Saha keşfi](https://github.com/engurulabory/Engurulaboratuvari/pull/203#issuecomment-6362269348); rapor SHA-256 `ed7a8a1beea64009fa45e4491a517895af558764e99f034e712f1ace5a2a93ad` |
| Açık anahtar kimliği | `KEY_ID_DIGEST_FORMAT=PEM_UTF8`; `SSH_AGENT_EXACT_PUBLIC_KEY_MATCH=HOLD_NOT_LOADED` | [Mac terminal kanıtı](https://github.com/engurulabory/Engurulaboratuvari/pull/203#issuecomment-6362402417) |
| Standart `.pub` kapsamı | `PUBLIC_FILES_CHECKED=0`, `EXACT_PUBLIC_MATCHES=0` — **sıfır incelenen dosya** | [Mac terminal kanıtı](https://github.com/engurulabory/Engurulaboratuvari/pull/203#issuecomment-6362576995) |
| Owner trust + Ed25519 özel anahtar kontrolü | `HOLD_NOT_AUTHENTICATED` | Tek görevlik owner onayı [kapsam niyeti](https://github.com/engurulabory/Engurulaboratuvari/pull/203#issuecomment-6360849903) olup imzalı trust grant değildir |
| Gerçek `HumanReview.accepted`, audit/ledger, merge, exact-main | `HOLD`; imza=0, resmî makbuz=0, merge=0 | Doğrulanmış resmî bitiş kanıtı bekleniyor |

**Sabit kimlikler:** `TASK_ID=ENGURU_MANAGEMENT_V69_PR_203`; `VERIFICATION_RESULT_ID=MGMT69_VR_GITHUB_RUN_39852715540`; `REVIEWER_CANDIDATE=enguru-mac-local-human-authority`; `KEY_ID_CANDIDATE=ed25519-sha256:40c6a9cc82815ea5a9755cd4b843d35cd701b4b90d8f65ecb656f1c37a4ef64f`.

**Otorite sınırı:** OSi/Mac kaynak ve runtime hakikati; GitHub kaynak inceleme ve CI; DoneCheck™ teknik ve audit; insan sahibi gereken kabul. Sohbette verilen kapsam izni ≠ Ed25519 imzası ≠ resmî DoneCheck makbuzu ≠ GitHub merge. Korunmuş Gate12 v0.8 yetkisi başka üründe otomatik yetki sağlamaz.

### 2. Mühendislik öğrenme olayları (kanıtlı beklenti → gerçekleşen fark)

**Sınıflar:** `DOĞRULANDI` = kaynak/gerçek saha kanıtı; `SINIRLI_GÖZLEM` = belirli yöntem ve kapsam; `HİPOTEZ` = açıklaması henüz sınanacak. Önleyici kuralın yazılması, o kuralın otomasyonla uygulanmış olduğunun kanıtı değildir. Her olay tekil `MK-xx` kimliğiyle kalıcıdır.

| ID / kanıt seviyesi | Beklenti / uygulama zaafı | Gerçekte gözlenen ve düzeltme | Sonraki çalışmada önleyici kontrol |
|---|---|---|---|
| **MK-01 · DOĞRULANDI** | 4/4 yeşil CI'nin tam ürün bitişine yaklaşımını olduğundan yüksek yorumlama riski | `verifyTask` teknik PASS; owner trust, HumanReview, audit ve merge ayrı `HOLD` | Önce **icra / kanıt / bağımsız doğrulama / insan yetkisi / yayın** kapılarını ayrı raporla; her `PASS` kendi sınırını taşısın |
| **MK-02 · DOĞRULANDI** | Ed25519 `keyId` özetinin SPKI-DER üzerinden hesaplandığını varsayma | SPKI karşılaştırması `false`; gerçek Mac deneyi `PEM_UTF8` eşleşmesi verdi | Hash iddiası öncesi **tam bayt temsili** (`PEM_UTF8`, `SPKI_DER`, raw) ve encoding bilgisini göster; güven kararını doğrulanmış canonical tanıma bağla |
| **MK-03 · DOĞRULANDI** | Saha aracının `HOLD` çıktısını bir olumsuz gerçek test sanma | İlk araçta signer ve bazı aşama durumları sabit `HOLD` atanıyordu | Çıktı alanının kökeni `MEASURED / CONSTANT_DEFAULT / INFERRED` olarak denetlensin; sabit değer `NOT_VERIFIED` olarak yorumlansın |
| **MK-04 · SINIRLI_GÖZLEM** | Dar kapsamda `0` eşleşmeyi sistem çapında yokluk sayma | İki klasörde grant araması, varsayılan Keychain 0/3 ve üç kökte `*.pub` 0 dosya; sonuç global yokluk kanıtı değil | Her yokluk iddiasına `SEARCH_ROOTS`, `PATTERN`, `FILES_EXAMINED`, `COVERAGE`, `LIMIT_REACHED` ekle; `0 examined` → `NO_TEST` |
| **MK-05 · DOĞRULANDI** | Dosya/fonksiyon adını imzalayıcı üretim arayüzü sanma | `enguru_goal_final_acceptance.py::signcheck` ve `verify_existing_signed_ht_bundle` **imza doğrulayıcı**; `auth_broker.py` token/Keychain politikası | Adayları AST/metin işaretinden **çağrının işlevsel yönüne** geçir: `SIGN / VERIFY / STORE_TOKEN / UNKNOWN`; imza yazma iddiası için gerçek API gövdesi gerekli |
| **MK-06 · DOĞRULANDI** | `ssh-agent` içinde anahtar yüklenirse mevcut kabul otomatik çalışır beklentisi | Agent'ta aynı public key yüklü değil; OSi bridge `private_key_pem` tüketiyor | **Signer arayüz sözleşmesini** önce karşılaştır; `ssh-agent`/Keychain/PKCS#8 PEM türleri ve kriptografik algoritma uyumluluğu açıklığa kavuşsun |
| **MK-07 · DOĞRULANDI** | Tek Mac açılış şifresi bütün resmî owner kabulünün eşdeğeri olabilir beklentisi | macOS yerel kimlik doğrulaması ve DoneCheck Ed25519 tasdikinin farklı kanıtlar olduğu ortaya kondu | En kısa **tek owner etkileşimi** amaçlanır; imzalı özgün `taskId + resultId + reviewer + karar` kanıtı ayrıca doğrulanır; parola Mac yerel ekranında kalır |
| **MK-08 · DOĞRULANDI** | v0.8 Gate12 reviewer yetkisinin yeni Yönetim V6.9 görevine aktarılabileceği varsayımı | Önceki Gate12 kapsamı yalnız v0.8; V6.9 owner enrollment ayrı | Grant kabulü öncesi `PRODUCT + TASK_ID + RESULT_ID + reviewerId + keyId + allowedDecision + süre` tam eşleşme |
| **MK-09 · DOĞRULANDI** | İzole `--self-test=12/12` veya `10/10` sonucunu Mac signer saha bitişiyle karıştırma riski | Testler yardımcı araçları doğruladı; Mac üzerindeki Ed25519 imza ya da ledger işlemine yetki kanıtı vermedi | Test raporlarına `TEST_ENV`, `SUBJECT`, `SIMULATED`, `FIELD_EXECUTED`, `AUTHORITY_PROVEN` ekle |
| **MK-10 · DOĞRULANDI** | Python AST çağrı sayısı `0` → gerçek runtime DoneCheck çağrısı yok çıkarımı | Gerçek Python gövdesi JS subprocess içinde `signHumanReviewAttestation`, `recordVerifiedFinish`, `JsonlAuditLedger` çağrıları taşıyor | Çok dilli iç gömülü runtime kodunu ayrı analiz et; negatif yetenek hükmü için gerçek tüm yürütme yolu kontrolü |
| **MK-11 · DOĞRULANDI** | DoneCheck iki commit SHA farkını kaynak motoru değişimi sanma riski | `8b90a8...` → `4181f48...` bir commit ve yalnız iki test dosyası; runtime kaynakları eşdeğer | `EXACT_PIN` ile `SOURCE_EQUIVALENCE` iki ayrı alan olsun; kaynağın aynı olması runtime yetkisini varsaydırmasın |
| **MK-12 · KAYNAK İNCELEMESİ** | Ledger'e iki olay yazımının tek atomik iş olduğu varsayımı | `recordVerifiedFinish` `human_review_authorized` ve `verified_finish` olaylarını ardışık yazar; ara kesinti olasılığı mühendislik riski | Gerçek yazımdan önce ledger eski head, duplicate ID, kısmi olay ve restart/recovery planı denetlensin; kaynak incelemesi ≠ sahada hata gözlemi |
| **MK-13 · DOĞRULANDI** | Tek hipotezle yeni paket veya geniş tarama tekrarlayarak hedefe hızla varma | 561 kaynak / 18 dizin, ardışık dar scan ve hâlâ gerçek signer yetkisi `HOLD`; maliyet oluştu | Aynı hipotez iki denemede yeni kanıt yaratmadığında **GÜVENLİ_DUR / yöntem değiştir**; bir sonraki iş yalnız doğrulanabilir yeni fark üretmeli |
| **MK-14 · DOĞRULANDI** | Github PR yorumlarını ana ürün ilerleme metriği sayma | Çok sayıda izlenebilir yorum var; PR #203 hâlâ açık, gerçek owner imzası yok | Yorum `EVIDENCE_POINTER` olarak sınıflansın; gerçek ürün ilerlemesi özgün kabul kontrolü ile ölçülsün |
| **MK-15 · DOĞRULANDI** | Sohbet sahibi tek kullanıcı olduğundan kapsam onayının otomatik kriptografik grant olabileceği yorumu | Owner `onaylıyorum` kapsam niyeti var; bağımsız Ed25519 grant ve `HumanReview.accepted` yok | `OWNER_INTENT`, `SIGNED_GRANT`, `SIGNED_HUMAN_REVIEW`, `AUDIT_RECEIPT` ayrı kimlikler; tamamlanma ilanı son üçlü özgün kanıta bağlı |
| **MK-16 · SÜREÇ SINIRI** | ChatGPT'nin oturum dışında otomatik dosya izlemesi/güncellemesi beklentisi | Canlı oturumda GitHub dosyası güncellenebilir; kendi başına kesintisiz arka plan yürütme yok | Her yeni gerçek raporda aynı dosyayı bağlı GitHub üzerinden oku, yalnız delta ekle, SHA/commit kaydet; gerekirse ayrı açık planlanmış görev oluştur |

### 3. OSi beklenmedik durumlar sözlüğü

| Gerçek çıktı | Doğru karar semantiği | Güvenli sonraki hareket |
|---|---|---|
| `HOLD_NOT_LOADED` | SSH agent'da o anda yüklenmiş açık anahtar eşleşmesi yok | Signer/bridge sözleşmesini uzlaştır, başka kaynak türlerini ancak gerekliyse incele |
| `PUBLIC_FILES_CHECKED=0` | Test kümesi boş; anahtar var/yok hükmü yok | Bu sorguyu tekrarlamadan owner signer bağlama arayüzüne odaklan |
| `fingerprint=false` + `PEM_UTF8=PASS` | DER bekleyen kontrol ile mevcut PEM metin kimlik hesabı farklı | Canonical fingerprint tanımını normalize et; özel anahtar kontrolü hâlâ ayrı |
| `PASS_TECHNICAL_ONLY` | Makine criteria başarılı, resmî ürün kabulü açık | Yetkili signer → gerçek review → ledger → merge kapılarını koru |
| `SOURCE_PIN=PASS`, `OWNER_GRANT=HOLD` | Dosya bütünlüğü kanıtlı; yetki kapsamı kanıtlanmamış | Güven kökü ve tek göreve özgü izin zincirini doğrula |
| `PRIVATE_KEY_PEM_EXPECTED` | Mevcut bridge PKCS#8/PEM-benzeri key materyali tüketen girdi ister; doğrudan ajan imza API'sı kanıtlanmadı | Anahtar gizliliği korunarak güvenli owner-controlled imza yolu tasarla; mevcut bridge ile uyumunu test et |

### 4. Önleyici kontrol matrisi — uygulanacak mühendislik farkları

Bunlar **ürüne uygulanması önerilen/gereken kontrollerdir**, bu belgeyi oluşturmakla otomatik `PASS` olmazlar.

| ID | Kabul koşulu / gerçek test | Şimdiki mühendislik uygulama durumu |
|---|---|---|
| `KM-01-EVIDENCE-CLASS` | Model beyanı, simülasyon, gerçek Mac testi, bağımsız doğrulama, signed authority ayrı makine alanlarında | `SPECIFIED / IMPLEMENTATION_OPEN` |
| `KM-02-NEGATIVE-COVERAGE` | `0 examined` sonucu otomatik `INSUFFICIENT_COVERAGE`; kapsam tamamlanmadıysa global yokluk sonucu `HOLD` | `SPECIFIED / TEST_OPEN` |
| `KM-03-KEY-REPRESENTATION` | SPKI-DER, raw key, PEM-UTF8 varyant testleri ve sabit vektör; doğru alan adı | `FIELD_DISCOVERY_PASS_PEM_UTF8 / REGRESSION_TEST_OPEN` |
| `KM-04-SIGNER-CONTRACT` | Gerçek source callable, `private_key_pem`/agent/KC karşılaştırması, authorized Ed25519 signature **test environment** + negatif test | `SOURCE_OBSERVED / FIELD_AUTHORITY_HOLD` |
| `KM-05-SCOPE-BOUNDARY` | Başka ürünün Gate12 reviewer kaydı, başka task/result ve chat-intent testlerinde `HOLD` | `SPECIFIED / NEGATIVE_TEST_OPEN` |
| `KM-06-LEDGER-RECOVERY` | Duplicate event, ilk event sonrası kesinti, stale head, yeniden çalıştırma: ledger doğrulama ve güvenli tekrar | `SOURCE_RISK_IDENTIFIED / FAULT_TEST_OPEN` |
| `KM-07-PRE-SEND-FILTER` | Son yanıtta kanıtsız `PASS`, `VERIFIED_FINISH`, `main merged` ifadelerine otomatik engel | `SPECIFIED / TEST_OPEN` |
| `KM-08-ANTI-LOOP` | Aynı hipotez+aynı işlem 2 kez fark üretmeyince yöntem yeniden değerlendirilir | `SPECIFIED / ADOPTION_OPEN` |
| `KM-09-GITHUB-LEASE` | PR expected HEAD ve base yeniden okunur; yalnız gerçek yetkili imza/receipt sonrası owner merge; exact-main yeniden test | `PR_STILL_OPEN / MERGE_HOLD` |
| `KM-10-LEARNING-DELTA` | Aynı olay ID tek satır; düzeltme yeni tarih/revizyon ve kaynak SHA'yla; eski kanıt korunur | `THIS_DOCUMENT_V1_INITIALIZED / FIELD_UPDATES_PENDING` |

### 5. Sonraki tek gerçek ürün hareketi

**`NEXT_SINGLE_ACTION=OWNER_CONTROLLED_ED25519_SIGNER_AND_SCOPED_GRANT_INTEGRATION`**  
Geçerli public reviewer kaydıyla aynı Ed25519 özel anahtarın gerçekten owner kontrolünde olduğunu yerel güvenli ortamda ispatlayan yol belirlenir. Mevcut DoneCheck v1.2 `record_verified_finish` köprüsünün beklediği `private_key_pem` girişi ve korunmuş owner imzalama tasarımı **aynı teknik sözleşmede** karşılaştırılır. Gerçek görev/sonuç kapsamlı owner trust grant ve imzalı `HumanReview.accepted` kanıtlandıktan sonra verified ledger receipt üretilir. Son olarak owner onaylı PR #203 merge ve exact-main CI değerlendirilir.

**Koruma:** Şifre, private key PEM/seed, yetkilendirme tokenı ve ham gizli veriler sohbet, GitHub ve yardımcı öğrenme dosyasına taşınmaz. Canonical kaynaklar orijinal bırakılır; tarihli ve SHA-256 kilitli saha raporları `~/Desktop/AudiV13` içinde; Masaüstü yalnız doğrulanmış kopyadır.

### 6. Sürekli güncelleme sözleşmesi — aynı dosya

1. **Tetikleyici:** Yeni Mac saha çıktısı, güven kökü/bridge kod farkı, bug, yanlış beklenti, bağımsız test sonucu, gerçek onay/ret, PR merge veya exact-main kanıtı geldiğinde.
2. **Toplu al:** Mevcut belgenin en son GitHub branch blob SHA'sı, canonical V3 pin'i, ürün task/result ve son gerçek kaynaklar bir kez okunur.
3. **Farkı sınıflandır:** `OBSERVED`, `HYPOTHESIS`, `ROOT_CAUSE_CONFIRMED`, `DESIGN_DEFECT`, `USER_EXPECTATION_GAP`, `TEST_DEFECT`, `AUTHORITY_BOUNDARY`.
4. **Mevcut ID'yi güncelle veya yeni ID ekle:** Her kayıtta `WHEN`, `EXPECTED`, `OBSERVED`, `EVIDENCE_URI/SHA`, `CAUSE_STATUS`, `FIX`, `TEST`, `STATE`, `NEXT_ACTION`. Tarihçeyi korumak için düzeltme paragrafını veya revizyon satırını ekle. Bir kaynak/deney bir kez sayılır.
5. **Karşıt sınama ve kayıt:** Yetkisiz PASS, yanlış hash temsili, eksik kapsama rağmen negatif hüküm, başka ürün grant'i, kısmi ledger ve kaynak drift senaryolarını yeni farkın uygun alt kümesinde gerçek/izole testle doğrula. Test yeri ve sonucu ayrı göster.
6. **GitHub yazım sınırı:** Yalnız bu öğrenme dosyasının ayrı inceleme dalına commit; önce güncel blob SHA'yı al ve update işleminde kullan. Ürün PR #203, `main`, V3 lock ve canonical OSi kabul kaydı korunur. Her commit ve belge SHA'sı raporlanır.
7. **Güvenli durma:** Otorite kanıtı veya uygulanabilir yeni müdahale yoksa `GÜVENLİ_DUR`, doğrulanmış kazanımları ve tek somut sonraki eşiği kaydet. Belge güncellenmesi resmî ürün bitişini artırmaz.

**Yazım formatı (bir sonraki yeni olay için aynı dosyada çoğalt):**

```text
MK-17 | WHEN=YYYY-MM-DDThh:mm:ssZ | TYPE=... | EVIDENCE_LEVEL=A/B/C/D
EXPECTED=...
OBSERVED=...
SEARCH_SCOPE/ENV=...
EVIDENCE_URI=... | EVIDENCE_SHA256=...
CAUSE_STATUS=CONFIRMED/HYPOTHESIS/UNKNOWN
ENGINEERING_DIFFERENCE=...
NEGATIVE_TEST=NOT_EXECUTED/PASS/HOLD | FIELD_TEST=NOT_EXECUTED/PASS/HOLD
STATE=OPEN/VERIFIED_RESOLVED/HOLD
NEXT_ACTION=...
```

### 7. Öz değerlendirme ve ölçüm (ürün kabulünden bağımsız)

| Ölçü | Başlangıç V1.0 | Hedef ve karar kuralı |
|---|---:|---|
| Geçmiş olaya bağlanan tekil öğrenme kaydı | 16 | Her gerçek yeni olay kapsam doğruluğuyla eklenir; salt sayı kalite değildir |
| Önleyici kontrol sözleşmesi | 10 | Gerçek uygulanmış ve test edilmiş yüzdesi ayrıca izlenir: başlangıç `0/10 FULLY VERIFIED` |
| Mac signer resmî kabul | `HOLD` | Gerçek kriptografik tasdik + yetki + audit PASS |
| Ürün resmi bitiş | `HOLD` | `VERIFIED_FINISH` yalnız tüm G1–G6 şartları gerçek PASS olduğunda |
| Tekrarlı etkisiz müdahale | Ölçüm başlangıcı | Aynı hipotez + aynı müdahalenin ilerleme üretmeyen tekrarını azalt |
| Kanıtsız kesin yokluk / PASS hükmü | Ölçüm başlangıcı | Her yeni hükümde 0 uygunsuz beyan hedefi, bağımsız örneklemle değerlendir |

**ENGÜRÜ çalışma disiplini:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Bu kayıt sekiz aşamanın içinde yaşayan mühendislik geri beslemesidir.

### 8. V1.0 kayıt hareketi

`2026-10-23 / INITIAL_LEDGER_CREATED` — PR #203 ve Mac OSi saha kanıtlarından öğrenme olayları derlendi; mevcut yetkili V3 `main` içeriğine dayanan sınırlarla hizalandı; ürünün resmî durumuna veya owner trust kaydına müdahale edilmedi. **Sonraki sürüm bu dosyaya delta ekler.**