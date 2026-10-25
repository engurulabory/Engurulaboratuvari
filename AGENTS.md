# ENGÜRÜ — Ortak İCRA Başlangıcı

Bu depo ENGÜRÜ ürün, proje ve iş oturumlarının ortak çalışma talimatının **tek kaynak adresidir**.

## 1. Evrensel kanıtlı tamamlama

Önce [ENGÜRÜ Evrensel Kanıtlı Tamamlama Talimatı™ V3](governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_TALIMATI_V3.md) metnini oku. Sonra [SHA-256 kilit kaydı](governance/enguru-suzgeci/ENGURU_EVRENSEL_KANITLI_TAMAMLAMA_V3_LOCK.json) ile kaynak bütünlüğünü doğrula. V3 **bütün ENGÜRÜ İCRA oturumlarının genel çalışma disiplini**; ürünün kendi yetkili canonical sözleşmesi ve insan onayları önceliklidir.

## Kalıcı sekiz aşamalı disiplin ve Pozitif Dil Evreni

**Her ENGÜRÜ oturumunda bağlayıcı çalışma referansı:** [ENGÜRÜ Kalıcı Çalışma Disiplini™ V1](governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1.md) — `governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1.md`; [SHA-256 kilidi](governance/enguru-suzgeci/ENGURU_KALICI_CALISMA_DISIPLINI_V1_LOCK.json). CI baytları ve sekiz sıralı aşamayı doğrular.

**Hakikati gör → Değeri koru → Eksikleri ve ihtiyaçları tespit et → Gerekli farkı üret → Eksikleri tamamla → Kanıtla → Sonraki ihtiyaçları belirle → İlerlet.**

**Kalıcı sabit hedef:** Eksikleri tamamlanmış. Uçtan uca tam bitmiş. Gerçek testlerle kanıtlanmış. Yetkili kabulü alınmış.

Bu yöntem, mevcut canonical V3 ile özgün ürün kabul şartlarını birlikte korur. Kurulum, gerçek ürün PASS'i ve Human Threshold kendi kanıtlı yetki sınırında ilerler.

## 2. Tek ortak yöntem

- **Tek ana hedef, bütünleşik yürütme, aynı turda erişilebilir eksikleri tamamlama.**
- Mevcut yetkili kaynakları, kullanıcı kararlarını, kodu, araçları ve kanıtları koru.
- Başarı şartlarını özgün ID ve ayrı icra/kanıt/yetki kapılarıyla belirle.
- Ön simülasyonu gerçek test ve bağımsız doğrulamadan ayır.
- Gerekli gerçek kanıtla karşılanan özgün kontrolleri topluca kabule sun; her ID bağımsız değerlendirilir.
- `VERIFIED_FINISH → BITTI_DUR` yalnız bütün zorunlu şartlar ve gerçek yetkili kararlar PASS olduğunda.
- Engel varsa `GÜVENLİ_DUR` + korunmuş gerçek işler + kesin engel ve sonraki kapanış şartı.

## 3. Kaynak ve oturum sınırı

Her yeni İCRA oturumunun ilk işi: güncel **yetkili** V3 kaynağını, sürümünü, SHA-256 kilidini ve ilgili projenin son doğrulanmış durumunu okumaktır. Başka bir ürünün sayacını kullanma. GitHub dokümanı ayrı bir ChatGPT sohbetine kendi başına bağlam taşımaz; oturum açılışında bu yol/bağlantı açıkça verilmeli veya bağlı GitHub üzerinden okunmalıdır.

**Tasarım rubriği 100/100**, yazarın teorik değerlendirmesidir. **Saha başarısı, real-time izinler ve resmi Verified Finish bu belgeyle otomatik kabul edilmiş sayılmaz.** Yeni sürüm için ayrı gözden geçirme, sürüm/lock SHA ve geçerli yetki gerekir.

## 4. Kalıcı sabit hedef

ENGÜRÜ Süzgeci™ **sekiz aşama** korunur. K1–K8 mevcut aşamalardaki kabul kontrolleridir; yeni çekirdek veya yeni aşama kurulmaz. Her ürünün gerçek canonical sözleşmesi ve korunmuş Human Threshold yetkileri geçerlidir.
