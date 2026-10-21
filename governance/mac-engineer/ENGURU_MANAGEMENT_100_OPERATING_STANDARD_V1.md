# ENGÜRÜ Mac Engineer™ — Yönetim 100/100 Tasarım Standardı v1

**STATE:** PROPOSED / GITHUB_PREPARATION / OSI_FIELD_ACCEPTANCE_HOLD  
**DATE:** 2026-10-21  
**OWNER:** ENGÜRÜ Yönetim; gerçek saha hakikati OSi ve yetkili canonical kaynaklarda kalır.  
**SCOPE:** Mevcut ENGÜRÜ Süzgeci™ sekiz aşamasının Yönetim–İCRA uygulaması; yeni core, yeni kabul otoritesi, dokuzuncu aşama veya paralel süreç değildir.  
**PRODUCT ORDER:** Önce ENGÜRÜ Mac Engineer™ Verified Finish; bundan sonra ayrı kapsamda ENGÜRÜ PLive™ ürün çalışması.

## 1. Kalıcı sabit hedef ve rol ayrımı

Mac Engineer: `H1 Signer 4/4 → H2 Writer 4/4 → H3 GitHub–OSi 4/4 → Native Mac Engineer OSi → Verified Finish → BITTI_DUR`.

Canonical kapsam kayıtları incelendiğinde eski V7–V9 raporlarında `F05 Native PLive V3.1` adı geçmektedir. Bunun Mac Engineer son kabulüyle gerçek ürün/authority ilişkisi **HOLD_SCOPE_RECONCILIATION** sayılır. İsim değişikliği veya yeni yönetim notu yetkili canonical sözleşmeyi otomatik değiştirmez. Gerçek kabul sahibi ve OSi kaynaklarıyla mutabakat gerekir. PLive ürün geliştirmesi bir sonraki aşamadır.

- Yönetim: sabit hedef, scope, yetki, bütün engeller, öncelik, gerçek kabul hükmü ve sonraki tek emrin sahibi.
- İCRA: gerçek Mac kaynak tespiti, onarım, test, negative test, receipt, güvenli dur ve saha devrinin sahibi.
- Ortak hakikat: mevcut canonical kaynaklar, Progress Core™, DoneCheck™ v1.2, Human Threshold™, kaynak SHA/HEAD, AudiV13 receipt'leri.
- GitHub yönetim PR'ı geliştirme/proposal kanıtıdır; OSi accepted source, release, native field veya Verified Finish değildir.

## 2. Yönetim tasarım hedefi: 100/100

| Yönetim yeteneği | Tasarım hedef puanı | Kanıtlanabilir davranış |
|---|---:|---|
| Ana hedefi koruma | 20/20 | Tek sabit Mac Engineer Verified Finish; PLive sonraki ürün |
| Yönetim–İCRA rol ayrımı | 15/15 | Yetki sahibi, icra yetkisi ve escalation kaydı açık |
| Kanıta dayalı karar | 20/20 | Ayrı saha gözlemi, source pin, evidence ve acceptance |
| Engel yönetimi | 15/15 | F01–F06 kök neden, çözüm, bağımlılık, Human Threshold, closure |
| İş yükü sınırı | 15/15 | En fazla 1 ana kapanış + 1 bağımsız destek |
| Gerçek bitiş yönetimi | 15/15 | Kapanan engel ya da kesinleşmiş karar eşiği, sonraki kritik adım |

**Tasarım hedefi 100/100 ≠ ölçülmüş saha performansı 100/100.** Tarihsel 85/100 bir yönetim kanaatidir. Gerçek performans ancak bitiş çevrimleri ve saha kanıtıyla ölçülür; puanlar kabul token'ı üretmez.

## 3. İş seçme ve akış

