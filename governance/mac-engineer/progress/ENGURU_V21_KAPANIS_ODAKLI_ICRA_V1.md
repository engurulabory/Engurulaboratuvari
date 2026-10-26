# ENGÜRÜ Yönetim → İCRA V21 | Kapanış odaklı bütünleşik yürütme

**V20 kaynak doğrulaması:** Gerçek Mac raporu `ENGURU_V20_F01_F05_FIELD_20261021T151555209916Z.json` SHA-256 `1a99a53669ce831e9431790b11983eade4206cbb8c7a3bf1263bebc07edf9f3a`, bağımsız dosya baytları üzerinden PASS. `EXIT_CODE=0`, izole Git/7 karşıt test PASS. **Tekil yeni kontrol PASS=0; Yönetim sayacı 22/100.** Resmî 0/12, tam engel kapanışı 0/6.

## V21 bağlayıcı hedef — 30/100

**Yönetim emri:** Kanıtlı başlangıç **22/100**; aynı İCRA turunun ölçülebilir hedefi **30/100**, yani **+8 farklı, kabul şartı karşılanmış kontrol**. 30 sayısı geçerli kazanımdır, test PASS varsayımı değildir. 30'a erken ulaşılırsa kalan izinli bağımlı işler de tamamlanır.

**İCRA uygulaması:** 100 maddelik Yönetim JSON içindeki HOLD kriterlerini önce kanıt/bağımlılık/yetki durumuna göre tek bütünleşik planla sırala; F01 ana ve F05 bağımsız destek içinde tamamlanabilir gerçek mühendislik farklarını uygula, regresyon ve tam kanıtla sonuçlandır. Her tamamlanan alt işin sonunda planı yeniden değerlendir; **ilk PASS veya salt-okuma raporuyla işi kapatma**. Hedefe ulaşmak için yeni kontrol üretme, kriteri gevşetme, önceki PASS'i tekrar sayma veya Human Threshold™ sonucunu varsayma. 30/100'ün altında bitiş yalnız kesin, kanıtlı kaynak/yetki engeli ve yapılabilir diğer işlerin tamamlanmasıyla `GÜVENLİ_DUR` olarak raporlanır.

**Sekiz kontrolün kanıtı:** Her `Bxx-yy` özgün ID, önceki `HOLD` durumu, yeni yerel Mac/CI receipt SHA-256, karşıt test ve mevcut resmî yetki kapısı ile eşleşir. Kaynak sahibi kararını gerektiren kontroller karar gerçekleşince PASS alır; hazırlık adımı resmî kabul üretmez.

**Sonuç:** `SAYAÇ=22/100→N/100; HEDEF=30/100; FARK=30-N`. `N` yalnız sahada gerçek kanıtlanan ve Yönetimce kabul edilen kontrol sayısıdır; sayaç güncellemesi ayrı Yönetim kararıdır.

## V20 → V21 düzeltici Yönetim hükmü

**Gözlem:** V20 7/7 karşıt test, gerçek Mac ve izole Git PASS üretti; fakat kabul edilmiş yeni 100-kontrol ID'si **0**. Bu, tekrar teşhisini bitirip somut kapanış üretmeye yönelme ihtiyacını gösterir. `+10` performans hedefi, owner/reviewer Human Threshold ve canonical kaynak kabulünün yerine geçmez.

**V21 somut teslim kapısı:**
1. **F05 tamamlanabilir mühendislik farkı:** Mevcut V16 patch + PR #14 Native dört dosya farkı + aktif 0.8/PR 0.6 sürüm ve ikon kaynak kapsamını **izole geçici kaynakta** birleştirilebilir inceleme adayı olarak hazırla. Gerçek patch/diff, exact input-output SHA, 2 dirty yol/185 commit preservation ve kapsamlı regresyon receipt ile sun. Canonical yazım, sürüm ilanı, ikon lisansı ve imza yalnız yetkili owner kararından sonra.
2. **F01 tek gerçek karar:** Var olan V13 A/B yetki yolunu, mevcut owner/reviewer ve Ed25519 authorization kaynakları üzerinden kesinleştir. Bulunan yetkili kaynağı test/adapter bağına bağla; gerçek yetki boşluğu kalırsa sahibine sunulacak **tek karar dosyası** hazırla: A/B, owner-source/path, reviewer key authorization, CRITERIA_SET_SHA ve kalan gerekli receipt alanları. Yetkili insan onayı yalnız onay sahibinden gelir.
3. **Yürütme bitiş eşiği:** Yapılabilir güvenli onarım/entegrasyon/simülasyon zinciri tamamlanınca ölçülen 100-kontrol ID'lerini kanıtıyla sun. İnsan kararı tek engelse `GÜVENLİ_DUR` + tam karar paketi; aynı SHA/aynı testlerle tekrar keşif yeni İCRA turunun hedefi değildir. Bir sonraki emir somut yetki/owner yanıtı veya yeni kanıt getirmeli.

