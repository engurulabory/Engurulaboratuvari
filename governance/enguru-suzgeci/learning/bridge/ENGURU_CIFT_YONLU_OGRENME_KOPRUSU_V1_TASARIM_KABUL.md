# ENGÜRÜ Çift Yönlü Öğrenme Köprüsü™ — V1 Tasarım ve İcra Kabul Sözleşmesi

**Durum:** `DESIGN_SCOPE_ACCEPTED_FOR_PREPARATION / THEORETICAL_100_100 / REFERENCE_SIMULATION_PASS / GITHUB_AND_MAC_FIELD_HOLD`  
**Tarih:** 2026-10-24  
**Kalıcı sabit hedef:** `GERÇEK_OLAY → KANIT → ÇİFT_YÖNLÜ_ÖĞRENME → DOĞRULANMIŞ_KOD_PAKETİ → GITHUB_CI + MAC_OSI_SAHA → YETKİLİ_KABUL → ÖLÇÜLMÜŞ_KAZANIM`.

## 1. Yetki, kapsam ve sabitler

- **Tek mantıksal Mühendislik Kası™, iki pilot düğümü:** `GITHUB_MK` (kod, PR, bağımsız CI, yayımlanabilir öğrenme); `MAC_OSI_MK` (yerel SQLite olay deposu, Mac ortam sınaması, yerel kanıt/geri bildirim). İki düğümün her birinde bir pilot ve bir depo bulunur. Yeni ayrı karar çekirdeği veya ikinci issuer oluşturulmaz.
- **Mevcut canonical hiyerarşi:** `main/AGENTS.md` → mevcut kilitli Evrensel V3 → Mühendislik Kası V3 → ürünün özgün canonical sınırları → DoneCheck™ v1.2 ve Human Threshold™. ENGÜRÜ Süzgeci™ sekiz aşama korunur.
- **İlk pilot kapsamı:** `ENGURU_MANAGEMENT_V69_PR_203` için kaynak/olay adaptörü; Yönetim ve İcra motorlarını üreten diğer oturumların canlı dallarına ve iş listelerine hiçbir yazım yapılmaz. Genişleme, her yeni ürünün yetkili kaynak ve kabul sözleşmesine bağlanır.
- **GitHub depolama:** mevcut `engurulabory/Engurulaboratuvari` deposunda, yalnız ayrı *inceleme dalında* `governance/enguru-suzgeci/learning/bridge/` altında olay adayları, ACK ve SHA-256 makbuzları. Kamusal depoya yalnız *owner tarafından bağımsız doğrulanmış ve gizlisiz olarak yayıma kabul edilmiş* allowlist alanları alınır. Özel kaynak, parola, anahtar, token, kişisel veri ve yerel ham loglar Mac'te kalır.
- **OSi depolama (önerilen; henüz kurulu değil):** `~/Enguru/Runtime/MacEngineer/state/mk-bridge/bridge.sqlite`; `journal_mode=WAL`, benzersiz kimlik ve sıra indeksleri, atomik transaction; `~/Desktop/AudiV13` altında SHA doğrulanmış, üzerine yazılmayan kanıt kopyası. Kopyalar özgünlerin yerini almaz.
- **ChatGPT rolü:** geçici mühendislik değerlendirme ve kod/inceleme yardımcısı; her tur güncel GitHub kaydını okur, erişilebilir Mac kanıtını yalnız kullanıcı/yetkili köprü sağladığında kullanır. Otomatik arka plan otoritesi, ikinci karar defteri veya sürekli açık üçüncü düğüm değildir.
- **Bağımlılık:** Ürünleştirme ve gerçek çift yönlü Mac kurulumu, Yönetim ve İcra motorlarının ayrı oturumlardaki kabul süreçlerine göre ilerler. Köprünün tasarım ve karşıt simülasyon hazırlığı bağımsız yapılabilir.

## 2. Çift yönlü mimari

