# ENGÜRÜ V6.9 Hedef 1 — Ana Çalışma Yöntemleri V2 Uzlaştırma Kaydı V1

DATE=2026-10-25
STATE=SOURCE_ALIGNED_GITHUB_REVIEW_ONLY
GOAL=TARGET_01_MIMARLIK
REFERENCE_MAIN=f754b3a48e46224251d2717f1b28e6cf60bf2812
REVIEW_BRANCH=feat/management-v69-github-osi-handoff-v1
TRIPLE_TARGET=DESIGN_100/100 + THEORY_100/100 + SIMULATION_100/100
TARGETS_02_TO_09=PRESERVED
OSI_MUTATION=0

## Gerçek kaynak ve yöntem hiyerarşisi
- `main/AGENTS.md` başlangıç ve yetki disiplini.
- `governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md`: SHA-256 tam içerik hesabı = `11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc`; main lock ile EŞLEŞTİ. Git blob SHA1 = `7f47f3c6d3ee5c5138e53b67ae46cced37cb1a61`; lock ile EŞLEŞTİ.
- `governance/enguru-suzgeci/ENGURU_GITHUB_METHOD_ENTRY_V2.md`: tek GitHub giriş ve üç turlu ölçülebilir düzeltme.
- `governance/enguru-suzgeci/ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md`: yöntemlerin envanteri ve yetki/kanıt sınırları.
- `governance/enguru-suzgeci/ENGURU_ANA_TERAZI_5X100_V1.md`: teori, tasarım ve üç ayrı simülasyon için beş bağımsız 100/100 ölçümü; ürün sahasından ayrık.
- `tools/enguru_method_dynamic_loop_v2.py` ve `tools/enguru_method_dynamic_adversarial_v2.py`: gerçek main kaynakları; dinamik üç turlu sentetik hata/onarma döngüsü, ayrı karşıt oracle.
- Ürüne özgü `governance/management-v69/README.md` ve korunan canonical owner/DoneCheck/Human Threshold yetkileri önceliklidir.

## Uzlaştırma ve somut açık
GitHub compare(main,review branch) gözlemi: `ahead_by=115`, `behind_by=93`, `status=diverged`, `merge_base=113d8ffd18a6f36c840770f30f38da6d5900aa43`. Main'de bulunan V2 giriş ve simülasyon modülleri bu inceleme dalındaki aynı yollarda bulunamadı (404). Dolayısıyla Mimarlık Hedef1'in final kabulü için önce dallar arasındaki kaynak/contract farklarının etkisi incelenmeli ve onaylı yöntemle uzlaştırılmalıdır. Yeni core veya issuer ihtiyacı üretilmez.

Son bilinen önceki V6.9 dalı commit'i `413e5a13f5bbd0de6eec7c0385d432c8f9bc6f19` için GitHub `fetch_commit_workflow_runs` sonucu `[]` gözlendi. Bu kayıt hiçbir koşunun hiçbir zaman çalışmadığını ispatlamaz; exact-head RUN_ID ve SUCCESS bulunmadığından `CI=UNVERIFIED`. Önceki 24 Pilot davranış testi *tanımlanmış* kapsamdır, gerçek PASS sayacı değildir.

## Üç turlu yöntem provası ve ek dördüncü karşıt tur
Aşağıdaki karar provası JS üzerinde aynı turda çalıştırılmıştır; gerçek GitHub Actions test koşusu veya kaynak üzerinde mühendislik PASS değildir.

| Tur | Girdi / bozulan şart | Beklenen ve gözlenen karar |
| --- | --- | --- |
| 1 | V3 kaynak SHA lock ile kayıyor | HOLD_CANONICAL_V3_SOURCE |
| 2 | Canonical SHA doğru; gözlenen branch 93 commit geride | HOLD_BRANCH_MAIN_RECONCILIATION |
| 3 | Dal uzlaşmış varsayımı; exact-HEAD CI kanıtı yok | HOLD_EXACT_HEAD_CI |
| 4 | Dal ve CI geçerli varsayımı; 300 ayrı kanıt eksik | HOLD_TRIPLE_EVIDENCE |

`MODEL_DECISION_ASSERTIONS=4/4_PASS`; `TRIPLE_VERIFIED=HOLD`; `FIELD_ACCEPTANCE=HOLD`.

## Uygulanabilir birleştirilmiş iş blokları
1. **Kaynak eşleştirme:** Güncel main'in V2 yöntemleri ile PR #211'deki mevcut kabul sözleşmesini ve yeni dosyaları karşılaştır. Korunan imza/provenance yetkileri ve farklı ürün sayaçları sabit kalsın. GitHub merge/rebase için bağımsız CI ve yetki kararı ayrı.
2. **Teorik matris:** Mevcut 24 tanımlı testi, gerçekten özgün `CONTROL_ID→SOURCE_SHA→ASSERTION_ID→REAL_RUN_ID→REVIEW` kanıtlarıyla eşleştir. D/T/S üç ayrı payda; aynı test farklı kriterler için kanıt diye çoğaltılmaz. V2 Ana Terazi'nin teori+tasarım+SIM1+SIM2+SIM3 ayrımı ayrıca korunur.
3. **Gerçek GitHub yürütmesi:** Yetkili GitHub workflow olayı/dispatch ile exact-HEAD gerçek koşuyu elde et; source hash, run ID, conclusion, branch/main delta ve ilgili artefaktı doğrula. İşleyişteki tarihsel source drift resmi yeni receipt'le ayrı kapanır.
4. **Bağımsız Mimarlık son kontrolü:** Pilot yönetim→mühendis→verifier→görev defteri→devam/idempotency/rollback karşıt testleri; üç ayrı teorik puanın kaynaklı hesabı; gerçek kabul ayrı.
5. **Saha ve owner:** Mac OSi sonraki kullanıcı aşaması; G2–G6, gerçek owner imzası, DoneCheck ve Human Threshold ayrı kapılar.

## Ölçüm ve karar
MEASURED: V3 SHA256=PASS; BRANCH_AHEAD=115; BRANCH_BEHIND=93; MODEL_SCENARIOS=4/4; LATEST_OBSERVED_CI_RUN_IDS=0.
TARGET: ADDITIONAL_SPEND=0; ROUTINE_HUMAN_PROCEDURES=0; DESIGN=100/100; THEORY=100/100; SIM1=100/100; SIM2=100/100; SIM3=100/100.
UNKNOWN: TRUE_JOB_DURATION; ACTUAL_SPEND; EXECUTED_GITHUB_TEST_COUNT_FOR_LAST_HEAD; INDEPENDENT_300_CONTROL_EVIDENCE.
STATE=SOURCE_RECONCILIATION_REQUIRED
CLAIM=canonical methods verified, branch-to-main method compatibility still open
EVIDENCE=main V3 SHA256 pin, main method sources, GitHub branch compare
NEXT_ACTION=review branch/main 93-behind scope and perform an authorized, test-backed reconciliation
VERDICT=GUVENLI_DUR_FOR_ARCHITECTURE_FINAL