- Bütün F01–F06 engel haritasını aynı anda gör; aktif görev `1 ANA` ve en fazla `1 BAĞIMSIZ DESTEK` olarak sınırlandır.
- Mevcut geçiş sırası: `F01 → F02 → F03 → F04 → Native/F05 → F06`. Yetkili resmi kabul bağımlılıkları korunur.
- F05 kaynak/ürün sahibi ve izole build hazırlığı, yetkisi ve bağımsızlığı doğrulanırsa F01–F04 yanında destek olabilir. Gerçek kurulum/imzalama ayrı Human Threshold ile yürür.
- Önceki PASS ancak aynı source pin ve aynı kapsam için devralınır. Değişmiş HEAD, scope veya freshness yeniden doğrulama gerektirir.
- Kritik canlı signer, canonical write, dış Git write, install ve Verified Finish tek yazıcı ve güncel işlem yetkisiyle yürütülür. Dış Git exact-head parity H2 4/4 ve kapsam onayına bağlıdır.
- Mevcut İCRA turu çalışırken sırf yönetim standardı için yeni görev yayınlanmaz; sonuç raporu geldikten sonra karar üretilir.
- HOLD çıktısı sonraki belirli çözümü, gerekli kanıtı ve onay sahibini taşır. Hazır bağımsız iş devam eder.

## 4. Her Yönetim Devir Kaydı™ sonrasında zorunlu karar

1. **Hakikati gör:** Tarih, OSi runtime, exact HEAD, SHA-256, yetkili rapor ve eski kanıt kapsamını kontrol et.
2. **Değeri koru:** PASS, dirty worktree, Git geçmişi, orijinal receipt ve ürün kimliklerini koru.
3. **Eksikleri ve ihtiyaçları tespit et:** Bütün F01–F06; yeni doğrulanmış engeller kapsam kararına gider.
4. **Gerekli farkı üret:** En yüksek bitiş darboğazı + en fazla bir bağımsız destek işi belirle.
5. **Eksikleri tamamla, ihtiyaçları karşıla:** REUSE → EXTEND → ADAPTER → HUMAN THRESHOLD; mevcut sistem içinde onarım.
6. **Kanıtla:** Gerçek Mac, negatif senaryo, bağımsız receipt, kabul sahibi ve yetkili PASS/HOLD.
7. **Bir sonraki ihtiyaçları belirle:** Ortaya çıkan gerçek root cause/karar ihtiyacını netleştir.
8. **İlerlet:** Tek bütünleşik, sonlu ve hedefe bağlı emir; sonraki raporda aynı sayaçları güncelle.

### F01–F06 başına karar alanları

`engel_id, state, real_evidence, root_cause_status, acceptance_boundary, concrete_solution, dependencies, human_threshold, closure_receipt, finish_effect`.

`PASS_CLOSED` yalnız mevcut yetkili kabul sınırında doğrulanan gerçek kapanışı temsil eder. `NEDEN_BEKLIYOR` kanıtlanmış kök neden değildir.

## 5. Yüzdeli grafik: üç ayrı ölçü

1. **Resmî kriter kabulü**: `(H1_accepted + H2_accepted + H3_accepted) / 12 × 100`. Örneğin 0/12 = 0%. Burada kabul edilen kriter resmî yetkiyle doğrulanmış olandır; ara test sayısı kabul sayılmaz.
2. **Engel kapanışı**: Başlangıç F01–F06 kümesinde `PASS_CLOSED / 6 × 100`. 1/6 = 16,7%. Yeni engel bulunursa envanter mutabakatıyla payda sürümlenir; otomatik oynatılmaz.
3. **Teknik alt kazanımlar**: Her testin kendi `passed / total` yüzdesi. Örnek 6/6 reliability = %100 **yalnız o izole kapsamda**; ürün %100 değildir.

Tam ürün bitiş hükmü ayrı alandır: `H1=4/4 AND H2=4/4 AND H3=4/4 AND Native=PASS AND VerifiedFinish=PASS` koşulu gerçekleşince `BITTI_DUR`.

**Provenance sınırı:** `tools/enguru_management_progress_v1.py` sadece önceden incelenmiş ve normalize edilmiş bir devir girdisinden **okunabilir projeksiyon** üretir. Kaynak receipt'in SHA'sını veya yetkili imzayı kendi başına doğrulamaz; verdict üretmez, Git/Mac üzerinde yazma yapmaz. Çıktı `PROJECTION_ONLY` ile etiketlenir. H1/H2/H3 sayaçları bağımsız kabul kaynağıyla Yönetim tarafından önceden doğrulanır.

