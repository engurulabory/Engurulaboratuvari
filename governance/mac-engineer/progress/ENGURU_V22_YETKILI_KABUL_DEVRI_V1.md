# ENGÜRÜ Yönetim — V22 Yetkili Kabul ve Kaynak İnceleme Devri

**Tarih:** 21.10.2026 · **Durum:** `PASS_V22_ISOLATED_ENGINEERING / GÜVENLİ_DUR_AUTHORITY` · **Sayaç:** 22/100 (Hedef 30/100, kalan 8). Resmî H1/H2/H3 0/12; F01–F06 kapanan 0/6; Verified Finish HOLD.

**Gerçek Mac raporu:** `ENGURU_V22_F01_F05_FIELD_20261021T163553301614Z.json`, SHA-256 `80a8a7f9d4f2f27c2274a823fffaa442cd65331378f4ed2d227bcf31f8b5c745`; dosya baytları Yönetim incelemesinde bağımsız doğrulandı. İlgili GitHub kaynak PR'leri: [Yönetim #191](https://github.com/engurulabory/Engurulaboratuvari/pull/191) ve [Engineer #14](https://github.com/engurulabory/enguru-mac-engineer/pull/14).

## F01 — tek kapsamlı Human Threshold™ insan kararı

**Karar dosyası:** `F01_TEK_HUMAN_THRESHOLD_KARARI_V22.md` · V22 raporunda bildirilmiş SHA-256 `666c73f2ac30b912f23735a78d0191bd2905a11d7d7f8cb960e1255c02f7c67c`. Bu dosyanın gerçek baytları Yönetim oturumuna sağlanmadı; hash rapordaki manifest değeridir.

**Tek karar sorusu:** H1/H2/H3 4+4+4 için var olan canonical yetkili 12-kriter sözleşmesinin tam kaynak/branch/commit/blob, `OWNER_ID` ve yetkili Ed25519 reviewer kaydı hangi kaynakta? Bulunursa **A** mevcut sözleşmeye bağlama; gerçek ve kanıtlanmış boşluk varsa **B** mevcut V13 dar kapsam adayı için yetkili insan kararı ve durable receipt.

**Kararı verecek:** Gerçek canonical kaynakta yetkisi ispatlanan owner ve kapsam için yetkilendirilmiş reviewer. PR yazarı, GitHub CI, sohbet veya Yönetim notu tek başına bu yetkiyi vermez. H1 Secure Enclave P-256 ile DoneCheck Ed25519 ayrı kapsamdır.

**Kararın tamamlanmış kanıtı:** `OWNER_ID`, `OWNER_AUTHORITY_SOURCE`, `REVIEWER_ID`, `REVIEWER_KEY_AUTHORIZATION`, `CRITERIA_SET_SHA` (V22 aday kriter SHA `208a32c7a8b93204c6b9a414086c8d43bf9216b22c7ccbf53ef5dac09cde9ada` henüz resmî değil), `BRANCH_COMMIT_BLOB`, `MAC_PROGRESS_DONECHECK_BINDING`, `VERIFYTASK_RESULT`, `HUMAN_REVIEW_RECEIPT`.

**Sınırlı izin:** F01 yetkisi kanıtlanınca yetkili Mac → Progress Core™ → Mandatory DoneCheck JSON → `verifyTask` adapter kabulü gerçek test/receipt ile ilerler. H1/H2/H3 0/12, yetkili kabul gelene kadar korunur.

## F05 — çalışan Native 0.8'in owner source review kapısı

**İzole onarım:** `F05_V22_PR14_TO_V08_UNIFIED_REVIEW.patch` · V22 raporunda bildirilen SHA-256 `7b2b8b44a2a07d5e4c4ed32c109a0e38066361220181a58b0f5e8a5afa75ebf3`, boyut 15.020 bayt. Patch gerçek dosya baytları bu Yönetim oturumunda erişilebilir değil; henüz GitHub PR #14 source diff'ine aktarılmış değildir.

**İnceleme tabanı:** V22 raporundaki PR #14 HEAD `e67203e6229a175c852dffb990a8666de3a3332d`, yerel HEAD `26925c21c7816a90edc0eb047382aba8c696764c`; reviewer işlemi anında güncel HEAD ile SHA mutabakatı yeniden doğrulanır.

**İzole teknik kabul:** Dört native kaynak dosyası, Swift kaynak SHA `4864834bebadce99f606860a336e616837111c66e96ec807c50eba2f33e1b27f`, gerçek SDK build RC=0, binary SHA `1d7fc13b7b61370d1c9a10966c1220ff0ebeb5a69614afdbbc7e87f93f6d5973`. Restart/eşzamanlı/kapanış korumaları kaynak byte kimliğiyle korunmuş; canlı davranış regresyonu `HOLD`. 3 negatif derleme senaryosu `PASS_FAIL_CLOSED`.

**Owner review kararı:** Patch'in gerçek dosya baytları ve SHA eşlenerek kaynak sahibinin erişebileceği yetkili inceleme yüzeyine alınır; dört dosyada diffin semantiği, 0.8 sürüm kimliği, yaşam döngüsü test matrisi, ikon lisansı ve Git blob provenance kararına bağlanır. `.icns` lisansı, exact kaynak owner review ve canonical source promotion ayrı kapanış kapılarıdır. Yerel 185 commit, 2 dirty dosya, çalışan uygulama, tarihsel v0.6 lock korunur.

## Yönetim ilerleme ve V23 yürütme sınırı

V22'de yeni 100 kontrol PASS **0**. `B02-05/06/07/08`, `B06-07/08/09`, `B07-07` özgün kabul şartını henüz karşılamıyor. Mühendislik hazırlık sonucu teknikte PASS olsa da sayaç **22/100** sabittir. 30/100 hedefi korunur; yalnız yeni ve kanıtlı özgün PASS ID kabul edilir.

**Öncelik:** Gerçek yetkili F01 insan kararı; F05 review patch'in yetkili source review'a erişimi ve canlı Native regresyon planı. Bu kararlar verildiğinde mühendis, güvenli bütün bağımlılıkları aynı turda tamamlar. İnsan veya source review sonuçlanıncaya kadar aynı izole build/teşhis turu tekrarından yeni kabul puanı türetilemez.

**Sonraki kesin kapı:** `HOLD_AUTHORIZED_OWNER_REVIEWER_DECISION_AND_NATIVE_SOURCE_REVIEW`. GitHub PR üzerinde inceleme isteği, yetkili Human Threshold™ kabul receipt'i yerine geçmez.
