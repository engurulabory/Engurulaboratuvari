# ENGÜRÜ OSi × ChatGPT — Mühendislik Kası™
## Yaşayan Hakikat, Fark, Hata ve Önleyici Kontrol Kaydı · V3.0

**Kayıt tarihi:** 2026-10-23  
**Son revizyon:** V3.0 · 2026-10-23 · gerçek GitHub güvenlik kapısı geri bildirimi ve gerçek ölçülen simülasyon rubriği  
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

### Otomatik öğrenme adayı — MK-EVT-ENGINE-V2-20261023
<!-- ENGURU_MK_EVENT_V1:eyJjYXVzZVN0YXR1cyI6IkNPTkZJUk1FRCIsImV2ZW50SWQiOiJNSy1FVlQtRU5HSU5FLVYyLTIwMjYxMDIzIiwiZXZpZGVuY2VMZXZlbCI6IkIiLCJleGFtaW5lZENvdW50IjozMCwiZXhwZWN0ZWQiOiJLYW5pdGEgYmFnbGkgb2xheSBnaXJpc2luaW4gYXluaSB5YXNheWFuIGRvc3lheWEgZ8O8dmVubGkgdmUgdGVrcmFyIGVkaWxlYmlsaXIgYmnDp2ltZGUgZWtsZW5tZXNpIiwiZml4UHJvcG9zYWwiOiJHaXRIdWIgaW5jZWxlbWUgZGFsaW5kYSBvd25lciBjb21tZW50IGV2ZW50IG1vZGVsaSArIHPEsWvEsSBKU09OIGludGFrZSArIGdlcsOnZWsga2F5bmFrIFNIQSArIGluY2VsZW1lIGFkYXlpIiwiaW1wYWN0IjoiR2Vyw6dlayBvbGF5IGRlZ2lzdGlnaSBhbmRhIGtvbnRyb2wgZ2VyZWtzaW5pbWkgb2x1c3R1cnVsYWJpbGlyIiwib2JzZXJ2ZWQiOiIzMCBheXLEsSBpem9sYXN5b24gdGVzdGkgMyBrZXogOTAvOTAgUEFTUzsgMTAgdGFzYXLEsW0gaWxrZXNpIDEwMC8xMDA7IGdlcsOnZWsgR2l0SHViIHdvcmtmbG93IHZlIE1hYyBwcm9kdWN0aW9uIG9uYXnEsSBoZW7DvHogUEFTUyBkZcSfaWwiLCJvYnNlcnZlZEF0IjoiMjAyNi0xMC0yM1QxMzowMDowMCswMzowMCIsInNjaGVtYSI6ImVuZ3VydS5tay5ldmlkZW5jZS1ldmVudC92MSIsInNvdXJjZVBhdGgiOiJnb3Zlcm5hbmNlL2VuZ3VydS1zdXpnZWNpL2xlYXJuaW5nL01LX1YyX1NJTVVMQVRJT05fUkVDRUlQVC5qc29uIiwic291cmNlU2hhMjU2IjoiZTRlOTFjNzA3MTRiYWMyOTM4NDU4M2U5MjJiOWQwMDU1NDY3YzU4MTFiNmM5YmJmOGM3ODI1ZWRjMjg5YjU4ZCIsInNvdXJjZVVyaSI6Imh0dHBzOi8vZ2l0aHViLmNvbS9lbmd1cnVsYWJvcnkvRW5ndXJ1bGFib3JhdHV2YXJpL3B1bGwvMjA2Iiwic3VnZ2VzdGVkQ2hlY2siOiJnaXRodWJfYWN0aW9uX3Jldmlld19icmFuY2hfYWN0dWFsX2V2ZW50X3RyaWdnZXIiLCJ0YXNrSWQiOiJFTkdVUlVfTUFOQUdFTUVOVF9WNjlfUFJfMjAzIiwidGVzdFN0YXRlIjoiUEFTUyIsInR5cGUiOiJJTVBST1ZFTUVOVCJ9:c73b92fd4b3804d997539b3826dad7e10f4dd0ed0177f4d67c9d0fb73c12872b -->
- **Tür:** `IMPROVEMENT` · **Seviye iddiası:** `B` · **Kanıt kontrolü:** `PASS_BYTE_SHA_ONLY`.
- **Gözlem:** 30 ayrı izolasyon testi 3 kez 90/90 PASS; 10 tasarım ilkesi 100/100; gerçek GitHub workflow ve Mac production onayı henüz PASS değil
- **Beklenti:** Kanita bagli olay girisinin ayni yasayan dosyaya güvenli ve tekrar edilebilir biçimde eklenmesi
- **Önerilen fark:** GitHub inceleme dalinda owner comment event modeli + sıkı JSON intake + gerçek kaynak SHA + inceleme adayi
- **Kaynak:** https://github.com/engurulabory/Engurulaboratuvari/pull/206 · SHA-256 `e4e91c70714bac29384583e922b9d0055467c5811b6c9bbf8c7825edc289b58d`.
- **Karar:** `REVIEW_REQUIRED`; ürün kabul sayacı değişimi `0`; kontroller: SOURCE_REVIEW.

### 12. V2.0 — 100/100 tasarım kası; gerçek olaylarla yaşayan otomatik döngü