## 6. Çalıştırılabilir kontrol ve kabul sınırı

Normalized girdi: `enguru.management.handoff/v1`; örnek ve testler `tests/test_enguru_management_progress_v1.py`.

```bash
python3 -m unittest tests.test_enguru_management_progress_v1 -v
python3 -B tools/enguru_management_progress_v1.py --input governance/mac-engineer/examples/ENGURU_MANAGEMENT_V9_PROJECTION_INPUT.json
python3 -B tools/enguru_management_progress_v1.py --input governance/mac-engineer/examples/ENGURU_MANAGEMENT_V10_PROJECTION_INPUT.json
# veya yeni rapor incelendikten sonra:
python3 -B tools/enguru_management_progress_v1.py --input /path/to/reviewed_handoff.json
```

Çıktı stdout JSON; repo/canonical dosyası değişmez. Şema, altı engel kimliği, kabul sayaç aralıkları ve kapanış receipt alanları fail-closed sınanır. Kanıt belirsizse resmi `PASS` ataması yapılmaz. Gerçek Mac raporu formatı farklıysa, Yönetim kayıtlarını **inceleyerek normalize eder**; script ham raporu sahte doğrulayıcıya dönüştürmez.

**PREPARED:** GitHub izole dalı + test + review.  
**ACTUAL GATES:** Yetkili canonical kabul sözleşmesi, OSi saha kanıtı, mevcut DoneCheck ve Human Threshold ayrı ayrı PASS.  
**VERIFIED FINISH:** Yalnız yetkili finalizer gerçek receipt'i.

## 7. Mevcut taban ve sonraki rapor

2026-10-21 V10 son saha raporu: `H1=0/4, H2=0/4, H3=0/4, Native=HOLD, VerifiedFinish=HOLD, open_F=6`; izole `H2=6/6, H3=13/13`, iki transport PASS. V10 iki yapılandırılmış canonical kaynakta **Native Mac Engineer ürün kimliğini** doğruladı: `com.engurumaya.macengineer`; Native izole build kaynak kapısında HOLD, `BUILD_RC=UNRUN`. Resmî acceptance %0, engel kapanışı %0. Gerekli Git HEAD kaynak dosyasının kimliği V10 `F05.source` ile kesinleştirilecektir. F01 resmî 12 kriter ve Mac acceptance binding HOLD; sonraki aktif yönetim önceliği F01, bağımsız F05 Native source/build hazırlığıdır. Bu not sahadaki kaynakları değiştirmez.

Gelecek gerçek İCRA raporuyla aynı sayaçlar gözden geçirilecek; bütün engellere çözüm bulunurken aktif emir kapsamı 1 ana + en fazla 1 bağımsız işe odaklanacak.

**STATE → CLAIM → EVIDENCE → JUDGMENT → NEXT ACTION.**


## 8. V12 Yönetim kararı — yeni çalışma modelinin ilk saha girdisi

**Gerçek saha kanıtı:** `ENGURU_DORT_HEDEF_V12_F01_F05_20261021T110149917554Z.json`, bildirilen SHA-256 `06823eb5837ec1461994cd7b32dc8bc8a4b9e07188ee70afdbaa49ddc80ecd6c`. Bu kaynak Mac üzerinde bağımsız doğrulandığında hukuki/teknik kabul zincirinde yetkili kanıt olabilir; GitHub fixture yalnız raporun projeksiyonudur.

**F01 ana kritik iş:** DoneCheck doğrulayıcıları biliniyor; V12'nin 4+4+4 kategoride 12 kriteri `UNAPPROVED_ENGINEERING_PROPOSAL` statüsündedir. `OFFICIAL_CRITERIA=0/12_HOLD`. Yetkili mevcut kriter kaynağı ve sahibi araştırılır. Mevcut kayıt gerçekten yetkisiz ise yalnız `ENGURU_MAC_ENGINEER_H1_H2_H3_OFFICIAL_4X4_ONLY` kapsamlı onay-hazır Human Threshold kararı hazırlanır; insan kararı ayrı bağımsız eşiği oluşturur.