```
        GITHUB_MK                                      MAC_OSI_MK
   Mevcut GitHub repo/PR                         Yerel Python + SQLite
   CI + inceleme dalı                            Native OSi gözlemi
   Append-only event/ACK   <---- GitHub HTTPS ---->  Transactional outbox/inbox
   Patch/test/artefaktlar      authenticated pull/push  Yerel immutable evidence
                 \                |                /
                  \---- mevcut ENGÜRÜ Süzgeci™ ----/
                        DoneCheck™ + Human Threshold™
                               (tek gerçek kabul)
```

Mac bağlantıyı **outbound** başlatır. GitHub Actions'ın Mac'e giriş bağlantısı ve ham disk erişimi bulunmaz. GitHub tarafı bir olay/yayımlama için yalnız mevcut GitHub kimliğiyle sınırlandırılmış review branch yazımı yapar. GitHub `schedule` best-effort; kod ve olay push/PR/dispatch tetikleri birincil sinyaldir. Mac `launchd`, açıkça etkinleştirilirse aralıklı yerel kontrol sağlar; süre garantisi gerçek saha ölçümü gerektirir.

### 2.1 Olay zarfı V1

Aşağıdaki JSON, olayın **gizlisiz metadata** kısmını örnekler; içerik dışarıdan yürütülebilir talimat değildir:

```json
{
  "schema": "enguru.mk.bridge-event/v1",
  "eventId": "EVENT_MAC_OSI_MK_00001",
  "taskId": "ENGURU_MANAGEMENT_V69_PR_203",
  "blockId": "OSIBLOCK-20261024-ABC",
  "correlationId": "OSIBLOCK-20261024-ABC",
  "producer": "MAC_OSI_MK",
  "sequence": 1,
  "runId": "RUN-20261024-001",
  "type": "ERROR",
  "observedAt": "2026-10-24T14:00:00+03:00",
  "sourceCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sourceSha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "visibility": "OWNER_REVIEW",
  "payload": {"code": "NODE_TAP_MISMATCH", "status": "OBSERVED"}
}
```

`sourceCommit` ve `sourceSha256` örnektir, gerçek kaynak olduğuna ilişkin iddia değildir. Gerçekte SHA-256 **yetkili, aktarım için hazırlanmış kanıt baytını** tanımlar. Özel Mac kaydının SHA'sı kamusal yayımlama yetkisi değildir; kamuya çıkan işaretçinin kaynak kapsamı ayrıca gözden geçirilir. `payload` yalnız daraltılmış hata/durum kodları içerir. İnsan metni, shell komutu, `.env` veya ham log zarf içinde taşınmaz.

### 2.2 Güven ve olay durumları

`LOCAL_OBSERVED → PREPARED_SANITIZED → REVIEW_CANDIDATE → VERIFIED_EVIDENCE → OWNER_ACCEPTED` bir *gözlem ve inceleme zinciridir*; `OWNER_ACCEPTED` statüsünü ancak **mevcut canonical owner/Human Threshold mekanizması** verir. Olay metni, GitHub yorumu veya SHA iddiası bir statüyü resmî kabul seviyesine yükseltmez. Hata kök nedeni yalnız kaynak + bağımsız doğrulayıcı kanıtıyla `CONFIRMED`; aksi durumda `HYPOTHESIS` / `UNKNOWN`.

Kabul: `EVENT_RECEIVED` ≠ `EVIDENCE_VERIFIED` ≠ `CODE_EXECUTED` ≠ `HUMAN_ACCEPTED` ≠ `VERIFIED_FINISH`.

### 2.3 Teslim protokolü, dayanıklılık ve çakışma

