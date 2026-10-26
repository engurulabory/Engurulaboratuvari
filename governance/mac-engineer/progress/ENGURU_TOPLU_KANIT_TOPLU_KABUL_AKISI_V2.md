# ENGÜRÜ Süzgeci™ v2.4 — Toplu Kanıt → Toplu Kabul Akışı™ V2

**Tarih:** 2026-10-22 · **Kabul:** Yönetim çalışma yöntemi · **Önceki yöntem:** [Tek Kapı Kabul Akışı V1](ENGURU_TEK_KAPI_KABUL_AKISI_V1.md). **V2, V1'in tek başlık/tek kabul turu zorunluluğunu iyileştirir; per-ID gerçek kabul disiplini ve yetki sınırlarını korur.**

## 0. Kaynak hakikati ve hedef

**Yönetim canonical kabul cetveli:** `ENGURU_100_BIRIM_FINIS_SAYACI_V1.json` ve `.md`; son doğrulanmış `27/100 PASS_EVIDENCE, 73 HOLD`. **Hedef:** `32/100` ara eşik → `100/100` özgün ID → ayrıca tam yetkili Verified Finish → `BITTI_DUR`. **H1/H2/H3 0/12**, F01–F06 kapanmış 0/6, Native/DoneCheck/HumanReview/Verified Finish HOLD. GitHub PR #191 feature-branch kabulü ile Mac OSi canonical/remote main ayrı kaynaktır.

**Yöntemin tek yeniliği:** *Tek odaklı bütünleşik mühendislik turu*, buna bağlı **1–10 benzersiz özgün ID'nin tek ortak kanıt paketi içinde ayrıştırılmış kabulü**. Yeni core, dokuzuncu Süzgeç aşaması, yetki issuer'ı, paralel ledger veya 100-ID kriter revizyonu üretilmez.

## 1. Hesap ve iş yükü

73 kalan benzersiz ID için 1 kontrol/tur = 73 tur; 3/tur = `ceil(73/3)=25`; 5/tur = `15`; 8/tur = `10`; 10/tur = `8` tur (yalnız teorik alt sınır). İCRA+Yönetim en az iki oturum mesajı üzerinden sırasıyla 146 / 50 / 30 / 20 / 16 mesaj örneğidir; gerçek kaynak, bağımlılık, Mac çalıştırma ve insan kararları ek tur yaratır. 5/tur ≈ %79, 8/tur ≈ %86 azalma **varsayımsal iletim tasarrufu**; teslim/kabul verimi ölçümü değildir.

**Birikimli eşiğimiz:** 27→32 (5), 32→42 (10), 42→52 (10), 52→62 (10), 62→72 (10), 72→82 (10), 82→92 (10), 92→100 (8). Bu aralıklar **raporlama kilometre taşıdır**, bir icra turunun zorunlu quota'sı değildir.

## 2. Kalıcı rol/oturum ayrımı

| Yüzey | Sorumlu | Tek birleşik teslim |
|---|---|---|
| Yönetim | Tek hedef, ortak bağımlılık ve 1–10 özgün kontrol ID'yi önceden işaretler; gerçek özgün acceptance, PASS/HOLD, ledger ve geçerli HEAD/CI | `BATCH_SCOPE` + `PER_ID_VERDICT` + tek consistent ledger |
| İCRA | Gerekli tüm mevcut kaynakları toplu okur; kod/onarım, izole saha, test, kaynak SHA, risk ve owner karar adayı üretir | `BATCH_ACCEPTANCE_PACKET` + ID bazlı kanıt tablosu |
| Yetkili owner | Birden fazla kontrolü kapsayan açık **ID+exact SHA+scope** kararı verebilir; signer/issuer ve ayrı reviewer rollerini korur | Tam scope'lu gerçek signed/durable kararlar |
| Kullanıcı | Yalnız gerçek ürün-sahibi insan eşiğinde yetki verir; günlük 1%'lik cetvel sürükleme işi Yönetim'dedir | Gerekli sınırlı human approval |

## 3. Tek tur sözleşmesi — 8 Süzgeç aşamasına yerleşir