**F05 bağımsız yürütme/onarma işi:** Canonical ürün kaynaklarının üçlü commit bağı PASS; staged AST tarifinin doğru tek tireli Swift seçeneği PASS. Yerel gerçek Swift compiler çağrısı `RC=1` ve `NEDEN_BEKLIYOR`; ilk compiler hata satırlarının yeri `F05.build.build_errors`, stderr digest `F05.build.stderr_sha256`. Gerçek hata satırları bu yönetim özetinde olmadığı için kök neden atanmaz. Önce orijinal V12 JSON ve hata çıktısı, ardından doğrulanmış neden → kalıcı kaynak/ortam onarımı → geçici izole build → executable SHA ve receipt zinciri gerekir.

**GitHub macOS CI ile yerel Mac build ayrımı:** Ürün PR #14'ün GitHub CI Swift kontrolü PASS olmuş olabilir; farklı source commit/SDK/toolchain/config nedeniyle yerel V12 `RC=1` sonucu bundan bağımsızdır. Yetkili değerlendirmede aynı kaynak pini, tam compiler komutu, SDK ve toolchain kıyaslanır. CI PASS gerçek OSi kabulüne terfi ettirilmez.

**Sayaçlar:** Resmî H1/H2/H3 `0/12`, kapalı F01–F06 `0/6`, Native HOLD, Verified Finish HOLD. Yetkili kriterler, izole build ve gerçek saha kabulü ayrıdır.

**İCRA yetenekleri:** 12 yetenek, 6 işlevsel bölüm ve kanıt disiplininin mevcut ürün kaynak gelişimi `engurulabory/enguru-mac-engineer` PR #14 ile ilişkilidir. Tasarım hedefi her yetenek ve Yönetim uyumu için 100/100; geçmiş gözlem puanları İCRA 80/100, ürün 74/100 ve uyum 91/100 olarak ayrı izlenir. Bu rakamlar formel saha değerlendirmesi/benchmark değildir.

```bash
python3 -B tools/enguru_management_progress_v1.py --input governance/mac-engineer/examples/ENGURU_MANAGEMENT_V12_PROJECTION_INPUT.json
```

**Yönetim aktif kararı:** F01 yetkili kriter/owner mutabakatı (tek ana iş), F05 gerçek Swift `RC=1` onarımı ve izole build (tek bağımsız destek). F02–F04 ve F06 finiş haritasında görünür ve mevcut resmî sıralarıyla kapanır. Sonraki İCRA emri uygulaması ayrıca mühendis oturumuna devredilir.


## 9. V13 saha kazanımı ve Yönetim kabul ayrımı

**Kaynak bildirimi:** `ENGURU_DORT_HEDEF_V13_F01_F05_20261021T112710918324Z.json`, SHA-256 `d4512aa7b57e3fe1195a0d5c4ac967883057c2d25f7b5574d158600d08a860c4`. Bu GitHub fixture bir projeksiyondur; gerçek yerel receipt'i bağımsız doğrulamadan resmî kanıt veya izin statüsü üretmez.

**F05 gerçek kazanım:** Yerel Swift standart kütüphane yükleme problemi `arm64-apple-macosx26.0` için A/B tekrar üretim yapıldı. Sınırlı gerçek neden, Swift derlemede macOS SDK'nın `-sdk` ile açık bağlanmasıdır. `RC=0` ve `PASS_ISOLATED_SWIFT_APP` gözlendi. Binary SHA-256: `6cd91aa5163418165a0b9746dfe27613d6bce4e78e85322f78606bcf6c847c08`. Üçlü kaynak ve build receipt PASS; **canonical build komutuna kalıcı kaynak değişikliği, ikon Git provenance, gerçek imza, kurulum, smoke ve Native kabul HOLD**.

