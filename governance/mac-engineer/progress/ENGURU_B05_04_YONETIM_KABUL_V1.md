# ENGÜRÜ Yönetim — B05-04 exact branch/base/ancestry kabulü

**Tarih:** 22.10.2026
**Kontrol:** `B05-04`
**Özgün şart:** Yetkili branch, base ve ancestry izleri doğrulandı
**Önce:** `HOLD`
**Karar:** `PASS_EVIDENCE` — source lineage recognition/preservation scoped acceptance

## Onay ve teknik temel

Yetkili ürün sahibinin 22.10.2026 Yönetim oturumundaki açık onayı, iki deponun **ayrı ve eşzamanlı korunacak Git kaynak geçmişleri** olarak tanınması, mevcut kaynakların ve B05-06 onaylı 138 dosyanın yerinde korunması kapsamındadır. Bu izin `ENGURU_B05_04_OWNER_BRANCH_BASE_DECISION_20261022.json` olarak GitHub PR #191 inceleme dalında kayıt altındadır; chat/GitHub kriptografik özdeşleştirme ve imzalı canonical issuer statüsü ayrıca sağlanmış sayılmaz.

**Gerçek Mac İCRA raporu:** isolated ancestry 2/2 PASS, karşıt öz test 13/13 PASS, kaynak korunması PASS, mutation/remote write 0. İzole Mac acceptance packet SHA256 `43b68bbd8781ef4c9f9d46655546fcbc87cb3070012d89bfa5eb9924587dc0b8`. Bu SHA saha mühendisliği tesliminden alınmıştır; bu Yönetim ortamında özgün Mac paket baytları yeniden hashlenmedi.

**Control:** local branch `feat/mac-engineer-v08-product-engineering-operator`, HEAD `269854b8a42a27e9419eae65a3c9e349bdcc7300`; PR #191 at scoped decision `8b2819ee612de896fe9237123c4a2a00c7d4df67`; Mac recorded local↔main 634/50, local↔PR 634/117.

**Product:** local branch `feat/v08-native-productization-provenance`, HEAD `26925c21c7816a90edc0eb047382aba8c696764c`; PR #14 at scoped decision `a512e1efbc5e6f9c64c8965b2cebbb474d8225d8`; Mac recorded local↔main 185/0, local↔PR 185/66.

**Koruma:** `B05-06` owner preservation commit `d4cc4cc448586b082141389f77e9773095ae24a2`; 138 file preservation decisions. GitHub reviewer approval veya merge, remote parity, canonical writer, signer, Ed25519 attestation, full Native live application NOT asserted by this B05-04 scope.

## Yönetim kapsam kararı

Gerçek Mac izole geçmiş ayrışma raporunun exact path/SHA delilleri, bağlı GitHub PR başlıkları, önceki B05-06 kapsamlı koruma kararı ve bugünkü yeni owner açık onayı birlikte **özgün branch/base/ancestry tanıma ve koruma** şartını karşılamaktadır. Ayrı `B05-05/B05-08/B05-09/B05-10` kontrolleri HOLD kalır. İCRA'nın 13/13 test sonucu ayrıca yeniden çalıştırılmış gibi sunulmaz.

**Kabul muhasebesi:** 26→27/100, 73 HOLD; JSON+Markdown tekil B05-04 güncellemesi ve exact-head CI sonrası kesinleşir. H1/H2/H3 resmî 0/12; F01–F06 kapanmış 0/6; Native/DoneCheck/Verified Finish HOLD.

**Sonraki:** B05-05 gerçek local/remote HEAD parity, source owner scope ve korunmuş izolasyon; alternatif olarak bağımsız B06-09 Native Info.plist v0.8 dar teknik kabul şartı, her biri özgün acceptance ile ayrı değerlendirilir.
