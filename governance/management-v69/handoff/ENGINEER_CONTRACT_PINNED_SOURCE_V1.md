# ENGÜRÜ Engineer İCRA — GitHub → OSi Kanıtlı Devir V1

STATE=REVIEW_ONLY / OSI_MUTATION=0 / VERIFIED_FINISH=HOLD

## Bağlam
Yönetim PR #211, aynı anda Engineer PR #14 ve ENGÜRÜ Süzgeci™ V3 kabul sınırları korunur. Bu belge main veya canonical ürün kabulü yerine geçmez. Engineer PR #14 üzerindeki değişiklikler ayrı açık dalda kalır; yetkili gözden geçirme sonrası gerekli fark entegre edilir.

## Yönetimden mühendisliğe devir
Zorunlu: task_id, canonical_source_commit, canonical_source_sha256, required_evidence, executor_scope, rollback_plan, producer, independent_reviewer, owner_grant_ref, accepted_control_ids, open_control_ids, target_inventory_pin, exact_head, acceptance_state. Ana yönetim kontrolü özgün ID'yle; mühendislik test sonucu kendi kanıt ID'siyle izlenir. Reviewer != producer. Kaynak drift veya eksik yetki -> HOLD.

## Kurulum tersine mimarlığı
Beklenen çalışan ürün ve sağlık denetimi → executable/source SHA → installation paths & permissions → dependencies/OS architecture and disk → approved inventory SHA → archived rollback point → verified immutable installer artifact. Üç ayrı exact-head GitHub CI başarı koşusu doğrulanmadan GITHUB_HANDOFF_READY oluşmaz.

## Saha
GitHub Actions macOS runner, kullanıcının Mac OSi sahası değildir. Kurulum ancak daha sonra owner-authorized local preflight, exact SHA-256 paket doğrulaması, path/symlink guard, çakışma kontrolü, idempotent second run, rollback proof ve Human Threshold ile gerçekleşir. Komut, gerçek doğrulanmış kurulum paketi üretildiğinde paket SHA'sıyla birlikte sunulur.

## DoneCheck
DESIGN_PASS / CI_PASS / OWNER_GRANT / FIELD_PASS / DONECHECK_AUTHORIZED ayrı sonuçlardır. Herhangi biri HOLD ise VERIFIED_FINISH=HOLD. Bu doküman üretim anahtarlarına, canonical ledger'a veya OSi dosyalarına müdahale etmez.
