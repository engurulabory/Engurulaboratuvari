# ENGÜRÜ V23 — Tek Yetkili Human Threshold™ Kararı

**STATE:** `HOLD_OWNER_REVIEWER_AUTHORITY`  
**İCRA ürün kapsamı:** ENGÜRÜ Mac Engineer™ — resmî H1/H2/H3 4+4+4, F01.  
**Tek karar sahibi:** Mevcut ENGÜRÜ canonical kaynağında bu on iki kriteri kabul etmeye yetkili **owner** ve kapsamı doğrulanmış **Ed25519 reviewer**. İsim/key kimliği, source authorization ile henüz PASS değildir.

## Karar sorusu — bir kapsam

**H1/H2/H3 on iki kriterin yetkili canonical sahibi, kriter sözleşmesi ve yetkilendirilmiş reviewer hangi kesin kaynak/branch/commit/blob ve audit zincirinde?**

**A:** Yetkili kaynak mevcutsa `OWNER_ID`, `OWNER_AUTHORITY_SOURCE`, `REVIEWER_ID`, `ED25519_KEY_ID_AND_AUTHORIZATION`, `CRITERIA_SET_SHA`, `BRANCH_COMMIT_BLOB` değerlerini gerçek kayıt ve yetkili kararla bağla.

**B:** Kanıtlanmış kaynak boşluğunda yetkili owner, yalnız bu on iki kriter için dar kapsamlı karar/grant ve reviewer authorization'ı mevcut Human Threshold mekanizmasıyla sonuçlandırsın; tam audit receipt sunsun.

**Eşik:** Bu karar sahibinin kanıtlı izni gelince Mac runtime → Progress Core™ → Mandatory DoneCheck JSON → DoneCheck `verifyTask` zincirini doğrulamak üzere adapter kabulü ve negatif test yapılır. H1 P-256 Secure Enclave signer yetkisi, DoneCheck Ed25519 reviewer yetkisinden ayrıdır.

## Mevcut kanıt kimlikleri

- V22 insan karar dosyası SHA256: `666c73f2ac30b912f23735a78d0191bd2905a11d7d7f8cb960e1255c02f7c67c` (V22 AudiV13 kaynak bytes tekrar doğrulandı).
- V22 candidate-only kriter SHA256: `208a32c7a8b93204c6b9a414086c8d43bf9216b22c7ccbf53ef5dac09cde9ada` (**yetkili CRITERIA_SET_SHA değildir**).
- Yerel kontrol HEAD: `269854b8a42a27e9419eae65a3c9e349bdcc7300`.
- Güncel Yönetim PR #191 HEAD: `758e4ad1d133a3c62311cfb0f4c4b71f35c7e8d2`.
- Canonical main DoneCheck blob: `a3fa94c6a65ae768259dea40f066e09ede5ace63`; yerel blob: `a37c2fbb19a50f5e8b788172b880c116a30d1775` (kaynak kapsam farkı).
- `governance/mac-engineer/DONECHECK_AUTHORITY_MODEL_V1.md`; blob `a37c2fbb19a50f5e8b788172b880c116a30d1775`, SHA256 `8b50a85ee082fe4be45ead4d27b329bde60472b368c9c68cabf763c41aa88765`; status `PASS_SOURCE_IDENTIFIED_NOT_CRITERIA_OWNER_AUTHORIZATION`
- `governance/mac-engineer/V08_GATE12_REVIEWER_AUTHORITY_V1.json`; blob `552b0a671693db6b20e7271328a4bbfbf0562ed3`, SHA256 `c0da28b74e05c05dca5cdfa9978be908c5220abbd5ac17ee1a10c083324dff40`; status `PASS_SOURCE_IDENTIFIED_NOT_CRITERIA_OWNER_AUTHORIZATION`
- `governance/mac-engineer/V08_GATE12_REVIEWER_AUTHORITY_V1.schema.json`; blob `54820d7a000acb512862c010020923ecc1925334`, SHA256 `b3339c75777ae8e8c25c8957d80b4986e8e4aad45c0d5d515e42e79f05c9872d`; status `PASS_SOURCE_IDENTIFIED_NOT_CRITERIA_OWNER_AUTHORIZATION`
- `governance/mac-engineer/EVIDENCE_DONECHECK_HUMAN_THRESHOLD_BINDING_V1.json`; blob `8fdbdbcbd33289398a1d8d7b2b515d16c1dcd40a`, SHA256 `57159e0c0dee401bfa69a8b131b395fa04d4817f6c437785f13ddd9bc7c139e5`; status `PASS_SOURCE_IDENTIFIED_NOT_CRITERIA_OWNER_AUTHORIZATION`
- `governance/mac-engineer/MAC_NATIVE_ENGINEERING_AUTHORITY_V1.md`; blob `421f678243d93556f104555fdf8c662171f83491`, SHA256 `4d37b6c22a18852ddd402ed5ae2925b00ec44e46caba67e9379d2e36a4199e84`; status `PASS_SOURCE_IDENTIFIED_NOT_CRITERIA_OWNER_AUTHORIZATION`

## Kabulün gerekli receipt alanları

`OWNER_ID`, `OWNER_AUTHORITY_SOURCE`, `REVIEWER_ID`, `REVIEWER_KEY_ID`, `REVIEWER_ED25519_PUBLIC_KEY_AUTHORIZATION`, `CRITERIA_SET_SHA`, `BRANCH_COMMIT_BLOB`, `MAC_RUNTIME_PROGRESS_CORE_MANDATORY_DONECHECK_BINDING`, `VERIFYTASK_RESULT`, `SIGNED_HUMAN_REVIEW`, `DURABLE_AUDIT_RECEIPT`.

**Şimdi:** `OWNER_AUTHORIZED=HOLD` · `REVIEWER_AUTHORIZED=HOLD` · `MAC_DONECHECK_LIVE_BINDING=HOLD` · `H1/H2/H3=0/12`.
**Tek sonraki insan kararı:** A mevcut yetkili sözleşmeyi kanıtlı kabul veya B kaynak boşluğuna scoped authorization; ardından yetkili entegrasyon ve doğrulama.
