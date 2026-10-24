# ENGÜRÜ GitHub → OSi Tek Geçiş İcra Sistemi™ V2 — Teorik Final Sözleşmesi
STATE=DESIGN_REVIEW; OSI_MUTATION=0; OFFICIAL_G2_G6=HOLD

## Kalıcı hedef
Mevcut ENGÜRÜ Yönetim İCRA ve Mühendis İCRA iki kolunu koruyarak bir ürünün hedef, gerçek OSi salt-okunur envanteri, tersine mimarlığı, simülasyonu, derlemesi, paketlemesi, geri dönüşü, tek-komut devir ve yetkili saha kabulünü kanıtla yönetmek. Yeni üçüncü icra motoru oluşturulmaz.

## Uçtan uca özgün kapılar
T00 ürün niyetini/kapsamını ve özgün acceptance ID'lerini, gerçek müşteri beklentisini sabitle.
T01 OSi envanteri yalnız sahibinin yetkili salt-okunur kanalıyla, kaynak ID, zaman, nonce, izin, hash ve geçerlilik süresi ile alınır; sırlar ve özel içerikler git deposuna alınmaz.
T02 envanter + ürün contract kaynak sürümünü eşleştir; stale / unknown / drift → HOLD.
T03 mevcut çalışan üründen geriye: sağlık testi → dosyalar ve izinler → bağımlılıklar → OS/CPU → disk → imza/notarization gereği → reproducible build → kaynak commit.
T04 dependency DAG, sürüm kilidi, SBOM/lisans, tedarik zinciri, güvenlik; cycle/unknown/unsafe HOLD.
T05 üretici ile bağımsız reviewer ayrı; yönetim task ID ↔ mühendis output ID, source SHA, rollback, executor scope ve handoff receipt gerekir.
T06 kaynak üzerinde gerçek test + negatif test + macOS runner build; bu gerçek Mac OSi saha kanıtı sayılmaz.
T07 izolasyonda kurulum testleri: path traversal, symlink, TOCTOU, concurrency lock, crash recovery, atomic stage, restore prior, idempotency, disk failure, corrupt payload, revoked grant.
T08 deterministic signed-or-verified package manifest: source commit, artifact SHA256, inventory pin, version, origin, targets, dependencies, rollback, health, expected evidence, TTL.
T09 her kod değişimi sonrası HEAD sabitle; aynı exact HEAD için üç ayrı gerçek GitHub CI run ID ve sonuç PASS; simülatör içinde üç tur ayrıca ve ayrı rapor.
T10 bağımsız review + yetkili GitHub merge; varsa gerekli owner Human Threshold. CI, gerçek imza ya da saha otoritesi oluşturmaz.
T11 yalnız sonradan OSi'de güncel envanter teyidi, exact artifact pin, tek komut authorized installer, transaction journal, live health check, rollback.
T12 DoneCheck v1.2, bağımsız doğrulama ve Human Threshold ile resmi Verified Finish.

## Fail-closed
Bir T kontrolüne kanıt gerekip kanıt yoksa HOLD; NOT_EXECUTED gerçek PASS değildir. Tek bir fail resmi BITTI_DUR'u engeller. Yanlış reviewer, exact HEAD drift, manifest drift, eski envanter, eksik owner, kısmi test, sahte run ID, mevcut dosya çakışması ayrı HOLD.
Yöntem kendi içinde tasarım testlerinin tümünü geçerse DESIGN_THEORETICAL_100/100 verilebilir; gerçek teslim, T10-T12 ve resmi G2-G6 ayrı HOLD kalır.
Her düzeltme, yeni commit olduğunda üç gerçek CI run hesabını sıfırlar.

## Kullanım rahatlığı
Kullanıcıya üç giriş: PRODUCT_GOAL, OWNER_APPROVED_INVENTORY_REFERENCE, APPROVAL_SCOPE.
Motor çıktısı: STATE, toplam özgün PASS/HOLD, tek kritik engel, tek gerekli insan hareketi, bundle SHA, exact commit, next action. Tek komut yalnız gerçek paket üretildiğinde ve hash teyidinde verilir. Kısa mod varsayılan, ayrıntılı audit isteğe bağlıdır.

## Teorik 100/100 yedi ölçüt
Her kategori 10 maddelik kontrolle değerlendirilir. 100 yalnız tüm kontrol id'leri PASS olduğunda; modelin tamamı 70/70 PASS gerekir.
A mimarlık: canonical kimlik, özgün ID, iki rol, bağımlılıklar, ters mimarlık, envanter, sürüm, yetki, risk, kapanış.
B iş yeteneği: görev çözümleme, uygulanabilirlik, plan, DAG, gerçek kod, build, test, kanıt, devir, sürdürme.
C finiş: kaynak pin, envanter pin, üç CI, artifact, SHA, installer gate, rollback, health, DoneCheck, owner.
D rahatlık: üç giriş, tek karar, az müdahale, kısa rapor, anlaşılır hata, devamlılık, tekrar kullanım, arşiv, kullanıcı izni, izlenebilirlik.
E akış: T00-T12 tamlık, ileri bağımlılık, tüm dallarda duruş, retry, drift geri dönüş, tek paket, devir, idempotency, terminal kapanış, ilerleme.
F güvenlik: least privilege, source SHA, manifest SHA, TTL, symlink, path, TOCTOU, secret protection, reviewer ayrımı, audit.
G kurulum hazırlığı: OS, arch, space, deps, version, destination, backup, preflight, atomic rollout, health/rollback.
Bu 70 tasarım maddesinin onayı metin varlığına değil, executable formal invariant test ve karşıt senaryo sonuçlarına bağlıdır. Eksik gerçek saha kanıtı teorik tasarım puanından ayrı tutulur.

## Kanıt kapısı
THEORY_100_100 ancak tam formal kabul rubriği test edildikten sonra. Üçlü düşünsel simülasyon ayrı; gerçek CI 3 run ayrı; Mac OSi kurulumu ayrı. Bu belge teorik final sözleşmesi adayıdır.
