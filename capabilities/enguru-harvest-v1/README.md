# ENGÜRÜ Yetenek Hasadı ve Kanıtlı Kaynak Fabrikası™ V1.1

**Durum:** GitHub mühendislik inceleme adayı. `main`, diğer ürünler, canonical V3, Zülfikar V1.3 ve Human Threshold™ korunur.

## Üretim hattı

Kaynak gözlemi → lisans/güvenlik/bütçe → kaynak SHA-256 → tekrarlı test → gerçek görev karşılaştırması → bağımsız inceleme → gereken insan kararı → ENGÜRÜ Mühendislik Kası.

Altı kütüphane: Skills · Advanced Prompts · Proven Sources · Data & Knowledge · Engineering Recipes · Evidence.

- `source_candidates.json`: GitHub connector üzerinden README'si gözlenmiş 30 kaynak adayı ve README Git SHA-1 blob kimlikleri. Bunlar repo commit SHA'sı veya tüm kaynak SHA-256'sı değildir. Lisans = UNVERIFIED, güvenlik = PENDING.
- `skill_kernel.py`: 12 taşınabilir, yerel Python işlevi; hiçbir ücretli API veya haricî kod çağrısı yapmaz.
- `harvest.py`: kendiliğinden PASS/ADOPTED terfisine kapalı kaynak sınıflandırıcı.
- `evidence_gate.py`: SHA-256 ve makbuz aşaması uyumu; sonucu yalnız EVIDENCE_CANDIDATE.
- `run_three_simulations.py`: mantıksal SIM1/SIM2/SIM3, gerçek sahayla ayrıştırılmış.
- `verify_head.py`: tam Git HEAD çalışma baytları ve V3 canonical SHA-256 denetimi.
- `ACCEPTANCE_MATRIX.md`: H01–H10 kanıt tablosu.
- `OSI_HANDOFF_PREPARATION.md`: yalnız gelecekteki Mac OSi sahası için geçiş hazırlığı.

## Çalıştırılabilir GitHub testleri

```bash
cd capabilities/enguru-harvest-v1
python3 -B -m unittest -v test_harvest test_evidence_gate test_skill_kernel
python3 -B run_three_simulations.py
python3 -B verify_head.py
```

Codex keşif adaptörü `.agents/skills/enguru-evidence-harvest/SKILL.md`, Claude Code keşif adaptörü `.claude/skills/enguru-evidence-harvest/SKILL.md`. Ortak beceri kaynağı aynıdır; sağlayıcıya ait hesap/ücret gereksinimleri bu modüle aktarılmaz.

## Doğruluk sınırı

Kaynak kayıtları gerçek 30 açık repo README gözlemine dayanır. 12 yerel deterministik işlev, 12 haricî PROVEN becerisi olarak gösterilmez. Lisans onayı, gerçek kullanıcı değeri, dış beceri çalıştırma, bağımsız PR incelemesi ve resmî Verified Finish kendi kanıtlarıyla HOLD. OSi yürütme 0.

## 2026-10-25 gerçek kaynak inceleme kazanımı

30 kaynağın README Git kimlikleri ve 29 kaynağın kök lisans dosyası Git kimlikleri gözlendi. Lisans dosyasının gözlemlenmesi tek başına yeniden dağıtım/çalıştırma izni vermez; bütün kaynaklar için `REDISTRIBUTION_APPROVAL=HOLD`. Kök lisans taraması eksik olan `anthropics/skills` için beceri bazında inceleme gerekir.

`license_gate.py` ile 30 kayıt eşleştirmesi; `external_skill_proof_plan.json` ile 12 somut dış beceri gerçek görev kabul vakası tanımlandı. Henüz kanıtlanmış **haricî** beceri sayısı 0/12'dir. Bu rakam, CI'de çalışan 12 bağımsız yerel Python operasyonundan ayrı tutulur.

OSi saha icrası 0; bu paket yerel kurulum/emir değildir.
