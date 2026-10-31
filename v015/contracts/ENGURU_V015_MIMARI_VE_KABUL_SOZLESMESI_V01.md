# ENGÜRÜ OSi Üçlü Yerel Zekâ™
## V015 — Ortak Deterministik Mühendislik Çekirdeği™
### Özgün 75 koşul ↔ Dokuz mühendislik kapısı · Mimari/Kabul Sözleşmesi V0.1

**Tarih:** 30 Ekim 2026
**Nihai amaç:** Mac OSi’de tek komuttan gerçek iş, doğrulanmış sonuç, güvenli araç ve Ulak görünümüyle uçtan uca tam bitmiş ürün.
**Belge statüsü:** `SOURCE_ALIGNED_DESIGN_SPECIFIED / OWNER_CANONICAL_FINAL_HOLD` — ön-mühendislik taslağı; ürün veya hazırlık PASS değildir.
**GitHub V014.MAC dayanağı:** `04d67c9bf9981a900dc2f9931deb577d2518683f` (kayıt amaçlı, V015 commit’i değildir).

## 1. Kanonik kaynak doğrulaması

| Kaynak | SHA-256 ve yetki seviyesi |
|---|---|
| Özgün 75 kabul koşulu | `a0ea2e161c639b079947301a6001021e43ff198aabca5105ed69586da2789756` · **bayt eşliği doğrulandı** |
| V0.8 75 ikili kapı defteri | `db3aee647310e2cb3a53fdb34d9f5a3cf0192c7c3d98f9d08d453c8158524c40` · aynı 75 özgün ID ve ölçüt metni |
| V0.8 typed arayüz sözleşmesi | `986ee46bb55df6d3205284a6e17a80c2a7f59bdbe3676a7972dd77526cb8882a` · tasarım girdisi |
| 34 owner karar eşleme taslağı | `6ca4d1375608ed681f3ae06376a005a1344d82eb0cd7759bc05c24f6588a5589` · **OWNER SIGNED CANONICAL DEĞİL** |

**Kimlik ad uzayı:** Owner kararları `OWN.K01–OWN.K34` (eski kayıtlar `K01–K34`), V0.8 hazırlık kapıları `V08.G01–V08.G09` (eski kayıtlarda `G01–G09`), bu belgeye özgü mühendislik kapıları `V015.G01–V015.G09`. Böylece kayıt ve API alanları çakışmaz.

**Sabit:** 15 özgün alanın ve 75 ID’nin metni, puan paydası ve ayrı hazırlık/saha ölçüsü değişmedi. V015.G01–V015.G09 yeni bir puan paydası değildir; mühendislik izleme/audit kapılarıdır. Her özgün ID tek bir birincil kapıda, uygun olduğunda diğer kapılarda ikincil bağımlılık olarak görünür.

## 2. Mimari görev ve otorite ayrımı

| Bileşen | Girdi → çıktı | Yetki sınırı |
|---|---|
| **Ulak** (tek chat yüzeyi) | Kullanıcı emri → `UserCommand`; `ReadOnlyTaskProjection` → gerçek ekran | UI durum/proof defterini doğrudan değiştiremez; owner imzası üretemez. |
| **Yönetici Zekâ** | typed emir + özgün kabul → `PlanCandidate` | Plan ve kapsam önerir. Shell, araç izni veya sahte owner grant oluşturamaz. |
| **Ortak deterministik çekirdek** | PlanCandidate, task/scope SHA, grant, typed tool proposal, gerçek tool/test/evidence | Planı mühürler, broker yetkisini ve güvenli icrayı denetler; bağımsız verifier ve makbuzlarla gerçek state/projection hesaplar. |
| **İcracı Zekâ** | SealedPlan + izinli yetenekler → `ToolProposal` + kod/test adayı | Modelin önerisi icra izni değildir. İcra yalnız çekirdek/tool broker aracılığıyla. |
| **Owner (Human Threshold™)** | Açık task/scope/action/resource/expiry/nonce → `OwnerApproval` | Kritik eylem öncesinde gerçek insan yetkisi; model/UI owner taklidi yapamaz. |

