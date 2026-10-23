# EMÜS V1.1 — GH-01 Kaynak Envanteri ve GAP_MATRIX (ilk doğrulanmış kesit)
Tarih: 2026-10-23
Base main: 113d8ffd18a6f36c840770f30f38da6d5900aa43
STATE: PARTIAL_READ_ONLY_DISCOVERY / GAP_MATRIX_PRELIMINARY / GH01_HOLD

## Kaynak kanıtları (Git blob SHA-1; SHA-256 ile karıştırılmamalı)
| Kaynak | Blob SHA-1 | Gözlem |
|---|---|---|
| AGENTS.md | 0a08f2e4202bbf240760cb0abd30e6a826531688 | Sekiz aşama, V3 kaynak önceliği, yetki sınırı |
| governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md | 7f47f3c6d3ee5c5138e53b67ae46cced37cb1a61 | K1–K8, bağımsız kanıt düzeyleri, tamamlama muhasebesi |
| governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json | b5ba280e60924f33f601a826aa0b243c74f5674f | V3 kaynak blob SHA eşleşiyor; SHA-256 kaynak baytı ayrı doğrulanacak |
| tools/mac_engineer_control.py | 906336b57e32bcffca6d68df544a5c1a866bffad | Tek kontrol noktası adayı; v0.6 bağlantıları; mevcut ürünün tamamı doğrulanmadı |
| tools/package3_working_memory_donecheck.py | abbf8cf62f2d9c1bbfd71923ed44b4532c1d8829 | PersistentWorkingMemory restart/revision test örnekleri var |
| governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md | a3fa94c6a65ae768259dea40f066e09ede5ace63 | DoneCheck v1.2 ve Human Threshold™ birbirinden ayrılmış; resmî yetki bu belgeyle PASS değildir |

## İlk gerekli fark değerlendirmesi
| Kontrol | Mevcut aday | Durum | Gerekli gerçek hareket |
|---|---|---|---|
| K01 çok araçlı icra | Mac Engineer control plane | PARTIAL | Aktif ürün deposu ve görev çalışma sözleşmesiyle bire bir eşleştirme |
| K02 dayanıklılık | shared_ai.working_memory, package3 test | PARTIAL | SQLite/WAL, idempotency, crash recovery ve görev tekrarları karşılaştırması |
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
2. Kaynak dosyalarının SHA-256 kilitlerini bayt düzeyinde doğrula; V3 kilit ile tam karşılaştır.
3. Her kontrol için üretim kodu, test, CI ve yetki kanıtı topla; ardından EXITS/PARTIAL/MISSING/UNKNOWN sınıflarını güncelle.
4. Yetki kökü ve owner kararına göre GH-01 bağımsız tamamlanma hükmünü ver.

## Korunan hüküm
Tasarım kapsamı 100/100, ancak gerçek `GH-01=HOLD`; `GH-02–04=HOLD`, `OSI=HOLD`. Yeni review PR, canonical merge veya resmî DoneCheck makbuzu anlamına gelmez.