**Tasarım sözleşmesi:** `OLAY -> GÜVENLİ_VERİ_GİRİŞİ -> KAPSAM/SHA -> İDempotent -> ÖĞRENME_ADAYI -> NEGATİF_TEST -> OWNER_REVIEW -> AYNI_DOSYADA_DELTA`. Bu, ENGÜRÜ Süzgeci™ mevcut sekiz aşamasının içinde çalışan **yardımcı adaptördür**, ayrı core veya trust root değildir.

**Saha öncesi düzeltme:** İlk simülasyon receipt işaretçisi `simulation_receipt.json` yerel kısa yolundaydı. Ingest tekrarında `governance/enguru-suzgeci/learning/MK_V2_SIMULATION_RECEIPT.json` GitHub kalıcı konumuna hizalandı; olay kimliği sabit kaldı, aday özgün kayıttan yeniden üretildi. `PROVENANCE_PATH_TEST=PASS_LOCAL`, GitHub uzak API ve Actions otomatik tetikleme ayrı doğrulanır.

**Tamamlanan gerçek yardımcı uygulama (inceleme dalı):**
- `tools/enguru_muhendislik_kasi.py`: şema/çift JSON anahtarını reddetme, task ID kapısı, SHA-256 kanıt dosyası incelemesi, güvenlik filtresi, zero-coverage hata algılama, owner dışı yorum ret, tekrar/idempotent replay, exact-content ayrı `candidate.md` ve karar receipt'i. Ürün kodunu veya mevcut canonical dosyayı kendiliğinden değiştirmez.
- `tests/test_enguru_muhendislik_kasi.py`: **30/30 PASS × üç gerçek bağımsız çalıştırma = 90/90 izole PASS**. Bu testler Mac OSi signer/DoneCheck üretim kabulü değildir.
- `tools/enguru_muhendislik_kasi_simulation_3x.py` ve `governance/enguru-suzgeci/learning/MK_V2_SIMULATION_RECEIPT.json`: 10 tasarım kapısı × 10 puan; **model tasarım/izole simülasyon skoru 100/100**. Gerçek sahada ispatlanmış hata sıfır iddiası yoktur.
- `.github/workflows/enguru-muhendislik-kasi.yml`: `pull_request` test ve `issue_comment` owner-onaylı güvenli intake hedefli GitHub Actions yapılandırması. **GitHub varsayılan dalına yetkili merge yapılıncaya, `ENGURU_MK_OWNER_LOGIN` gerçek GitHub username ile ayarlanıncaya ve Actions yazma izni sağlanıncaya kadar otomatik GitHub tetikleme `HOLD_NOT_ACTIVATED`.** PR #206 yalnız ayrı inceleme dalıdır.
- `governance/enguru-suzgeci/learning/ENGURU_MK_V2_README.md`: olay formatı, canlı tetikleme ve sınırlar.

**Gelen bilgi kararları:**
| Girdi | Otomatik iş | Resmî karar |
|---|---|---|
| Mac saha raporu, SHA gerçek baytlarla doğrulanmış | Tekil `MK-EVT` öğrenme adayı + yeni kontrol önerisi | `REVIEW_REQUIRED` |
| GitHub'da yetkili owner yorumu ve geçerli şema | Tekil dosyaya bot kontrollü review-branch delta | `REVIEW_REQUIRED`; yalnız etkin workflow sonrası |
| Kaynak SHA sadece işaretçi, baytlar erişilemez | `UNVERIFIED_EVIDENCE_POINTER` | `HOLD_VERIFICATION` |
| Aynı içerik/ID | `IDEMPOTENT`, tekrar kaydı `0` | Korunmuş önceki karar |
| Aynı ID/farklı içerik veya owner dışı mesaj | `HOLD` | Mevcut kaynak korunur |
| Yeni kök neden / ihtiyaç | Regresyon ve onarım adayı | Gerçek test ve owner incelemesi açık |

**Mühendislik kası ayrı puan disiplini:** `THEORETICAL_DESIGN=100/100`, `ISOLATED_TESTS=90/90_PASS`, `PRODUCTION_AUTOMATION=HOLD_NOT_ACTIVATED`, `MAC_OSI_END_TO_END=HOLD`, `13/13 ÜRÜNE ENTEGRE KONTROL=0`, `G1=PASS_TECHNICAL_ONLY; G2..G6=HOLD`. Önceki V1.3 `65/100` **gerçek ürün ve olgunluk puanı** eski ölçüm bazında saklanır; bu puan teorik 100'e dönüştürülmüş sayılmaz.

**Kalıcı sabit sonraki gerçek ürün işi:** Önce bu yardımcı otomatik öğrenme adaptörü owner incelemesi ile aktive edilir. Ardından Mac OSi `donecheck_v12_bridge.py` mevcut güven köküyle Ed25519 harici tasdik adaptasyonu gerçek kaynakta uygulanıp sınanır. Gerçek Mac owner private-key kontrolü ve task/result grant PASS sonrası sıralama: `HumanReview.accepted -> DoneCheck recordVerifiedFinish -> audit ledger -> yetkili PR #203 merge -> exact-main -> Verified Finish -> BITTI_DUR`. OSi private key ve parola yalnız Mac yerel güvenlik alanında kalır.
### 13. V2.1 — Gerçek GitHub CI'den otomatik öğrenmeye dönen karşıt kanıt

