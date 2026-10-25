# ENGÜRÜ PiLive™ — Bütünleşik hazırlık V2

**STATE:** REVIEW_CANDIDATE / GITHUB_PREPARED=HOLD. Mac kaynak yazımı ve uygulama açılışı bu hazırlıkta 0.

**CLAIM:** Mevcut Brain V3 modelini kaynak SHA ile yeniden kullan; gerçek Mac keşfini sınırlı kanıt olarak değerlendir; G00–G09'u tek plana bağla. Kanıtlanan açıklara yalnız gereken hazırlık farkını uygula.

**EVIDENCE:** `PLAN.json`, `REUSE_PROVENANCE.json`, `tools/pilive_prepare_v2.py`, `tools/pilive_osi_source_observer_v2.py`, özgün 51 Brain testi ve yeni 15 regresyon. Exact PR HEAD ve CI ayrıca okunur. Ekli saha raporunun orijinal SHA-256 pini `17cd00711ac8eed82ef802f69769400f9fade7414a0e27d6e1faccf94d18fbb0`.

**JUDGMENT:** Genel yöntem ve Hybrid yapısal 5×100, PiLive'ın gerçek canonical kaynak/uygulama bağı ölçümünden ayrı tutulur. Birleşik hazırlık her eksende bu ölçümlerin asgari değeridir. PiLive semantik kontrolünde açık kaynak şartı varsa `GITHUB_PREPARED=HOLD` sürer. Yeşil CI bu HOLD'un doğru korunmasını da sınar.

**NEXT ACTION:** Yetkili yerel yürütücü yedi adlandırılmış canonical dosyanın içeriğini ve tracked PiLive/Progress kaynak adaylarının isim/SHA envanterini salt-okunur devretsin. Sonra gerçek CLI/şema ve Swift build bağı kaynak incelemesiyle eşleştirilsin. Kaynak haritası netleşince bütün beş ölçüm aynı sabit paydada yeniden çalıştırılır.

## Kaynakların ayrı kimlikleri

| Kaynak | Exact kimlik | Statü / sınır |
|---|---|---|
| GitHub main | `0b374b1469ef8a249509bd51dd5dfc8bce3e301e` | Yöntem kaynağı; bu gözlemde PiLive canonical dosyaları ve Swift uygulama kaynağı mevcut ağaçta yok |
| PR #188 | `1e0685f2aab95522ec6101e9a5fda22a54051562` | Taslak; base başka feature dalı; Brain modeli/tasarım sözleşmesi |
| PR #189 | `cd142dbe5d26ed443ecfc6b72b4408253cccf39e` | Taslak; base #188 dalı; bütünleşik finiş devri ve tarihsel politika kaydı |
| Mac ana repo | `269854b8a42a27e9419eae65a3c9e349bdcc7300` | Keşif raporunda 11 tracked değişiklik; içerik diff'i bu raporda yok |
| Mac Engineer repo | `26925c21c7816a90edc0eb047382aba8c696764c` | Keşif raporunda 2 tracked değişiklik; PiLive canonical otoritesi ayrı |
| V3.1 binary | `32d533bed479434f77f848fd030c4330a2a33447e8e28d281f215bcb7b6db466` | Metadata SHA eşleşmesi; GUI/build-source/parity/performance ayrı test |

Yerel Mac HEAD'inin GitHub tree çözümü API 422 döndürdü. Bu yalnız bu uç noktadan nesneye erişimin kurulamadığını kanıtlar; commit'in başka dal/yerel arşivdeki varlığı hakkında genel kayıp hükmü üretmez.

## Korunan iki kabul ve yetkiler

**SCREEN:** Gerçek uygulama görünür, gerçek kaynak verisiyle eşleşir, aktif iş/ilerleme doğrudur, ⌘R/kapanış/yeniden açılış ve erişilebilirlik gözlenir; owner görsel kabulü alınır.

**P02:** Kendi 12 özgün işi + 4 DoneCheck + 7 saha önkoşulu + güvenlik + gerçek Human Threshold + native Verified Finish. Plan G00–G09 ayrı hazırlık kimlikleridir.

P01 önceki 2/2 VERIFIED/LOCKED ve P06'nın ayrı güvenlik yetkisi korunur. Metadata pin eşleşmesi güncel native verify yerine ayrı envanter kanıtı olarak kullanılır. Progress Core mevcut reader/projection otoritesidir. Bu araçlar issuer, grant veya writer kurmaz; resmî kabul yazımı 0.

## Önceki duruşun kanıtı

19 Ekim `ENGURU_PLIVE_FINAL_ACCEPTANCE_GATE_20261019T122020113187Z.json` içeriği yeniden okundu: `PASS_SOURCE_RECONCILIATION__HOLD_REAL_AUTHORITY`; G3-A'da authenticated owner, issuer identity, protected custody, policy-bound scope ve `-34018` çözümü açık. G3-B'de ayrı pilot kararı/signed grant/revocation-replay; G3-C'de approved writer/atomicity/crash durability/recovery; G3-D'de bounded ilk geçiş/fresh evidence/native readback açık.