**F01 karar eşiği:** 12 kriterin SHA bağlı onay-hazır taslağı V13 `ENGURU_V13_F01_HUMAN_THRESHOLD_DECISION_20261021T112700085955Z.md` içinde bildirildi. SHA-256: `3ec5a01b3939b27d82cc60efc83edd944959a4b158fd8e5ff81faf1ed49cac1b`. **Onaylı kriter 0/12**, yetkili kabul sahibi/belge doğrulaması HOLD. Önce mevcut yetkili kanonik kaynak ve gerçek reviewer kimliği aranır; doğrulanmış boşlukta yalnız dar `ENGURU_MAC_ENGINEER_H1_H2_H3_OFFICIAL_4X4_ONLY` kapsamında insanın inceleyebileceği karar kullanılır. GitHub yazma ve PR CI bu kararın yerini tutmaz.

**Yönetim kararı:** 1 ana F01 (yetkili kriter sahibi ve Progress Core/DoneCheck runtime kabul bağı), 1 bağımsız F05 (kanıtlı `-sdk` farkını mevcut yetkili build tarifine kalıcı bağlama, ikon provenance ve imzalı saha hazırlığı). F02/F03/F04/F06 korunmuş sıralı kapanış haritasıdır. Teknik onarım kapanışı ile bütünsel F05 kapanışı ayrı takip edilir.

```bash
python3 -B tools/enguru_management_progress_v1.py --input governance/mac-engineer/examples/ENGURU_MANAGEMENT_V13_PROJECTION_INPUT.json
```

**Resmî sayaç:** H1/H2/H3 = 0/12; F01–F06 kapalı = 0/6; Native = HOLD; Verified Finish = HOLD. Tasarım 100/100, gerçek çalışan mühendislik becerisi ve sahadaki kabul puanları ayrı ölçülür.


## 10. Kaynak bütünlüğü ve dayanıklı derleme — Engineer PR #14 kabul kanıtı

**Pozitif ENGÜRÜ çalışma ilkesi:** **Tek kaynak → Uyumlu yürütme → Güvenilir derleme → Karşıt sınama → Doğrulanmış sonuç → Kalıcı teslim.**

**Gerçek GitHub ürün kanıtı:** `engurulabory/enguru-mac-engineer` PR #14, kaynak HEAD `9f3b0fa9f0d5de86d9aa5dbd42e8e40c43ec5e24`; GitHub macOS Product CI [#39598242347](https://github.com/engurulabory/enguru-mac-engineer/actions/runs/39598242347) **SUCCESS**. Toplam **90/90 runtime test**, aynı shared Swift SDK stage'i kullanan gerçek Swift compile, Mach-O, Info.plist ve kaynak/binary SHA-256 receipt eşleşmesi PASS. Güvenlik regresyonları SDK keşfi, kaynak değişimi, derleme hatası, symlink ve mevcut çıktının korunması kapılarını sınar.

**Mühendislik yeteneği:** Kanıtlanmış geçici `-sdk` çözümü, mevcut GitHub ürün kaynak hazırlığında `swift_build_stage.command` üzerinden tek kaynak tarifiyle Native hazırlık ve CI akışına bağlandı. Bu kaynak hazırlığı **İCRA oturumuna otomatik aktarım** veya **yerel Mac v0.8 canonical kabulü** değildir.

**Yerel uygulama kararı:** V14 kaynak `GUVENLI_DUR_UNRECOGNIZED_CANONICAL_PREP_SCRIPT` gözlemi üzerinden aktif yerel HEAD/working tree ve Swift komut yapısı kanıtla okunur. GitHub ürün PR #14 kodunun **yeteneği ve doğrulanmış davranışı**, yerel mevcut `v0.8` kaynak yapısına en küçük uygun farkla adapte edilir. Geçerli `v0.6 VERIFIED_LOCKED` geçmişi korunur. Derleme işlemi geçici alanda gerçekleştirilir; kurulum, imza, üretim sistemi kabulü ve yetkili insan kararları ayrı kapılarda tutulur.

