# ENGÜRÜ CAPABILITY & AGENT AUTHORITY CONTRACT™ v0.1

## Niyet
Yeni model, araç, bağlantı, yürütme yüzeyi veya alt-ajan kabiliyeti kazanımının otomatik yetki artışına dönüşmesini engellemek; delegation ve self-modification akışlarını fail-closed yönetmek.

## Kilit hükümler
1. **Capability ≠ Authority.**
2. **Delegation ≠ Authority Transfer.**
3. Yeni kabiliyet mevcut yetkiyi genişletmez.
4. Alt-ajan ebeveyn yetkisini otomatik miras almaz.
5. Credential inheritance varsayılanı DENY'dır.
6. Governance, evidence, DoneCheck™ veya Human Threshold™ kurallarını değiştirme girişimi dış otorite gerektirir.
7. Kritik eylemde claim producer ile final verifier ayrılır.
8. Belirsizlikte HOLD; açık yetki ihlalinde BLOCKED uygulanır.

## Authority Levels
- L0 — Observe
- L1 — Analyze
- L2 — Draft
- L3 — Execute Reversible
- L4 — Execute External
- L5 — Sensitive / Irreversible

Actor kendi authority level'ını yükseltemez.

## Capability Escalation Gate™
Gate şu değişimleri capability escalation sayar: model upgrade, yeni tool/connector, shell, filesystem write, network, production deploy, secret/credential access, payment, external messaging, persistent runtime, self-code/runtime modification, agent creation/delegation, governance mutation.

Akış:
state → claim → evidence → next action

Karar:
- PASS — talep mevcut grant + scope + policy ceiling içindedir.
- HOLD — yeni explicit grant veya Human Threshold™ gerekir.
- BLOCKED — policy tarafından yasaklanan escalation/bypass vardır.

## Agent Reproduction & Delegation Gate™
Effective authority:
`min(parent_authority, task_authority, policy_ceiling, explicit_grant)`

No Transitive Authority™: ebeveynin sahip olduğu yetkiler alt-ajana kendiliğinden geçmez.

Delegation depth sözleşmede açık tanımlanır. Limitsiz recursive delegation BLOCKED'dır.

## Credential Non-Inheritance™
API key, token, private key, session credential, payment credential ve signing key alt-ajana otomatik verilmez.

Gerekli olduğunda minimum secret + minimum scope + minimum lifetime uygulanır.

## Self-Modification Boundary
Verified-learning serbesttir; authority/policy/governance bypass değildir.

Şu değişiklikler explicit external authority gerektirir:
- system/governance policy
- authority rules
- verification/DoneCheck™ logic
- Human Threshold™
- credential policy
- deployment policy

## Human Threshold™
Varsayılan olarak şu eylemler Human Threshold™ gerektirir:
- production deletion
- payment / financial transfer
- contract / legal statement
- public publication
- real-person external communication
- secret rotation
- privileged actor creation
- irreversible data mutation

## DoneCheck™
Verified Finish için:
1. task completed
2. authority valid
3. scope respected
4. evidence verified
5. required Human Threshold satisfied

## Failure Taxonomy
- CAPABILITY_ESCALATION_UNAPPROVED
- AUTHORITY_ESCALATION_ATTEMPT
- AUTHORITY_SCOPE_VIOLATION
- TRANSITIVE_AUTHORITY_ATTEMPT
- CREDENTIAL_INHERITANCE_ATTEMPT
- UNAPPROVED_DELEGATION
- DELEGATION_DEPTH_EXCEEDED
- SELF_MODIFICATION_ATTEMPT
- GOVERNANCE_BYPASS_ATTEMPT
- HUMAN_THRESHOLD_BYPASS_ATTEMPT
- EVIDENCE_BYPASS_ATTEMPT
- AUTONOMY_WINDOW_EXPIRED
- IRREVERSIBLE_ACTION_UNAPPROVED

## Fail-closed
Kanıt veya grant eksikse olumlu hüküm üretilmez.
