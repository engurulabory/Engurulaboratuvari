# EMÜS V1.1 — GH-01 Kaynak Envanteri ve GAP_MATRIX (ilk doğrulanmış kesit)
Tarih: 2026-10-23
Base main: 113d8ffd18a6f36c840770f30f38da6d5900aa43
STATE: PARTIAL_READ_ONLY_DISCOVERY / GAP_MATRIX_PRELIMINARY / GH01_HOLD

## Kaynak kanıtları (Git blob SHA-1; SHA-256 ile karıştırılmamalı)
| Kaynak | Blob SHA-1 | Gözlem |
|---|---|---|
| AGENTS.md | 0a08f2e4202bbf240760cb0abd30e6a826531688 | Sekiz aşama, V3 kaynak önceliği, yetki sınırı |
| governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md | 7f47f3c6d3ee5c5138e53b67ae46cced37cb1a61 | K1–K8, bağımsız kanıt düzeyleri, tamamlama muhasebesi |
| governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json | b5ba280e60924f33f601a826aa0b243c74f5674f | V3 kaynak blob SHA eşleşiyor; GitHub bağlantısından okunan UTF-8 içeriğin SHA-256 değeri canonical lock ile eşleşti (2026-10-23) |
| tools/mac_engineer_control.py | 906336b57e32bcffca6d68df544a5c1a866bffad | Tek kontrol noktası adayı; v0.6 bağlantıları; mevcut ürünün tamamı doğrulanmadı |
| tools/package3_working_memory_donecheck.py | abbf8cf62f2d9c1bbfd71923ed44b4532c1d8829 | PersistentWorkingMemory restart/revision test örnekleri var |
| governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md | a3fa94c6a65ae768259dea40f066e09ede5ace63 | DoneCheck v1.2 ve Human Threshold™ birbirinden ayrılmış; resmî yetki bu belgeyle PASS değildir |

## İlk gerekli fark değerlendirmesi
| Kontrol | Mevcut aday | Durum | Gerekli gerçek hareket |
|---|---|---|---|
| K01 çok araçlı icra | Mac Engineer control plane | PARTIAL | Aktif ürün deposu ve görev çalışma sözleşmesiyle bire bir eşleştirme |
| K02 dayanıklılık | shared_ai.working_memory, package3 test | PARTIAL | Mevcut kalıcı görev mekanizmaları, idempotency, crash recovery ve tekrar testlerini karşılaştır; SQLite yalnız kanıtlı fark için aday |
| K03 yetki | DoneCheck Authority Model v1 | PARTIAL | Yetkili owner/reviewer/issuer kaynağı, canlı grant ve audit uzlaştırması |
| G01 görev yeterliliği | V3 kabul matrisi | PARTIAL | Model/araç yetenek testi ve görev kabul sözleşmesini ölçme |
| G02 kalıcı defter | PersistentWorkingMemory adayı | PARTIAL | Şema, backend, checkpoint ve failover incelemesi |
| G03 kaynak bütçesi | Mac Engineer kontrol girişi | UNKNOWN | Gerçek yerel model/RAM/disk limit testleri |
| G04 kanıt | V3 ve DoneCheck | PARTIAL | EMÜS görev kanıt zarfı ve oracle |
| G05 güven | Human Threshold™ canonical ilkeleri | PARTIAL | EMÜS etkili araç izin matrisi |
| G06 köken/hafıza | shared_ai adayı | UNKNOWN | Canonical hafıza ve veri yaşam döngüsü incelemesi |
| G07 benchmark | V3 kabul standardı | PARTIAL | EMÜS sabit gerçek görev benchmark'ı |
| G08 kurulum | Mac Engineer preflight adayları | PARTIAL | Güncel model ağırlığı lisansı, offline ve rollback |
| G09 sürüm | V3 kaynak kilidi | PARTIAL | EMÜS model/Skill/görev lock matrisi |
| G10 geçiş | V3 K1–K8 | PARTIAL | GH-04 resmî kabul ve ayrı OSi readiness gate |

## Kesin kalan GH-01 işleri
1. Yönetim/İcra/Mac Engineer ürün depolarının gerçek default branch ve HEAD kimliklerini bağımsız doğrula.
2. V3 GitHub API'den alınan UTF-8 içeriğinin SHA-256 kilidi eşleşti: `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`; Git blob SHA-1 da eşleşti. Diğer ürün dosyalarının SHA-256 bütünlüğü ve yerel OSi kaynağı ayrıca karşılaştırılacak.
3. Her kontrol için üretim kodu, test, CI ve yetki kanıtı topla; ardından EXISTS/PARTIAL/MISSING/UNKNOWN sınıflarını güncelle.
4. Yetki kökü ve owner kararına göre GH-01 bağımsız tamamlanma hükmünü ver.

## Korunan hüküm
Tasarım kapsamı 100/100, ancak gerçek `GH-01=HOLD`; `GH-02–04=HOLD`, `OSI=HOLD`. Yeni review PR, canonical merge veya resmî DoneCheck makbuzu anlamına gelmez.