**Performans ölçütü:** Kapanan doğrulanmış kontrol sayısı; somut hazır kaynak farkı ve tek karara indirgenmiş yetki ihtiyacı. Gözlem ve tekrar test, kabul kriterini karşılamadıkça ek ✓ üretmez.

**Kalıcı sabit hedef:** H1 4/4 → H2 4/4 → H3 4/4 → Native OSi → Verified Finish → `BITTI_DUR`.

**Ana iş F01 — gerçek otorite kararı:** Mevcut V13 Human Threshold™ 12-kriter önerisini ve canonical DoneCheck Authority Model yerel blob `a37c2fbb...` ↔ origin/main `a3fa94c6...` farkını, exact kaynak/commit/blob ve satır bazında incele. Farkın gerçek yetki/kapsam sonucunu belirle. Yetkili owner/reviewer kaynağı ve Ed25519 reviewer key yetkilendirmesi bulunursa 12 kriter SHA, Mac → Progress Core™ → Mandatory DoneCheck JSON → `verifyTask` yolundaki yapılabilir yetkili testleri tamamla. Yetki boşluğu kanıtlanırsa mevcut V13 dar kapsamlı kararı **tek Human Threshold™ incelemesine** yetki sahibi ve eksik alanlarıyla sun. Hakiki imza/attestation/receipt öncesi resmî 0/12 korunur.

**Bağımsız destek F05 — aktif Native ürün korunarak kaynak kabulü:** V20 kanıtı: çalışan iki uygulama Bundle `com.engurumaya.macengineer`, sürüm `0.8` ve aynı Info.plist/icns SHA; PR #14 `Info.plist` sürüm `0.6`, beklenen `.icns` kaynak Git nesnesi yok. Mevcut 185 yerel commit ve 2 tracked dirty path korunur; V16 patch'in exact SHA ve dört native dosya farkı izole olarak çalışılmış mevcut kanıttan başlanır. `0.6` kaynak kimliğinin tarihsel v0.6 kilitli kabul ile ilişkisi ve çalışan `0.8` sürümünün yetkili ürün kimliği **ayrı** doğrulanır. Uyum kararı olmadan sürüm düşürme veya .icns kopyalamaya geçilmez. İkon adayının kaynak hakları/lisans, SHA, Git provenance ve owner'ı kanıtlanır. Yetkili source review'a tek uygulanabilir fark/çakışma planı + regresyon receipt sunulur. Canonical promotion/merge, signing/install/live smoke yalnız kendi onay kapısında yürütülür.

**Yürütme:** Bir ana F01 + bir bağımsız F05. Aynı turda bütün gerçekten erişilebilir güvenli alt bağımlılıkları topluca tamamla; eski PASS testlerini ikinci kez sayaçta kullanma; plan-only ve CI doğrulaması gerçek ürün kabulü değildir. V21 ölçülebilir hedef **30/100** (22→30, +8); daha fazla yapılabilir kanıtlı kontrol uygun olduğunda devam, **erken durma kotası yok**. Kanıt/yetki sınırında `GÜVENLİ_DUR`, tek karar sahibini ve eksik kesin kanıtı bildir.

**Teslim:** ZIP gerçekten gerekiyorsa A) verified ZIP bağlantısı/ad/SHA, B) tek bütün ve doğrudan kopyalanabilir `zsh` Terminal bloğu (dosya/SHA/symlink kontrolleri, AudiV13), C) 6 satırlık sonuç. ZIP gerekmiyorsa yalnız altı satırlık rapor.

**Altı satır:** `STATE` · `SAYAÇ=22/100→...` · `YENİ_PASS` · `F01` · `F05` · `RESMÎ=...; RAPOR_SHA256=...; SONRAKİ=...`.
