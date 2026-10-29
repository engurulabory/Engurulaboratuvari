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