1. **HAKİKAT:** Yönetim güncel ledger SHA, PR/head, Mac evidence, 100 özgün koşul ve owner status okur. Başlangıç `N` exact.
2. **KORUMA:** Kullanıcı worktree/138 owner-protected paths ve tüm yerel commitler; salt-okuma / izole işlemler. Ek yazım kendi yetki kapsamına bağlanır.
3. **TESPİT:** Bir **ana mühendislik hedefi** belirle; aynı source/owner/receipt bağımlılığını paylaşan **1–10 farklı Bxx-yy ID** seç. `BATCH_SCOPE` içinde `ORIGINAL_CONDITION`, mevcut kanıt, tek gerçek eksik, owner, kapatma testi.
4. **FARK:** İCRA ilişkili tüm kaynakları topluca değerlendirip gerçek onarım/kanıt üretir; birebir kontrol başına sıfırdan rapor döngüsü oluşturmaz.
5. **TAMAMLA:** Geçerli owner scope kararları, yetkili local stage, PR reviewer ve ihtiyaç duyulan saha testleri kapsamında bütün uygun işleri bitir. İnsan eşiğinde `READY_FOR_OWNER`; diğer bağımsız ID'lerde İLERLE.
6. **KANITLA:** Her kontrolün bağımsız PASS şartı ayrı satırda tamamlanır: `ID | ORIGINAL_CONDITION | BEFORE_STATE | REPO/BRANCH/HEAD/BLOB/SHA | EXECUTION | TEST_POS/NEG | OWNER_RECEIPT_APPLICABILITY | EVIDENCE_SHA | CLAIM`. Aynı upstream evidence birden fazla ID'ye referans olabilir ama özgün criterion/authority bağı her satır için ayrı incelenir.
7. **SONRAKİ İHTİYAÇ:** İCRA tek `BATCH_ACCEPTANCE_PACKET` sunar; Yönetim aynı devirde her ID'yi `PASS_EVIDENCE`, `READY_FOR_OWNER`, `HOLD_SOURCE` veya `HOLD_TECHNICAL` kararıyla ayrıştırır. Hazır `k` ID sayılır; `N→N+k`; sıfır artışta kilit owner/teknik sorunu ve alternatif kanıtlı ID rotası belirlenir.
8. **İLERLET:** Yönetim tek gerekçeli kabul işleminde 100-ID JSON+MD ve karar kayıtlarını birlikte mutabık hale getirir; exact HEAD'i yeniden okur, GitHub CI ve `PASS_COUNT==verified_units`, `remaining==100-verified`, `unique_IDs==100` denetler; sonraki ana odak emrini yalnız bu karardan sonra çıkarır.

## 4. Tek karar/çok ID bağımsızlığı ve kanıt kapısı

- `BATCH_ACCEPTANCE_PACKET` aday ID seti **1..10**, her ID özgün 100 cetvelden, benzersiz ve daha önce `HOLD`. Bir kontrol iki kez sayılmaz.
- Management `PASS_EVIDENCE` yalnız ilgili *original exact condition* + gerçek source/CI/field + gerekliyse owner/reviewer scope/expiry/receipt eksiksiz olduğunda verir.
- 1 batch'te 8 adayın 3'ü PASS 5'i HOLD ise sayaç **N→N+3**. Eksik 5'in nedenleri ve owner hareketi tek dar karar listesine girer. Hiçbir tur 10 garanti etmez.
- Yetkisiz kaynak, stale HEAD, kaynak SHA uyuşmazlığı, sahte/imzasız zorunlu owner, uygulanmamış test, negatif fail durumlarında ilgili ID `HOLD`; diğer geçerli ID'ler korunur.
- 10 ID toplu kabulü **H1/H2/H3 dördüncü resmî şartı atlamaz**; Native signed/install/live, DoneCheck `verifyTask`, Ed25519 HumanReview ve durable `recordVerifiedFinish()` her biri kendi ayrı yetki zincirindedir.
- Bilinçli ayrı yerel kaynak geçmişleri B05-04 kapsamında kabul edilmiş olabilir; `B05-05 Local/remote exact HEAD mutabakatı` başka şarttır. Sırf `DIVERGED` gözlemi tam SHA eşliğine yükseltilemez. Saha eşitlik/yetki boşluğu açıkça sınıflanır.
- Yeni rapor yalnız değişen kabul kanıtları ve 1–10 ID satırlarını taşır. Bütün 73 açık ID ve F01–F06 **mevcut envantere referansla** korunur; kopya 76 sayfalık rapor döngüsü sona erer.