**F01:** Mevcut yetki karar kaydı `APPROVED_FOR_AUTHORIZED_REVIEW_ONLY`; onaylı kriter `0/12`, Mac DoneCheck binding HOLD. Yetkili kaynak/sahip incelemesi ana kapanış. **F05** tek bağımsız destek olarak kalıcı yerel source adaptation + regresyon ve receipt. H1/H2/H3 resmî sayaç `0/12`, tam F01–F06 kapanış `0/6`, Verified Finish HOLD.

**Tasarım ve saha ayrımı:** Engineer kapasitesi 100/100 ve Yönetim uyumu 100/100 sabit tasarım hedefidir. GitHub CI PASS mühendislik ilerlemesidir; İCRA saha kabiliyeti ve çalışan ürünün yetkili bitişi kendi mevcut gözlem ve doğrulamasında ölçülür.

## 11. Bütünleşik tek-tur yürütme ve V19 oturum devri

**Bağlayıcı İCRA yeteneği:** Bir ana F01 + bir bağımsız F05 kapsamında, tek emirle bütün yapılabilir alt bağımlılıklar kaynak → güvenli fark → yürütme → regresyon → Evidence olarak topluca tamamlanır. İlk teknik PASS sonrasında kapsamın kalan uygun işleri sürer; kesin insan/yetki/kanıt eşiğinde `GÜVENLİ_DUR` ve tek karar hazırlanır. Yeni core, paralel yönetim veya ilave Süzgeç™ aşaması oluşmaz.

**Kapasite:** +10 kanıtlı kontrol çalışma hedefi, +20 uygun durumlarda genişleme; bir sınır veya başarı ilanı değil. 100 maddelik GitHub ilerleme listesi sabittir; yalnız gerçek ✓ üretir. H1/H2/H3 ve Verified Finish yalnız gerçek yetkili kayıtla yükselir.

**Süreklilik:** Mevcut V18 İCRA raporu tamamlanınca yeni mühendislik oturumu `engurulabory/enguru-mac-engineer` PR #14 üzerindeki `docs/ENGURU_ENGINEER_V19_SESSION_BOOT.md` ile başlatılır. Başlangıçta son Mac AudiV13 saha raporu SHA ve bu depodaki `governance/mac-engineer/progress/ENGURU_100_BIRIM_FINIS_SAYACI_V1.json` mutabıklaştırılır. GitHub kaynak adayları ve yerel canonical Mac kabulleri ayrı tutulur.

**Yanıt şekli:** 6 satır: STATE; 100 sayaç; yeni ✓; F01; F05; resmî kabul + rapor SHA + sonraki karar.

## 12. Kopyala-yapıştır teslim standardı ve V20 mühendislik hizası