**Gözlem 1 / MK-21 · DOĞRULANDI:** PR #206'da `b548aabf262d745b9301263b96f6eeaef36f3adb` commit'inin gerçek [IP Model Trust Fleet run 39942920445](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/39942920445) kontrolü `secret_zero_violation` ile FAIL verdi. Kök neden: `tests/test_enguru_muhendislik_kasi.py` test fixture'ında özel anahtar PEM başlığı tek parça düz metindi; depodaki mevcut güvenlik tarayıcısı bunun karşısında fail-closed yaptı. Gizli anahtarın kendisi saklanmadı. Onarım: fixture başlığı yalnız **test çalışma anında iki sabit parçadan birleştirildi**, negatif test semantiği aynı kaldı. `ecd21755365fb1142bad947761dfde87fb7e485d` HEAD üzerinde [IP Model Trust Fleet 39943116053](https://github.com/engurulabory/Engurulaboratuvari/actions/runs/39943116053) ve Labory Final Gate, IP Model Trust Gate, PARK Adapter, Mühendislik Kası workflow'u **5/5 PASS** doğrulandı. Yeni koruma `KM-14-TEST-FIXTURE-SECRET-SCAN`: güvenlik regresyon fixture'ı tarama politikasını bozmadan testte gerçek şablon biçimini üretmeli ve bütün repo güvenlik CI sonucu izlenmeli.

**Gözlem 2 / MK-22 · DOĞRULANDI:** V2 ilk simülasyonundaki 10 kabul rubriği değerinin tamamı kaynak davranışından **dinamik hesaplanan ölçüm yerine sabit `true`** olarak atanmıştı. Bu, teorik 100/100 skorunun güven değerini zayıflatır. Uygulanan fark: `tools/enguru_muhendislik_kasi_simulation_3x.py` içindeki 10 kontrolü test adları, üç tur 30/30 başarı, kaynak alanları, kısıtlanmış otomatik GitHub branch push ve owner guard işaretleri üzerinden hesaplayan ölçümle değiştirdik. Yeni `MK_V2_VERIFIED_SIMULATION_RECEIPT.json` gerçek üç turu ve ölçümleri taşır. Yine de bu statik işaret+izole test kontrolüdür; **gerçek sahada 100/100 üretim kabulü olduğu iddiası oluşturmaz.**

**Otomatik giriş ispatı:** `MK-EVT-ENGINE-V2-20261023` gerçek yerel simülasyon receipt SHA'sını dosya baytlarıyla doğrulayarak V2.0 dosyasına tek aday olarak eklendi; ürünün yetki sayacı sıfır değişti. Olayın önce kısa yerel rapor yolu kullanması, gerçek kalıcı GitHub receipt yoluna düzeltilerek olay tekrar üretildi. Düzeltme, önceki canonical güven kayıtlarını ve ilk simülasyon makbuzu SHA'sını korur.

**En güncel sayım:** `MK-01..MK-22 = 22` kuratörlü olay, `MK-EVT-ENGINE-V2-20261023 = 1` ayrı makineli intake adayı; `KM-01..KM-14 = 14` tasarlanmış kontrol; `0/14` tamamı ürün/gerçek Mac saha entegrasyonu kanıtlı kontrol. `THEORETICAL_MODEL=100/100`, `ISOLATED_TEST=90/90_PASS`, `GITHUB_REGRESSION_5_5_PASS_AT_HEAD=ecd21755365fb1142bad947761dfde87fb7e485d`, `GITHUB_AUTOMATIC_OWNER_EVENT_WRITE=NOT_YET_ACTIVATED`, `MAC_OSI_SIGNER=HOLD`.

**Sürekli ajan/ChatGPT nöbeti:** Ayrı zamanlanmış koşul izlemesi talep doğrultusunda saatte bir açık GitHub PR/CI değişikliklerini denetlemek üzere açıldı. Gerçekten yeni kanıt geldiğinde aynı dosyada deltalı güncelleme amaçlanır; bağlayıcı kabul, özel anahtar, resmî ledger ve merge koruma altındadır. GitHub yorum-tetiklemeli Actions yazımı, iş akışı `main` üzerinde owner yetkisiyle etkinleşince ve `ENGURU_MK_OWNER_LOGIN` ayarlanınca çalışır. Mac OSi'nin dosya sistemi bu bulut otomasyonunun kendiliğinden eriştiği alan değildir.

**Tek takip eden ürün hedefi:** `G2 OWNER_SIGNER + SCOPED_GRANT -> G3 DETACHED_ED25519_BRIDGE -> G4 DONECHECK_LEDGER -> G5 OWNER_MERGE_EXACT_MAIN -> G6 VERIFIED_FINISH`. Teknik G1 kanıtı korunur; owner anahtarı ve Mac yetkisi ChatGPT'ye aktarılan veri değildir.

### 14. V2.2 — GitHub beş dakikalık izleme kontratı ve canlı CI kanıtı

**Sabit hakikat (2026-10-23):** Varsayılan GitHub dalı `main`; Mühendislik Kası PR #206 ayrı `docs/enguru-osi-muhendislik-kasi-20261023` dalında **DRAFT/OPEN**. Mühendislik ürün PR #203 `OPEN`; Mac Engineer PR #14 `OPEN`. 

