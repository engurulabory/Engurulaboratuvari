# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™
## Yaşayan Hakikat, Fark, Hata ve Önleyici Kontrol Kaydı · V1.3

**Kayıt tarihi:** 2026-10-23  
**Son revizyon:** V1.3 · 2026-10-23 · GitHub taslak PR #206 · GitHub kaynak + izole signer sözleşme testi  
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

| **MK-17 · DOĞRULANDI** | GitHub çok adımlı yazımda dosya commit’i başarılıysa sonraki PR açma adımı da başarıyla bitecek varsayımı | `create_branch` ve `create_file` başarıyla tamamlandı; `create_pull_request` ilk çağrısı zorunlu `repository_full_name` alanı eksikliğiyle reddedildi; şema düzeltilince taslak PR #206 gerçekten açıldı | Her bağlayıcı çağrıdan önce **tam parametre şeması**, her adımdan sonra ayrı işlem receipt’i; kısmi başarıda yeniden baştan başlamak yerine **idempotent toparlama** ve uzak durumu yeniden okuma |

| **MK-18 · KAYNAK DOĞRULANDI / İZOLE TEST** | Mevcut DoneCheck çekirdeğini değiştirmek veya Python köprüsüne her koşulda `private_key_pem` vermek zorunlu sanma | Pinned DoneCheck `recordVerifiedFinish` gerçek API'si **dışarıdan imzalanmış** `attestation` kabul ediyor. PEM isteği OSi `record_verified_finish` wrapper'ının yerel imza üretim tercihidir. Yerel ephemerally generated Ed25519 anahtarıyla, kaynak semantiğini tekrar eden 14/14 **izole sözleşme testi** geçti; gerçek DoneCheck derlemesi ve Mac OSi signer kullanılmadı | Mevcut `humanReviewSigningPayload` tam canonical UTF-8 bytes → owner-kontrollü yerel imza → bağımsız public verify → existing DoneCheck `recordVerifiedFinish` akışı için yeni ayrı writer yaratmadan **bridge adapter**; gerçek sahada CI+OSi+ledger testi gerekli |
| **MK-19 · KAYNAK SÜRÜM FARKI** | Ön hazırlık JSON'undaki `machine_verification.NOT_EXECUTED` alanını bugünkü gerçek CI sonucu sanma | PR #203'ün tarihsel `DONECHECK_TASK_REGISTRATION_PREP_V1.json` dosyası hazırlık anının snapshot'ı; daha sonra GitHub CI artifact 12457199441 içinde 4/4 PASS üretildi. İki kaydın zaman ve yetki kapsamı farklı | Her durum raporu `AS_OF`, `REF_HEAD`, `EVIDENCE_KIND`, `CURRENT_VERIFIED_RESULT_ID` ile birlikte; hazırlık snapshot'ı ile sonraki bağımsız gerçek sonucu üstüne yazmak yerine uzlaştır |
| **MK-20 · DOĞRULANDI / ÖNLEYİCİ DÜZELTME** | Yaşayan dosyanın kendi sayaç ve örnek olay ID şablonunu güncel tutacağı beklentisi | V1.2 değerlendirme tablosu “Başlangıç V1.0” sütununda 19 olay saydı; asıl V1.0 16 idi. Yeni olay şablonu mevcut MK-18 ID’sini örnek verdi ve kopyalamada tekrar ID riski taşıyordu. | Her güncellemede gerçek olay ID kümesi, tarihsel başlangıç sayısı, şablonun sıradaki boş ID olması ve GitHub remote exact blob test edilsin; dönemsel sayı ve güncel sayı ayrı kaydedilsin |

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
| `KM-11-TOOL-TRANSACTION` | GitHub çok adımlı çağrı kasıtlı hatalı parametreyle başarısız olduğunda daha önce oluşturulan branch/dosya korunsun; eksik adım şema düzeltilerek tamamlanıp PR gerçek API üzerinden doğrulansın | `REAL_RECOVERY_PASS_PR_206 / AUTOMATED_REGRESSION_OPEN` |
| `KM-10-LEARNING-DELTA` | Aynı olay ID tek satır; düzeltme yeni tarih/revizyon ve kaynak SHA'yla; eski kanıt korunur | `V1.3_DELTA_REMOTE_EXACT_MATCH_PASS / AUTOMATED_REGRESSION_OPEN` |

