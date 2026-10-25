#!/usr/bin/env python3
"""Creates frozen local Zulfikar V1.2 design evidence and concise human report."""
import sys, subprocess, json, hashlib, zipfile, re
from pathlib import Path
from zulfikar_v1_2_engine import evaluate_design_coverage, CLOSURES, FROZEN_SCORE_93, canonical_digest
from test_zulfikar_v1_2 import design_contract, MUTATIONS
ROOT=Path(__file__).resolve().parent
repo='engurulabory/Engurulaboratuvari'
head='8947cb6c240a12950be1f8be9e186d0ecbfa3022'
paths={
 'AGENTS.md':'59dc8054896b932413d25abf10c6244e5899126d',
 'governance/enguru-suzgeci/ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md':'acf55d6292bc0ae91407afec686c146ac9d2dbf3',
 'governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md':'7f47f3c6d3ee5c5138e53b67ae46cced37cb1a61',
 'governance/enguru-suzgeci/learning/ENGURU_MK_KALICI_AMAC_HEDEF_KABUL_V3.md':'d93adb31787ff6e6ac9b9bfda99311198da3e54c',
 'governance/enguru-suzgeci/ENGURU_GITHUB_METHOD_ENTRY_V2.md':'391b66aac526eb8b01d6a73437c8afcc171bc707',
}
contract=design_contract()
contract.update({
 'title':'ENGURU Zulfikar integrated design acceptance contract V1.2',
 'date':'2026-10-25','scope':'DESIGN_ONLY / LOCAL_OFFLINE_VALIDATOR',
 'canonical_repository':repo,'main_snapshot':head,'source_blob_sha1_pins':paths,
 'sha256_canonical_v3_lock':'11edc63cc3b3549d050e916f3efe67cd431bb7394ed318452cf5871c7cc727cc',
 'existing_suzgec_eight_stages':True,'new_core_created':False,'new_owner_created':False,
 'base_score':list(FROZEN_SCORE_93),'scoring_maximum':100,
 'valid_scores_only_after_test':'YES','real_field_scores_must_remain_separate':True,
 'packages':{
  'K01':{'purpose':'Success/failure Muscle + measurable learning transfer',
   'closure_ids':['Z02_EVENT','Z03_TRANSFER'],
   'observables':['event id, outcome taxonomy, source/evidence, unproven cause classified',
                  'three distinct frozen comparable downstream tasks with baseline/after and independent review'],
   'real_acceptance':'3/3 separately verified task transfers and regression-free outcome'},
  'K02':{'purpose':'End-to-end Consistency Muscle and single-writer Work/GitHub/OSi lineage',
   'closure_ids':['Z04_LINEAGE','Z10_CONCURRENCY'],
   'observables':['9-hop trace + original control IDs + source SHA + claims',
                  'exact snapshot, scoped lease, one writer, replay and rollback'],
   'real_acceptance':'one real end-to-end project with verified chain and a deliberate source-drift test'},
  'K03':{'purpose':'Versioned comparable peer benchmark and verified gap closure',
   'closure_ids':['Z05_BENCHMARK'],
   'observables':['frozen identical task/input/rubric, budget normalization, disclosed environment',
                  '>=5 paired trials, actual peer output evidence, blinded judge'],
   'real_acceptance':'peer execution and objectively scored results, NOT_MEASURED until completed'},
  'K04':{'purpose':'User impact + advisory FIN Veri̇ci without new issuer',
   'closure_ids':['Z08_IMPACT','Z10_SAFE_FIN'],
   'observables':['real-user before/after matched cohort, source and privacy evidence',
                  'all K1-K7 gates, evidence+second look and needed Human Threshold'],
   'real_acceptance':'real impact observed and existing DoneCheck+Human Threshold evaluated externally'},
 },
 'bench_selection':['OpenAI Codex','Claude Code','Cursor','GitHub Copilot','Devin','OpenHands','Replit Agent','Kiro','Cline','Lovable'],
 'benchmark_state':'FEATURE_REFERENCES_ONLY / REAL_PEER_TRIALS_NOT_MEASURED',
 'authority':'Only official canonical DoneCheck + required Human Threshold may issue VERIFIED_FINISH',
 'untested_real_world':['main/new PR CI','Work session handoff','native Mac OSi','user impact','external agent trials','issuer and reviewer signatures'],
})
contract_path=ROOT/'zulfikar_v1_2_design_contract.json'
contract_path.write_text(json.dumps(contract,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
res=subprocess.run([sys.executable,'-B','-m','unittest','-v','test_zulfikar_v1_2'],cwd=ROOT,text=True,capture_output=True)
(ROOT/'zulfikar_v1_2_test_log.txt').write_text(re.sub(r'Ran (\d+) tests in [0-9.]+s', r'Ran \1 tests (elapsed excluded for deterministic digest)', res.stdout+res.stderr),encoding='utf8')
if res.returncode:
    print(res.stderr,file=sys.stderr)
    raise SystemExit(res.returncode)
score=evaluate_design_coverage(contract,True)
assert score['provisional']==100 and len(contract['closure_ids'])==7
assert len(MUTATIONS)==45
source_files=['zulfikar_v1_2_engine.py','test_zulfikar_v1_2.py','zulfikar_v1_2_design_contract.json','zulfikar_v1_2_test_log.txt']
checksums={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in source_files}
receipt={
 'schema':'enguru.zulfikar.design-review.v1.2',
 'date':'2026-10-25', 'repository_source_snapshot':head,
 'state':'LOCAL_DESIGN_COVERAGE_VALIDATED',
 'claim':'BASELINE_ARCHITECTURAL_RUBRIC_93_PLUS_7_DESIGN_CLOSURES',
 'design_rubric':score,
 'baseline_from_prior_v1_1_analyst_assessment':93,
 'new_closures':{key:{'category':item[0],'extra_design_point':item[1]} for key,item in CLOSURES.items()},
 'rubric_assessment_type':'AUTHOR_DEFINED_FROZEN_10x10_DESIGN_RUBRIC; NOT_CANONICAL_5x100',
 'tests':{'unittest_methods':8,'positive_component_checkers':7,
          'targeted_negative_mutations':45,'malformed_schema_cases':512,
          'deterministic_combined_adversarial_cases':3072,'result':'PASS',
          'note':'Fixtures assert claimed evidence; no external source authenticity is validated'},
 'source_sha256':checksums,
 'real_github_ci':'NOT_RUN_FOR_THIS_V1_2',
 'real_external_peer_benchmark':'NOT_MEASURED',
 'learning_transfer_on_real_3_tasks':'NOT_OBSERVED',
 'real_work_github_osi_chain':'NOT_TESTED',
 'measured_real_user_impact':'NOT_OBSERVED',
 'official_verified_finish':'HOLD',
 'authorization':'NO_NEW_ISSUER_OR_OWNER / NO_MAC_OR_GITHUB_WRITES',
 'next_action':'After Work returns, reconcile its exact source/contract evidence; independent review; GitHub isolated integration; actual trials; needed Mac field and canonical acceptance',
}
receipt_path=ROOT/'zulfikar_v1_2_receipt.json'
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
report=f'''# ENGÜRÜ Zülfikar™ — Bütünleşik Mimari Finiş V1.2

**25 Ekim 2026 · Yönetim tasarımı · Salt-okunur GitHub kaynakları ve yerel sentetik testler**

## Yönetim hükmü

- **STATE:** K01–K04 için ayrı kanıt sözleşmeleri ve çalışan izole doğrulayıcı hazırlanıp üç karşıt sınama ailesinde çalıştırıldı.
- **CLAIM:** Önceki V1.1 mimari rubriği `93/100` + tanımlanıp testlenen **7 özgün tasarım açığı** = **100/100 tasarım adayı**.
- **EVIDENCE:** 7 kuralın olumlu yol sınaması; 45 hedefli negatif mutasyon; 512 bozuk şema denemesi; 3.072 sabit tohumlu birleşik karşıt test. 8 unittest yöntemi PASS. İlgili kodlar ve test çıktısı bu pakette.
- **VERDICT:** `THEORETICAL_DESIGN_CANDIDATE=100/100; LOCAL_SYNTHETIC_POLICY_TEST=PASS; REAL_EXECUTION=HOLD; REAL_PEER_BENCHMARK=HOLD; OFFICIAL_VERIFIED_FINISH=HOLD`.

**Sınır:** Tasarım 100/100 yalnız geçmiş turda belirlenen 10×10 **analist rubriğinin kapsanması**dır; ENGÜRÜ Ana Terazi™ 5×100 GitHub hazırlığı, ürünün bitiş puanı, gerçek kullanıcı başarısı ya da bağımsız sertifika değildir. Testte kullanılan kanıt adresleri `fixture://` türünde sentetiktir.

## 1. Korunan canonical yapı

`AGENTS.md → SHA-256 kilitli Evrensel V3 → ilgili ürünün kendi canonical sözleşmesi → mevcut DoneCheck™ → gereken Human Threshold™`.

Sekiz aşama ve Y01–Y24 atlası aynı kalır. Başarı Kası, Uçtan Uca Tutarlılık Kası, Benchmark ve FİN Verici™ mevcut ENGÜRÜ sisteminin **iç yetenekleridir**; yeni core, yeni owner veya yeni issuer oluşmaz. Mevcut Work işi ve `main` üzerinde hiçbir yazma yapılmadı.

GitHub `main` okuma anlık görüntüsü: `{head}`. V3 SHA-256 kilit kaydı: `{contract['sha256_canonical_v3_lock']}` (GitHub'daki kaynak beyanı; bu yerel paket bağımsız olarak güncel git ağacını yeniden hesaplamaz).

## 2. 93/100'dan 100/100 tasarım adayına kapatılan 7 özgün kontrol

| Kaynak kategori | Önce | Tasarım adayı | Kapanış oracle'ı | İş paketi |
|---|---:|---:|---|---|
| Z02 Başarı / başarısızlık | 9 | 10 | Olay sınıfı, SHA, ayrılmış kök neden / hipotez | K01 |
| Z03 Başarı kası transferi | 9 | 10 | Önceden seçilmiş 3 bağımsız karşılaştırılabilir görev; önce/sonra ölçümü; regresyon 0 | K01 |
| Z04 Tutarlılık zinciri | 9 | 10 | Niyet–hedef–sözleşme–plan–kaynak–icra–test–kullanıcı–yetki 9 halkası | K02 |
| Z05 Muadil benchmark | 9 | 10 | Aynı görev, açıklanmış koşul, 5 eşleştirilmiş deneme, karşılaştırılabilir gerçek peer kanıtı | K03 |
| Z08 Kullanıcı etkisi | 9 | 10 | Eşleşen gerçek kullanıcı ölçümü, başlangıç/bitiş kanıtı, etik/gizlilik | K04 |
| Z10 Çakışma ve devir | 8 | 9 | Tek yazıcı, yetkili lease, snapshot SHA, replay ve rollback | K02 |
| Z10 Finişe güvenli devam | 9 | 10 | K1–K7, bağımsız kanıt, saha ve insan eşiği; resmî imza üretme yetkisi ayrı | K04 |
| **Toplam** | **93** | **100** | **7/7 tasarım oracle'ı tanımlı ve yerel test edildi** | |

Rubrikten önceden gelen Z01, Z06, Z07 ve Z09'un her biri 10/10 korunur; değiştirilen puan paydası veya silinen zorunlu kabul kontrolü yoktur.

## 3. K01 — Başarı–Başarısızlık Kası™ ve Başarı Kası Geliştirici™

Olay sözleşmesi `event_id/task_id/outcome/observed_at/provenance_digest/owner/cause_status` ister. Olaylar SUCCESS, FAILURE, PARTIAL, INTERRUPTED, FALSE_PASS, RECOVERED olarak ayrılır. `HYPOTHESIS` ile `EVIDENCE_CONFIRMED` kararı ayrı kalır; kanıtı bulunmayan kök neden resmîleştirilmez.

**Başarı aktarım koşulu:** Önceden sabitlenmiş aynı görev ailesine ait 3 farklı gerçek görev, her biri çift baseline–after kanıtı, bağımsız inceleme, ölçülen iyileşme ve regresyonsuz sonuç taşımalıdır. Denemeler başarıya göre sonradan seçilirse `HOLD_TRANSFER_SURVIVORSHIP_SELECTION_RISK`.

**Gerçek kapı:** `REAL_TRANSFER_3_OF_3=HOLD_NOT_OBSERVED`. Fixture testlerinde `PASS` gerçek saha başarısı değildir.

## 4. K02 — Uçtan Uca Tutarlılık Kası™

`INTENT → GOAL → CONTRACT → PLAN → SOURCE → EXECUTION → TEST → USER_OUTCOME → AUTHORITY`.

Her halkada tek proje ID, kaynak SHA, özgün kabul kontrolü ID ve kanıt referansı bağlanır. Uyuşmazlıkla `SIMULATED_HOLD`; gerçek sistemde `HOLD_CONSISTENCY` aday kararı üretilir. Work–GitHub–OSi eşzamanlılığı için aynı değişikliğin tek yetkili yazıcısı, geçerli iş sahipliği/lease, replay idempotency, yedek/checkpoint ve yeniden devralma planı şarttır.

**Gerçek kapı:** `REAL_CHAIN_AND_CONCURRENT_WORK=HOLD_NOT_TESTED`. Aktif Work oturumuna yazı/çakışma oluşturulmadı.

## 5. K03 — Gerçek Muadil Benchmark™

On muadillik araştırma havuzu korunur: Codex, Claude Code, Cursor, GitHub Copilot, Devin, OpenHands, Replit Agent, Kiro, Cline, Lovable. Mevcut inceleme **yetenek karşılaştırmasıdır**. Gerçek üstünlük iddiası için aynı dondurulmuş görev seti ve giriş verisi, açıklanmış platform/versiyon, bütçe denkliği veya sapma açıklaması, aynı değerlendirme rubriği, kör değerlendirici, en az 5 eşleştirilmiş deneme ve iki tarafın bütün çıktı kanıtları gerekir.

**Seçici hasat:** `MUADİL AVANTAJI → ÖLÇÜLMÜŞ FARK → MEVCUT ÖZGÜN CONTROL_ID → EN KÜÇÜK ONARIM → REGRESYON → YENİDEN BENCHMARK → KANITLI KAZANIM`.

**Gerçek kapı:** `REAL_PEER_BENCHMARK=HOLD_NOT_MEASURED`. Bu raporda dış ürünlerin gerçek işte göreli performans puanları yoktur. Ek benchmark tüm görev türlerine zorunlu yük bindirmez; kıyas iddiası/gereksinimi varsa zorunludur.

## 6. K04 — FİN Verici™ ve Gerçek Kullanıcı Etkisi

Gerçek etki, sabit gerçek kullanıcı hedefi, eşleşen başlangıç/sonuç kohortu, zaman, ölçü, birim ve kaynak kanıtıyla değerlendirilir. Olumlu değişim dışında etkileyici sayı gösterimi kabul yerine geçmez.

FİN Verici™, yetkili kararları **oluşturan** mekanizma değildir. K1–K7, tekilleştirilmiş kabul paydası, kaynak kanıtı, bağımsız inceleme, gereken saha ve insan kararı kontrolünü yapar. Açık gerçek şartlarda gereken sıradaki işi belirler; bütün hazırlık şartları karşılandığında mevcut DoneCheck/owner mekanizmasına yönlendirir. Bu yerel kontrol yalnız `SIMULATED_DESIGN_READY_TO_REQUEST_REVIEW` üretebilir; resmî `VERIFIED_FINISH` üretemez.

**Gerçek kapılar:** `REAL_USER_IMPACT=HOLD_NOT_OBSERVED`, `CANONICAL_DONECHECK=HOLD_NOT_EVALUATED`.

## 7. Üç tur simülasyon ve karşıt denetim

| Tur | Uygulama | Testlenen farklılık | Sonuç |
|---|---|---|---|
| SIM-1 | 7 kontrol olumlu yol + tüm-kontrol tasarım hesaplayıcısı | Tasarım kabulü, resmî yetki korunumu | PASS |
| SIM-2 | 45 hedefli bozulma | Sahte kanıt, regresyon, yetki, karşılaştırılamayan muadil, kimlik kayması | 45/45 PASS |
| SIM-3 | 512 bozuk şema + 3.072 birleşik rastlantısal (sabit tohumlu) vaka | Fail-closed şema, deterministik tekrar ve çoklu açık | 3.584/3.584 PASS |

8 unittest yöntemi başarıyla çalıştırıldı. Aynı kod test kaynağını ve değerlendirmeyi birlikte içerdiğinden **bağımsız dış reviewer kanıtı mevcut değildir**. Tamamı yazılımdan türetilmiş sentetik vakadır; gerçek saha senaryosu olarak gösterilmez.

## 8. 24 yöntemle bağ ve sonraki gerçek adım

K01: Y01–Y03, Y06–Y09, Y15, Y16, Y18, Y24. K02: Y01–Y04, Y10–Y14, Y16–Y19, Y23. K03: Y05–Y09, Y11, Y20–Y22. K04: Y02–Y04, Y07–Y10, Y13, Y16–Y19, Y22–Y24. Bu eşleştirmeler atlası genişletmez; kalan Y kodları da ana sistemde korunur.

İcra sırası: **Work çıktısının SHA/owner/ödev kapsamıyla uzlaştırılması → bağımsız V1.2 tasarım incelemesi → tek izole GitHub PR ile gerçek entegrasyon ve CI → 3 gerçek görev öğrenme aktarımı + gerçek muadil benchmark + kullanıcı etkisi → Mac OSi saha kanıtı → canonical DoneCheck ve gereken Human Threshold**.

**Nihai durum:** `ZULFIKAR_V1_2_DESIGN_CANDIDATE=100/100` · `LOCAL_SYNTHETIC_POLICY_TEST=PASS` · `OFFICIAL_FINISH=HOLD`.

**Kalıcı sabit hedef:** Gerçek doğrulama tamamlandıktan sonra `VERIFIED_FINISH → BITTI_DUR`.
'''
report_path=ROOT/'ENGURU_ZULFIKAR_V1_2_MIMARI_FINIS_RAPORU.md'
report_path.write_text(report,encoding='utf8')
receipt['report_sha256']=hashlib.sha256(report_path.read_bytes()).hexdigest()
receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
print('UNITTEST=PASS (8 methods)')
print('DESIGN_SCORE=100/100 CANDIDATE')
print('TARGETED_MUTATIONS=45 SCHEMA=512 STRESS=3072')
print('RECEIPT_SHA256='+hashlib.sha256(receipt_path.read_bytes()).hexdigest())
print('REPORT_SHA256='+receipt['report_sha256'])
print('OFFICIAL_VERIFIED_FINISH=HOLD')