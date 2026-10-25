# ENGÜRÜ — Tek GitHub Yöntem Girişi V2

**Konum:** `engurulabory/Engurulaboratuvari` → güncel `main`.
**Statü:** GitHub üzerindeki ana yöntem için giriş rehberi. **Yeni çekirdek, üretim motoru veya otorite içermez.**

## Tek oturum başlangıcı

1. GitHub bağlantısını aç, `main` dalındaki **anlık HEAD** kimliğini kaydet.
2. [AGENTS.md](../../AGENTS.md) → [canonical V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) ve [kilidi](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) → ürünün özgün kabul sözleşmesini sırayla doğrula.
3. İşin türünü belirle: [Altı alan](ENGURU_ALTI_URETIM_ALANI_V1.json): CORE / ENGINE / AGENT / WEB / APP / COMMERCE. İş birden fazla alanı kapsarsa özgün şartları bir kez sayıp uygun adaptörleri birlikte uygula.
4. Kullanıcıyla ilk kurguda gerçek amaç, maliyet, risk, başarı ölçütü, karşıt örnek ve yetkiyi sabitle. [Ana Terazi](ENGURU_ANA_TERAZI_5X100_V1.md) teoriyi / tasarımı / üç farklı karşıt simülasyon ailesini ayrı değerlendirir.
5. [Dinamik tasarım döngüsü](../../tools/enguru_method_dynamic_loop_v2.py): **ilk kurgu → simüle et → puanla → eksik/ihtiyaç/gereksinim/hata/yanlış/kaynak hatasını teşhis et → kanıta bağlı düzelt → yeniden simüle et**. En fazla üç tasarım turu hedefi 100/100; açıklar varsa gerekçeli HOLD.
6. [Dışarıdan karşıt senaryolar](../../tools/enguru_method_dynamic_adversarial_v2.py), özgün kabul paydası, sentetik/gerçek test ayrımı ve eylem yetkisi ayrı kontrol edilir.
7. Erişilebilir gerçek mühendislik ve GitHub CI çalıştırılır; somut kaynak, commit, job, çıktı ve SHA kaydedilir. DoneCheck™ v1.2 ve gereken Human Threshold™ yalnız canonical kabul zinciri üzerinden kullanılabilir.

## Tek çıktı sözleşmesi

```text
GOAL=<tek kabul hedefi>
DOMAIN=<CORE|ENGINE|AGENT|WEB|APP|COMMERCE|COMPOSITE>
SOURCE_MAIN=<anlık HEAD SHA>
ORIGINAL_CONTROLS=<tekilleştirilmiş ID ve sabit payda>
THEORY_DESIGN_SIM1_SIM2_SIM3=<her biri gerçek ölçülmüş puan>
THREE_REPAIR_ROUNDS=<başlangıç, değişim, sonuç, kalan HOLD>
REAL_GITHUB_TESTS=<işlem/job/commit/SHA>
INDEPENDENT_VALIDATION=<mekanizma + reviewer yetkisi ayrı>
REAL_FIELD_AND_AUTHORITY=<gerekli kendi PASS/HOLD>
NEXT_ACTION=<tek somut hareket>
VERDICT=<PASS veya delilli HOLD>
```

**Yalnız GitHub ile başlayan kullanımda OSi saha testleri** `HOLD_NOT_EXECUTED` olarak tutulur. **Gerçek kullanıcı kurgusu**, örnek simülatördeki sentetik kullanıcı girdisinden ayrıdır. GitHub ana yöntemin kod başarısı, altı alanın gerçek ürün kabulü anlamına gelmez.

## Önceki kayıt ve güncellik

- PR #221 birleşmesi: `9900f4ca7a17f99898521bdab1bfbe86784ecc07` — **tarihsel kesin kaynak**.
- Bu belgede sabitlenen SHA, sonsuza kadar güncel HEAD kabul edilmez. Güncel kaynak GitHub `main` üzerinden okunur.
- [Atlas](ENGURU_CALISMA_YONTEMLERI_ATLASI_V1.md), [Altı Alan V1](ENGURU_ALTI_URETIM_UYARLAMA_V1.md), [V3](ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) ve ürün özgün sözleşmeleri içerik otoritesidir. Bu giriş yalnız çalışma sırasıdır.

**Bitiş:** `GERÇEK HAKİKAT → 3 TUR KANITLI TASARIM → YETKİLİ GERÇEK İCRA → BAĞIMSIZ KANIT → GEREKEN KABUL → İLERLE`.