| `KM-12-EXTERNAL-ATTESTATION-BRIDGE` | Güncel OSi wrapper, mevcut DoneCheck `humanReviewSigningPayload` ve `recordVerifiedFinish` arayüzlerine bağlı, özel anahtarı JSON/stdin/GitHub'a taşımayan owner-controlled **detached-signature** yolu; orijinal Node validator ve audit kullanımı; yanılma/çift yazım testleri | `SOURCE_INTERFACE_CONFIRMED / ISOLATED_CONTRACT=14/14_PASS / MAC_BRIDGE_IMPLEMENTATION_OPEN` |
| `KM-13-FRESHNESS-RECONCILIATION` | Eski hazırlıkta `NOT_EXECUTED`, sonraki original artifact 4/4 PASS olduğunda rapor `LATEST_TECHNICAL=PASS`, `PREP_HISTORICAL=NOT_EXECUTED`, `OFFICIAL=HOLD` olarak ayrışır | `SOURCE_RECONCILED / AUTOMATED_REGRESSION_OPEN` |

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
MK-<SONRAKI_BOS_ID> | WHEN=YYYY-MM-DDThh:mm:ssZ | TYPE=... | EVIDENCE_LEVEL=A/B/C/D
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
| Geçmiş olaya bağlanan tekil öğrenme kaydı | 16 (V1.0) → 20 (V1.3) | Gerçek yeni olaylar özgün ID ile eklenir; salt sayı kalite değildir |
| Önleyici kontrol sözleşmesi | 13 | Gerçek uygulanmış ve test edilmiş yüzdesi ayrıca izlenir: başlangıç `0/13 FULLY VERIFIED` (KM-11 manuel recovery kanıtı, otomatik ürün kontrol testi değildir) |
| Mac signer resmî kabul | `HOLD` | Gerçek kriptografik tasdik + yetki + audit PASS |
| Ürün resmi bitiş | `HOLD` | `VERIFIED_FINISH` yalnız tüm G1–G6 şartları gerçek PASS olduğunda |
| Tekrarlı etkisiz müdahale | Ölçüm başlangıcı | Aynı hipotez + aynı müdahalenin ilerleme üretmeyen tekrarını azalt |
| Kanıtsız kesin yokluk / PASS hükmü | Ölçüm başlangıcı | Her yeni hükümde 0 uygunsuz beyan hedefi, bağımsız örneklemle değerlendir |

**ENGÜRÜ çalışma disiplini:** Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla → Kanıtla → Bir sonraki ihtiyaçları belirle → İlerlet. Bu kayıt sekiz aşamanın içinde yaşayan mühendislik geri beslemesidir.

### 8. V1.0 kayıt hareketi

`2026-10-23 / INITIAL_LEDGER_CREATED` — PR #203 ve Mac OSi saha kanıtlarından öğrenme olayları derlendi; mevcut yetkili V3 `main` içeriğine dayanan sınırlarla hizalandı; ürünün resmî durumuna veya owner trust kaydına müdahale edilmedi. **Sonraki sürüm bu dosyaya delta ekler.**

### 9. V1.1 canlı öğrenme ve GitHub kurtarma kaydı

`2026-10-23 / MK-17 / GITHUB_CONNECTOR_SCHEMA_RECOVERY` — GitHub inceleme dalı `docs/enguru-osi-muhendislik-kasi-20261023` mevcut `main` commit `1f7dfd708d652764ac74df27dcbbd393779e2b3b` üzerinden üretildi. Öğrenme dosyasının ilk commit’i `60aaffffeba58228513570863dabd09ecf0f7c09`; dosya uzaktan okunarak yerel içerikle birebir eşlendi. İlk taslak PR çağrısı zorunlu `repository_full_name` argümanı eksik olduğu için reddedildi. Yeniden baştan kaynak üretmek yerine yalnız hatalı adım giderildi; **taslak PR #206 OPEN** olarak oluştu. Bu olay **gerçek araç/iş akışı hatası ve gerçek toparlama PASS** kaydıdır; resmi ürün kabulüne etkisi **0**. Kaynak değişimleri yalnız ayrı öğrenme inceleme dalındadır.

**Güncelleme kuralı:** Bu dosya yeni kanıt geldiğinde **aynı yol** üzerinden yeni sürüm ve diff ile güncellenecek; önceki tarih ve kanıt kayıtları korunacaktır.


