# ENGÜRÜ Ana Yöntem™ — D01–D48 Üç Ayrı Karşıt Anlamsal İnceleme V1

**Tarih:** 25 Ekim 2026. **İş:** ENGÜRÜ masa başı 97/100 değerlendirmesindeki son kaynak-anlam incelemesini farklı üç bozma türüyle sınamak. **Hedef:** 98/100 değerlendirmesinin dürüst kanıt zemini.

**Korunan otorite:** `AGENTS.md`, SHA-256 kilitli Evrensel V3, 48 canonical D kontrolü, 5 × 100 teorik Ana Terazi, altı üretim alanı, mevcut DoneCheck™ v1.2 / Human Threshold™.

## Doğrudan kaynak incelemesi

Sekiz üretici referansının kamuya açık **asıl kapsamına** bakıldı; bu bir AI masa başı semantik ikinci bakıştır, **ayrı yetkili insan reviewer** sonucu değildir.

- [NIST AI RMF Playbook](https://airc.nist.gov/airmf-resources/playbook/) — GOVERN/MAP/MEASURE/MANAGE, risk, kullanıcı etkisi ve yönetişim.
- [DORA software-delivery metrics](https://dora.dev/guides/dora-metrics/) — değişiklik teslim süresi, sıklık, başarısızlık ve toparlanma metrikleri; toplam para veya API ücreti hesabı değildir.
- [SLSA Provenance](https://slsa.dev/spec/v1.2/provenance) — sürüm ve build kökeninin denetlenebilir izi; kullanıcı deneyimi veya hukuki sözleşme sertifikası değildir.
- [Google SRE Implementing SLOs](https://sre.google/workbook/implementing-slos/) — SLI/SLO/error budget; native uygulamanın gerçek restart testi değildir.
- [NIST SSDF SP 800-218](https://csrc.nist.gov/pubs/sp/800/218/final) — güvenli yazılım geliştirme ve güvenlik açığı kök nedeni; her türlü ENGÜRÜ ürün koşulunu tek başına kanıtlamaz.
- [Anthropic Demystifying Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) — görev, trial, grader, regression ve human-calibration; gerçek insan reviewer kimliği yerine geçmez.
- [OpenSSF Scorecard](https://openssf.org/projects/scorecard/) — taranan depo güvenlik kontrolleri; bütün ENGÜRÜ depolarının tarandığını otomatik iddia etmez.
- [LangGraph Persistence](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/persistence.mdx) — checkpoint, store ve state recovery; dış yan etkide tam idempotency garantisi değildir.

## 48/48 özgün kontrolün tespitleri

[Makine-okunur ayrı semantik inceleme kayıt dosyası](ENGURU_D48_SEMANTIK_KARSIT_INCELEME_V1.json) her D01–D48 için özgün ID, kaynak ID/URL, yöntem, anlam gerekçesi, sınıf ve iddia sınırı içerir.

| Sınıf | Adet | Kabul anlamı |
|---|---:|---|
| **MECHANISM_ALIGNED** | 17 | Kaynağın gerçekten açıkladığı somut mekanizmayla benzerlik; ENGÜRÜ gerçek uygulama/sertifika PASS'i değil |
| **LIMITED_ANALOGY** | 22 | Yarar sağlayan kavramsal aktarım; özgün alan/yetki/sonuç için ek ENGÜRÜ kanıtı gerekir |
| **EVIDENCE_NOT_EQUIVALENT** | 9 | Orijinal kaynağın kontrolün bütün iddiasını doğrudan kanıtladığı hükmü geçerli olmaz; özgün kanıtla tamamlanır |

**Özellikle dikkat:** `D02` (tek hedef ≠ DORA beş metriği), `D08` (pozitif dil ≠ Anthropic eval zorunluluğu), `D10` (reuse önceliği ≠ NIST SSDF), `D12` (ürünler arası entegrasyon ≠ LangGraph checkpoint), `D16` (bütün repo kapsamı ≠ tek OpenSSF taraması), `D18` (kritik yol ≠ DORA metric), `D40` (ücretsiz maliyet ≠ DORA throughput), `D42` (dış etki idempotency ≠ checkpoint), `D45` (tek giriş UX ≠ SLSA provenance).

Bu dokuz sınırlı eşleştirme **saklanarak puan kazanılmaz**: yeterli olmayan kaynak beyanı `REQUIRE_ENGURU_SPECIFIC_PROOF` olarak açıkça işaretlendi. D40 için gerçek maliyet/sayaç, D42 için mevcut effect-ledger/replay testi, D45 için ENGÜRÜ GitHub tek giriş kaydı kanıt olarak ayrıca kullanılmalıdır.

## Üç farklı tekrar sınaması

Ayrı [`tools/enguru_d48_semantic_adversarial_v1.py`](../../tools/enguru_d48_semantic_adversarial_v1.py) kodu, PR ve `main` CI'da şu deneyleri yapar:

1. **SOURCE:** İlgili 48 kontrolün kaynak kimliği, URL'si ve mekanizması tek tek bozulur; ayrıca 48 matriste kaynak URL kayması uygulanır. Beklenen: **192/192 HOLD tespiti**.
2. **SEMANTIC:** Destek sınıfı şişirilir, yanlış normatif kanıt etiketi eklenir, gerekçe boşaltılır; ayrıca dokuz zayıf kaynak zorla doğrudan kanıt yapılır. Beklenen: **153/153 HOLD tespiti**.
3. **AUTHORITY:** Kontrol ID'si yinelenir, AI incelemesi sahte insan onayıyla değiştirilir, gayrimeşru PASS eklenir; 48 ayrı forged-human tekrar denemesi yapılır. Beklenen: **192/192 HOLD tespiti**.

**Toplam beklenen:** `537/537` ayrı sentetik karşıt bozma reddi, `0` yanlış PASS. Bu sayılar birer plan ölçüsüdür; **yalnız GitHub'da gerçekten koşmuş CI makbuzunda gözlenirse kanıt** olur. Orijinal 5 × 100/100 sınamaları aynen korunur. Yeni testlerin her biri ayrı `SOURCE/SEMANTIC/AUTHORITY` makbuzu üretir.

## Karar ve puan disiplini

- Bu yöntem **daha önce aşırı geniş yorumlanan 9 referansı**, doğrudan kanıt değil sınırlandırılmış analoji/özgün kanıt gereksinimi olarak şeffaflaştırır.
- `DESKTOP_SEMANTIC_REVIEW=AI_SECOND_LOOK`. Bu çalışmanın testçisi ve yorumlayanı aynı asistan olduğu için `INDEPENDENT_HUMAN_REVIEW=HOLD`.
- **Masa başı mühendislik puanı** önce 97/100 idi. **98/100 ancak 48/48 anlamsal sınıf açıklığı, 3 ayrı test turunun başarısı ve exact-main CI kanıtı uzlaştırıldığında**, insan semantik review eksikliği açık sınır olarak gösterilerek *öznel mühendislik değerlendirmesi* şeklinde verilebilir. Bu, harici sertifikasyon/bağımsız insan PASS anlamına gelmez.
- `REAL_MAC_OSI_FIELD=HOLD`, `OFFICIAL_DONECHECK=HOLD`, `PRODUCT_VERIFIED_FINISH=HOLD`. Kullanıcının OSi entegrasyonu sonraki aşamadır.

**Kalıcı sabit hedef:** Teknik hatayı doğru saptamak, ihtiyaç ve kanıt açığını açık tutmak, tasarımın gerçekten güçlendiğini farklı karşıt sınamalarda göstermek; hakikati koruyarak ilerlemek.
