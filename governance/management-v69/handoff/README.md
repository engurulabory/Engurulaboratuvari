# ENGÜRÜ Yönetim V6.9 — GitHub → OSi kanıtlı devir V1

STATE: REVIEW_ONLY / OSI_MUTATION=0 / G2_G6_OFFICIAL=HOLD

Canonical authority: main AGENTS.md, ENGÜRÜ Evrensel Kanıtlı Tamamlama V3; PR #203, #204, #209 ve Engineer PR #14 farklı kanıt/yetki katmanlarıdır. Bu ek hiçbir G2–G6 kapısını kendi başına PASS yapmaz.

## Dört geliştirme
1. G2–G6: owner scope, Ed25519 gerçek imza, bağımsız reviewer, exact-head DoneCheck, append-only audit/recovery, yetkili merge ve Human Threshold gerçek kaynaklara bağlanır. Eksik olduğunda HOLD.
2. Yönetim → Mühendis devir: her özgün kontrol için task_id, source_commit, source_sha256, required_evidence, executor_scope, rollback_plan, reviewer, authority_ref, previous_state ve acceptance verilir. Üretici ve reviewer ayrıdır.
3. GitHub → OSi: destination inventory manifesti yalnız yetkili salt-okunur envanterden; OS/CPU/dependency, path allowlist, existing file conflict, disk, signature, previous SHA, rollback, idempotent second run, deny-on-drift. GitHub Actions macOS runner'ı gerçek OSi yerine geçmez.
4. Exact commit üç final tur: aynı 40 haneli head commit, aynı sözleşme, ayrı run id ve immutable receipts; tüm testler gerçek koşar. Bir düzeltme commit değiştirirse üç tur yeni HEAD'de baştan koşar.

## Ayrık nihai kapılar
- GITHUB_DESIGN_PASS: kaynak + doğrulayıcı + karşıt testler.
- GITHUB_HANDOFF_READY: exact HEAD'de üç gerçek CI koşusu, ayrı reviewer, paket SHA-256, idempotency/rollback ve manifest kabulü.
- OSI_FIELD_PASS: yalnız daha sonra, yetkili Mac üzerindeki yerel envanter, gerçek tek komut kurulum, sağlık denetimi, geri dönüş kanıtı.
- VERIFIED_FINISH: canonical DoneCheck + geçerli owner/issuer/reviewer + Human Threshold.

Birinci hedef yalnız GitHub hazırlık ve gerçek CI kanıtıdır. OSi alan hazırlığı ve kurulum, ayrı yetkili saha icrası ile yapılır. Gizli anahtarlar, kimlik bilgileri ve kullanıcı özel envanteri repoya taşınmaz. 
