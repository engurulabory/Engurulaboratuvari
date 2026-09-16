# ENGÜRÜ YAYIN MOTORU™ v0.1 — Foundation Specification

## STATE
**TECHNICAL THEORY — PASS**
**IMPLEMENTATION — HOLD**
**REAL FIELD VERIFIED FINISH — HOLD**

Bu belge, ENGÜRÜ YAYIN MOTORU™ v0.1 için uygulanabilir ve test edilebilir foundation sözleşmesidir.

Temel hüküm:

> Yayın, dosyayı internete yüklemek değildir. Yayın; doğrulanmış bir kaynağın doğrulanmış bir domain üzerinde, geri alınabilir ve kanıtlanabilir biçimde canlıya bağlanmasıdır.

Kanonik zincir:

`Source → Build → Artifact → Preview → Human Threshold → Production → Domain → DNS → TLS → Public Response → Source Parity → Evidence → DoneCheck™ → VERIFIED LIVE`

---

## 1. AMAÇ

Tek bir Mac terminal yüzeyinden yaklaşık 10–15 web sitesini yönetmek.

Mac yalnız **Control Plane**'dir.
Production runtime Mac değildir.

Mac kapanırsa siteler yayında kalmalıdır.

### V0.1 ana hedefleri

- tek domain girdisiyle doğru site kaydını bulmak,
- exact source doğrulamak,
- deterministic build üretmek,
- artifact digest üretmek,
- Cloudflare-first yayın yapmak,
- DNS/TLS/HTTPS doğrulamak,
- source ↔ deployed artifact parity kanıtlamak,
- rollback noktası üretmek,
- Evidence Receipt yazmak,
- DoneCheck™ girdisi üretmek,
- production publication ve rollback için Human Threshold™ korumak,
- domain satın alma bedeli dışında zorunlu yeni altyapı maliyeti oluşturmamak.

---

## 2. FOUNDATION THEORY

### 2.1 Verified Publication Theory™

`DEPLOY != VERIFIED PUBLICATION`

Bir yayın yalnız aşağıdaki koşulların tamamı sağlanırsa **VERIFIED LIVE** olabilir:

1. exact source commit doğrulanmış,
2. source tree temiz ve beklenen branch üzerinde,
3. build başarılı,
4. artifact digest sabitlenmiş,
5. doğru target account/project seçilmiş,
6. domain doğru siteye bağlı,
7. DNS doğrulanmış,
8. TLS geçerli,
9. HTTPS public response başarılı,
10. deployed artifact ile source/artifact provenance bağlanmış,
11. önceki verified release rollback noktası olarak kayıtlı,
12. evidence receipt yazılmış,
13. DoneCheck™ PASS,
14. production mutation için Human Threshold™ geçmiş.

Eksik koşul varsa olumlu final hüküm verilemez.

### 2.2 Control != Runtime Principle™

Mac:
- kontrol eder,
- doğrular,
- yayın emri verir,
- evidence toplar.

Cloud runtime:
- siteyi internet üzerinde servis eder.

Mac hiçbir v0.1 senaryosunda production web server değildir.

### 2.3 Static First Principle™

`STATIC → EDGE ONLY IF REQUIRED → EXTERNAL SERVICE ONLY IF NECESSARY`

Sunucusuz çözülebilecek bir gereksinim runtime servisine dönüştürülmez.

Amaç:
- maliyet yüzeyini küçültmek,
- hata yüzeyini azaltmak,
- güvenliği sadeleştirmek,
- free-tier kapasitesini korumak.

### 2.4 Zero-Cost Guard™

Yayın Motoru ücretli plana otomatik geçemez.

Free limit aşımı veya ücretli özellik gereksinimi tespit edilirse:

`STATE — HOLD`

çıkar.

Maliyet doğuran hareket yalnız Human Threshold™ sonrası ayrı karar olabilir.

---

## 3. PROVIDER STRATEGY

### Primary publication adapter
**Cloudflare-first**

V0.1 kapsamı:
- Cloudflare Pages / Workers Static Assets
- Cloudflare DNS
- managed TLS
- custom domain binding

### Secondary adapter contract
Vercel ve başka provider'lar sonraki adapter olarak eklenebilir.

Kural:

`vendor-neutral control plane + provider-specific adapter`

Provider mantığı core içine gömülmez.

---

## 4. REPOSITORY / RUNTIME TOPOLOGY

Yeni production repository bu specification ile otomatik oluşturulmaz.

Mevcut Labory execution order korunur.

Implementation başladığında önerilen bağımsız repository:

`engurulabory/enguru-publish-engine`

Önerilen Mac yerleşimi:

