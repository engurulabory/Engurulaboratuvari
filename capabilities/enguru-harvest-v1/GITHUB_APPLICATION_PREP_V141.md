# ENGÜRÜ Yetenek Hasadı™ · Zülfikar V1.4.1 · GitHub Uygulama Öncesi Hazırlık

**Sabit hedef:** GitHub üzerinde gerekli uygulamayı güvenli, tekrarlanabilir ve tam kanıt sözleşmeli olarak gerçekleştirmeye hazır olmak. Buradaki **100/100 yalnız hazırlık PASS**; gerçek uygulama, haricî ürün yeteneği PROVEN, resmî Verified Finish ve owner yetkili DoneCheck ayrı değerlendirilir.

## 8 kapı · her aşamada 5 kontrol, 5/5 = hazırlık 100/100

T01 **Temel:** sabit kullanıcı hedefi; canonical V3 kaynağı; kaynak envanteri; tek insan owner ve korunacak kazanımlar; risk ve kullanım kısıtları. Belgeler: `goal.json`, `UPSTREAM_GITHUB_PINS_30.json`, `root_license_observations.json`, `ZULFIKAR_V141_SOURCE_REUSE.json`.

T02 **Hedef hazırlığı:** H01–H10 kabul kimliği, P01–P12 farklı dış beceri, K01–K05 sıralı iş listesi, gerçek kullanıcı görevine özel beş pilot, 100 kabul sözleşmesi ve duruş. Belgeler: `ACCEPTANCE_MATRIX.md`, `external_skill_proof_plan.json`, `WORK_PACKAGES_ZULFIKAR_V13.json`, `PILOT_APPLICATION_PREP_V141.json`, `ZULFIKAR_V131_100_GATE_CONTRACT.json`.

A01 **Mimari/mühendislik:** tek `skill_kernel.py`; repo/haklar zinciri; SHA-256 ve GIT HEAD kapısı; dış API ve yetki izolasyonu; teknik CI ürün makbuzu ayrımı. Kaynaklar: `skill_kernel.py`, `verify_head.py`, `evidence_gate.py`, `k02_source_policy.py`, `ZULFIKAR_V141_SOURCE_REUSE.json`.

A02 **Teori/karşıt:** üç simülasyon sözleşmesi, gerçek regresyon, negatif hak testi, kaynak kayması ve sahte PASS testleri, orijinal V1.4.1 DÖM 177 testinin GitHub runner'da source-locked tekrar yolu. Kaynaklar: `run_three_simulations.py`, `test_evidence_gate.py`, `test_a05_license_scope_routing.py`, `test_zulfikar_v141_reuse.py`, `reuse_zulfikar_v141.py`.

A03 **Uçtan uca / finiş sözleşmesi:** kanıt akışı, 12 özgün becerinin PROVEN şartı, gerçek kullanıcı deneyi, canonical DoneCheck, Human Threshold ve tekrarlı gözlem. Kaynaklar: `harvest.py`, `external_skill_proof_plan.json`, `PILOT_APPLICATION_PREP_V141.json`, `ZULFIKAR_V131_100_GATE_CONTRACT.json`, `V141_SESSION_ACCEPTANCE_V1.json`.

A04 **GitHub teknik hazırlık:** bir PR üzerinden izole yetkili dal; GitHub CI koşu tanımı; `verify_head.py` canonical ve exact HEAD; kaynak lisans kanıtı; yayın kararı ve merge HOLD. Kaynaklar: `.github/workflows/enguru-harvest-v1.yml`, `verify_head.py`, `verify_license_text_bytes.py`, `a05_license_scope_routing.py`, `TECHNICAL_TRIAL_LEDGER_V1.md`. Son commit için tüm 5 workflow SUCCESS şartı ayrı yürütme denetimidir.

A05 **Gerçek görev pilotlarının hazırlığı:** beş gerçek kullanıcı görevine ait giriş, karşılaştırma, kalite, negatif vaka ve owner kabul planı; 12 dış beceri özgün ID'leri; yetkili erişim ihtiyacı; sıfır zorunlu ücretli API; gerçek saha bağımsız kanıtı. Kaynaklar: `PILOT_APPLICATION_PREP_V141.json`, `run_a05_real_github_tasks.py`, `external_skill_proof_plan.json`, `a05_license_scope_routing.py`, `test_a05_real_github_tasks.py`. GitHub'da geçen 15 kaynak işi, owner'ın gerçek kullanıcı fayda kabulü değildir.

A06 **OSi'ye gitmeden önce GitHub çıkışı:** kaynak SHA kilitli paket üreticisi, güvenli rollback, Mac uyumlulukta sorulacak sorular, ayrı owner saha eşiği, Mac yazma/çalıştırma sıfır. Kaynaklar: `build_github_osi_handoff.py`, `test_github_osi_handoff.py`, `OSI_HANDOFF_PREPARATION.md`, `ZULFIKAR_100_FINIS_VE_SINIRLAR.md`, `READINESS_AUDIT_V3.json`.

## Zülfikar Döngü Onarım™ 

Her kapıda `simüle et → puanla → eksik bul → onar → gerçek test → karşıt test → yeniden simüle et → puanla`; ölçüt 5/5 doğrulanmadan o kapının **hazırlık PASS** hükmü üretilmez. 8 kapının toplamı 40/40. CI kaynak ID ve bayt eşliğini denetler, üç ayrı hazırlık simülasyonu gerçek Python çalışmasıdır fakat kanıt kapsamı **GitHub hazırlık** ile sınırlıdır.

## Uygulama yetki sınırları

- Haricî kaynaklar, lisans hakları veya üçüncü taraf ücretli erişim `HOLD`; bir kaynağın commit+LICENSE doğrulaması yasal izin sağlamaz.
- Hazırlık 100/100 sonunda `READY_FOR_AUTHORIZED_GITHUB_APPLICATION`; mevcut PR teknik deneyleri ayrıca raporlanır. `GITHUB_VERIFIED_FINISH` ve `PROVEN=12/12` otomatik kabul edilmez.
- Gerçek beş kullanıcı görevi, owner ve DoneCheck doğrulanınca uygulama geçer.
- Mac OSi yürütmesi, `main` merge ve yeni owner/issuer üretimi: **0**.