**Kaynak:** [Engineer PR #14](https://github.com/engurulabory/enguru-mac-engineer/pull/14), `runtime/governance.py` → `ENGINEER_DELIVERY_100`, `PASTE_READY_TERMINAL`, `PACKAGE_DELIVERY_BOUNDARY`. Bu standart mevcut Engineer 100/100 tasarımına eklenen teslim disiplinidir; gerçek Mac saha kapasitesi ve resmî kabul gerçek kanıtla ayrıca izlenir.

**Yönetimin beklediği sade mühendislik yanıtı:** `STATE`; 100 birim önce→sonra; tekil yeni ✓; `F01`; `F05`; `RESMÎ + RAPOR_SHA256 + SONRAKİ` — toplam altı satır.

**Teslim paketi gerektiğinde:** **A ZIP İNDİR** gerçek ve SHA-256'sı doğrulanmış dosya bağlantısı; **B MAC TERMİNAL KOPYALA-YAPIŞTIR** tek tamamlanmış `zsh` kod bloğu (exact indirilen dosya adı, tırnaklı yollar, dosya/symlink/SHA kontrolü, AudiV13 arşiv); **C BEKLENEN SONUÇ** kısa PASS/HOLD. ZIP ihtiyacı olmayan salt-okuma turunda sade rapor yeterli. Blok içindeki talimat ve kod birbirinden açıkça ayrılır.

**Kapsam:** Tek F01 + tek bağımsız F05; bir turda erişilebilir bütün kanıtlı bağımlılıklar. %10–20 kontrol artışı çalışma hedefidir, zorunlu bitiş kotası değildir. Human Threshold™, canonical kaynak koruması, resmî DoneCheck kabulü ve tarihsel v0.6 kilidi sabit kalır.

**Yönetim kararı:** GitHub test PASS, ürün/OSi final kabul PASS iddiası üretmez. Yeni mühendislik sohbeti başta GitHub son PR14 kaydını ve V19/V20 oturum devir kaydını okur.


## 13. İCRA'nın asli mühendislik rolü

**İCRA**, ENGÜRÜ Mac Engineer™ gerçek ürün mühendisi ve teknik icracıdır: mimari ve kaynak incelemesi, doğrulanmış kök neden, kod/kalıcı onarım, entegrasyon, gerçek yürütme, pozitif-negatif regresyon, koruma/güvenlik, Evidence/DoneCheck sınırı, owner review'a hazır somut teslim. **Yönetim** kalıcı sabit hedefi, iş önceliğini, 100 maddelik kabul sayacını yönetir. **Yetkili canonical owner/reviewer** korumalı imza, lisans, source promotion, 12 kriter ve resmî kabul kararlarını yürütür.

**V22 icra hedefi:** Yönetim 22/100 → 30/100 (+8 yalnız özgün kriter PASS). F01 ana: tek mevcut Human Threshold karar adayını yetkili sahibi ve kaynak/kanıta bağla. F05 bağımsız: Native 0.8'in yeniden başlatma, eşzamanlı çalışma ve kapanış korumalarını muhafaza eden izole birleşik kaynak onarımı; gerçek Swift ve negatif regresyon; Git kaynak, patch ve SHA; owner inceleme adayı. Bir tek teşhis veya ilk testte durmak yerine tüm uygun güvenli bağımlı işleri tamamla.

**Sıfır-artış disiplini:** Yeni benzersiz kabul şartı gerçekleşmeden sayaç yükselmez. Yetki engeli varsa kalan bağımsız işleri tamamlayıp tek gerekçeli Human Threshold kararıyla `GÜVENLİ_DUR`. Geçmiş başarılı test, resmî H1/H2/H3 kabulü değildir.

**Kaynak:** Mühendislik PR #14 `runtime/governance.py` içindeki `ENGINEER_ROLE_AUTHORITY_SPLIT`, `ENGINEER_ROLE_OWN_THE_CLOSE`, `ENGINEER_ROLE_DECISION_READY_STOP`, `ENGINEER_ROLE_30_MEASURE`; bağlı mühendislik standardı ve oturum boot. GitHub PR review yetkili Mac OSi canonical aktivasyonundan ayrıdır.


## 14. V23 — Ana hedefe bağlı tam mühendislik ve onar kontrol birimlik Yönetim turu

**P0:** ENGÜRÜ Mac Engineer™ yerel Product Engineering Operator resmî Verified Finish/`BITTI_DUR`. **P1:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → DoneCheck resmî kabul sırası. **P2:** İCRA güncel F01 canonical owner/reviewer Human Threshold ana ve F05 Native 0.8 kaynak incelemesi bağımsız destek; F01–F06 bütün bağımlılıklar görünür.

**İCRA'nın görev alanı:** mevcut kaynak gözlemi, analiz, mimari, doğrulanmış kök neden, plan, tasarım, kod, gerçek onarım, entegrasyon, Mac build/çalıştırma, adversarial/regresyon/lifecycle, güvenlik, Git/provenance/CI, SHA/Evidence, DoneCheck sınırı, ürün kabul test matrisi, tam rapor ve engel başına uygulanabilir çözüm. Her turda yetki dahilindeki bütün güvenli işlerin tamamlanması ve tek kesin insan kararının sunumu zorunludur.

**Yönetim 10 birim çalışma modeli:** son teyitli **22/100**, 30/100 ilk ara eşik, **V23 hedefi 32/100 (+10)**. Sonraki tur, kabul edilmiş gerçek N üzerinden **N+10** hedefler. Yalnız sabit 100 ID ve özgün tam kabul koşulu karşılanınca ✓; GitHub kod ilerleme, izole Swift build, hazır owner-review veya resmî 12 kriter kararı birbirinden ayrılır. H1/H2/H3 resmî 0/12 ve F01–F06 kapanan 0/6, gerçek onay receipt'i gelince güncellenir.

**İCRA devir raporu:** 6 satır yönetici özeti + AudiV13 tam raporu. Raporda **bütün yapılan işler ve testleri, ID/evidence/owner gate kabul matrisi, kalan işlerin tamamı, engellerin kanıtlı nedenleri, hangi owner kararı gerektiği, her engel için çözüm önerisi ve net sonraki eylem**, preservation ve H1/H2/H3/Native/DoneCheck/Verified Finish durumu zorunlu. Yönetim her raporda gerçek tekil kontrol kapanışlarını kabul edip sayaç/mini ilerlemeyi günceller.

**Tek bağlayıcı emir:** `governance/mac-engineer/progress/ENGURU_V23_BUTUNSEL_FINIS_ICRA_V1.md`. İCRA Engineer PR #14 `V23_GOAL_HIERARCHY`, `V23_FULL_SCOPE_ENGINEER`, `V23_ACCEPTANCE_FINISH`, `V23_BATCHED_MANAGEMENT_10`, `V23_FULL_REPORT_BLOCKERS` runtime guidance ile hizalanır. Gerçek yetkili approval ve local Mac canonical aktivasyonu kendi kapısında.


## 15. V26 — Süzgeç, pozitif dil ve 10-kontrol finiş

**Kaynak/bağ:** `governance/ENGURU_LANGUAGE_GOVERNANCE_V1.md` pozitif ve doğru çalışma evreni; mevcut ENGÜRÜ Süzgeci™ sekiz aşama; `governance/mac-engineer/progress/ENGURU_V26_ONARIM_VE_ONAR_KONTROL_FINIS_EMRI_V1.md` Yönetim V26 ana emri; Engineer PR #14 `runtime/governance.py` V26 runtime guidance. Yeni canonical core veya ek kabul otoritesi kurulmaz.

**Yönetim rolü:** Ana P0 Verified Finish/`BITTI_DUR`; P1 H1 4/4→H2 4/4→H3 4/4→Native 0.8→DoneCheck/HumanReview resmî kapıları; P2 F01 ana + F05 bağımsız desteğin gerçek mühendislik kapanışı. F01–F06 ve 100 özgün ID bütünsel izlenir. `STATE → CLAIM → EVIDENCE → NEXT ACTION → VERDICT` doğru ve pozitif sunumla uygulanır.

**Onar kontrol evreleri:** 22/100 mevcut, V26 32/100 çalışma hedefi; ardından 42→52→62→72→82→92→100 (son sekiz). İCRA tüm izinli güvenli bağımlılıkları tamamlar, gerçek ✓ ID ve exact receipt sunar. Yönetim özgün tam kabul koşulu karşılanmış benzersiz ID'yi ledger'a yazar. İnsan kapısı veya bağımsız saha delili HOLD ise gerçek N ve eksik yetki/kanıt sınıflandırılır.

**V25 kanıt kesiti:** PR #191 F01 karar review dokümanı commit `ef0483e1af033e782e1c4513be5442b84e19060e`; PR #14 Native review patch commit `dbf34e055672ba4c93afddbac80662f288c37d3e`. Review-only yayın PASS; owner/reviewer canonical H1–H3, actual Native source diff, ikon/versiyon ve gerçek GUI kabulü HOLD. V26 görevlerin önceliği gerçek acceptance kapılarını tamamlamaktır.

**Tam devir:** Altı satır gerçek sayaç/hüküm; AudiV13'te 78 açık kontrolün tamamının kabul/owner/evidence durumu, F01–F06 doğrulanmış neden/hipotez ayrımı, kod/test/onarım, insan kararı ve sonraki uygun işi içeren JSON/MD. Yönetim alındığında yeni 10'lu grubu gerçek kabul edilmiş N'den oluşturur.
