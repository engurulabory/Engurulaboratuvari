# ENGÜRÜ IP & MODEL TRUST GATE™ v1.0

## Niyet
Engürü fikrî mülkiyetini, ticari sırlarını, erişim sırlarını ve emanet veriyi yapay zekâ kullanımında minimum gerekli erişim ilkesiyle korumak.

## Otorite akışı
Asset Classification → Model Trust Check → Context Minimization → Sanitization → Access Decision → Session Evidence → Output Verification → Human Threshold™ → Verified Finish

## IP sınıfları
- T0 Public — kamuya açık içerik.
- T1 Internal — düşük riskli kurum içi içerik.
- T2 Confidential — ticari değer taşıyan kurum içi içerik.
- T3 Core IP — özgün mimari, algoritma, scoring, yayınlanmamış ürün çekirdeği.
- T4 Crown Jewel — kaybı stratejik zarar doğuran patentlenebilir yöntem, gizli formül, ekonomik motor veya kritik araştırma.
- T5 Restricted — sırlar, kimlik/emanet veri, erişim anahtarları ve hukuken kısıtlı içerik.

## Temel hükümler
1. T5 hiçbir genel amaçlı model bağlamına girmez.
2. T4 local-first çalışır. Dış modele yalnız açık Human Threshold™ kararı ve sanitize edilmiş minimum bağlamla çıkabilir.
3. T3 için minimum disclosure ve fragmentation zorunludur.
4. API key, token, private key, seed phrase, parola, production secret ve `.env` içerikleri Secret Zero Rule™ kapsamındadır.
5. Model çıktısı evidence değildir. Test + Evidence + DoneCheck™ olmadan PASS verilmez.
6. Provider/model güven seviyesi beyana göre değil `MODEL_REGISTRY.json` içindeki doğrulanmış sınıra göre uygulanır.
7. Sağlayıcı şartı doğrulanmamışsa `policy_status=HOLD` kalır ve gate daha dar olan sınırı uygular.
8. Her karar makinece kaydedilebilir bir Decision Envelope üretmelidir.

## Fail-closed
Belirsizlikte izin genişletilmez. Gate `HOLD` veya `BLOCKED` döndürür.

## Human Threshold™
Şu durumlarda insan kararı gerekir: T4 dış model kullanımı, yeni provider ekleme, provider güven seviyesini yükseltme, güvenlik istisnası, irreversible publish/payment/legal action, veri ihlali değerlendirmesi.

## DoneCheck™ kabul ölçütleri
- policy schema doğrulanır,
- secret scanner kritik örnekleri yakalar,
- T5 daima BLOCKED,
- T4 cloud varsayılanı BLOCKED/HOLD,
- T0/T1 uygun sağlayıcıyla PASS,
- karar nedeni ve next action üretilir,
- CI testleri yeşildir.