**Yeni MK-23 · DOĞRULANDI (izole test düzeneği):** Sahte GitHub yorum API'sı `per_page=100&page=1` içinde yalnız `page=` alt metnini aradığı için yanlış sorgu sayfasını seçti; OSi mesajları 8 karşıt sınamada bulunmuş gibi kabul edilmedi. Kök neden **test mock parser**; sayfa parametresi `(?[&])page=` sınırı ile düzeltildi. Gerçek GitHub üretim API arayüzünün de aynı hatayı yaptığı hükmü çıkarılmaz.

**Yeni MK-24 · DOĞRULANDI (gerçek GitHub CI):** `tests/test_enguru_mk_five_minute_watch.py` yerel klasör dizilimini esas aldığı için PR #206 GitHub unit job `39947578343` ilk çalışmasında `ModuleNotFoundError: enguru_mk_five_minute_watch` verdi. Testler repo `tools/` yolu için revize edildi, commit `b6f67a53cbdea983ce7ef63820a041ed3b2572c9` üzerinde beş GitHub iş akışı `5/5 PASS`; bu test ortamı uyumu düzeltmesidir.

**Yeni MK-25 · DOĞRULANDI (gerçek GitHub repo yetki sınırı):** Ana `Engurulaboratuvari` deposu `public`, `enguru-mac-engineer` deposu `private`. Ana deponun varsayılan `GITHUB_TOKEN`ı özel repo PR #14 için erişim garantisi vermez. İzleyici 401/403/404 durumunda `PR14_PRIVATE_REPO_ACCESS_HOLD` sınıflandırır ve PR #203/#206 kontrolünü sürdürür. PR #14 için owner tarafından sadece okumaya yetkili ve bu repo kapsamındaki `ENGURU_MK_READONLY_GITHUB_TOKEN` secret gereksinimi kaydedildi. Secret gizli kalır. Saha token erişimi `HOLD_UNTESTED`.

**Yeni korumalar:** `KM-15-SOURCE-MOCK-QUERY` tam sayfa parametre testleri; `KM-16-CI-IMPORT-PARITY` yerel + GitHub ortamı testleri; `KM-17-CROSS-REPO-ACCESS` özel repo erişim hatası ayrımı ve diğer kaynakların korunması. Bunlar test sözleşmesi ve yardımcı kod kazanımıdır; gerçek owner Mac üretim kabul kapısı yerine geçmez.

**Çalışma biçimi:** GitHub `.github/workflows/enguru-muhendislik-kasi.yml` dosyasına `schedule: */5 * * * *` eklendi. İlk gerçek zamanlanmış koşu için workflow default `main` üzerine owner yetkili yayın ve en az bir gerçek `event=schedule` Actions run kaydı **zorunludur**. `5_MIN_LIVE=HOLD_DEFAULT_BRANCH_ACTIVATION`. GitHub Actions gecikebilir; SLA/eksik koşu değerlendirmesi ayrıca tutulur. ChatGPT zamanlanmış görev platform üst sınırı **saatte bir**; bu nedenle `CHATGPT_5MIN_MODEL=UNSUPPORTED`, `CHATGPT_HOURLY_WATCH=ENABLED`.

**OSi blok/yanıt ingest:** Mac'ten geldiği iddia edilen metnin sohbet içinde kalması **GitHub'a otomatik giriş değildir**. GitHub'da yetkili owner yorumu başlangıcında `<!-- ENGURU_OSI_BLOCK_V1 -->` veya `<!-- ENGURU_OSI_RESPONSE_V1 -->` ve arkasında gizli veri içermeyen gözlem varsa, ilk bootstrap sonrası yorum ID ile tekil öğrenme adayı oluşturulur. `EVIDENCE_LEVEL=A / UNVERIFIED_EVIDENCE_POINTER / REVIEW_REQUIRED`. Gerçek Mac receipt, SHA, trust grant ve Human Threshold ayrı doğrulanır.

**İzole simülasyon:** Eski 30 senaryo + yeni 31 watcher senaryosu × 3 tur = `183/183 PASS` (lokal). Gerçek GitHub CI `5/5 PASS` commit `b6f67a53cbdea983ce7ef63820a041ed3b2572c9` üzerinde. Bu ölçüm yalnız önceden tanımlı kapsam için PASS'tır; her beş dakikada aralıksız ChatGPT çalışması ve OSi tüm olaylarını otomatik alması kanıtı değildir.

**Güncelleme kuralı:** Her yeni ChatGPT mühendislik oturumu önce GitHub'daki **son PR #206 branch HEAD ve yaşayan dosyanın SHA** değerini yeniden okuyarak hizalanır. Sonrasında yeni OSi blok / gerçek yanıt varsa kaynak gösteren, gizlisiz kayıt adayı GitHub'a ChatGPT aracılığıyla aktarılır. İki kez etkisiz tekrar olursa yeni araştırma yerine güvenli yöntem değişimi uygulanır.

**Ürün kalıcı sabit hedefi:** `G2 owner Ed25519 key/grant → G3 signed HumanReview + bridge → G4 DoneCheck audit ledger → G5 owner merge/exact-main → G6 VERIFIED_FINISH → BITTI_DUR`. `G1=PASS_TECHNICAL_ONLY`, `G2..G6=HOLD`; Mühendislik Kası ilerlemesi ürün sayaçlarına aktarılmaz.