`ENGURU_PLIVE_P02_OWNER_POLICY_REGISTRATION_20261018T232952723976Z.json` içeriği yeniden okundu: `PASS_OWNER_POLICY_RECORDED__G3_REAL_AUTHORITY_HOLD`; önce/sonra P01 `2 VERIFIED`, P02 `0 HOLD`; yedi kaynak pini aynı. Politika kabulü korunur. Ayrı gerçek signer/grant/writer ve nihai ürün kabulü kendi kanıtını bekler.

Finiş makbuzunda DoneCheck `0/4_NOT_ASSESSED`, saha şartları `0/7_NOT_ASSESSED` yazıyor. Daha eski belgede bulunan `1/7` başka gözlemdir; güncel saha PASS sayısı olarak birleştirilmez. `SecItemAdd=-34018` tek başına hatanın kesin entitlement/provisioning nedenini belirlemez. Kök neden teşhisi için ham signing/entitlement/provisioning çıktısı gerekir.

## Beş ölçüm ve sınamalar

PiLive semantiği için **her eksen 10 özgün kontrol ×10 puan**, toplam 50 ayrı ID. Kontroller evaluator içinde sabittir. İlk orijinal rapor ölçümü: **THEORY=70, DESIGN=70, SIM1=80, SIM2=100, SIM3=80**. Bu puanlar kullanıcı ekranı veya resmî P02 ilerleme yüzdesi değildir.

- Teori açıkları: gerçek P02 sözleşme semantiği, gerçek Progress Core semantiği, kurulu binary→build source bağı.
- Tasarım açıkları: mevcut adaptör API'si, exact Swift build/launch recipe, native project resolver.
- SIM1 açıkları: güncel kaynak üzerinden açılış veri yolu ve gerçek adaptör fixture eşliği. İş/alan/teknik-resmî durum/çekmece/tazelik/JSON yeniden açılış modeli fiilen çalıştı.
- SIM2: eksik kaynak, bozuk/çift-key/nonfinite JSON, yanlış yüzde, çift kimlik, DAG döngüsü, stale snapshot, yetkisiz PASS, kısmi kesinti girdisi, kimlik kayması, rollback/revalidation — 10/10 sentetik karşıt kontrol.
- SIM3 açıkları: gerçek kaynak→native→adaptör parity ve Swift→görünür çıktı bağı. Ayrı `Fraction` aritmetik oracle'ı, ham SHA, explicit heading oracle, serileştirilmiş replay, input preservation ve yetki sınırı fiilen sınandı.

Hazırlık modeli native uygulama yaşam döngüsünü, OS restart'ını veya gerçek writer crash recovery'sini çalıştırmış sayılmaz. SIM1/2/3 üç farklı aile; düzeltici T1/T2/T3 turları ayrı gelişim kaydıdır. Açık kaynak engeline üç aynı simülasyon eklemek puan kazandırmaz.

## Saha devrinin kesin kapsamı

`tools/pilive_osi_source_observer_v2.py` yalnız Darwin CLI'da çalışır. Varsayılan root `~/Enguru/Projects/Engurulaboratuvari`. Yedi named dosya UTF-8 içerik/SHA ve ilgili tracked aday isim/SHA üretir. Dosya okuması O_NOFOLLOW/dizin fd, normal dosya, 2 MiB ve scope sınırlarıyla korunur. Git opsiyonel lock ve fsmonitor kapalıdır. JSON yalnız stdout'a çıkar. Kaynak önce/sonra bracket'ı drift yakalar; ABA için native revision protokolü ayrıca gerekir.

Bu dar araç uygulama açılışı, ağ, Keychain, yerel kod import/verify yürütmesi ve canonical yazım için **0** hedefler. Mac'te henüz çalıştırılmadı. Yeni makbuz orijinali AudiV13 altında benzersiz adla, masaüstü kopyası aynı SHA ile ve mevcut dosya çakışmasında HOLD politikasıyla yetkili yürütücü tarafından saklanır. Kurulum/aktarım/uygulama değişikliği ayrı açık insan kararına bağlıdır.

## İcra sırası ve maliyet

Kaynak dalı: G00→G01→G03→G04. Ekran kolu: G02+G04→G05→G06/G07→SCREEN kabulü. Resmî kol: G01/G03→G08 G3-A→B→C→D→S01→S02→S03→S04. G09 bütün hazırlık/kanıt bağlarını uzlaştırır. Ekranın salt-okunur okunabilirliği G3 writer yetkisinden ayrı ilerler; resmî P02 geçişi kendi zincirinde kalır.

Ek satın alınan kredi 0; ücretli model/API çağrısı 0; yeni satın alma 0. Hesap/Actions faturası okunmadı: `HOLD_ACCOUNT_BILLING`. Python stdlib ve var olan Git yeniden kullanılır. Yeni model servisi veya ücretli bağımlılık eklenmez.

**Sonraki ürün yolu:** PiLive → ENGÜRÜ Hakikat ve Yetenek Mimarisi 2 → ENGÜRÜ Truth Boundary™ — Hesap Veren Doğrulayıcı.