**Görünür ekranlar:** Ana Cockpit fabrikanın genel görünümü; PiLive portföy takibi için read-only modal; Ulak yalnız aktif görevin kanıtlı ilerlemesi ve sohbet. V0.6 kabul edilmiş baykuş/görsel kimlik korunur; V0.7.1 adayın son görsel kabulü HOLD. iPad dikey görüntü referansı, çalışan iPad uygulaması kanıtı değildir.

## 3. Tipli icra ve sonuç sözleşmesi

**Sıra:** `UserCommand → PlanCandidate → SealedVersionedTaskPlan → ToolProposal → PolicyDecision/ExecutionPermit → OperationReceipt → VerifiedReceipt → ProofLedger → DoneCheckResult → ReadOnlyTaskProjection`.

1. **Kimlik:** `command_id, idempotency_key, task_id, plan_version, plan_sha256, scope_sha256, source_sha256`; alanlar ve sürümler typed schema ile doğrulanır.
2. **Plan:** DAG döngüsüz, tanımlı bloklar, toplam ağırlık tam `10000` baz puan. Bilinmeyen/çift blok veya yanlış tip reddedilir.
3. **İcra:** Atomik tek aktif iş, FIFO uygun iş ve bağımlılık kontrolü. `UNKNOWN` dış etkide read-only reconciliation; otomatik replay yok.
4. **Yetki:** Scope+task+plan+resource+expiry+nonce+kimlik eşliği güvenilir kaynaktan; yetki eylem öncesinde denetlenir.
5. **Kanıt:** Modelin `ran_tests` veya `DONE` beyanı değil, gerçek tool ve test makbuzları; `VerifiedReceipt` yalnız bağımsız verifier tarafından.
6. **İlerleme:** `done_weight = Σ(weight_i | ilgili blok için geçerli başarılı VerifiedReceipt)`; `0 ≤ done_weight ≤ 10000` ve yüzde `done_weight/100` (2 basamak).
7. **DoneCheck:** 10000 baz puan tek başına final değil; eksiksiz özgün kriter makbuzları, kritik owner kapıları, ürün saha ve ilgili git kaynak eşliği ayrıca.
8. **OSi:** Yerel model için sıfır zorunlu ücretli API; Mac M5 Pro/24GB hedefi ve yalnız aktif işlemde sistem uykusu yönetimi. Ekran uyuyabilir, kapalı kapak sistem uykusu gerçek icrayı sürdürüyor varsayılmaz.
9. **Koruma:** Eski Ulak, PiLive SQLite ve yedekleri salt-okunur referans; silme/değiştirme/merge/yayın ayrı owner kararı gerektirir.

## 4. V015.G01–V015.G09 mühendislik kapıları ve pozitif/karşıt testler