1. Üretici `eventId + producer + sequence + canonicalHash` alanlarını yerel transactional **outbox**'a kaydeder; kaynak `commit` ve sha gözlemine bağlar.
2. Gönderici kimliği aktarım kanalı üzerinden ayrı doğrulanır: GitHub için GitHub API'nin gerçek authenticated actor/commit/branch bilgisi; Mac için yerel kabul edilmiş kaynak ve scope. JSON'daki `producer` kendi başına kimlik kanıtı değildir.
3. Alıcı (GitHub inceleme deposu veya Mac SQLite) kaynak ve görünürlük yetkisini, şema/sürümünü, sıkı alan allowlist'ini, secret taramasını, sıralama sürekliliğini ve aynı kimlikle farklı hash çakışmasını inceler. Sonucu önce kalıcı yazar, sonra **ACK** üretir.
4. Başarılı ACK üretici outbox'ına teslim onayıdır; resmî ürün kabulü değildir. ACK kaybolursa yeniden gönderim **idempotent** olur. Aynı ID/farklı hash, sıra boşluğu, stale commit, yarışan GitHub branch update → belirli `HOLD` / yeniden uzlaştırma.
5. Ağ kesintisi sırasında outbox kalır. Yeniden bağlanma FIFO, önceki ACK/kimlik ve expected GitHub HEAD CAS kontrolüyle sürer. SQLite veritabanı eşzamanlı ham dosya senkronizasyonuna konu edilmez. Dosya kopyaları atomik snapshot/backup akışıyla alınır.
6. Temizleme/retention, gözden geçirilen politika ve geri alınabilir yedekler sonrasında; kontrolsüz otomatik silme yoktur. `ACK`/cursor ve audit makbuzları orijinalleri korunur.

### 2.4 Toplu kod aktarım sözleşmesi

GitHub kod tarafında PR / `git bundle` / açıkça SHA-kilitli patch + manifest; Mac tarafında karantinaya alınmış **staging** alanı + `dry-run` + test + yedek + atomik terfi + doğrulanmış rollback. Manifest, `taskId`, dosya tam yolu (depo göreli), `baseCommit`, `headCommit`, dosya SHA, uygulama/test politikası, üretici kimliği ve bağımsız kabul referansı taşır. Güven kaynağı **authenticated GitHub commit / owner-approved bundle release**; yalın SHA kimlik ve bütünlük gösterir, yazarı ispatlamaz.

Pakette yalnız izinli göreli yollar; simgesel bağlantı, `../`, mutlak yol, çift giriş, büyük/sıkıştırma oranı aşımı, manifest dışı dosya, kaynak sürüm kayması güvenli duruş üretir. İcra komutları veri metninden türetilmez; allowlist'teki sabit sürümdeki operatör prosedürü kullanılır. Gerçek Mac kurulum ve çalışma için owner izni ve özgün ürün DoneCheck gereklidir.

## 3. İş listesi ve bağımlılık planı

| Blok | Özgün iş ID'leri | Tamamlanacak iş | Kabul kanıtı | Tasarım durumu |
|---|---|---|---|---|
| B00 — Kaynak hizası | MK-BR-01/02 | `AGENTS.md` + kilitli V3 + MK V3 + PR #212 + çalışan ürün dallarını exact SHA ile bağla; önceki saha hata örneklerini al | Source map, owner scope, başlangıç P01–P06 | DESIGNED |
| B01 — Tek protokol | MK-BR-03/04/05 | V1 event/ACK şeması, kimlik/sequence/visibility, sürüm yükseltme ve geçiş kuralı | Strict validation, unknown schema HOLD, ürün sınırı | DESIGNED |
| B02 — GitHub düğümü | MK-BR-06/07/08 | Mevcut repo altındaki inceleme event deposu, authenticated ingest, PR/CI test ve publisher | İnceleme dalı, kamuya yalnız sanitised review; `main` korunur | DESIGNED |
| B03 — OSi düğümü | MK-BR-09/10/11 | SQLite WAL outbox/inbox, yerel dosya SHA ve yedek, seçmeli `launchd` pilotu | Restart/transaction/backup/yerel read-only test | DESIGNED |
| B04 — İki yönlü teslim | MK-BR-12/13/14 | GitHub→OSi, OSi→GitHub, ACK/replay/gap/conflict/offline/cursor/CAS | Gerçek iki yön test, idempotency ve crash recovery | DESIGNED |
| B05 — Kod alışverişi | MK-BR-15/16/17 | PR/manifest/git bundle, güvenli karantina, preflight/staging/rollback | Exact source, güvenli patch testi, runtime UI ve HTTP | DESIGNED |
| B06 — Öğrenme ve ölçüm | MK-BR-18/19/20 | Hata→gereksinim→regresyon adayı, eski MK yaşayan kayda uyum, P01–P06 baseline/after | Sürüm-bağlı test ve kanıta dayalı ölçüm | DESIGNED |
| B07 — ChatGPT bağlantısı | MK-BR-21/22 | Güncel GitHub kaynak okuma, izinli Mac receipt tüketme ve tek bütünleşik sonraki hareket raporu | Eski kaynak HOLD, yanlış PASS engeli | DESIGNED |
| B08 — Resmî kapanış | MK-BR-23/24/25 | Linux/macOS CI + 3 tekrar, owner-onaylı iki yönlü Mac saha pilotu, mevcut DoneCheck/Human Threshold kabulü | Exact-main kanıt, saha ledger, SHA, gerçek `VERIFIED_FINISH` | DESIGNED; FIELD HOLD |