## 2026-10-23 — Kanıtlı SHA ve yetki ayrımı
- GitHub `main` V3 kaynağı doğrudan okundu; SHA-256, salt JavaScript uygulamasıyla UTF-8 içerikten hesaplandı. `sha256('abc')` bilinen test vektörü PASS; hesaplanan V3 SHA-256 canonical kilit değeriyle eşleşti. Git blob SHA-1 de kilitle eşleşti.
- Bu doğrulama bağlantının döndürdüğü kaynak metni için geçerlidir; bağımsız ham Git blob aktarımı ve OSi yerel eşleşmesi ayrı kapıdır.
- `governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md` rol sırasını açıklıyor; EMÜS'e özel geçerli reviewer/issuer/owner grant veya imza makbuzu henüz kanıtlanmadı.
- GH-01 = PARTIAL, GH-02 = PARTIAL, GH-03/04 = HOLD; insan onayı korunur.

## GH-01 — Yönetim/İcra ve gerçek yetki uzlaştırması (2026-10-23)
- Yönetim güncel görünür aday: `governance/enguru-suzgeci/ENGURU_OSI_MUHENDISLIK_KASI_CANLI_KAYIT_V1.md` (Git blob SHA-1 `538b1ae4321488112fabffa0112739d696ab5378`), `ENGURU_MANAGEMENT_V69_PR_203` için kaynak/CI kanıtı gösteriyor. Bu kayıt PR #203'e özgüdür, EMÜS owner grant'i değildir.
- Paylaşılan İcra mimarisi: `governance/ENGURU_VERIFIED_AGENT_OPERATING_CORE_V0_1.md` (Git blob `5ee98d4615a1764973d955543f2fb5ecdf8b8b79`) mimari VISION LOCKED, implementation evidence-gated; tek başına aktif ürün icra yetkisini kanıtlamaz.
- Mac Engineer icra eşlemesi: `governance/mac-engineer/CAPABILITY_EXECUTION_BINDING_V1.json` (Git blob `419bff0005109644938aae08b8e0b4421af8098b`) yalnız kanıtlı/registered handler'lar üzerinden araç kullanımını kabul ediyor, eksik binding HOLD. Bu dosya yeni yetki üretmiyor.
- Ürün/çekirdek haritası: `governance/ENGURU_PRODUCT_CORE_MAP.md` (Git blob `1b240b7a9a63aa67ad1c0898a8c78639f57d591b`) envanter durumu HOLD; tam depo ve embedded-core incelemesi açık.
- Yönetim saha kaydına göre PR #203 için teknik verifyTask 4/4 PASS raporlanırken owner trust, Ed25519 key/grant, HumanReview, ledger ve merge HOLD. EMÜS'e aynı PASS veya yetki aktarımı yapılmaz.
- `governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md` teknik producer → DoneCheck v1.2 → Human Threshold sırasını tanımlar. EMÜS'e özgü canlı owner/reviewer/issuer grant, imza/receipt ve yetki geçerliliği bu kaynaklarda kanıtlanmadı: `HOLD_AUTHORITY`.
- GH-01 kaynak keşif kapsamı genişletildi; gerçek canonical İcra sürüm/owner doğrulaması, özel ürün kaynak geçerliliği ve EMÜS-specific authority kanıtı hâlâ açık. Bu kaynak keşfi kaynakların yokluğunu ispatlamaz.
- Karar: `GH01=PARTIAL`, `GH02=PARTIAL`, `GH03/04=HOLD`, `OSI_READY=HOLD`. İlgisiz ürünün grant'i EMÜS'e uygulanmaz.

## 2026-10-23 — DoneCheck yetki uygulaması kaynak keşfi
- Canonical ürün deposu `engurulabory/donecheck` GitHub bağlantısında bulundu; `main` üzerinde `src/domain/donecheck/verification-engine.ts` gerçek `verifyTask` uygulaması, `src/runtime/node/reviewer-attestation.ts` imzalı reviewer doğrulama altyapısı ve `src/runtime/node/verified-finish-runtime.ts` kapanış uygulaması kaynakları görüldü.
- `README.md` DoneCheck'in Ed25519 reviewer kimlik doğrulaması, reviewer-karar yetkilendirmesi, değişiklik izli JSONL ledger ve ancak makine PASS + kriptografik yetkili insan kabulü sonrası `recordVerifiedFinish()` makbuzu tanımladığını bildiriyor. Bu satırlar **ürün yeteneği kaynak kanıtıdır**; EMÜS için verilmiş grant, kayıtlı reviewer, gerçek imza veya makbuz değildir.
- EMÜS görev kimliğiyle eşlenen canlı reviewer public key/allowlist, issuer grant, imzalı human review, yetkili ledger ve exact-main receipt henüz doğrulanmadı: `EMUS_AUTHORITY=HOLD`.
- Sade yöntem: mevcut DoneCheck yetki kökünü kullan; yeni reviewer, issuer, ikinci ledger veya bağımsız kabul motoru kurma. EMÜS görev kapsamı ve mevcut güven kökü ayrı kanıtlarla uzlaştırıldığında kabulü değerlendir.
- Bu tur salt kaynak keşfi + kayıt; `GH01_PARTIAL / GH02_PARTIAL / GH03_HOLD / GH04_HOLD / OSI_READY_HOLD`.
