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
# veya yeni rapor incelendikten sonra:
python3 -B tools/enguru_management_progress_v1.py --input /path/to/reviewed_handoff.json
```

Çıktı stdout JSON; repo/canonical dosyası değişmez. Şema, altı engel kimliği, kabul sayaç aralıkları ve kapanış receipt alanları fail-closed sınanır. Kanıt belirsizse resmi `PASS` ataması yapılmaz. Gerçek Mac raporu formatı farklıysa, Yönetim kayıtlarını **inceleyerek normalize eder**; script ham raporu sahte doğrulayıcıya dönüştürmez.

**PREPARED:** GitHub izole dalı + test + review.  
**ACTUAL GATES:** Yetkili canonical kabul sözleşmesi, OSi saha kanıtı, mevcut DoneCheck ve Human Threshold ayrı ayrı PASS.  
**VERIFIED FINISH:** Yalnız yetkili finalizer gerçek receipt'i.

## 7. Mevcut taban ve sonraki rapor

2026-10-21 V9 son saha raporu: `H1=0/4, H2=0/4, H3=0/4, Native=HOLD, VerifiedFinish=HOLD, open_F=6`; izole `H2=6/6, H3=13/13`, iki transport PASS. V10 İCRA çalışması sürüyor. Bu not sahadaki kaynakları değiştirmez.

Gelecek gerçek İCRA raporuyla aynı sayaçlar gözden geçirilecek; bütün engellere çözüm bulunurken aktif emir kapsamı 1 ana + en fazla 1 bağımsız işe odaklanacak.

**STATE → CLAIM → EVIDENCE → JUDGMENT → NEXT ACTION.**
