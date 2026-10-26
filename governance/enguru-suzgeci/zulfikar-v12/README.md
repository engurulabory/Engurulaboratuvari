# ENGÜRÜ Zülfikar™ V1.2 — Tasarım, Teori ve GitHub İnceleme Girişi

**Durum:** `ISOLATED_GITHUB_REVIEW_CANDIDATE / FIELD_HOLD`

Bu dizin, 25 Ekim 2026 tarihli Zülfikar V1.2 tasarım adayını mevcut ENGÜRÜ Süzgeci™ ve Evrensel V3 içinde **yardımcı kalite/öğrenme adaptörü** olarak barındırır. Sekiz aşama, K1–K8, V3 SHA-256, ürünün özgün canonical yetkisi, DoneCheck™ ve Human Threshold™ aynen korunur. Yeni owner, issuer, core veya resmî bitiş motoru kurulmaz.

## Sabit ana hedef ve ölçü ayrımı

**Tasarım 100/100 → Teori 100/100 → SIM1/SIM2/SIM3 her biri 100/100 → gerçek GitHub exact-head CI ve sahibin kapsamlı kararı → GitHub hazırlık kararı → ayrı yetkili Mac OSi saha / ürün kabulü.**

Mevcut yerel `93+7=100` sonucu **analist tasarım rubriği adayıdır**. Bu aday, evrensel `tools/enguru_ana_terazi_v1.py` ile ayrı 5×100 yeniden sınamadan, V1.2 proje testlerinin exact-head CI'sinden, gerçek CI doğrulamasından ve kaynak/kanıt uzlaştırmasından muaf tutulamaz.

## Kaynak dosyaları

- `zulfikar_v1_2_design_contract.json`: Donmuş 93+7 kontrolü ve dört paket.
- `zulfikar_v1_2_engine.py`: K01–K04 danışman **sentetik** politika oracle'ı.
- `test_zulfikar_v1_2.py`: Olumlu, 45 negatif, 512 bozuk şema ve 3072 çoklu stres senaryosu.
- `zulfikar_v1_2_five_gate.py`: Canonical kaynağın SHA-256'sını yeniden hesaplayan, teori/tasarım/üç test ailesini ayrı ölçen **yerel proje aday** kapısı.
- `build_receipt_and_report.py`: Kaynak, yerel test ve tasarım raporu yeniden üreticisi; resmî kabul belgesi üretmez.
- `GERCEK_BENCHMARK_PLAN_V1_2.json`: On dış muadil için referans havuzu. **Gerçek eş koşullu denemeler henüz ölçülmedi.**

## GitHub test komutları

Depo kökünden:

```bash
python3 -B tools/enguru_ana_terazi_v1.py
cd governance/enguru-suzgeci/zulfikar-v12
python3 -B -m unittest -v test_zulfikar_v1_2
python3 -B zulfikar_v1_2_five_gate.py
python3 -B build_receipt_and_report.py
```

Projeye özgü beş kapı, **THEORY/DESIGN/SIM1/SIM2/SIM3** için bağımsız paydaları ve kontrolleri raporlar. `LOCAL_FIVE_GATE_CANDIDATE_PASS`, resmî 5×100 ürün kabulü veya `GITHUB_PREPARED` kararı değildir.

## K01–K04 gerçek kabul şartları

| Paket | Tasarım kapısı | İlerideki gerçek kanıt |
|---|---|---|
| K01 | Başarı/başarısızlık sınıflama, üç öğrenme aktarımı oracle'ı | 3/3 gerçek karşılaştırılabilir görev, çift ölçüm, bağımsız inceleme |
| K02 | Niyet→kaynak→kanıt→yetki dokuz halkası, tek yetkili yazıcı | Kaynak drift testi, gerçek Work/GitHub/OSi izi |
| K03 | Aynı görev, sürüm, bütçe, kör değerlendirme, en az beş eş deneme | Gerçek muadil yürütme çıktıları, karşılaştırılabilir ölçüler |
| K04 | Kullanıcı etki ölçümü, K1–K7, güvenli FİN yönlendirmesi | Gerçek kullanıcı ölçümü, DoneCheck ve gereken Human Threshold |

## Nihai karar disiplini