**Kural:** Bloklar özgün iş kimliklerini ve bağımlılıklarını korur. B00→B01→(B02 + B03)→B04→B05→B06→B07→B08. Mevcut **PR #212** üçlü OSi ön kontrol/öğrenme/ölçüm dayanağı olarak korunur; ayrı oturumlardaki Yönetim/İcra dalları için yazım yetkisi `0`.

## 4. Kabul matrisi (25 kriter × 4 puan = 100 teorik)

Tasarımda her satırın **sözleşme ve karşıt senaryo tanımı** bulunması 4 puandır. Bu rubrikte `100/100`, yalnız mimari ve simülasyon yeterliliği; gerçek saha veya güvenlik sertifikası anlamına gelmez.

| Grup | Kontrol kimlikleri (5 × 4) | Tasarım kabul şartı |
|---|---|---|
| KANONİK | K01–K05 | Tek yetki zinciri; iki düğüm, tek MK; task/commit/source SHA; V3 ve owner sınırı; başka motorlara izolasyon |
| TAŞIMA | K06–K10 | Tekil kimlik/sıra; kalıcı outbox/inbox; ACK sonrası commit; replay/gap/conflict; offline kurtarma ve CAS |
| GÜVEN | K11–K15 | Authenticated actor; public allowlist/owner release; sır/özel depo sınırı; veri kaynaklı komut engeli; immutable archive |
| KOD | K16–K20 | PR + patch/bundle manifest; kaynak pin; zip path/size/symlink; sandbox dry-run; backup/rollback/CI+saha |
| ÖĞRENME | K21–K25 | Kök neden ve P01–P06 ayrımı; GitHub schedule best-effort; ChatGPT güncel okuma; gerçek saha ve Human Threshold; Verified Finish sınırı |

Sahada ayrıca gerekecek bağımsız kapılar: F01 **gerçek Github→Mac olay ve ACK**; F02 **gerçek Mac→GitHub owner onaylı gizlisiz olay ve ACK**; F03 **offline + restart + replay**; F04 **yanlış SHA/secret/özel veri reddi**; F05 **toplu patch staging + rollback + gerçek macOS smoke**; F06 **P01–P06 karşılaştırılabilir gerçek ölçüm**; F07 **mevcut DoneCheck/Human Threshold ve exact-main kabulü**. Gerekli her kapı ayrı gerçek makbuzla PASS olur. `DESIGN_100_100` bu kapıları otomatik karşılamaz.

## 5. Üç tasarım gözden geçirmesi ve karşıt model simülasyonu

