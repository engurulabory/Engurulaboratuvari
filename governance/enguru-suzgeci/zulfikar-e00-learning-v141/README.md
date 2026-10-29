# ENGÜRÜ Zülfikar™ V1.4.1 — E00 Deneyimden Görev ve Kanıtlı Öğrenme

**Yetki sınırı:** Yalnız mevcut Zülfikar V1.4.1 DÖM V1.0 motorunu kullanan **izole, atılabilir test çalışma alanı**. Yeni owner/issuer, GitHub birleştirmesi, Mac OSi yetkisi, genel Verified Finish veya sessiz kod öz-güncellemesi oluşturmaz.

## Neyi çalışır hâle getirir?

1. Somut bir olumsuz/olumlu deneyim kaydını girdi kabul eder.
2. Etkin kaynak dosyasının **gerçek bayt SHA-256** değeriyle olayın kaynak kimliğini karşılaştırır.
3. Olayın bildirdiği kriter açığını **görev adayı** olarak çıkarır: `E00_REPAIR_TASK_CANDIDATE`.
4. **Yalnız mevcut yetkili DÖM'ün** simulator/evaluator/repairer/real_tester/independent_verifier callback'lerini, en fazla üç turda koordine eder.
5. DÖM gerçek alt süreç ve ayrı doğrulayıcı kanıtıyla 100 teşhis adayı üretirse `E00_ISOLATED_TEST_CANDIDATE` döndürür.
6. İnsan yetkisi + ürün kabulü ayrı kalır: `officialPassIssued=false`, `productVerifiedFinish=NOT_ISSUED`. PASS etiketi yalnız **izole test kapsamının** CI'ındadır.

## İstenen mini rapor şablonu

`olumsuz durum → gerçek makbuz → sebep → küçük fark/onarım → yeniden test → korunan kazanım → yeni yetenek → GitHub exact-head CI → Mac FIELD / resmi finish`.

Yalnız olay kaydı, kendiliğinden PASS veya otomatik sürüm güncellemesi değildir.
Ölçütler zaten doğruysa `E00_NO_CHANGE_REPORTED` verilir; bu resmî PASS da sayılmaz.
Başarısız veya kanıtsız durumda `HOLD`.

## Gerçek negatif testler (yalnız GitHub runner'ının izole dosyaları)

```bash
python3 -B -m unittest discover -s governance/enguru-suzgeci/zulfikar-e00-learning-v141 -p 'test_experience_learning.py' -v
```

En az 18 sınama: kaynak kayması, bozuk şema, sahte boolean, sahte kriter, sahte yetki kapsamı, tekrarlı kriter, izin verilmeyen tür, kontrolsüz tur sayısı, onarımsız tekrar, bağımsız doğrulayıcı reddi, çıktı sonradan değişimi, gerçek subprocess ile doğrulanmış onarım, olumlu deneyimde gereksiz güncelleme yapılmaması.

## Kanonik bağımlılık

`governance/enguru-suzgeci/zulfikar-v12/v141/dom/engine.py` — mevcut **DÖM**. Motor kaynaklarının hiçbiri bu dalda yeniden yazılmaz. GitHub `main`, PR #247, gerçek Mac OSi, Cinema Factory kaynakları ve Human Threshold değiştirilmez.

**Bitiş sınırı:** `E00_GITHUB_TECHNICAL_TESTS=PASS` yalnız ilgili PR exact-head CI geçtiğinde. `E00_MAC_FIELD=NOT_TESTED`, `E00_SELF_UPDATE_PRODUCTION=NOT_IMPLEMENTED`, `OFFICIAL_VERIFIED_FINISH=HOLD`.


## E00-DVK — Durumdan Vazife Kutusu (çalışan izole teknik aday)

`experience_box.py` SQLite WAL + FULL synchronous günlükleriyle **12 alan × 8 olay türü = 96 başlangıç sınıfını** destekler. Bu bir sınıflandırma haritasıdır; 96 gerçek yaşanmış olay veya sınanmış üretim sonucu değildir.

**Kalıcı öğrenme sözleşmesi:**

- Her olumlu/olumsuz deneyimin olay kimliği, kaynak SHA, açıklaması ve dersi korunur.
- Başarısızlık tanısında **neden, açık koşul, gereksinim ve düzeltme** ayrı kayıtlanır.
- Çözüm hazırsa `READY`, araştırma gerekiyorsa `RESEARCH`; aynı hedef/kaynak/alan için en fazla 12 olay tek geliştirme paketine alınır.
- Her çevrim en çok üç tur gerçek izole test/karşıt denemedir; üç tur sonunda başarısızlık `HOLD` ve makbuz olarak korunur. **Bu sınır öğrenme kaydının ömrüne bir sınır koymaz.**
- Yeni çevrim, önceki başarısızlıktan sonra **yeni teşhis ve gerçek çözüm farkı** olmadan başlatılamaz. Çevrim sınırı sayesinde sonsuz tek yürütme önlenir; ayrı yetkili çevrimler gerekçe ve kaynakla sürdürülebilir.
- Paket kısmen başarıya ulaşsa bile önceki adaylar tekrar doğrulanır; eski PASS yeni koşula otomatik taşınmaz.
- `attempts` ve `diagnostics` kayıtları korunur; yeniden başlatma ve araştırma kuyruğu kalıcılığı sınanır.
- **Arşivleme** yalnız tüm paket teknik adayları + dış kaynak/insan doğrulamasından sonra bir kayıt hareketidir. Bu adaptör kod yayınlama, otomatik merge, gerçek üretimde kendini değiştirme veya resmî Verified Finish verme yetkisi taşımaz.
- Arşivlenen geçmiş kalır; aynı deneyimin yeni olay kimliğiyle yeniden yaşanması yeni açık görev olabilir.

**Günlük mini bildirge:** yaşanan hata → neden → açık gereksinimler → uygulanan küçük onarım → gerçek test ve karşıt test → sağlanan yeni yetenek → kaynak HEAD/CI → kalan HOLD/owner eşiği.

**CI kapsamı:** `test_experience_learning.py` (18 senaryo) + `test_experience_box.py` (48 senaryo), üç kaynaklı CI tekrarı: **3 × 66 = 198 test yürütmesi** (aynı 66 senaryonun tekrarıdır). Bu rakam yalnız GitHub job gerçek başarıya ulaştığında PASS olarak ifade edilir. Ölçülmemiş gerçek Mac OSi sürekliliği/saha ürünü kabulü HOLD kalır.

**Sınır:** Bu uygulamanın `archive_authorized` mekanizmasındaki dış doğrulayıcılar test adaptörüne enjekte edilen callback sözleşmesidir; gerçek güvenilir imza/issuer veya Mac operatör yetkisi değildir. Saha bağlantısı, resmi Human Threshold ve gerçek bağımsız kabul kendi aşamasında gerçekleşir.