```
~/Enguru/Cores/PublishEngine/
├── engine/
├── adapters/
├── sites/
├── evidence/
├── schemas/
├── tests/
└── publish
```

Foundation içerisinde minimum modüller:

```
engine/
  registry
  source_gate
  build_gate
  artifact_gate
  publication_gate
  domain_gate
  dns_gate
  tls_gate
  live_gate
  parity_gate
  rollback_gate
  evidence_gate
  cost_guard
  state_machine

adapters/
  github
  cloudflare

cockpit/
  terminal_ui
```

Yeni abstraction yalnız mevcut modüller yetersiz olduğunda eklenir.

---

## 5. SITE MANIFEST CONTRACT

Her site yalnız bir manifest ile tanımlanır.

Kural:

`N sites = N manifests + 1 engine`

Manifest:
- domain,
- canonical source repository,
- branch,
- build command,
- output directory,
- publication provider,
- provider project,
- verification rules,
- cost policy,
- Human Threshold policy

taşır.

Secret manifest içine yazılamaz.

Schema:
`governance/publish-engine/SITE_MANIFEST_SCHEMA_V0_1.json`

---

## 6. STATE MACHINE

Kanonik state machine:

```
DRAFT
  ↓
SOURCE_RESOLVED
  ↓
SOURCE_VERIFIED
  ↓
BUILDING
  ↓
BUILD_VERIFIED
  ↓
ARTIFACT_SEALED
  ↓
PREVIEW_DEPLOYED
  ↓
PREVIEW_VERIFIED
  ↓
READY_FOR_PUBLICATION
  ↓
HUMAN_APPROVED
  ↓
PRODUCTION_DEPLOYING
  ↓
DOMAIN_BOUND
  ↓
DNS_VERIFIED
  ↓
TLS_VERIFIED
  ↓
PUBLIC_RESPONSE_VERIFIED
  ↓
SOURCE_PARITY_VERIFIED
  ↓
EVIDENCE_SEALED
  ↓
DONECHECK_PASS
  ↓
VERIFIED_LIVE
```

Failure semantics:
- eksik kanıt → HOLD
- gerçek teknik engel → BLOCKED
- verified invariant ihlali → FAIL

State atlama yasaktır.

`VERIFIED_LIVE` yalnız evidence-backed terminal state'tir.

---

## 7. TERMINAL COCKPIT CONTRACT

Birincil kullanıcı yüzeyi:

`publish`

Ana ekran yalnız şu gerçekleri göstermeli:

- site/domain,
- source SHA,
- provider,
- current state,
- latest verified release,
- DNS,
- TLS,
- public health,
- cost state,
- rollback availability.

Ana eylemler:

- YENİ YAYIN
- PREFLIGHT
- YAYINA AL
- VERIFY ALL
- ROLLBACK
- EVIDENCE
- HISTORY

Premium kalite ilkesi:

`minimum operator input + maximum verified truth`

Kullanıcıya provider teknik ayrıntısı yalnız hata çözmek için gerektiğinde gösterilir.

---

## 8. PREFLIGHT GATES

Production öncesi zorunlu minimum gates:

1. Registry Gate
2. Source Gate
3. Exact SHA Gate
4. Clean Tree Gate
5. Build Gate
6. Artifact Digest Gate
7. Provider Auth Presence Gate
8. Domain Ownership/Zone Gate
9. Free-Capacity / Cost Guard
10. Rollback Availability Gate

Hepsi PASS olmadan:

`READY_FOR_PUBLICATION`

oluşamaz.

---

## 9. CLOUDFLARE ADAPTER CONTRACT

Adapter core'un şu operasyonlarını sağlamalı:

- account/zone identity read,
- project resolve/create under explicit scope,
- preview deploy,
- production deploy,
- custom domain bind,
- DNS state read,
- DNS record mutation only through approved path,
- TLS state read,
- deployment list,
- prior verified deployment resolve,
- rollback/promote previous verified release,
- usage/capacity observation where API surface permits,
- machine-readable receipts.

Secrets:
- source code içinde bulunamaz,
- evidence içine yazılamaz,
- logs içinde maskesiz görünemez.

Adapter output core'a normalized result döndürür.
Cloudflare'a özgü response core state machine'e sızmaz.

---

## 10. EVIDENCE RECEIPT

Her publication run immutable bir receipt üretir.

Minimum alanlar:

