# ENGÜRÜ Zülfikar™ V1.2 — Tasarım, Teori ve GitHub İnceleme Girişi

**Durum:** `ISOLATED_GITHUB_REVIEW_CANDIDATE / FIELD_HOLD`

Bu dizin, 25 Ekim 2026 tarihli Zülfikar V1.2 tasarım adayını mevcut ENGÜRÜ Süzgeci™ ve Evrensel V3 içinde **yardımcı kalite/öğrenme adaptörü** olarak barındırır. Sekiz aşama, K1–K8, V3 SHA-256, ürünün özgün canonical yetkisi, DoneCheck™ ve Human Threshold™ aynen korunur. Yeni owner, issuer, core veya resmî bitiş motoru kurulmaz.

## Sabit ana hedef ve ölçü ayrımı

**Tasarım 100/100 → Teori 100/100 → SIM1/SIM2/SIM3 her biri 100/100 → gerçek GitHub exact-head CI ve bağımsız inceleme → GitHub hazırlık kararı → ayrı yetkili Mac OSi saha / ürün kabulü.**

Mevcut yerel `93+7=100` sonucu **analist tasarım rubriği adayıdır**. Bu aday, evrensel `tools/enguru_ana_terazi_v1.py` ile ayrı 5×100 yeniden sınamadan, V1.2 proje testlerinin exact-head CI'sinden, yetkili bağımsız incelemeden ve kaynak/kanıt uzlaştırmasından muaf tutulamaz.

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

`GITHUB_PREPARED`, ilgili **exact source/head başarılı CI, özgün kabul matrisi ve gereken bağımsız inceleme** ile ayrıca kararlandırılır. `VERIFIED_FINISH`, gerçek ürünün DoneCheck/Human Threshold mekanizmalarına aittir.

Bu inceleme dalı, PiLive Work oturumunu ve korunan `main` kaynaklarını değiştirmez. PiLive çıktısı geldiğinde özgün kabul ID'leri ve SHA kanıtlarıyla ayrıca uzlaştırılır.