`GITHUB_PREPARED`, ilgili **exact source/head başarılı CI, özgün kabul matrisi ve tek sahipli kabul sözleşmesi** ile ayrıca kararlandırılır. `VERIFIED_FINISH`, gerçek ürünün DoneCheck/Human Threshold mekanizmalarına aittir.

Bu izole inceleme dalı yalnız Zülfikar'ın kendi kaynaklarını kapsar; diğer proje ve ürün kararları ayrı sözleşmelerinde yürütülür.

## V1.3 — Hedef 100 ve Teknik Altyapı 100

Bu sürüm mevcut V1.2 motorunun üzerinde bir **uyarlamadır**. Sekiz ENGÜRÜ Süzgeci aşaması, canonical V3 SHA-256, DoneCheck ve Human Threshold korunur.

**GOAL=100/100:** ZULFIKAR_GOAL_V1_3.json içindeki 10 sabit özgün hedef kontrolü; kullanıcı değeri, payda, kaynak, yetki, bağımlılık DAG, risk, negatif sınama, kanıt izi, canonical SHA, rollback ve bütçe. Sonuç HEDEFİN TANIM KALİTESİDİR, gerçek kullanıcı faydası değildir.

**INFRA_GITHUB_CODE=100/100:** 10 kapı gerçekten GitHub checkout byte kaynakları üzerinde Python sürümü, dosya varlığı, SHA kimliği, V3 kaynağı, AST syntax, 45 negatif senaryo, imzasız hüküm, subprocess unittest ve gerçek CLI JSON roundtrip sınar. Sonuç gerçek GitHub kod altyapısı test adaylığıdır; gerçek Mac runtime değildir.

**Sabit sıra:** HEDEF → TASARIM → TEORİ → GITHUB KODU/TEKNİK ALTYAPI → EXACT-HEAD CI/TEK SAHİP KABULÜ → ayrı OSİ TEKNİK ALTYAPI ve saha → ürün kabulü → mevcut DoneCheck/Human Threshold/Verified Finish.

**Çalıştırılabilir komutlar** (bu dizinde):
```bash
python3 -B zulfikar_v1_3_gates.py status
python3 -B zulfikar_v1_3_gates.py goal
python3 -B zulfikar_v1_3_gates.py infra
python3 -B -m unittest -q test_zulfikar_v1_2 test_zulfikar_v1_3_gates
```

**Hüküm sınırı:** Goal/specification, altyapı kod testi, exact-head CI, depo sahibinin yetkili kararı, OSi ve gerçek ürün ayrı değerlendirilir. GitHub testinin PASS olması resmî Verified Finish üretmez; ayrı ürün ve saha yetkileri korunur.


## Final 3 — R01/R02 gerçek kaynak onarımı (2026-10-25)

- **R01 tür ve şema güvenliği:** `goal_gate` H01/H02 değerlerini metin türü ve dolu içerik olarak sınar; kontrol ID'leri ve DAG referanslarının hash işlemlerinden önce türü doğrulanır. Bozuk girdiler `HOLD_GOAL_SPECIFICATION` olarak değerlendirilir.
- **R02 TA05 kaynak bütünlüğü:** Altı `SRC` dosyası `git show HEAD:<repo-relative-path>` üzerinden git commit'inin takip edilen baytlarıyla doğrudan karşılaştırılır. Eksik, symlink, değiştirilmiş, HEAD'de takip edilmeyen veya Git çalışma ağacı olmayan kaynaklar TA05'i kapatır. SHA-256 özetleri ayrıca raporlanır.
- **Karşıt regresyonlar:** Sayı/list türündeki hedef, unhashable kontrol ve DAG referansları, temp Git deposunda gerçek committed-byte eşleşmesi, yerel değişiklik ve silinen dosya denetlenir.
- **Güven sınırı:** TA05, **yerel checkout/HEAD tutarlılığı** kanıtıdır; uzaktan doğrulanmış SHA, bağımsız inceleme, yetkili signer, gerçek OSi runtime, müşteri etkisi veya saha kabulü değildir. Remote exact-head CI ayrıca kontrol edilir.
- **İcra yeri:** `infra` kapısı Git HEAD bulunan **gerçek checkout** içinde değerlendirilir; yalnız dosya kopyasıyla çalıştırıldığında TA05 `HOLD` verir.
- **Kabul:** Yeni commit'in exact-head CI ve gerçek ürün saha kabulü ayrı kanıttır. `OSI_FIELD=HOLD`; `OFFICIAL_VERIFIED_FINISH=HOLD`. Korunan `main` ve Human Threshold sınırları geçerlidir.