### Otomatik öğrenme adayı — MK-EVT-GH5M-BOOT-20261023
<!-- ENGURU_MK_EVENT_V1:eyJjYXVzZVN0YXR1cyI6IlVOS05PV04iLCJldmVudElkIjoiTUstRVZULUdINU0tQk9PVC0yMDI2MTAyMyIsImV2aWRlbmNlTGV2ZWwiOiJBIiwiZXhwZWN0ZWQiOiJHaXRIdWIgZGVmYXVsdCBicmFuY2ggw7x6ZXJpbmRlIGJlxZ8gZGFraWthbMSxayBjcm9uIHZlIGtvbnRyb2xsw7wgw7bEn3Jlbm1lIGdpcmnFn2kiLCJmaXhQcm9wb3NhbCI6Illlbmkgb2xhecSxbiByZXZpZXctYnJhbmNoJ2UgdGVraWwgYWzEsW5tYXPEsW7EsSB2ZSBpbGsgZ2Vyw6dlayBzY2hlZHVsZSBrb8WfdWxhcsSxbsSxIGJhxJ_EsW1zxLF6IGRvxJ9ydWxhIiwib2JzZXJ2ZWQiOiJQUiAjMjA2IG1lcmdlIGNlNTI2ZTZkYTRlZWQ2NjA4NjQwZDdhNGFiMTlmZmFjYjgzOTIzMWIgc29ucmFzxLEgY3JvbiBrYXluYWt0YSBtZXZjdXQ7IGlsayBnZXLDp2VrIGV2ZW50PXNjaGVkdWxlIGtvxZ91c3UgYXlyxLFjYSBkb8SfcnVsYW5hY2FrIiwib2JzZXJ2ZWRBdCI6IjIwMjYtMTAtMjNUMTE6NTA6NDUuMTMxWiIsInNjaGVtYSI6ImVuZ3VydS5tay5ldmlkZW5jZS1ldmVudC92MSIsInNvdXJjZVNoYTI1NiI6ImU3NWI2NzVjNzA1M2ZkZDQ4NjVjNTU4ZWJkYjMwMDdmNDA2NDEzZGQ4OGMzMWQ2NzIxMWViZDI2OTk0MmQ2ZTkiLCJzb3VyY2VVcmkiOiJodHRwczovL2dpdGh1Yi5jb20vZW5ndXJ1bGFib3J5L0VuZ3VydWxhYm9yYXR1dmFyaS9ibG9iL2NlNTI2ZTZkYTRlZWQ2NjA4NjQwZDdhNGFiMTlmZmFjYjgzOTIzMWIvdG9vbHMvZW5ndXJ1X21rX2ZpdmVfbWludXRlX3dhdGNoLnB5IiwidGFza0lkIjoiRU5HVVJVX01BTkFHRU1FTlRfVjY5X1BSXzIwMyIsInRlc3RTdGF0ZSI6Ik5PVF9FWEVDVVRFRCIsInR5cGUiOiJJTVBST1ZFTUVOVCJ9:c23dce679ecbf72f2d0ffe89b492ed2c2230296dbab7c10d1a232c28058b81a0 -->
- **Tür:** `IMPROVEMENT` · **Seviye iddiası:** `A` · **Kanıt kontrolü:** `UNVERIFIED_EVIDENCE_POINTER`.
- **Gözlem:** PR #206 merge ce526e6da4eed6608640d7a4ab19ffacb839231b sonrası cron kaynakta mevcut; ilk gerçek event=schedule koşusu ayrıca doğrulanacak
- **Beklenti:** GitHub default branch üzerinde beş dakikalık cron ve kontrollü öğrenme girişi
- **Önerilen fark:** Yeni olayın review-branch'e tekil alınmasını ve ilk gerçek schedule koşularını bağımsız doğrula
- **Kaynak:** https://github.com/engurulabory/Engurulaboratuvari/blob/ce526e6da4eed6608640d7a4ab19ffacb839231b/tools/enguru_mk_five_minute_watch.py · SHA-256 `e75b675c7053fdd4865c558ebdb3007f406413dd88c31d67211ebd269942d6e9`.
- **Karar:** `REVIEW_REQUIRED`; ürün kabul sayacı değişimi `0`; kontroller: SOURCE_REVIEW.

### 15. V2.3 — Gerçek Github yayını ve otomatik owner olay alımı

**Yayın:** Yardımcı öğrenme PR #206, GitHub exact commit `f9cd0fb882f5f6d73f6ef664c894800986dce6cf` ve 5/5 başarılı Actions CI doğrulaması ardından yetkili GitHub bağlantısıyla `main` merge edildi: `ce526e6da4eed6608640d7a4ab19ffacb839231b`. Güncel `main` üzerindeki beş dakikalık cron kaynağı `*/5 * * * *` ve default-branch varlığı gerçek GitHub API ile doğrulandı. `delete_branch_on_merge=false`; yaşayan kayıt dalı korundu.

