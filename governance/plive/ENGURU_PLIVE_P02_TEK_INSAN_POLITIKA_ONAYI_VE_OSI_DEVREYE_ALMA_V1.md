# ENGÜRÜ PLive P02 — Tek İnsan Sahipli Güven Politikası Onayı ve OSi Devir Protokolü V1

**Durum:** `OWNER_EXPLICITLY_APPROVED_POLICY__G3_GRANT_WRITER_STILL_HOLD`  
**Kapsam:** yalnız bir Mac, kullanıcı sahibi, `ENGURU_PLIVE_P02_USER_SCREEN`, ilk yetkili item `P02.S01.01`.  
**Tarih:** 19 Ekim 2026. Kullanıcı sohbetinde açık onay vermiştir; bu metin **yerel kimlik doğrulaması veya imzalı G3 grant'i değildir**.

## Onaylanan kaynak

- Tek insan sahipli politika metni: `governance/plive/ENGURU_PLIVE_P02_TEK_INSAN_GUVEN_G3_POLITIKASI_V1_ADAY.md`
- Değişmez onaylanan politika commit'i: `49ac971ef1090722ed75c1047bb07c413e5d39fc`
- Git blob SHA-1: `fff572f77ec9524a70367a4b3fe0bce2e74f8f6b`; Mac tesliminde ayrıca yerel SHA-256 hesaplanır.
- Kullanıcının kararının kapsamı: yerel tek Mac ve mevcut güvenlik sınırları için politika kabulü; **kendi başına issuer, signed grant, production writer, P02 countedPass veya Verified Finish değil**.

## Önce sözleşme uyumu

OSi'nin mevcut `PLIVE_P02_WORK_CONTRACT_V1.json` sözleşmesinde `workId=ENGURU_PLIVE_P02_USER_SCREEN`, `humanThresholdRequired=true`, `STATE_HEAD_PLUS_PACKAGE_DONECHECK` ve dört kanıt zorunluluğu korunur. P01 `2/2 VERIFIED`, P02 `0/12 HOLD`, yedi canonical SHA pini, HEAD ve kirli iş ağacı yeniden okunur.

PLive'ın onaylanmış insan hedefi zaten `ONE_HUMAN_OWNER_HUMAN_THRESHOLD`. Mevcut Security & Authority semantic review kuralları, makine PASS'inin geri alınamaz yetkili eyleme izin veremeyeceğini söyler. Mevcut daha yüksek yetki sözleşmesi **açıkça farklı ikinci bir insan** gerektiriyorsa politika bu şartı tek başına geçersiz kılamaz; `HOLD_UPPER_POLICY_CONFLICT` ve ayrı kayıt değişikliği gerekir.

## OSi'ye tek kontrollü teslim

**Tek yerel Python aracı:** `ENGURU_PLIVE_P02_ONAYLI_GUVEN_POLITIKASI_OSI_V1.py`  
**SHA-256:** `51a9ea2f732065b9185704604b812b4422469c145e34a8d2a6a76d198b3bf7c5`  
**Komut:** `python3 -B ~/Downloads/ENGURU_PLIVE_P02_ONAYLI_GUVEN_POLITIKASI_OSI_V1.py --run`

Bu program 23/23 offline karşıt test, yedi canonical SHA-256, exact HEAD ve Work Contract semantiği, tek kullanıcı kararının metni ve immutable GitHub blob SHA-1 denetimi yapar; varsa yerel üst güvenlik sözleşmelerinin sınırlı çelişki denetimini uygular. İnternet gerektiriyorsa yalnız GitHub commit-pinned **politika metnini** indirir; gerekirse aynı blob doğrulamasıyla `~/Downloads/ENGURU_PLIVE_P02_TEK_INSAN_GUVEN_G3_POLITIKASI_V1_ADAY.md` dosyasını okuyabilir. Kişisel anahtar almaz ve GitHub'a sır göndermez.

Uyum doğrulanırsa yalnız iki **yeni** dosya kaydeder:
- `governance/plive-p02-user-screen/ENGURU_PLIVE_P02_TEK_INSAN_GUVEN_G3_POLITIKASI_V1.md`: doğrulanmış politika metni;
- `governance/plive-p02-user-screen/ENGURU_PLIVE_P02_TEK_INSAN_POLITIKA_KARARI_V1.json`: kullanıcı sohbet kararının kayıt makbuzu ve gerçek kimlik doğrulama sınırı.

Mevcut herhangi bir dosyanın üzerine yazılmaz. Native P01/P02 state, registry, P06, Mac App ve AudiV13 orijinalleri korunur. İki yeni governance kaydı dışında canonical yazım **0**; yeni iki metadata kaydı açıkça sayılır. AudiV13'e olay raporu, Masaüstüne doğrulanmış aynı SHA-256 kopya. Çelişki/kaynak değişimi/önceden var olan kayıt ⇒ **HOLD**, otomatik tekrar, overwrite veya grant yok.

**G3 mühendislik devamı:** Politika kaydı gerçekleştiğinde yalnız `G3-A / insan politika kararı` kapanabilir; gerçek cihaz kimliği/issuer güven kökü, Keychain `-34018` saha sınırı, değişmez grant, durable canonical writer, OS çökme/yineleme ve bağımsız teknik denetim **henüz çalışılacak gerçek farktır**. Var olan V3 48/48 izolasyon testleri yeniden kullanılır, yeni core veya paralel sayaç kurulmaz. Bağımsız teknik denetçi yerine ikinci insan varmış gibi beyan yapılmaz.

**Kritik ayrım:** Chat onayı = politika kararı; yerel policy receipt = karar kökeninin kayıt altına alınması; gerçek kimlik doğrulaması ve G3 issuer/grant/writer = ayrı, kaynağa dayalı yetki; P02 Verified Finish = 12/12 + 4/4 + 7/7 + insan + native verified.

**Finiş hedefi sabit:** ENGÜRÜ Süzgeci™ v2.4 mevcut sekiz aşamada; biten işi koru → gerçek eksik farkı tamamla → kanıtla → ilerlet → ürün verified olduğunda **BİTTİ → DUR**.