## 5. Bir sonraki ilk birleşik mühendislik dalgası

**Ana hedef:** B05–B06 kaynak, sürüm ve Mac stage bağımlılıklarının izole ve korumalı kabul hazırlığı. **Kabul aday havuzu**, otomatik PASS beklentisi olmaksızın: `B05-05` (local/remote exact HEAD, ayrı lineage koruması ve gerçek parity), `B06-09` (Native 0.8 Info.plist kaynak/iki app version), `B06-07` (authorized local HEAD ↔ stage source), `B06-08` (canonical stage entrypoint), `B01-09` (source owner+active version), `B01-10` (F01–F06 accepted canonical snapshot), `B07-04` (real owner source review), `B07-06` (source/PR/CI + authorized review). En çok **8 aday**, fakat zorunlu hedef yalnız kanıtla kapanan gerçek ID'lerdir. İCRA kendi mevcut yetki sınırında teknik eksikleri kapatır; gerektiğinde tek owner karar paketi içinde explicit ID/scope ayırır.

**Bağımsız güven zinciri:** F01 owner/Ed25519 reviewer ve H1 P-256 signer, H2 atomic writer, H3 authorized parity; F05 Native GUI/icon sign/install/live; DoneCheck/HumanReview/Verified Finish diğer bağlı kapılardır. Aynı turda, ana işi dağıtmadan hazırlık kanıtları korunur.

## 6. Gelecek Yönetim cevabının küçültülmüş zorunlu formatı

`STATE=PASS_PARTIAL_BATCH|HOLD_BATCH`
`BASE=N/100; CANDIDATES=[...]; ACCEPTED=[...]; HELD=[...]`
`NEW_LEDGER=N+k/100; REMAINING=100-N-k; FINAL_HEAD=<exact>`
`PROOF=<source commit SHA / Mac receipt / required owner IDs>`
`CI=<exact HEAD workflow status>`
`NEXT=<first shared blocker or next closeable batch>`

**Simülasyon örnekleri:** 8 aday/3 gerçek tam PASS/5 HOLD → N→N+3; tek owner receipt 5 ayrı ID'yi kapsar ve 5 özgün koşul ayrı ayrı tamam ise N→N+5; 8 adayın hepsi owner HOLD ise N→N ve bir toplu Human Threshold karar konusu. Hepsi teorik karar sınamalarıdır, olmuş saha kanıtı değildir.

**Sistem kalite testi:** Kabul sayacı için `N` kanıtlı, `N+k` yalnız accepted özgün ID'ler; ürün tamamlanma yüzdesi ile eşitlenmez. Bitiş ancak resmî ayrı otoritelerle `100/100 + Verified Finish → BITTI_DUR`.

## 7. Yönetim tarafından açık yöntem kabulü — 22.10.2026

**STATE=USER_APPROVED_V2_ACTIVE / SCOPE=REVIEW_BRANCH_OPERATING_METHOD**

Ürün sahibi, 22.10.2026 Yönetim oturumunda **Toplu Kanıt → Toplu Kabul Akışı V2** yöntemini açıkça benimsedi ve çalışma yöntemi olarak kaydını istedi. Etkin yöntem V2'dir. Önceki Tek Kapı V1'in **tekil özgün kontrol/kanıt/owner hükmü** korunur; **her yüzde birimi için ayrı Yönetim–İCRA turu** koşulu kaldırıldı. Bu kullanıcı onayı çalışma yöntemi kapsamındadır; canonical main merge, Secure Enclave signer, Ed25519 reviewer, Native install veya gerçek HumanReview izni değildir.

**Tek ana birleşik iş, birden çok bağımsız kabul:** İCRA aynı kaynak/owner/test bağımlılıklarını gerçekten paylaşan en fazla 10 *aday* ID'yi bir mühendislik turuna alır. Önceden bildirilen sekiz ID bir **aday havuzudur**, zorunlu sekiz iş değildir. İCRA bağımlılığı kanıtlananları gruplar; owner kararı bekleyenleri hazırlar ve diğer uygun güvenli işleri bitirir. Her ID'nin kendi `ORIGINAL_CONDITION`, gerçek test ve yetki şartı ayrı. Yönetim tek devirde `k` benzersiz PASS için `N→N+k` mutabakatını yapar.