## Final 3 — R03 sabit kabul kimliği koruması

**Kaynak incelemesi bulgusu:** Önceki H03 kapısı özgün on kontrol kimliğini, yalnız sayı ve benzersizlik düzeyinde sınadığı için, tüm bağımlılıkları birlikte değiştirilmiş bir `C01 → C11` yeniden adlandırmasını geçerli tasarım adayı sayabilirdi. Bu kabul kimliği kayması iş listesi ve kanıt eşleştirmesine risk taşır.

**Gerekli fark:** `C01–C10` özgün kimlik kümesi sabitlendi; hedef sözleşmesi kimliği, kabul/verifier/yetki metin türleri, risk açıklaması, kanıt adresi, dört özgün negatif kontrol örneği ve sıfır ücretli API bütçesinin tamsayı kimliği fail-closed denetlenir. Önceden düzgün görünerek yanlış kabul alabilecek değişiklikler H01/H03/H06/H07/H08/H10 üzerinden `HOLD_GOAL_SPECIFICATION` üretir.

**Karşıt test:** Tutarlı sahte kontrol ID yeniden yazımı, sayı/list türünde kanıt, veri tipi kayması, tekrar veya silinmiş negatif vaka, `paid_api=False` ve özgün hedef ID sapması. Teknik CI ile gerçek kullanıcı/saha kabulü ayrı kapılardır.

**Korunan hüküm:** GOAL=100/100 yalnız donmuş hedef tanımının teknik rubrik PASS'idir; `OSI_FIELD=HOLD`, `VERIFIED_FINISH=HOLD`. Sekiz aşama, canonical V3, korunmuş `main` ve Human Threshold devam eder.


## V1.3.1 — Tek sahipli GitHub teknik kabulü (26 Ekim 2026)

**Yetkili sahip kararı:** Bu depo `engurulabory` tarafından tek sahipli yürütülür. İkinci bir insan peer reviewer, GitHub teknik hazırlığının zorunlu şartı değildir. Kullanıcının açık bu kararına göre sözleşme `enguru.zulfikar.goal-contract/v1.3.1` olarak sürümlenmiştir. Önceki peer reviewer ifadeleri bu dar GitHub hazırlık kapsamı için güncel kabul ölçütü değildir.

**Yürütme:** Tek ana hedef → kaynak ve V3 SHA-256 → `C01–C10` özgün kabul kontrolü → ayrı CI yürütme ortamında gerçek test/negatif senaryo → exact-head başarılı CI ve artifact SHA-256 → depo sahibi `engurulabory` GitHub kabul/birleştirme kararı. Kullanıcıya ek form, sahte reviewer, ikinci GitHub kimliği veya paralel denetim motoru yüklenmez.

**Denetim haritası:** `C01–C03, C05–C09` = `Automated GitHub CI` (mekanik bağımsızlık); `C04, C10` = `Human Threshold`. `goal_gate.H01–H10` eşleşmesi, kaynak kimlikleri ve sabit kabul paydaları korunur. `peer_review_required=false` yalnız `decision_scope=GITHUB_TECHNICAL_ACCEPTANCE_ONLY` içindir. `issuer=EXISTING_CANONICAL_ONLY`; yeni imzacı, reviewer taklidi veya DoneCheck otoritesi oluşturulmaz.

**Negatif sınamalar:** owner/scope/issuer sapması, sahte bağımsız inceleme, bozuk tür, sürüm/kimlik kayması ve kanıtsız bitiş iddiası HOLD üretir. Gerçek kullanıcı etkisi, 3/3 gerçek öğrenme aktarımı, dış muadil benchmark'ı, saha kanıtı ve Verified Finish yalnız özgün gerçek kabul koşullarıyla kazanılır. Bu karar bu ürün-kabul kapılarına PASS taşımaz.

**Kısa karar:** Gerçek GitHub CI PASS + özgün kaynak/kanıt eşliği + geçerli tek sahipli kapsam kararı = `GITHUB_TECHNICAL_PREPARED`. Sonraki aşamaların kendi giriş yetkileri ve ölçümleri ayrıdır.