### V015.G01 — Kaynak ve kimlik sürekliliği · 5 birincil özgün koşul
**İşlev:** GitHub canonical mühendislik kaynağı, Mac yerel saha kopyası, task/plan/source/scope SHA kimlikleri ve değişmez provenance.
**Olumlu sınama:** Pinned HEAD ve gerçek dosya SHA eşliğiyle yetkili read-only kaynak keşfi; Mac/GitHub senkronunda drift raporu.
**Karşıt sınama:** Yanlış HEAD, eksik kaynak, eskitilmiş evidence ve sahte makbuzun reddi.
**Kanıt:** GitHub SHA, gerçek yerel dosya SHA, manifest ve drift regresyon makbuzları.
**Çıktı:** `SourceManifest, VersionPin, DriftReceipt`.
**Birincil ID:** HG05, GU04, YY03, YY04, IS05. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G02 — Görev ve plan sözleşmesi · 9 birincil özgün koşul
**İşlev:** Yönetici planı önerir; çekirdek plan kimliğini, bağımlılık DAG ve toplam 10000 baz puanını mühürler.
**Olumlu sınama:** Türkçe user command → typed UserCommand → kabul ölçütlü, sıralı DAG ve sabit plan.
**Karşıt sınama:** Döngü, bilinmeyen blok, 10100 ağırlık, yanlış deneme sayısı veya owner kararı olmadan kapsam değişimi reddi.
**Kanıt:** Şema validasyonu, DAG/weight karşıt testleri, sürüm ve owner-diff makbuzları.
**Çıktı:** `UserCommand, PlanCandidate, SealedVersionedTaskPlan`.
**Birincil ID:** HG01, HG02, YG01, YG02, YG03, YG04, YG05, YY01, YY02. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G03 — Yetki ve güven sınırı · 6 birincil özgün koşul
**İşlev:** Human Threshold ve en az yetki: modelin serbest metni, README ve araç yanıtı yetki üretmez.
**Olumlu sınama:** Gerçek task/scope/plan/source/expiry/nonce ile geçerli owner onayı için kontrollü izin.
**Karşıt sınama:** Sahte/expired grant, prompt injection, path traversal, symlink kök kaçışı, yanlış task ya da model tarafından uydurulmuş grant reddi.
**Kanıt:** Model dışı trusted facts ile pre-action broker karar testleri ve olumsuz yetki makbuzları.
**Çıktı:** `CapabilityGrant, OwnerApproval, PolicyDecision`.
**Birincil ID:** HG03, GU01, GU02, GU05, YS01, IS03. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G04 — Kalıcı görev defteri ve kurtarma · 8 birincil özgün koşul
**İşlev:** SQLite WAL single-writer, FIFO+dependency, tek aktif claim, idempotency, kesinti ve UNKNOWN dış etki uzlaştırması.
**Olumlu sınama:** Aynı command/payload kararlı sonuç, farklı payload conflict, bağımsız yerel işlerin ilerlemesi, restart sonrası tutarlı kayıt.
**Karşıt sınama:** Eşzamanlı çift claim, çelişkide REPLACE, UNKNOWN effect replay, tamamlanmamış işlemi DONE sayma, belirsiz yeniden yürütme reddi.
**Kanıt:** Gerçek SQLite kalıcılık/atomiklik/çok-işçi/öldür-yeniden-başlat/UNKNOWN testleri.
**Çıktı:** `TaskLedger, EventCheckpoint, RecoveryDecision`.
**Birincil ID:** YA02, YA04, MA03, MA05, YS04, YS05, IS02, IY02. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G05 — Güvenli ve gerçek araç icrası · 7 birincil özgün koşul
**İşlev:** Model önerisinin typed proposal olarak brokerden geçmesi; yalnız allowlist sandbox/worktree veya yetkili yerel araç; tool receipts.
**Olumlu sınama:** İzolasyonda gerçek Python dosyası onarımı, Git worktree oluşturma ve yetkili test komutu; doğru stdout/exit makbuzu.
**Karşıt sınama:** Kök dışı yazma, kullanıcı dosyası değişimi, yetkisiz shell, merge/publish/delete ve kaynak kaymasında icra engeli.
**Kanıt:** Isolated gerçek tool invocation, izin ve path karşıt testleri, before/after SHA.
**Çıktı:** `ToolProposal, ExecutionPermit, OperationReceipt`.
**Birincil ID:** GU03, IG01, IG02, IG03, IG05, IY03, IY05. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G06 — Bağımsız test ve kontrollü onarım · 4 birincil özgün koşul
**İşlev:** Kodun üretimi ile gerçek test icrası ayrılır; en fazla üç farklı kanıtlı onarım turu, iki tekrarda yeni teşhis için HOLD.
**Olumlu sınama:** Özgün beklenen fixture ve gerçek test komutuyla green, bağımsız test ve regresyon raporları.
**Karşıt sınama:** Beklenen sonucu değiştirme, sahte ran_tests, tekrar eden aynı hipotez, yorumla kod eksiltme ve 4. tur reddi.
**Kanıt:** Kırmızı/yeşil, karşıt ve regresyon testleri; exit/stdout/stderr ve source SHA kayıtları.
**Çıktı:** `TestPlan, TestReceipt, RepairCheckpoint`.
**Birincil ID:** IG04, IS01, IY01, IY04. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G07 — Kanıt, ilerleme ve DoneCheck · 8 birincil özgün koşul
**İşlev:** VerifiedReceipt, fail-closed verifier, append-only kanıt ve baz puandan gerçek ilerleme; owner final ayrı.
**Olumlu sınama:** Tam task/plan/source/receipt ile doğrulanan blok ilerler, kanıtlı 10000/10000 sonrası bütün DoneCheck koşulları ayrı değerlendirilir.
**Karşıt sınama:** Verified filtresi kaldırılması, sahte PASS, SHA var ama test fail, yüzde >100, model DONE ifadesi, eski makbuz reddi.
**Kanıt:** Provenance ve test makbuzları, karşıt proof drift, güvenilir yüzde ve owner gate testleri.
**Çıktı:** `VerifiedReceipt, ProofLedger, DoneCheckResult`.
**Birincil ID:** HG04, MA04, YS02, YS03, IS04, TU02, TU05, YD01. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G08 — Yönetici–İcracı–Çekirdek–Ulak bütünleşmesi · 6 birincil özgün koşul
**İşlev:** Tek yerel modelde ayrık iki rol, tek broker ve bağımsız verifier; Cockpit/PiLive/Ulak farklı ürün yüzeylerini korur.
**Olumlu sınama:** UserCommand → SealedPlan → ToolPermit → VerifiedReceipt → ReadOnlyProjection uçtan uca, pozitif yetkili görev.
**Karşıt sınama:** UI/metin doğrudan DB/kanıt yazamaz; PiLive/Ana Cockpit görev icra komutu üretemez; yanlış rol/plan mesajı reddi.
**Kanıt:** Event ordering, typed schema, rol izolasyonu, bağımlı hizmet ve pozitif E2E pilot.
**Çıktı:** `TypedIPC, RoleAdapter, ReadOnlyTaskProjection`.
**Birincil ID:** YA01, MA01, MA02, YY05, TU01, YD03. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