### 10. V1.2 — Gerçek kalan iş listesi ve uygulanabilir signer bağlantı tasarımı

**Kaynak zaman kaydı:** 2026-10-23 · GitHub API yeniden okuması: Yönetim PR #203 `OPEN`, HEAD `63fe22e7c1ce73adf94b0cbdd40924511e8211cd`, tüm 5 ilişkili Actions run `SUCCESS`, PR review = `0`; yardımcı öğrenme PR #206 `DRAFT / OPEN` HEAD `b49b7cda9444681934a64a01a3b2429dab2d172f`; İcra destek PR #14 `OPEN`, HEAD `f806d3e0e5d68e6f06af96a5a24a83762b49f0ab`. Bunlar ölçüm anı kayıtlarıdır; icrada yeniden doğrulanır.

| Sıra / kapı | İş / zorunlu kanıt | Gerçek hüküm | Sorumlu / bağımlılık |
|---|---|---|---|
| `G1` | Exact PR #203 HEAD, canonical V3 SHA ve GitHub makine `verifyTask` 4/4 kanıtı | `PASS_TECHNICAL_ONLY` | GitHub / korunmuş orijinal artifact |
| `G2-A` | Mevcut owner güven kökü ve Ed25519 imzalama kimliğinin gerçek özel anahtar kontrolü; public PEM match ve güvenli yerel ispat | `HOLD_OWNER_SIGNER` | Gerçek Mac OSi + owner; sohbetten özel anahtar/parola alınmaz |
| `G2-B` | Aynı `TASK_ID + RESULT_ID + REVIEWER_ID + KEY_ID` kapsamlı owner-imzalı canonical grant (owner scope intent ile ayrı) | `HOLD_SCOPED_GRANT` | Mevcut yetkili OSi enrollment yolu; başka ürün Gate12 yetkisi kullanılamaz |
| `G3` | Owner'un gerçek `HumanReview.accepted` kararı ve exact canonical payload'a Ed25519 imzası; DoneCheck public signature verify | `HOLD_SIGNED_REVIEW` | G2-A/B + güvenli detached-signer bridge bağlantısı |
| `G4` | `recordVerifiedFinish` gerçek çağrı, ledger'de `human_review_authorized` + `verified_finish` olayları, doğrulanmış SHA zinciri ve receipt | `HOLD_LEDGER_RECEIPT` | G3 + mevcut ledger recovery/duplicate ID preflight |
| `G5` | Owner yetkili PR #203 merge; sonrasında *yeni* `main` commit ve GitHub CI/exact-main kabulü | `HOLD_MERGE_EXACT_MAIN` | G4; GitHub mergeability tek başına owner release değildir |
| `G6` | Tek resmi nihai hüküm, G1–G5 özgün kanıtı ve Human Threshold karşılaştırması | `HOLD_OFFICIAL_FINISH` | Bütün önceki kapılar; `VERIFIED_FINISH → BITTI_DUR` |
| `AUX` | Mühendislik Kası PR #206 gözden geçirme/merge ve KM kontrollerini ürüne uygulama | `DRAFT_OPEN / INDEPENDENT` | Yardımcı öğrenme işi; G2–G6 resmî bitiş ön şartı değildir |

**Mevcut DoneCheck çekirdeğini kullanarak teknik kapanış yolu (kaynak bazlı tasarım):**

1. `humanReviewSigningPayload(review, signedAt)` — pinned `src/runtime/node/reviewer-attestation.ts` fonksiyonu; imzalanacak metin `canonicalJson({schema:"donecheck.reviewer-attestation/v1",signedAt,review})` UTF-8 baytlarıdır. Tasdik alanları: `scheme=ed25519`, `reviewerId`, `keyId`, `signedAt`, `signatureBase64`.
2. Yetkili OSi owner signer **bu baytları yerelde imzalar**. Güven kökü ve görev/sonuç grant'i kaynakta gerçek doğrulanır. OSi wrapper'ın eski `private_key_pem` zorlaması yerine, yeni *girdi adaptasyonu* gerçek harici `attestation` nesnesini `recordVerifiedFinish({ verificationResult, review, attestation, authority, ledger, finishId })` işlevine aktarır. Bu tasarım kaynak API'siyle uyumludur; henüz Mac runtime üzerinde uygulanmış sayılmaz.
3. `verifyHumanReviewAttestation` ile orijinal imza, kimlik, allowed decisions ve `VerificationResult`/HumanReview bağları test edilir. **Bu API tek başına görev kapsam grant'ini doğrulamıyor:** canonical OSi trust enrollment G2-B ayrıca bağımsız zorunlu kapıdır.
4. `JsonlAuditLedger` mevcut hash zincirini ve duplicate event kimliklerini kontrol eder. `recordVerifiedFinish` iki **ardışık** append yapar; yarım kalmış ilk olay senaryosu için ilk gerçek yazımdan önce durdur/yeniden deneme/iyileştirme prosedürü ve ledger bağımsız doğrulaması gerekir. Çift yazımdan kaynaklanan yeni bitiş beyanı kanıtsız kalır.
5. Owner imzası ve ledger özgün receipt doğrulandıktan sonra GitHub'daki resmî yayıma geçilir. `main` exact SHA güncellenmeden ürün bitişi PASS olamaz.