```json
{
  "schema": "enguru.publish.receipt/v0.1",
  "siteId": "example",
  "domain": "example.com",
  "sourceRepository": "owner/repo",
  "sourceBranch": "main",
  "sourceCommit": "<sha>",
  "artifactDigest": "sha256:<digest>",
  "provider": "cloudflare",
  "deploymentId": "<id>",
  "previousVerifiedDeploymentId": "<id|null>",
  "dnsVerified": true,
  "tlsVerified": true,
  "publicStatus": 200,
  "sourceParityVerified": true,
  "costGuard": "PASS",
  "startedAt": "<iso8601>",
  "verifiedAt": "<iso8601>",
  "doneCheck": "PASS",
  "verdict": "VERIFIED_LIVE"
}
```

Receipt secret, token, credential veya kişisel veri içeremez.

---

## 11. ROLLBACK CONTRACT

Rollback başarı sayılmaz çünkü komut çalıştı.

Kanonik akış:

`select previous VERIFIED release → Human Threshold → provider rollback/promote → domain unchanged check → DNS check → TLS check → public response → provenance check → rollback evidence → DoneCheck™`

Rollback sonrası final state:

`VERIFIED_LIVE`

ve receipt yeni rollback eventini açıkça göstermelidir.

---

## 12. MULTI-SITE CONTRACT

V0.1 hedef ölçek:
**10–15 site**

Motor site bazlı state izolasyonu sağlamalıdır.

Bir sitenin:
- build hatası,
- DNS hatası,
- provider hatası

başka siteyi etkilememelidir.

`VERIFY ALL` read-only olmalıdır.

Toplu production mutation V0.1 kapsamı dışındadır.

---

## 13. COST CONTRACT

V0.1 default policy:

```
domain purchase/renewal: external/user-owned
hosting incremental target: €0
SSL incremental target: €0
DNS incremental target: €0
CDN incremental target: €0
publication engine: local/open implementation
automatic paid upgrade: forbidden
```

Cost Guard herhangi bir ücretli geçiş riski görürse:

`HOLD — HUMAN THRESHOLD`

çıkar.

---

## 14. SECURITY / AUTHORITY BOUNDARY

Publication mutation authority hiçbir zaman:
- manifest boolean,
- caller supplied `approved=true`,
- local UI flag,
- stale evidence

ile üretilemez.

Production publish ve rollback:
- current verified preflight,
- current operator session,
- explicit Human Threshold

gerektirir.

Provider credentials least-privilege olmalıdır.

---

## 15. ACCEPTANCE GATES — 100/100 DEFINITION

Gerçek teknik 100/100 yalnız 10 gate'in her biri kanıtlandığında verilebilir.

Her gate = 10 puan.

1. Architecture Simplicity
2. Source Truth
3. Deterministic Build
4. Artifact / Provenance Truth
5. Cloud Publication
6. Domain / DNS / TLS Truth
7. Rollback
8. Multi-Site Isolation
9. Zero-Cost Guard
10. Evidence + DoneCheck™ + Cockpit

Her gate için PASS kanıtı zorunludur.
Puan varsayımla verilemez.

Test matrisi:
`governance/publish-engine/ACCEPTANCE_TEST_MATRIX_V0_1.md`

---

## 16. FIELD PROOF CONTRACT

İlk gerçek saha testi tek siteyle yapılır.

Kanonik döngü:

`domain → source → preflight → preview → Human Threshold → production → DNS → TLS → public health → parity → Evidence → DoneCheck™ → VERIFIED LIVE → rollback → re-verify → VERIFIED LIVE`

İlk saha testinde para doğuran otomatik işlem yapılamaz.

Test domaini kullanıcı kontrolünde olmalıdır.

---

## 17. FOUNDATION EXIT

Foundation specification PASS için gerekenler:

- [x] publication theory tanımlı
- [x] provider boundary tanımlı
- [x] site manifest contract tanımlı
- [x] state machine tanımlı
- [x] terminal cockpit contract tanımlı
- [x] cost guard tanımlı
- [x] evidence receipt tanımlı
- [x] rollback contract tanımlı
- [x] multi-site contract tanımlı
- [x] 100/100 acceptance standardı tanımlı
- [ ] implementation repository
- [ ] executable engine
- [ ] Cloudflare credentials/config commissioning
- [ ] real test site
- [ ] live publication evidence
- [ ] rollback evidence
- [ ] DoneCheck™ field PASS

## FINAL JUDGMENT

**FOUNDATION SPECIFICATION — PASS**

**IMPLEMENTATION — HOLD**

**FIELD VERIFIED 100/100 — HOLD**

NEXT ACTION:

`Foundation merge → implementation authority/sequence check → independent engine repository → executable core → local tests → one controlled field site → VERIFIED LIVE → rollback → VERIFIED LIVE → DoneCheck™ → Human Threshold™ → real 100/100 verdict`