### V015.G09 — Mac OSi, Ulak deneyimi ve saha kabulü · 22 birincil özgün koşul
**İşlev:** Gerçek Mac-native SwiftUI, V0.6 görsel kimlik, erişilebilir Ulak, eskilerin korunumu ve gerçek owner kabulü.
**Olumlu sınama:** Native derleme, oturum/uyku/kesinti, kullanıcı görevi, %/HOLD/DoneCheck gösterimi, masaüstü erişilebilirlik ve owner kabulü.
**Karşıt sınama:** Yanlış yüzde ve sahte DONE gösterimi, küçük pencerede taşma, VoiceOver/kontrast eksikliği, eski Ulak/PiLive verisine dokunma.
**Kanıt:** Native SwiftUI build, Mac üzerinde gerçek görev + restart, görsel V0.6 karşılaştırma, owner saha makbuzu.
**Çıktı:** `MacAppBuild, FieldReceipt, OwnerAcceptance`.
**Birincil ID:** YA03, YA05, TU03, TU04, KU01, KU02, KU03, KU04, KU05, YR01, YR02, YR03, YR04, YR05, VG01, VG02, VG03, VG04, VG05, YD02, YD04, YD05. **Kabul:** `HOLD / NOT_TESTED` (mimari kapsamı tanımlandı; ürün kanıtı yok).

## 5. Kaynak eşli 75 koşul — birincil ve çapraz bağlar

Bu tablo özgün kaynak dosyasındaki gereklilik cümlelerini **aynen** korur. İkincil kapı erişimi çapraz bağımlılıktır, ek puan değildir. Her satırdaki mevcut kurulum öncesi ve saha durumu sırasıyla `HOLD_VERIFICATION` / `NOT_TESTED`.

