# ENGÜRÜ Köprü V5 — Yetkili CI köküne bağlı tarihsel düzeltme kanıtı

**Kapsam:** Çalışan Mac V5 kurulumunu koruyarak tek gerçek tarihsel V4 sessiz aktivasyon hatasının kaynak düzeyindeki düzeltmesini bağımsız GitHub CI üzerinden yeniden doğrulamak.

- Kanıtın sabit GitHub commit'i: `80b2ca7fde92ec74c3e08229ac179ff8f5c27a3b`, kaynak inceleme PR #218.
- Bağımsız CI: run `40116582389` (push), `40116627850` (pull_request), `40116627848` (IP Fleet).
- Her run için `head_sha`, owner actor, repo, event, workflow yolu ve completed/success canlı GitHub REST yanıtıyla kontrol edilir.
- Gerçek regresyonun job tamamlanma ve başarı durumu kontrol edilir. GitHub API adım ayrıntısı eksik dönerse tam adım görünürlüğü iddia edilmez; kaynakta SHA-256 kilitli workflow ve test dosyaları ayrıca karşılaştırılır.
- Tarihsel V4 girişinde komut yönlendirme `0/1`; onarılmış V4.1 girişinde `1/1` (geçici sentetik ZIP ve sahte işleyici regresyon sınaması).

## Sınır ve gerçek bitiş

Bu çalışma `PASS_AUTHENTICATED_GITHUB_CI_SOURCE_LEVEL` üretebilir. **Tek düzeltme vakası**, Mac üzerindeki V5 öğrenme defterinde gerçek farklı vakaların kanıtla onaylanması anlamına gelmez. V5 mevcut `promote` callback'ine gerçek yetkili doğrulayıcı bağlanması; üç veya daha fazla ayrı **gerçek** düzeltme vakasında öncesi/sonrası ve tekrarlama ölçümleri; PR #217 güncel SHA CI; canonical owner, Human Threshold™ ve DoneCheck™ kabulü ayrıca açıktır.

`main`, Yönetim ve İcra motorları, Mac V5 SQLite, imzalar ve ürün dosyaları değişmeden korunur. İnceleme dalında yalnız CI sınaması ve belge yazımı vardır.

**Karar kapıları:** `SINGLE_REAL_CASE_SOURCE_FIX=PASS` → `AUTHENTICATED_CI_PROOF=PENDING` → `MULTI_CASE_VERIFIED_LEARNING=HOLD` → `OFFICIAL_VERIFIED_FINISH=HOLD`.
