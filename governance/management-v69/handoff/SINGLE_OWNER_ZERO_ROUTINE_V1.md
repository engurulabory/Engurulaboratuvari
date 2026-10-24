# ENGÜRÜ Yönetim İCRA V6.9 — Tek Owner / Bağımsız Makine Kanıtı V1
STATUS=PROPOSED_CANONICAL_AMENDMENT; OWNER_DESIGN_DIRECTION=ACCEPTED; CURRENT_CANONICAL_AUTHORITY=UNCHANGED
MAIN_TARGET=9_CAPABILITIES_THEORETICAL_100_100
OSI_MUTATION=0; G2_G6_OFFICIAL=HOLD; VERIFIED_FINISH=HOLD

## Sade çalışma sözleşmesi
Tek insan yetkili engurulabory. Yeni insan reviewer hesabı gerektirmeyen tasarım hedefi: bağımsız kod doğrulayıcı + gerçek GitHub Actions kanıtı + kaynağa bağlı hash + karşıt test + yalnız risk kapısında owner kararı. Makine doğrulaması bağımsız insan review olarak adlandırılmaz.

## Rutin iş akışı
PRODUCT_GOAL → READ_ONLY_INVENTORY_PIN → MANAGEMENT_TASK_DAG → ENGINEER_EXECUTE → ISOLATED_ADVERSARIAL_TEST → IMMUTABLE_ARTIFACT_MANIFEST → INDEPENDENT_MACHINE_VERIFIER → OWNER_THRESHOLD_IF_REQUIRED → THEORETICAL_ACCEPTANCE → OSI_FIELD_LATER.

## Koruma ve kabul
- canonical sözleşmede ikinci insan reviewer koşulu bulunuyorsa, bu V1 önerisi onun yerine geçmez. Yetkili, sürümlü politika değişikliği ancak ayrı onay/bağımsız koruma testleriyle yürürlüğe girer.
- Tek owner için otomatik self-approval, sahte reviewer kimliği, uydurma CI run ID, sahte Ed25519 kararı, sahte DoneCheck = HOLD.
- Üç ayrı gerçek run ID gerekiyor ise aynı run'ın üç attempt'i = HOLD. Geçerli kural ancak kanıta dayalı canonical güncelleme ile değişebilir.
- Maliyet hedefi 0 ek ücret; kullanım kota/ücretlerini gerçek GitHub ayarları belirler. Rutin manuel adım hedefi 0; gerçek owner Human Threshold korunur.
- Mutasyon: PR inceleme dalı; main ve Mac OSi değişikliği yok.

## Dokuz hedef
01 Mimarlık → 02 İş Yapma → 03 Finiş → 04 Rahatlık → 05 Akış → 06 Güvenlik ve Kanıt → 07 OSi Kurulum Hazırlığı → 08 Mühendislik → 09 İç İşleyiş/Uyum.
Her biri: özgün hedef → gerçek gereksinim → çalışan model → karşıt test → GitHub kanıtı → bağımsız teorik kabul.