| Özgün ID | Orijinal alan | Orijinal gereklilik (aynen) | Birincil | İkincil |
|---|---|---|---|---|
| HG01 | Hedef gücü | Tek net hedef ve gerçek sonuç | V015.G02 | — |
| HG02 | Hedef gücü | Kullanıcı niyeti → blok → çıktı | V015.G02 | V015.G08 |
| HG03 | Hedef gücü | Sıralı tam otomasyon + human gate | V015.G03 | V015.G05 |
| HG04 | Hedef gücü | Kanıt ve yüzde bağı | V015.G07 | V015.G09 |
| HG05 | Hedef gücü | Hazırlık/teknik/saha sınırları | V015.G01 | V015.G09 |
| YA01 | Yalınlık | Tek uygulama, tek sohbet | V015.G08 | V015.G09 |
| YA02 | Yalınlık | Tek aktif iş, FIFO | V015.G04 | V015.G08 |
| YA03 | Yalınlık | Minimal ekran, katlanır kanıt | V015.G09 | V015.G08 |
| YA04 | Yalınlık | Duraklat/devam/güvenli dur | V015.G04 | V015.G09 |
| YA05 | Yalınlık | Arka plan otomatizasyonu | V015.G09 | V015.G04 |
| MA01 | Mimari | Yönetici/İcracı ayrı yetki/bağlam | V015.G08 | V015.G03 |
| MA02 | Mimari | Tek yerel model adaptörü | V015.G08 | V015.G01 |
| MA03 | Mimari | Tek yazıcı, tek gerçek veritabanı | V015.G04 | V015.G07 |
| MA04 | Mimari | Bağımsız doğrulayıcı | V015.G07 | V015.G05 |
| MA05 | Mimari | Kurtarma + Zülfikar yedeği | V015.G04 | V015.G09 |
| GU01 | Güvenlik | En az yetki, izinli kaynaklar | V015.G03 | V015.G05 |
| GU02 | Güvenlik | İnsan eşiği kapsam/nonce/SHA | V015.G03 | V015.G05 |
| GU03 | Güvenlik | Yalıtılmış düzenleme ve geri alma | V015.G05 | V015.G09 |
| GU04 | Güvenlik | Kaynak/proof doğruluğu | V015.G01 | V015.G07 |
| GU05 | Güvenlik | Gizlilik, prompt enjeksiyonu ve audit | V015.G03 | V015.G05 |
| YG01 | Yönetici görev | Doğal emir → açık hedef | V015.G02 | V015.G08 |
| YG02 | Yönetici görev | Bağımlı uygulanabilir bloklara ayırma | V015.G02 | V015.G04 |
| YG03 | Yönetici görev | Sabit ağırlık/scope sürümü | V015.G02 | V015.G07 |
| YG04 | Yönetici görev | Ön simülasyon ve karşıt sınama | V015.G02 | V015.G06 |
| YG05 | Yönetici görev | İcracıya kesin yetkili devir | V015.G02 | V015.G03 |
| YS01 | Yönetici sorumluluk | Human Threshold koruması | V015.G03 | V015.G02 |
| YS02 | Yönetici sorumluluk | Yanlış beyanı PASS saymama | V015.G07 | — |
| YS03 | Yönetici sorumluluk | Gerçek DoneCheck kuralı | V015.G07 | V015.G09 |
| YS04 | Yönetici sorumluluk | Güvenli kuyruk ilerlemesi | V015.G04 | V015.G07 |
| YS05 | Yönetici sorumluluk | Durma kararı/öğrenme ve kanıt | V015.G04 | V015.G06 |
| YY01 | Yönetici yetenek | Planlama doğruluk sınavı | V015.G02 | V015.G06 |
| YY02 | Yönetici yetenek | Risk/bağımlılık analizi sınavı | V015.G02 | V015.G03 |
| YY03 | Yönetici yetenek | Kaynak keşif/araç seçimi | V015.G01 | V015.G02 |
| YY04 | Yönetici yetenek | GitHub+Mac durum uzlaştırma | V015.G01 | V015.G09 |
| YY05 | Yönetici yetenek | Kararların okunur raporlanması | V015.G08 | V015.G09 |
| IG01 | İcracı görev | Yalıtılmış üretim | V015.G05 | V015.G03 |
| IG02 | İcracı görev | İzinli Mac araçlarının icrası | V015.G05 | V015.G03 |
| IG03 | İcracı görev | Yetkili GitHub iş akışı | V015.G05 | V015.G01 |
| IG04 | İcracı görev | Test ve onarım döngüsü | V015.G06 | V015.G07 |
| IG05 | İcracı görev | Çıktı+receipt+rollback üretimi | V015.G05 | V015.G07 |
| IS01 | İcracı sorumluluk | Hatalı/eksik testle PASS yasak | V015.G06 | V015.G07 |
| IS02 | İcracı sorumluluk | Tekrarsız ve duruma bağlı icra | V015.G04 | V015.G05 |
| IS03 | İcracı sorumluluk | Sır koruma ve izin sınırı | V015.G03 | V015.G01 |
| IS04 | İcracı sorumluluk | Bağımsız verifier'a kanıt devri | V015.G07 | V015.G05 |
| IS05 | İcracı sorumluluk | Açık durum/kaynak eşliği | V015.G01 | V015.G07 |
| IY01 | İcracı yetenek | Swift/Python kod çözümleme ve onarım | V015.G06 | V015.G05 |
| IY02 | İcracı yetenek | SQLite ve kurtarma becerisi | V015.G04 | — |
| IY03 | İcracı yetenek | Git worktree/commit/branch kanıtı | V015.G05 | V015.G01 |
| IY04 | İcracı yetenek | Test/regresyon ve hata analizi | V015.G06 | V015.G07 |
| IY05 | İcracı yetenek | Geri alma ve güvenli durma | V015.G05 | V015.G09 |
| TU01 | Teknik altyapı ve ekran | Ulak, görev durumunu SQLite/tek hakikat kaydından sürümlenmiş IPC snapshot'ıyla okur; model metnini doğrudan statü olarak sunmaz. | V015.G08 | V015.G09 |
| TU02 | Teknik altyapı ve ekran | Yüzde, kilitli 10000 baz puanlı blok planında yalnız bağımsız doğrulanmış PASS ile artar. | V015.G07 | V015.G09 |
| TU03 | Teknik altyapı ve ekran | Bağlantı/süreç kesintisi ve yeniden bağlanmada ekran aynı görev/plan sürümünü gösterir. | V015.G09 | V015.G04 |
| TU04 | Teknik altyapı ve ekran | `HOLD/BLOCKED/RECOVERING/AWAITING_OWNER` durumları ayrı ve anlaşılır görünür; kanıt yokken DONE görünmez. | V015.G09 | V015.G08 |
| TU05 | Teknik altyapı ve ekran | `Kanıtları Gör` eylemi gerçek kaynak/test/DoneCheck referanslarını açar; gizli bilgiler maskelenir. | V015.G07 | V015.G09 |
| KU01 | Ekran sadeliği ve kolaylık | Açılışta tek sohbet kutusu, kanıtlı yüzde, aktif iş, kuyruk ve DoneCheck okunur. | V015.G09 | V015.G08 |
| KU02 | Ekran sadeliği ve kolaylık | Duraklat/Devam Et/Güvenli Durdur bağlama göre doğru etkinleşir; riskli hareket açıklaması vardır. | V015.G09 | V015.G04 |
| KU03 | Ekran sadeliği ve kolaylık | Terminal gerektirmeyen normal kullanım; hata mesajları anlaşılır Türkçe ve tek sonraki hareket içerir. | V015.G09 | V015.G05 |
| KU04 | Ekran sadeliği ve kolaylık | Klavye erişimi, VoiceOver etiketleri, dinamik yazı ve azaltılmış hareket desteklenir. | V015.G09 | V015.G08 |
| KU05 | Ekran sadeliği ve kolaylık | Teknik ayrıntılar isteğe bağlıdır; günlük kullanıcıya gereksiz karar/onay yükü çıkarılmaz. | V015.G09 | V015.G03 |
| YR01 | Ekran yerleşimi | Üst çubukta ürün/bağlantı/görev durumu; ilk görünür alan kanıtlı ilerleme kartıdır. | V015.G09 | V015.G08 |
| YR02 | Ekran yerleşimi | Aktif blok, kanıtlı yüzde, kalan yüzde ve durum aynı bakışta görülür. | V015.G09 | V015.G07 |
| YR03 | Ekran yerleşimi | Kuyruk tek satırda özetlenir; açılır detay vardır, kalıcı geniş panel kullanılmaz. | V015.G09 | V015.G04 |
| YR04 | Ekran yerleşimi | Sohbet alanı ana alan olarak kalır; yazma alanı her durumda kolay erişilir. | V015.G09 | V015.G08 |
| YR05 | Ekran yerleşimi | Standart/küçük Mac pencere, yüksek yazı ölçeği ve uzun Türkçe metinde taşma olmaz. | V015.G09 | V015.G08 |
| VG01 | Görsel estetik | Premium, minimal Mac-native kimlik; Engürü koyu yeşili ve ölçülü cam katmanları. | V015.G09 | V015.G08 |
| VG02 | Görsel estetik | Güçlü tipografik hiyerarşi: sonuç > aktif iş > kuyruk; gösteriş amaçlı dikkat dağıtıcı bileşen yok. | V015.G09 | V015.G08 |
| VG03 | Görsel estetik | Baykuş amblemi kontrollü ölçekte ve hakları doğrulanmış varlıkla kullanılır. | V015.G09 | V015.G03 |
| VG04 | Görsel estetik | Metin için hedef kontrast en az 4.5:1, ilgili büyük metin ve bileşenler için erişilebilirlik kuralları; yalnız renge bağımlı durum gösterimi yok. | V015.G09 | V015.G08 |
| VG05 | Görsel estetik | Animasyon yalnız anlamlı geçişlerde, azaltılmış hareket tercihiyle uyumlu; kullanıcı/owner gerçek ekranı beğeni ve işlev açısından onaylar. | V015.G09 | V015.G08 |
| YD01 | Yaratıcı deneyim | Durum mesajları yalnız doğrulanmış olay kaydıyla değişir; model metni statüyü belirlemez. | V015.G07 | V015.G09 |
| YD02 | Yaratıcı deneyim | Durum değişimi hafif ve anlamlı animasyonlarla sunulur; azaltılmış hareket seçeneği desteklenir. | V015.G09 | V015.G08 |
| YD03 | Yaratıcı deneyim | Yönetici, İcracı ve Ulak aynı ekranda ayrı renk zorunluluğu olmaksızın tanınır. | V015.G08 | V015.G09 |
| YD04 | Yaratıcı deneyim | HOLD/BLOCKED/RECOVERING bilgilendirmeleri olumlu, kesin Türkçe ve tek somut hareket içerir. | V015.G09 | V015.G07 |
| YD05 | Yaratıcı deneyim | Premium sakin deneyim ve gerçek kullanıcı başarı ölçütleri owner tarafından görünür önizlemede kabul edilir. | V015.G09 | V015.G08 |