**İlk gerçek saha kabul testi:** Güncel Yönetim 27/100; bir sonraki İCRA tesliminde batch adayı bazında bağımsız PASS/HOLD ile karar, JSON+Markdown eşitliği, exact HEAD ve GitHub CI. 27→32 **beş ID koşulsuz hedefi değil**, ancak beş ayrı özgün kontrolün tamamlanmış kanıtıyla gerçekleşebilecek birikimli eşiktir. `27→N` kanıta göre kararlandırılır.

**Oturum devri ve çalışma ekonomisi:** Yönetim son HEAD/ledger ve V2 kaynak linkini verir; İCRA aynı kaynakları ve AudiV13 gerçek Mac receipt'lerini yeniden kullanır. Büyük 73 satırlık arşiv raporları tekrar tekrar üretilmez; yalnız **değişen ID'ler, yapılan gerçek iş, ilgili kaynak/owner ve kabul kanıtları** devredilir. Tek ortak `BATCH_ACCEPTANCE_PACKET` ve tek Yönetim kararıyla akış ilerler. Mac local source, 138 korunan dirty path ve 634/185 local-only commitler yerinde korunur.

## 8. İcra hedefini %100 kanıta bağlayan Pre-Send tamamlama kapısı

**Amaç:** Bir üreticinin `%68–74` civarında kısmi icradan sonra `BITTI` ilan etmesini önlemek. Hedef her turda **seçilen ve yetki kapsamı izin veren işlerin %100 gerçek icrası**, gerekli tüm kontrol test/receipt'lerinin tamamlanması ve Yönetim'in gerçek kabul hükmüdür. **Her görevde modelin mutlak %100 doğruluğu garanti edilmez.**

**Mevcut V2'ye eklenen salt-okunur doğrulama yardımcısı:** `tools/enguru_batch_evidence_gate_v2.py`. Yeni canonical core veya 9. Süzgeç aşaması değildir; V2 teslim öncesi yapısal kanıt kapısıdır. Python 3.11 ve stdlib. `tests/test_enguru_batch_evidence_gate_v2.py` + Management Progress CI üzerinden 17 pozitif/negatif karşıt senaryo. Script gerçek dosyaların SHA-256'sını kendi başına hesaplamaz, GitHub kaynak HEAD'i veya Mac signer sahibini doğrulamaz, HumanReview imzasını üretmez ve resmî PASS kaydı yazmaz. Bu sınıra uyan çıkış `PRE_SEND_STRUCTURAL_CHECK_ONLY_NOT_AUTHORITY` ve `official_pass_added=0` biçimindedir.

**İCRA içinde mevcut 8 Süzgeç aşamasında döngü:** İlk `BATCH_ACCEPTANCE_PACKET` taslağını oluştur → özgün ledger 100-ID kimlik/şart/sayaç tabanını ve her ID'nin test, source SHA, owner kapsamı ve evidence alanlarını V2 denetleyiciye ver → `HOLD_EVIDENCE` ise gereken gerçek icra/kanıt/owner işlemini gerçekleştirip tekrar kontrol et → teknik açıdan erişilebilir tamamlanmış ID'ler `READY_FOR_INDEPENDENT_MANAGER_REVIEW` olur → Yönetim gerçek kanıt ve Human Threshold doğrulamasıyla ID başına PASS/HOLD kararı verir, sonra ledger'a kümülatif işler. Owner yetkisi bekleyen ID'ler HOLD kalırken diğer bağımsız ID'ler ilerler.

**Çalıştırma örneği** (paket kendi `schema: enguru.batch.evidence/v2` ve `items` alanlarını taşır):
```sh
python3 -B tools/enguru_batch_evidence_gate_v2.py \
  --ledger governance/mac-engineer/progress/ENGURU_100_BIRIM_FINIS_SAYACI_V1.json \
  --packet /path/to/BATCH_ACCEPTANCE_PACKET.json
```

**Hüküm:** `structural_coverage_percent` yüzdesi yalnız **aday paketindeki alanların eksiksizliği** için bir ön denetimdir; gerçek saha başarı puanı, özgün SHA bağımsız doğrulaması veya 100/100 Yönetim kabul puanı değildir. Kanıtlı PASS ancak gerçek bağımsız doğrulama sonrası canonical kriter için Yönetim yetkisiyle verilir. 27/100 gerçek sayaç bu V2 altyapı güncellemesiyle değişmez.
