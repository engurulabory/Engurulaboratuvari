# ENGÜRÜ Yönetim — F01 V13 Yetki İncelemesi / Karar v1

**STATE:** `PASS_FILE_INTEGRITY / APPROVED_FOR_AUTHORIZED_REVIEW_ONLY / HOLD_OFFICIAL_CRITERIA / HOLD_MAC_BINDING`  
**Tarih:** 2026-10-21  
**Kapsam:** `ENGURU_MAC_ENGINEER_H1_H2_H3_OFFICIAL_4X4_ONLY`  
**Ürün:** ENGÜRÜ Mac Engineer™; sıradaki bağımsız ürün PiLive™.  
**Kaynak:** `ENGURU_V13_F01_HUMAN_THRESHOLD_DECISION_20261021T112700085955Z.md`  
**Kaynak SHA-256:** `3ec5a01b3939b27d82cc60efc83edd944959a4b158fd8e5ff81faf1ed49cac1b` — bu karar incelemesinde yüklenen kaynak dosyanın baytları üzerinden doğrulandı.

## Yönetim hükmü

V13 kararındaki on iki teknik kriter, tanımlı **H1/H2/H3 4+4+4 resmî kabul kapsamı için yetkili insan incelemesine sunulabilecek adaylar** olarak uygun görülmüştür.

Bu hüküm `APPROVED_FOR_AUTHORIZED_REVIEW_ONLY` statüsündedir. Her kriterin gerçek canonical sahibi, reviewer yetkisi, exact branch/HEAD, kanıt sözleşmesi ve Mac Engineer kabul adapter'ı doğrulanıp kendi Human Threshold kararını tamamlayana kadar `OWNER_APPROVED=0/12`, `F01=HOLD_AUTHORITY`, `MAC_BINDING=HOLD`.

Özgün metnin `UNAPPROVED_ENGINEERING_PROPOSAL` statüsü korunur. Bu Yönetim incelemesi o öneriyi değiştirmez; resmî kabul, kriter PASS, anahtar yetkisi veya nihai Verified Finish üretmez.

## Kaynağa bağlı on iki aday

| Kapı | Kriterler | Kabul niteliği |
|---|---|---|
| H1 — Yetkili signer | `SIGNER_SOURCE`, `P256_CHALLENGE`, `ISSUER_GRANT`, `SIGNER_RECEIPT` | Kaynak/provenance, güncel Secure Enclave P-256 challenge, izinli issuer/grant, bağımsız imza/receipt doğrulama |
| H2 — Canonical writer | `WRITER_SOURCE`, `ATOMIC_IDEMPOTENT`, `CONFLICT_RECOVERY`, `WRITER_RECEIPT` | H1 4/4 yetkisi, atomik/tekrar-güvenli işlem, çatışma ve recovery kanıtı, tam receipt |
| H3 — GitHub–OSi | `BRANCH_PROVENANCE`, `LOCAL_REMOTE_PARITY`, `CI_REVIEW`, `GITHUB_RECEIPT` | H2 4/4 yetkisi, korunmuş branch/commit ancestry, exact-head ve CI/review kanıtı, bağımsız remote yazma receipt'i |

## Birincil mevcut yetki kaynaklarıyla mutabakat

1. `engurulabory/Engurulaboratuvari/governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md` GitHub `main` kaynak blob'u `a3fa94c6a65ae768259dea40f066e09ede5ace63`. Yüklenen karar dosyasındaki `origin/main` blob'u ile eşleşir. V13 yerel özellik dalı blob'u `a37c2fbb19a50f5e8b788172b880c116a30d1775` farklıdır; yerel branch gerçek kaynak mutabakatı ayrıca yapılır.
2. DoneCheck v1.2 `docs/FULL_PRODUCT_CONTROLS.md`: `verifyTask` makine doğrulaması ile `recordVerifiedFinish()` yalnız doğrulanmış **Ed25519 reviewer authorization + human accepted + machine pass + tamper-evident durable audit** sonucunda verified-finish receipt verebilir.
3. H1 Secure Enclave P-256 signer/grant yetkisi ve DoneCheck Ed25519 reviewer/attestation yetkisi **iki farklı güvenlik bağı** olarak ayrı ispatlanır.
4. Mac Engineer `PRODUCT_ROADMAP_V1.json` DoneCheck Authority Model yolunu ve mevcut v0.6 kilitli provenance'ı tarif eder; tek başına H1/H2/H3 yeni onaylı kriterleri bildirmez.
5. Bu kontrol yalnız bağlı GitHub görünürlüğü ile sunulan kaynakların incelemesidir. Yerel Mac OSi canonical branch, izinli reviewer kayıtları ve güvenli anahtar kanıtları ayrıca yetkili gerçek ortamda gözlenir.

## Yetkili kararın tek sonuçlandırma kapısı

Önce mevcut canonical kriter sözleşmesinin tam `source path / Git SHA / blob`, 12 kriterin mevcut owner kaydı ve reviewer public-key yetkisi bulunur ve doğrulanır.

- **A — Mevcut yetkili sözleşme bulundu:** Sahip/kriterler tam kaynakla bağlanır, V13 önerilerinin farkı belgeye alınır, `verifyTask` ve Mac runtime/Progress Core™ adapter yetkili kabul zinciri ile test edilir.
- **B — Gerçek yetki boşluğu doğrulandı:** V13'ün on iki adayı yalnız bu dar kapsam için belirlenmiş yetkili insan owner/reviewer tarafından Human Threshold incelemesinden geçirilir; yetki ve karar kanıtı canonical kaynak, Git provenance ve audit ile kayıt altına alınır.
- **HOLD — Yetki/karar kanıtı bekliyor:** F01 `HOLD_AUTHORITY` kalır; missing source/owner/reviewer/adapter alanları somut olarak raporlanır.

Her yolun sonuç kaydı şunları taşır: `OWNER_ID`, `OWNER_AUTHORITY_SOURCE`, `REVIEWER_ID`, `REVIEWER_KEY_ID/PUBLIC_KEY_AUTHORIZATION`, `CRITERIA_SET_SHA`, `BRANCH_COMMIT_BLOB`, `MANDATORY_DONECHECK_EVIDENCE_BINDING`, `MAC_RUNTIME_PROGRESS_CORE_ADAPTER`, `VERIFYTASK_RESULT`, `HUMAN_REVIEW_RECEIPT`. Gizli anahtar içermez.

## Bağlayıcı yürütme sırası ve durum

`H1 4/4 → H2 4/4 → H3 4/4 → Native Mac Engineer OSi → Verified Finish → BITTI_DUR`.

**Şimdi:** `OFFICIAL_H1_H2_H3=0/12`, `F01_F06_CLOSED=0/6`, Native HOLD, Verified Finish HOLD.

Ana F01 yetki kaynağı ve tam kabul adapter'ı ile bağlanır; bağımsız F05'in V13'te kanıtlanan `-sdk` izole build onarımı kalıcı kaynak tarifinde ve gerçek Native saha kabulünde ayrıca tamamlanır.

**Yönetim–İCRA uyumu:** Mevcut PR #191 (Yönetim 100/100) ve ürün PR #14 (Engineer 100/100) inceleme hazırlığıdır; canonical yürürlük, üretim sistemi yazımı, signer grant ve insan onayı yerine geçmez.