## 6. Kabul kapısı ve test/kanıt türlerinin ayrımı

| Değerlendirme | Mevcut durum ve kapsam |
|---|---|
| Özgün sözleşme kaynak kimliği | **PASS — 75/75 özgün ID metni bire bir; SHA eşliği** |
| V015 9-kapı eşleme bütünlüğü | **PASS — 75/75 ID birincil olarak tam bir kez eşlendi; bu yalnız statik belge denetimi** |
| 34 owner kararının kanonik imzalı sicili | **HOLD — kaynak eşleme belgesi taslak; owner canonical imza/yetki makbuzu yok** |
| 51 V014 mühendislik testi | **Tarihsel 51/51 Linux fixture PASS; üretime entegre çekirdek testi değildir** |
| 34 V013 toplayıcı regresyonu | **Tarihsel 34/34 PASS; gerçek Ulak entegrasyonu değildir** |
| V014.MAC rol sınavı | **40/40 gerçek model yanıtı; 13/20 karşıt etiket; profesyonel kabul HOLD** |
| 15 alan / 75 kurulum öncesi kabul | **0/75 kanıtlı kabul / HOLD (eski defterin kaynak durumu korunur)** |
| V015 9 mühendislik kapısının teknik kabulü | **0/9 / HOLD — icra başlamadı** |
| Mac uygulaması / owner saha kabulü | **NOT_TESTED — kurulum HOLD** |
| DoneCheck™ / Verified Finish | **HOLD** |

## 7. Kaynak/çıktı devri ve önerilen sonraki yetkili adım

**Yeni mühendislik bloğu henüz açılmadı.** Owner’ın uygun görmesi hâlinde bir sonraki iş: bu V0.1 eşlemeyi ve arayüz sözleşmesini gerçek GitHub kaynaklarına ekleyip bağımsız testlerle doğrulamak; 34 karar sicili ile çatışma incelemesi; sonra sıralı V015 çekirdek icrası. Mac kurulum/yayın/merge/ödeme/silme ayrı insan eşiğidir.

**Bitiş notu:** `DOCUMENT_CROSSWALK_VALIDATED / OWNER_CANONICAL_FINAL_HOLD / ENGINEERING_NOT_STARTED / MAC_FIELD_NOT_TESTED / VERIFIED_FINISH_HOLD`.

**Niyet → Çekirdek Üretim → Gerçek İş → Kanıt → Etki.**