**Tur 1 — mevcut fikir: 64/100 (teorik öz değerlendirme).** Güç: çift yön gereksinimi, Git/CI, yerel kanıt, owner sınırı. Gözlenen tasarım boşlukları: kimin yetkili yayımladığı belirsiz; aynı olayın ikinci kez yazımı; ACK kaybı; kimlik doğrulama ile SHA farkı; kamu/özel sınırı; aynı DB dosyasının iki yerde kullanımı; kesintiden devam ve ölçüm tanımı.

**Tur 2 — disiplinli taşıma: 88/100.** İki node + tek canonical, SQLite transactional outbox/inbox, ack-after-commit, replay/cursor ve source pin tanımlandı; alıcının gerçek kimliği henüz tam bağlanmadığı için sonraki düzeltme kapısına alındı. Kalan dört risk: branch CAS/çakışma, GitHub schedule SLA yanılgısı, code-bundle path traversal/rollback, ChatGPT kaynak eskimesi ve resmî kabul ayrımı.

**Tur 3 — bütünleşik karşıt düzeltme: 100/100 teorik rubrik (25/25).** `PUBLIC_SANITIZED` owner review/auth actor, güvenli bundle manifest, zip path/size/symlink/commit drift, branch CAS, ACK gönderen alıcının bağımsız doğrulanmış kanal kimliği, offline recovery, Node/TAP + UI/HTTP gerçek saha şartı, P01–P06 doğrulanan tamsayı/aralık tipleri ve baseline/after ve separate Human Threshold kabulü şartları tamamlandı. Referans Python modelinde **36 farklı test**, **3 temiz subprocess tekrarı** çalıştırıldı (108/108 PASS). Gerçek test sonuçları ayrı hazırlık makbuzunda sunulur.

**Karşıt rol denetimi:** GitHub ve Mac iki pilotta da doğrulanmamış kaynak `HOLD`; aynı ID farklı hash `HOLD`; iki tarafta eşzamanlı branch kaydı CAS ile yeniden uzlaştırılır; kullanıcı izin vermedikçe `PUBLIC_SANITIZED` gönderimi `HOLD`; mevcut özel anahtarlar/ledger koruma dışı bırakılmadan korunur; Mac pilot gerçekleşene kadar gerçek `FIELD_PASS` beyanı `HOLD`.

## 6. Hazırlık bitişi ve uygulama izni

- `DESIGN_READY`: İş listesi ve 25 teorik kriter 25/25; 3 tekrar referans simülasyonu PASS; dosyalar SHA-256 ile kilitli; ayrı review branch dışında yazım 0.
- `IMPLEMENTATION_READY`: B00–B08 sözleşmesi ve kaynaklar hazır; uygulamanın başlaması için owner'ın ayrı somut icra yetkisi ve ilgili ürünlerin kaynak uzlaştırması gerekir.
- `FIELD_PASS`: GitHub ve gerçek Mac OSi üzerinde F01–F07 tamamı kanıtlı; yerel veri güvenliği ve kaynak SHA yeniden doğrulanmış.
- `VERIFIED_FINISH → BITTI_DUR`: yalnız mevcut canonical DoneCheck™ ve Human Threshold™ resmî bağımsız kabulü; tasarım raporu veya ChatGPT metni bu makbuzun yerine geçmez.

**Bu turda uygulama sınırı:** Hazırlık/simülasyon/bağımsız GitHub taslak inceleme dokümanı; Mac kurulumu, `main` merge, ürün oturumlarına yazım, owner imzası ve yetkili makbuz üretimi `0`.

**Son simülasyonda yakalanan ek karşıt fark:** ACK makbuz hash’i tek başına kimlik belgesi sayılamaz; gönderen alıcı kimliği bağımsız doğrulanmış kanal bilgisinden bağlanır. P01–P06 ölçüm şeması boolean, negatif değer ve geçersiz schedule aralıklarını güvenli HOLD ile ayıklar. Bu hükümler teorik referans modelinde yeniden sınanmıştır; gerçek TLS/GitHub actor ve Mac OS kimliği uygulama safhasında ayrıca test edilecektir.