**Yeni uygulanan gerçek araştırma/doğrulama farkı:** `DoneCheck` pinned `4181f48df5ea0c060d9aa9f40a471c554b44b53d` dosyalarının gerçek API gövdeleri GitHub'da okunup uzlaştırıldı; ephemeral anahtarlı local Node v22 izolasyonunda 14/14 kontrat testi PASS: başarılı detached Ed25519 verify, signedAt/taskId/resultId/reviewer/decision tamper, farklı public key, keyId/reviewer/decision grant, canonical JSON negatif testleri. **Kanıt seviyesi: izole sözleşme simülasyonu / gerçek kriptografik test, ürün Mac OSi veya gerçek DoneCheck derlemesinde production PASS değildir.** KM-12 ve KM-13 canonical ürün onarım/CI testi `OPEN`, toplam ürünle bütünleşik kontrol `0/13 FULLY_VERIFIED`.

**Hemen sonraki tek ürün işi:** `G2-A/G2-B OWNER_TRUST + DETACHED_ED25519_SIGNER_ADAPTER`. Gerçek anahtar ve yetkili grant OSi üzerinde doğrulanınca `G3 → G4 → G5 → G6` bağımlılık sırasıyla tamamlanır. Yeni aynı-tür dosya taraması bağımlılık azaltmaz; yalnız mevcut gerçek signer entrypoint'i veya gerekçeli owner key enrollment farkı açılır.

**V1.2 dosya kontrolü:** `MK-01`–`MK-19` olay kaydı; `KM-01`–`KM-13` önleyici kontrol sözleşmesi; korunmuş geçmiş V1.0/V1.1 kayıtları. Bu doküman kaynak kanıtlı yardımcı kayıttır, **resmî DoneCheck makbuzu veya owner yetkisi yerine geçmez.**

### 11. V1.3 — Mühendislik Kası™ bağımsız kalite puanı ve sabit icra kararı

**Değerlendirme tarihi:** 2026-10-23. **Puan türü:** gerekçeli, **model mühendislik rubriği**; DoneCheck™ yetki kararı, saha kabulü veya bilimsel hata oranı istatistiği değildir. V1.2'nin kanıtlı çalışmaları ve güncel GitHub kaynak durumu esas alındı.

| Ölçüm boyutu | Ölçülen puan | Ağırlık | Gerekçe ve gerçek sınır |
|---|---:|---:|---|
| Mimari ve ENGÜRÜ Süzgeci™ bütünlüğü | 92/100 | %25 | Tek yaşayan dosya, sekiz aşama, tekil ID, yetki kapıları ve tek ana hedef |
| Kaynağa bağlı kanıt / izlenebilirlik | 90/100 | %25 | 19 V1.2 olayının tarihçe ve kaynak bağlantıları; SHA/PR bağları; kaynak tazeliği otomasyonu açık |
| Önleyici sınama ve öğrenme yöntemi | 75/100 | %20 | 14/14 izole Ed25519 kontrat testi ve gerçek GitHub kısmi işlem toparlaması; otomatik regresyon kapsamı henüz tam değil |
| Ürüne yerleşmiş gerçek saha önleme yeteneği | 15/100 | %30 | 13/13 kontrol tanımlı, **0/13 tam üretim entegrasyon + saha kabulü PASS**; Mac owner signer ve son ledger hâlen HOLD |
| **Ağırlıklı değerlendirme** | **65/100** | **%100** | `92×0,25 + 90×0,25 + 75×0,20 + 15×0,30 = 65` |