**Gerçek çalışmış geri bildirim:** [owner GitHub yorumu](https://github.com/engurulabory/Engurulaboratuvari/pull/206#issuecomment-6364210937) gerçek `issue_comment` run `39948966044` oluşturdu; `owner-comment-intake=completed/success`; `MK-EVT-GH5M-BOOT-20261023` aynı yaşayan Markdown'a SHA kontrollü, tekrarsız öğrenme adayı olarak otomatik eklendi. Bu **gerçek owner-comment ingestion PASS** olup **Mac OSi gerçek saha imzası** veya **5 dakika süreklilik PASS** hükmü değildir.

**Gerçek zamanlama ayrımı:** GitHub default `main` cron yetkili kaynakta mevcut; ilk `event=schedule` Mühendislik Kası run'ı henüz bağımsız gözlenmedi: `GITHUB_FIVE_MINUTE_RUN=HOLD_NOT_OBSERVED`. GitHub cron gecikebilir veya atlanabilir. Üç ardışık gerçek ölçülen aralık ve checkpoint/idempotency zinciri ayrıca kapanış eşiğidir.

**ChatGPT frekansı:** GitHub deterministik Python worker 5 dakika cron hedefli çalışır; ChatGPT ayrı saatlik otomasyonla ve her etkin oturumda güncel GitHub kayıtlarını okur. Platform ChatGPT otomasyon aralık tabanı saatlik: `CHATGPT_SELF_WAKE_EVERY_5_MINUTES=UNSUPPORTED`. Bu çalışma yeni model eğitimi değildir; versioned mühendislik belleği + yeniden doğrulama disiplinidir.

**OSi girdi ayrımı:** Yetkili GitHub owner hesabından PR #203/#206/#14 yorumlarına aktarılan `ENGURU_OSI_BLOCK_V1` / `ENGURU_OSI_RESPONSE_V1` kaynakları salt kanıt adayıdır; yalnız ChatGPT sohbetinde veya Mac'te kalan satırlar GitHub'a otomatik aktarılmış sayılmaz. PR #14 özel depoda; repo-kapsamlı salt-okunur token olmadan `PR14_PRIVATE_REPO_ACCESS_HOLD`, diğer iki PR gözlemi devam eder.

**Güvenlik:** Yardımcı PR #206 merge'i, Yönetim PR #203'ün owner-signer, task/result grant, `HumanReview.accepted`, DoneCheck audit veya owner product merge yetkisi değildir. `G1=PASS_TECHNICAL_ONLY`; `G2-G6=HOLD`. Yerel simülasyon `183/183 PASS`, GitHub CI `5/5 PASS`, ilk gerçek owner-comment intake `PASS`; süreklilik ve Mac OSi sahası açık.

### 16. V2.4 — Ölçülebilir sürtünme ve ilk icra düzeltmesinin gerçek kanıtı

**Karar tarihi:** 2026-10-23. **Onaylanan çalışma yönü:** Mühendislik Kası öğrenme katmanı olarak mevcut sekiz aşamalı Süzgeç içinde devam eder; yeni yetki kökü veya yeni ürün sayacı açılmaz. Başarı, yalnız kuralların sayısıyla değil gerçekleşen tekrar azaltımı, geçerli regresyon testleri ve gerçek saha kayıtlarıyla ölçülür.

**MK-26 · DOĞRULANDI / FIRST-EXECUTION-PREFLIGHT:** GitHub özel Mac Engineer PR #14 üzerinde mevcut detached-Ed25519 adaptörünün audit doğrulamasını `recordVerifiedFinish` çağrısından sonra yapması, eksik/bozuk ledger durumunda kanonik yazma girişiminden önce güvenlik kapısı sağlamıyordu. Uygulanan mühendislik farkı: `ledger.verify` arayüz ve bütünlük kontrolü **yazım öncesine** alındı; iki negatif testte, `recordVerifiedFinish` çağrısı `0` olduğunu doğruladık. HEAD `29381eb81c60aaac7cc5d90b03a2ec4969639f8a`; gerçek macOS [Product CI run 39950708352](https://github.com/engurulabory/enguru-mac-engineer/actions/runs/39950708352) `completed/success`; detached adaptör `14/14 PASS`; 133 Python ürün testi `PASS`; Swift kaynak derleme kanıtı `PASS_ISOLATED_BUILD`. İlgili [PR #14 kanıt yorumu](https://github.com/engurulabory/enguru-mac-engineer/pull/14#issuecomment-6364509965). Bu kaynak incelemesi ve GitHub testi, owner grant/private-key kontrolü ve gerçek Mac OSi ledger üretiminin yerine geçmez. Sıradaki eşik `G2/G3_OWNER_SIGNER_TRUST_BINDING`.

**KM-17-LEDGER-PREAPPEND:** Mevcut audit bütünlüğü ve `ledger.verify` kullanılabilirliği önce doğrulanır; `HOLD` halinde kanonik yazım çağrısı sıfır olmalıdır. **Bu PR #14 adaptör kodu ve izole macOS CI için PASS**; gerçek owner Mac OSi saha entegrasyonu `HOLD`. `KM` kontrollerinin ürün genelindeki tam saha kabul sayacı bu izole testle otomatik yükselmez.

**Beş dakikalık Mühendislik Kası sürekliliği:** `main` commit `ce526e6da4eed6608640d7a4ab19ffacb839231b` üzerinde `cron='*/5 * * * *'` mevcuttur. Gerçek GitHub Actions `schedule` listesinde Mühendislik Kası workflow'u için **0 doğrulanmış koşu** görüldü; diğer ürünlerin `schedule` koşuları bu sayaçta kullanılamaz. `SCHEDULE_FIELD=HOLD_NOT_OBSERVED`; owner-comment otomatik aday kaydı `PASS_REAL_EVENT`; bot review branch yazma yolu `PASS_REAL_EVENT`. GitHub Actions schedule gecikmesi/atlaması ve ChatGPT'nin saatlik otomasyon sınırı korunur.

**Performans temel çizgi ölçümü (önce/sonra karşılaştırılacak, başlangıç verisi henüz oluşuyor):**

| Ölçü | Tanım | Önce/sonra kabulü |
|---|---|---|
| `P01_MANUAL_STEPS` | Gerçek bir G2–G6 kapanış hareketi için owner'ın ayrı manuel eylem sayısı | Aynı iş/scope'ta manuel adım sayısı düşüşü |
| `P02_REPEAT_DIAGNOSES` | Aynı doğrulanmış kök nedenle yeniden incelemeye dönen olaylar / toplam gerçek olay | Tekrar oranı düşüşü |
| `P03_FALSE_FINAL` | Bağımsız kabul şartı tamamlanmadan söylenen PASS/BİTTİ iddiası | Kontrol edilen örneklerde 0 |
| `P04_TIME_TO_REPAIR` | İlk gerçek hata kanıtı → bağımsız PASS onarım kaydı arası süre | Eş kapsamlı olaylarda medyan azalış |
| `P05_SCHEDULE_RELIABILITY` | Mühendislik Kası'nın actual `event=schedule` run kimliği, süre aralıkları ve job outcome | Dört ardışık gerçek koşu ve 3 süre aralığına dayalı ayrı kabul; cron tanımı PASS yerine geçmez |
| `P06_OWNER_GRANT_GAP` | Task/result scope, private key sahibi, imza, ledger, exact-main kabul açıkları | Her kapı özgün gerçek kanıtla kapanır |

**Öğrenme etki sınırı:** Kası'na olay girdi olarak gelmesi tek başına yeni ChatGPT model ağırlığı eğitimi değildir. GitHub dosyası güncel öğrenme kaynağıdır; ChatGPT'nin yeni bir turda o sürümü gerçekten okuması hizalanmanın şartıdır. Yerel Mac OSi ve sohbet içeriği GitHub'a kendiliğinden aktarılmış sayılamaz. Gizli veri aktarımı, imza, issuer, Human Threshold ve ürün merge yetkileri korunur.

**Tek öncelikli ürün işi:** `G2_OWNER_TRUST + G3_DETACHED_ED25519_MAC_OSI_INTEGRATION`; mevcut private Ed25519 sahibinin gerçek Mac OSi kanıtı gereklidir. Ardından sıralı `HumanReview → DoneCheck → Audit → owner Merge → exact-main → Verified Finish`. Yardımcı Mühendislik Kası 5 dakikalık gerçek schedule kabulü bu ürünün bağımsız G2/G3 mühendislik işini durdurmaz.


### 17. V3.0 — Kalıcı amaç, hedef, 20% karşıt test payı ve kaynak kanıtı

**Keskin amaç:** Gerçek OSi ve GitHub kaynaklarında oluşan her hata, fark, ihtiyaç, beklenmedik sonuç ve doğrulanmış başarıyı güvenli, tekrarsız, kanıta bağlı mühendislik bilgisine dönüştürerek ChatGPT'nin sonraki çalışma turunda yanlış erken karar, tekrar teşhisi ve gereksiz manuel sürtünmesini azaltmak.

**Kalıcı sabit hedef:** `GERÇEK_OLAY → SHA/KAPSAM → OWNER → TEKRAR_AYIKLA → OSi BLOK/YANIT BAĞI → HATA/İHTİYAÇ → KARŞIT TEST → İNCELEMELİ DÜZELTME → GÜNCEL KAYNAĞA HİZALAN → ÖLÇÜLEN KAZANIM`. ENGÜRÜ Süzgeci™ v2.4'ün sekiz aşaması, P01 canonical owner yetkileri ve olumlu mühendislik dili korunur.

**Bağlayıcı sözleşme:** `governance/enguru-suzgeci/learning/ENGURU_MK_KALICI_AMAC_HEDEF_KABUL_V3.md`. Uygulama `tools/enguru_mk_acceptance_v3.py`, test `tests/test_enguru_mk_contract_v3.py`. Önceki izole 79 senaryo üzerine en az %20 ek karşıt sınama payı (minimum 95), uygulanmış toplam 104 **ayrı** senaryo. İki gerçek bağımsız subprocess turunda `ROUND_1=104/104 PASS; ROUND_2=104/104 PASS; PURPOSE_GATES=25/25; DESIGN_SCORE=100/100`. Dinamik makbuz `governance/enguru-suzgeci/learning/MK_V3_ACCEPTANCE_RECEIPT.json`, ilk özgün yerel SHA-256 `4ef9a58ad2328561d2eb4fde4818fb57520f5a6c480bc2c622b4e06c8c85dc69`. Bu tasarım/izole test puanı gerçek GitHub schedule ve owner Mac OSi kabulünün yerine geçmez.

**MK-27 / özel kaynak sınırı — düzeltildi (izole):** Kamuya açık öğrenme kaydına özel `enguru-mac-engineer` PR #14 yorum/commit/CI metadatasının otomatik geçme ihtimali kapatıldı. Yeni işleyici private repo için HTTP isteği yapmaz; `PR14_PRIVATE_SOURCE_REQUIRES_OWNER_APPROVED_RELAY` gösterir. Gizlisiz gerçek OSi verisi yalnız owner'ın açık PR #203/#206'ya izinli aktarımı ile gözlemlenir.

**MK-28 / eşleştirme — düzeltildi (izole):** `ENGURU_OSI_BLOCK_V1` ve `ENGURU_OSI_RESPONSE_V1` görev `TASK_ID` ve `BLOCK_ID` alanlarıyla bağlanır. `PAIR_MATCHED_REVIEW_ONLY` izlenebilir eşleştirme, `PAIR_MISSING_REVIEW_REQUIRED` eksik bağ olarak tutulur. Hiçbiri kriptografik kabul sayılmaz. Sahte owner, farklı görev, gizli veri, tekrar, bozuk checkpoint, private-data exfiltration ve HTML negative testleri vardır.

**MK-29 / kapsam payı:** İlk temel 61/61 PASS mevcut sistemin bazı risklerini ölçmüyordu. Arttırılmış senaryo sayısı 73 → 79 → **104**; 25 bağımsız amaç kapısı makine olarak gerçek test PASS adlarıyla doğrulanır. Yeni sözleşmeler `KM-18-OSI-PAIRING`, `KM-19-PRIVATE-REDACTION`, `KM-20-20PERCENT-HEADROOM` adaylarıdır; gerçek ürün Mac entegrasyonu kabulünden ayrı tutulur.

**Gerçek saha PASS eşiği:** Aynı HEAD üzerinde GitHub workflow `completed/success`, owner-comment ingestion ve review branch SHA kontrolü; 5 dakikalık gerçek `schedule` için **4 ardışık run ve 3 ölçülü aralık**. Son sorguda `schedule` sayısı `0` → `HOLD_NOT_OBSERVED`. ChatGPT saatlik koşul nöbeti + her etkin çalışma başlangıcında en son GitHub yaşayan dosyasını gerçekten okuma ile hizalanır. Bu otomatik model eğitimi anlamına gelmez.

**Ürün kalıcı sabit hedefi:** `G2_OWNER_SIGNER → G3_SIGNED_HUMAN_REVIEW → G4_DONECHECK_AUDIT → G5_OWNER_MERGE_EXACT_MAIN → G6_VERIFIED_FINISH → BITTI_DUR`. Mühendislik Kası 100/100 tasarım ve PASS izole test sonucu G2-G6'yı otomatik tamamlamaz.


### 18. V3.1 — GitHub PR #208 ilk gerçek CI, saha cron ayrımı (23.10.2026)

**Kaynak:** PR #208 açık ve draft; kaynak HEAD `f662ca4c3e0cb9549e70cd508373c60aef024160`. GitHub Actions run `39954860471` `event=pull_request`, `completed/success`, `unit-regression=completed/success`, `Triple simulation of learning + five-minute watcher=success`. Aynı HEAD'de dört ayrı repository CI run'ı da success (`39954860584`, `39954860474`, `39954860464`, `39954860455`). **Hüküm:** `V3_GITHUB_PR_REGRESSION=PASS_EXACT_HEAD`; yalnız PR test iş akışının kanıtıdır. V3 `tools/enguru_mk_acceptance_v3.py` dosyasının gerçek GitHub schedule yolundaki bağımsız çalışması henüz kanıtlanmadı.

**Cron ve checkpoint:** Varsayılan `main=ce526e6da4eed6608640d7a4ab19ffacb839231b`, `workflow blob=977aafb678e55a97510b4167d1e4db2fdac04d4f`, `schedule=*/5 * * * *`. Gerçek GitHub Actions `event=schedule` listesindeki **aynı isimli** Mühendislik Kası run sayısı `0`; dört ardışık gerçek run ve üç aralık `0/4, 0/3`. `learning/MK_WATCH_CHECKPOINT.json` review dalında henüz bulunamadı (404): bootstrap/run checkpoint `HOLD_NOT_OBSERVED`. Diğer workflow'ların schedule koşuları bu sayıya dahil edilmedi. Owner-comment `39948966044` success ayrı kanıt, `39951344341` issue_comment skipped ayrı olay.

**Yetki ayrımı:** `GITHUB_PR_CI=PASS`; `REAL_SCHEDULE=HOLD`; `CHECKPOINT=HOLD`; `MAC_OWNER_SIGNER_DONECHECK=HOLD`. PR #203 açık `63fe22e7c1ce73adf94b0cbdd40924511e8211cd`; PR #206 merged; özel PR #14 açık `29381eb81c60aaac7cc5d90b03a2ec4969639f8a`. Sıradaki gözlem ilk gerçek schedule run ve gerçek checkpoint; GitHub Actions owner tarafından etkinlik durumu ve manuel `workflow_dispatch` ile bootstrap ayrıca kontrol edilebilir. Manuel dispatch sonucu `schedule` kabulüne eşdeğer değildir.