**Sıfır hata hedefi:** Yön tayini olarak korunur. İşleyen uygulamada hata olasılığının sıfır olduğu **kanıtlanmış değildir**. Hata sınıfı başına test, sahadan geri dönüş, kaçan hata oranı ve bağımsız örneklem ile iyileşme ölçülür.

**Gözlenen kesin eksikler ve tamamlanma koşulları:**

1. **`KM-01..KM-13` ürün entegrasyonu:** 13 kuralın özellik tanımı hazır; tam ürün CI + gerçek saha kabulü `0/13`. Aynı kontrolleri bağımsız yeni bir motor kurmadan mevcut araç/CI/saha akışına göm; her özgün ID için test ve receipt iste.
2. **`G2-A/G2-B` güvenli owner imzası:** Geçerli reviewer public PEM kimliği görüldü, ama aynı private-key kontrolü ve Yönetim V6.9 task/result kapsamlı canonical trust grant sahada doğrulanmadı. Mevcut OSi owner kaynağı esas; kimlik doğrulama macOS'un yerel güvenli arayüzünde olabilir; ChatGPT içinde şifre/private key tüketilmez.
3. **`G3` teknik köprü uyarlaması:** Pinned DoneCheck core mevcut `recordVerifiedFinish` için **önceden oluşturulmuş `attestation`** kabul eder. Mevcut Python OSi wrapper `private_key_pem` ile kendi imzasını üretir. Tek mevcut köprüde owner-controlled detached-Ed25519 tasdikini alacak kontrollü adaptasyon ve gerçek Mac testleri açık. Başka trust kökü veya DoneCheck core açılmaz.
4. **`G4` ledger recovery:** `human_review_authorized` ve `verified_finish` iki ardışık yazım olduğu için gerçek commit öncesi duplicate/partial/restart senaryolarını test et; resmî makbuz + bağımsız ledger head kontrolü gerçek PASS olsun.
5. **`G5/G6` yayın ve nihai kabul:** Owner yetkisiyle [PR #203](https://github.com/engurulabory/Engurulaboratuvari/pull/203) merge, yeni `main` exact SHA'da GitHub CI/saha kabulü; ancak tüm kapılar PASS ise `VERIFIED_FINISH → BITTI_DUR`.

**Bilinçli öncelik ve bağımlılık:**

`G1=PASS_TECHNICAL_4/4 → G2 (OWNER SIGNER + SCOPED GRANT) → G3 (GERÇEK SIGNED HUMAN REVIEW + BRIDGE) → G4 (LEDGER + RECEIPT) → G5 (OWNER MERGE + EXACT_MAIN) → G6 (VERIFIED_FINISH)`

**Tek sonraki gerçek icra hareketi:** `OWNER_CONTROLLED_DETACHED_ED25519_ATTESTATION_BRIDGE`. Önce mevcut OSi'deki gerçek signer/owner trust arayüzünü *işlevsel uyumluluğa* bağla; sonra dar kapsamlı köprü uyarlamasını farklı görev/anahtar/karar negatifleriyle test ederek owner'ın **tek yerel onay etkileşimi** için hazırla. Gerçek owner imzası için yetkili özel anahtar ve grant kanıtı zorunludur; yalnız cihazın açılış şifresi her durumda Ed25519 trust grant olarak yeterli sayılmaz.

**MK-20 düzeltme denetimi:** V1.0 başlangıcı **16**; V1.1 **17**; V1.2 **19**; V1.3 **20** özgün öğrenme olayı. Yeni şablonda mevcut ID tekrarına yol açan örnek giderildi. KM sözleşmesi **13**, tam üretim entegrasyonu ve saha PASS **0/13**. Bu düzeltme **kayıt kalitesi** kazanımıdır; ürün G2–G6 statüsünde ilerleme iddiası yaratmaz.

**Sürüm sınırı:** V1.3 yalnız `docs/enguru-osi-muhendislik-kasi-20261023` inceleme dalındaki bu dosyayı değiştirir. Canonical V3, `main`, PR #203 HEAD, gerçek Mac OSi, trust grant, özel anahtar, ledger ve owner merge korunur. Bir sonraki güncellemede önce SHA/HEAD yeniden okunur ve yalnız kanıtlı yeni delta işlenir.

